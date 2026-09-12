"""Fetch real College Scorecard data into the raw CSV shape the V2.1 pipeline expects.

The ingestion pipeline in `apps/api/ingestion/college_data.py` already reads Scorecard
column names (UNITID, ADM_RATE, NPT4_PUB, ...) and already treats "PrivacySuppressed" as
missing, so this script only has to produce that CSV. Normalization stays there.

Usage:
    python apps/api/scripts/fetch_scorecard.py --api-key "$SCORECARD_API_KEY"
    python apps/api/scripts/fetch_scorecard.py --api-key DEMO_KEY --per-slice 50

Then run the existing pipeline over the output:
    python apps/api/scripts/ingest_college_data.py import \\
        --source-year 2023 --data-version scorecard-2023.1

Selection rule (documented in docs/data-dictionary.md): the union of the N most selective
and the N largest-by-undergraduate-enrollment US doctoral universities, where "doctoral
university" is Carnegie Basic 15-17 and institutions are public or private nonprofit with
a predominant bachelor's degree. No magazine ranking is involved, and the rule is
reproducible from these filters alone.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_ROOT = "https://api.data.gov/ed/collegescorecard/v1/schools"

# Each metric group is pinned to ONE explicit year for every school, rather than using
# Scorecard's `latest.*` aliases. Scorecard's own docs warn that "latest" fields can
# describe different years, and a probe confirmed it: cost/admissions/completion carry
# data through 2023 while earnings and median debt stop at 2020. Pinning a single year
# per group means a column never mixes vintages across schools.
#
# ponytail: no per-school fallback to an older year. A school missing 2023 cost stays
# missing rather than silently borrowing 2022 and breaking comparability. Add per-row
# year columns first if you ever want that fallback.
REPORTING_YEARS = {
    "admissions": 2023,
    "student": 2023,
    "cost": 2023,
    "completion": 2023,
    "earnings": 2020,
    "debt": 2020,
}

# raw CSV column -> Scorecard API field path.
FIELD_MAP = {
    "UNITID": "id",
    "INSTNM": "school.name",
    "CITY": "school.city",
    "STABBR": "school.state",
    "CONTROL": "school.ownership",
    "LOCALE": "school.locale",
    "LATITUDE": "location.lat",
    "LONGITUDE": "location.lon",
    "UGDS": f"{REPORTING_YEARS['student']}.student.size",
    "ADM_RATE": f"{REPORTING_YEARS['admissions']}.admissions.admission_rate.overall",
    "C150_4": f"{REPORTING_YEARS['completion']}.completion.completion_rate_4yr_150nt",
    "RET_FT4": f"{REPORTING_YEARS['student']}.student.retention_rate.four_year.full_time",
    "TUITIONFEE_IN": f"{REPORTING_YEARS['cost']}.cost.tuition.in_state",
    "TUITIONFEE_OUT": f"{REPORTING_YEARS['cost']}.cost.tuition.out_of_state",
    "NPT4_PUB": f"{REPORTING_YEARS['cost']}.cost.avg_net_price.public",
    "NPT4_PRIV": f"{REPORTING_YEARS['cost']}.cost.avg_net_price.private",
    "DEBT_MDN": f"{REPORTING_YEARS['debt']}.aid.median_debt.completers.overall",
    "MD_EARN_WNE_P10": f"{REPORTING_YEARS['earnings']}.earnings.10_yrs_after_entry.median",
    "RPY_3YR_RT": "latest.repayment.repayment_cohort.3_year_declining_balance",
}

# Scorecard program_percentage buckets -> readable major names, for deriving top majors.
PROGRAM_LABELS = {
    "agriculture": "Agriculture",
    "architecture": "Architecture",
    "biology": "Biology",
    "business_marketing": "Business",
    "communication": "Communications",
    "computer": "Computer Science",
    "education": "Education",
    "engineering": "Engineering",
    "english": "English",
    "health": "Health Professions",
    "history": "History",
    "humanities": "Humanities",
    "language": "Languages",
    "legal": "Legal Studies",
    "mathematics": "Mathematics",
    "parks_recreation": "Parks and Recreation",
    "philosophy_religious": "Philosophy and Religion",
    "physical_science": "Physical Sciences",
    "psychology": "Psychology",
    "public_administration_social_service": "Public Administration",
    "security_law_enforcement": "Criminal Justice",
    "social_science": "Social Sciences",
    "theology_religious_vocation": "Theology",
    "visual_performing": "Visual and Performing Arts",
}

# Columns the pipeline accepts but College Scorecard does not publish. Left empty on
# purpose: "missing data is never zero" (CLAUDE.md). Populating these needs IPEDS, which
# is V3.0 follow-up work, not something to invent here.
UNAVAILABLE_COLUMNS = [
    "STUFACR",
    "housing_available",
    "sports_division",
    "greek_life_rate",
]

RAW_COLUMNS = [
    "UNITID", "INSTNM", "CITY", "STABBR", "CONTROL", "LOCALE", "UGDS", "ADM_RATE",
    "LATITUDE", "LONGITUDE", "programs.cip_4_digit.title", "C150_4", "RET_FT4",
    "STUFACR", "TUITIONFEE_IN", "TUITIONFEE_OUT", "NPT4_PUB", "NPT4_PRIV", "GRANT_AMT",
    "DEBT_MDN", "MD_EARN_WNE_P10", "RPY_3YR_RT", "housing_available", "sports_division",
    "greek_life_rate", "culture_tags",
]

# Doctoral universities (Carnegie Basic 15-17), public or private nonprofit, predominantly
# bachelor's-degree granting, currently operating.
BASE_FILTERS = {
    "school.carnegie_basic": "15,16,17",
    "school.ownership": "1,2",
    "school.degrees_awarded.predominant": "3",
    "school.operating": "1",
}

PROGRAM_FIELDS = [f"latest.academics.program_percentage.{key}" for key in PROGRAM_LABELS]

# The API only permits sorting and filtering on `latest.*` aliases, so selection uses
# those while the fetched values stay pinned to REPORTING_YEARS. Selection order is
# therefore "latest reported", which is fine: it decides which schools are in the sample,
# never what any displayed number says.
SORT_ADMISSION_RATE = "latest.admissions.admission_rate.overall"
SORT_ENROLLMENT = "latest.student.size"


def request_page(api_key: str, params: dict[str, str], timeout: int) -> dict:
    query = urllib.parse.urlencode({**params, "api_key": api_key})
    url = f"{API_ROOT}?{query}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:400]
        if error.code == 429:
            raise SystemExit(
                "Scorecard API rate limit reached. DEMO_KEY allows roughly 30 requests "
                "per hour; a free key with a much higher limit is issued instantly at "
                "https://api.data.gov/signup. Pass it with --api-key, then retry."
            ) from error
        raise SystemExit(f"Scorecard API returned {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise SystemExit(f"Could not reach the Scorecard API: {error.reason}") from error


def fetch_slice(api_key: str, sort: str, limit: int, timeout: int, extra: dict[str, str]) -> list[dict]:
    """Fetch `limit` schools for one selection slice, paging 100 at a time."""
    fields = ["id", *FIELD_MAP.values(), *PROGRAM_FIELDS]
    collected: list[dict] = []
    page = 0
    while len(collected) < limit:
        payload = request_page(
            api_key,
            {
                **BASE_FILTERS,
                **extra,
                "fields": ",".join(dict.fromkeys(fields)),
                "sort": sort,
                "per_page": "100",
                "page": str(page),
            },
            timeout,
        )
        results = payload.get("results") or []
        if not results:
            break
        collected.extend(results)
        page += 1
    return collected[:limit]


def top_majors(result: dict, count: int = 3) -> list[str]:
    shares = []
    for key, label in PROGRAM_LABELS.items():
        value = result.get(f"latest.academics.program_percentage.{key}")
        if isinstance(value, (int, float)) and value > 0:
            shares.append((float(value), label))
    shares.sort(key=lambda item: (-item[0], item[1]))
    return [label for _, label in shares[:count]]


def culture_tags(result: dict) -> list[str]:
    """Structural tags derived from reported fields only - never invented descriptors."""
    tags: list[str] = []
    ownership = result.get("school.ownership")
    if ownership == 1:
        tags.append("public")
    elif ownership == 2:
        tags.append("private-nonprofit")

    locale = result.get("school.locale")
    if isinstance(locale, int):
        tags.append({1: "urban", 2: "suburban", 3: "town", 4: "rural"}.get(locale // 10, ""))

    size = result.get(FIELD_MAP["UGDS"])
    if isinstance(size, (int, float)):
        if size >= 20000:
            tags.append("large")
        elif size >= 5000:
            tags.append("mid-size")
        else:
            tags.append("small")

    if result.get("school.carnegie_basic") == 15:
        tags.append("very-high-research")
    return sorted(tag for tag in tags if tag)


def to_raw_row(result: dict) -> dict[str, str]:
    row = {column: "" for column in RAW_COLUMNS}
    for column, field in FIELD_MAP.items():
        value = result.get(field)
        row[column] = "" if value is None else str(value)
    row["programs.cip_4_digit.title"] = "|".join(top_majors(result))
    row["culture_tags"] = "|".join(culture_tags(result))
    for column in UNAVAILABLE_COLUMNS:
        row[column] = ""
    row["GRANT_AMT"] = ""  # Scorecard publishes aid rates, not an average grant amount.
    return row


# Public and private net price are alternatives, not independent columns: a public
# school fills NPT4_PUB and a private one fills NPT4_PRIV, and the pipeline's pick()
# takes whichever is present. Counting them separately makes both look half-empty.
EITHER_OR_COLUMNS = {"NPT4_PUB": "NPT4_PRIV"}


def fill_report(rows: list[dict[str, str]]) -> list[tuple[str, int]]:
    """Per-column count of populated values. Catches a wrong year pin immediately."""
    report = []
    for column in RAW_COLUMNS:
        partner = EITHER_OR_COLUMNS.get(column)
        if column in EITHER_OR_COLUMNS.values():
            continue
        if partner:
            count = sum(
                1 for row in rows if row.get(column, "").strip() or row.get(partner, "").strip()
            )
            report.append((f"{column}/{partner}", count))
        else:
            report.append((column, sum(1 for row in rows if row.get(column, "").strip())))
    return report


def self_check() -> None:
    """Offline check of the pure transforms. Runs without an API key or network."""
    sample = {
        "id": 110635,
        "school.name": "University of California-Berkeley",
        "school.city": "Berkeley",
        "school.state": "CA",
        "school.ownership": 1,
        "school.locale": 12,
        "school.carnegie_basic": 15,
        "location.lat": 37.871918,
        FIELD_MAP["UGDS"]: 32831,
        FIELD_MAP["ADM_RATE"]: 0.1129,
        FIELD_MAP["MD_EARN_WNE_P10"]: None,
        "latest.academics.program_percentage.computer": 0.1909,
        "latest.academics.program_percentage.engineering": 0.1108,
        "latest.academics.program_percentage.social_science": 0.1405,
        "latest.academics.program_percentage.theology_religious_vocation": 0.0,
    }

    # Top majors: ranked by share, zero-share programs excluded, capped at three.
    assert top_majors(sample) == ["Computer Science", "Social Sciences", "Engineering"], top_majors(sample)
    assert "Theology" not in top_majors(sample)
    assert top_majors({}) == []

    # Tags come only from reported structural fields.
    tags = culture_tags(sample)
    assert tags == sorted(tags), "tags must be deterministic"
    assert "public" in tags and "urban" in tags and "large" in tags and "very-high-research" in tags, tags
    assert culture_tags({}) == []

    row = to_raw_row(sample)
    assert set(row) == set(RAW_COLUMNS), "row must match the raw CSV header exactly"
    assert row["UNITID"] == "110635"
    assert row["CONTROL"] == "1", "ownership must stay numeric for CONTROL_TYPES lookup"
    assert row["LOCALE"] == "12", "locale must stay numeric for LOCALE_SETTINGS lookup"
    # A null from the API must become an empty cell, never a zero.
    assert row["MD_EARN_WNE_P10"] == "", "missing earnings must be empty, not 0"
    for column in [*UNAVAILABLE_COLUMNS, "GRANT_AMT"]:
        assert row[column] == "", f"{column} must stay empty rather than invented"

    counts = dict(fill_report([row]))
    assert counts["UNITID"] == 1 and counts["MD_EARN_WNE_P10"] == 0

    print("self-check passed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--api-key", help="api.data.gov key, or DEMO_KEY for a rate-limited trial")
    parser.add_argument("--self-check", action="store_true", help="run offline transform checks and exit")
    parser.add_argument("--per-slice", type=int, default=50, help="schools per selection slice (default 50)")
    parser.add_argument(
        "--output",
        default="data/raw/college_snapshot.csv",
        help="raw CSV path consumed by ingest_college_data.py",
    )
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()

    if args.self_check:
        self_check()
        return
    if not args.api_key:
        raise SystemExit("--api-key is required (get a free key at https://api.data.gov/signup)")
    if args.per_slice < 1:
        raise SystemExit("--per-slice must be at least 1")

    print(f"Reporting years pinned per metric group: {REPORTING_YEARS}")

    selective = fetch_slice(
        args.api_key,
        sort=f"{SORT_ADMISSION_RATE}:asc",
        limit=args.per_slice,
        timeout=args.timeout,
        # A range bound forces a reported admission rate; sorting alone can surface nulls.
        extra={f"{SORT_ADMISSION_RATE}__range": "0.01..0.40"},
    )
    print(f"  most selective slice: {len(selective)}")

    largest = fetch_slice(
        args.api_key,
        sort=f"{SORT_ENROLLMENT}:desc",
        limit=args.per_slice,
        timeout=args.timeout,
        extra={f"{SORT_ENROLLMENT}__range": "1000.."},
    )
    print(f"  largest slice:        {len(largest)}")

    merged: dict[int, dict] = {}
    for result in [*selective, *largest]:
        unitid = result.get("id")
        if unitid is not None:
            merged.setdefault(int(unitid), result)
    if not merged:
        raise SystemExit("No schools returned - check the API key and filters.")

    rows = [to_raw_row(merged[unitid]) for unitid in sorted(merged)]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=RAW_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    overlap = len(selective) + len(largest) - len(merged)
    print(f"\nWrote {len(rows)} unique schools to {output} ({overlap} in both slices)")
    print("\nPopulated values per column:")
    for column, count in fill_report(rows):
        share = count / len(rows)
        flag = "  <-- empty" if count == 0 else ("  <-- sparse" if share < 0.5 else "")
        print(f"  {column:<30} {count:>4}/{len(rows)}{flag}")

    manifest = output.with_suffix(".manifest.json")
    manifest.write_text(
        json.dumps(
            {
                "reporting_years": REPORTING_YEARS,
                "school_count": len(rows),
                "selection_rule": {
                    "carnegie_basic": BASE_FILTERS["school.carnegie_basic"],
                    "ownership": BASE_FILTERS["school.ownership"],
                    "per_slice": args.per_slice,
                    "slices": ["most_selective_by_admission_rate", "largest_by_undergraduate_enrollment"],
                },
                "unavailable_columns": UNAVAILABLE_COLUMNS + ["GRANT_AMT"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote reporting-year manifest to {manifest}")


if __name__ == "__main__":
    sys.exit(main())
