"""Fetch real College Scorecard data, plus an IPEDS supplement, into the raw CSV shape
the V2.1 pipeline expects.

The ingestion pipeline in `apps/api/ingestion/college_data.py` already reads Scorecard
column names (UNITID, ADM_RATE, NPT4_PUB, ...) and already treats "PrivacySuppressed" as
missing, so this script only has to produce that CSV. Normalization stays there.

Scorecard does not publish student-faculty ratio, on-campus housing, athletics division,
or an average grant amount, so those four columns come from IPEDS through the keyless
Urban Institute Education Data API (EADA for athletics).

Usage:
    python apps/api/scripts/fetch_scorecard.py --api-key "$SCORECARD_API_KEY"
    python apps/api/scripts/fetch_scorecard.py --api-key DEMO_KEY --per-slice 50

Then run the existing pipeline over the output:
    python apps/api/scripts/ingest_college_data.py import \\
        --source-year 2023 --data-version scorecard-2023.1

Selection rule (documented in docs/data-dictionary.md): the union of the N most selective
and the N largest-by-undergraduate-enrollment US doctoral universities, where "doctoral
university" is Carnegie Basic 15-17 and institutions are public or private nonprofit with
a predominant bachelor's degree, excluding online-only institutions. No magazine ranking
is involved, and the rule is reproducible from these filters alone.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ingestion.college_data import REPORTING_YEARS  # noqa: E402

API_ROOT = "https://api.data.gov/ed/collegescorecard/v1/schools"
IPEDS_ROOT = "https://educationdata.urban.org/api/v1/college-university"

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

# Columns the pipeline accepts but no official source publishes. Left empty on purpose:
# "missing data is never zero" (CLAUDE.md).
UNAVAILABLE_COLUMNS = ["greek_life_rate"]

RAW_COLUMNS = [
    "UNITID", "INSTNM", "CITY", "STABBR", "CONTROL", "LOCALE", "UGDS", "ADM_RATE",
    "LATITUDE", "LONGITUDE", "programs.cip_4_digit.title", "C150_4", "RET_FT4",
    "STUFACR", "TUITIONFEE_IN", "TUITIONFEE_OUT", "NPT4_PUB", "NPT4_PRIV", "GRANT_AMT",
    "DEBT_MDN", "MD_EARN_WNE_P10", "RPY_3YR_RT", "housing_available", "sports_division",
    "greek_life_rate", "culture_tags",
]

# Doctoral universities (Carnegie Basic 15-17), public or private nonprofit, predominantly
# bachelor's-degree granting, currently operating. Online-only institutions are excluded
# in is_campus() instead of here: the API rejects school.online_only as a filter column.
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

# "NCAA Division I-FBS", "NCAA Division III without football", and free-text "Other"
# notes such as "NCAA DIII w/FB; M/W LAX DI". Longest numeral first so III is not read as I.
DIVISION_PATTERN = re.compile(r"\b(?:Division|D)\s*(III|II|I)\b")


def urlopen_json(url: str, timeout: int, attempts: int = 3) -> dict:
    """GET a JSON document, retrying transient failures with a short backoff.

    A single read timeout from the Urban Institute API once killed a full refresh even
    though the identical request answered in 0.2s moments later. Timeouts, dropped
    connections, and 5xx responses are retried. Client errors are not: a malformed query
    will not fix itself, and Scorecard's 429 is an hourly limit no quick retry can clear.
    """
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            # HTTPError subclasses URLError, so it has to be handled before the clause below.
            if error.code < 500 or attempt == attempts:
                raise
        except (TimeoutError, ConnectionError, urllib.error.URLError):
            if attempt == attempts:
                raise
        time.sleep(2**attempt)
    raise AssertionError("unreachable: the final attempt either returns or raises")


def request_page(api_key: str, params: dict[str, str], timeout: int) -> dict:
    query = urllib.parse.urlencode({**params, "api_key": api_key})
    url = f"{API_ROOT}?{query}"
    try:
        return urlopen_json(url, timeout)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:400]
        if error.code == 429:
            raise SystemExit(
                "Scorecard API rate limit reached. DEMO_KEY allows roughly 30 requests "
                "per hour; a free key with a much higher limit is issued instantly at "
                "https://api.data.gov/signup. Pass it with --api-key, then retry."
            ) from error
        raise SystemExit(f"Scorecard API returned {error.code}: {detail}") from error
    except (OSError, ValueError) as error:
        # Includes read timeouts, which are not URLError subclasses and used to escape as a
        # raw traceback. The message never includes the URL, which carries the API key.
        raise SystemExit(f"Could not reach the Scorecard API: {error!r}") from error


def is_campus(result: dict) -> bool:
    """Online-only units are not campuses a student can explore.

    ASU Digital Immersion entered the largest-enrollment slice on headcount alone, with no
    housing, aid, or athletics record. A missing flag keeps the school: exclusion needs a
    reported value, not an absent one.
    """
    return result.get("school.online_only") != 1


# Every Scorecard field the script reads, including ones that are not raw CSV columns:
# is_campus() reads online_only and culture_tags() reads carnegie_basic. Leaving one out
# fails silently - carnegie_basic was once missing, so no school ever received the
# very-high-research tag, while the self-check passed on a hand-built sample.
REQUESTED_FIELDS = ["id", "school.online_only", "school.carnegie_basic", *FIELD_MAP.values(), *PROGRAM_FIELDS]


def fetch_slice(api_key: str, sort: str, limit: int, timeout: int, extra: dict[str, str]) -> list[dict]:
    """Fetch `limit` schools for one selection slice, paging 100 at a time."""
    fields = REQUESTED_FIELDS
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
        # Filtered while paging, so each slice still reaches `limit` campuses.
        collected.extend(result for result in results if is_campus(result))
        page += 1
    return collected[:limit]


def ipeds_rows(path: str, unitids: list[int], timeout: int, **filters: str) -> dict[int, dict]:
    """One row per school from an Urban Institute IPEDS endpoint, following pagination.

    ponytail: every unitid goes in one query string. Fine for a ~100-school corpus; chunk
    the id list if the corpus grows into the thousands and the URL gets too long.
    """
    query = urllib.parse.urlencode({"unitid": ",".join(map(str, unitids)), **filters}, safe=",")
    url: str | None = f"{IPEDS_ROOT}/{path}/?{query}"
    rows: dict[int, dict] = {}
    while url:
        try:
            payload = urlopen_json(url, timeout)
        except (OSError, ValueError) as error:
            # Retries are exhausted by now. OSError covers HTTP, URL, and socket errors,
            # including read timeouts; ValueError covers a malformed JSON body. Fail the whole
            # refresh rather than write Scorecard rows with silently blank IPEDS columns,
            # which would look like a real data regression.
            raise SystemExit(f"IPEDS request failed for {path}: {error!r}") from error
        for row in payload.get("results") or []:
            # Re-check the filters client-side so an ignored query parameter cannot let a
            # different aid type or student population overwrite the intended row.
            if all(str(row.get(key)) == value for key, value in filters.items()):
                rows[int(row["unitid"])] = row
        url = payload.get("next")
    return rows


def ipeds_number(value: object) -> str:
    """IPEDS reports missing, not-applicable, and suppressed as -1, -2, -3: never values."""
    if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
        return str(int(value)) if float(value).is_integer() else str(value)
    return ""


def ipeds_housing(value: object) -> str:
    """1 = provides on-campus housing, 0 = does not. Anything else is unknown, not "no"."""
    if isinstance(value, bool) or not isinstance(value, int):
        return ""
    return {1: "true", 0: "false"}.get(value, "")


def athletics_division(name: object, other: object) -> str:
    """Map an EADA classification to the DI/DII/DIII/NAIA values the ranking engine matches.

    "Other" is resolved from its free-text note, where the first division named is the
    institution's primary one (Johns Hopkins: DIII overall, Division I lacrosse). A note
    with no recognisable division stays empty rather than guessed.
    """
    text = other if name == "Other" else name
    if not isinstance(text, str) or not text.strip():
        return ""
    if "NAIA" in text.upper():
        return "NAIA"
    match = DIVISION_PATTERN.search(text)
    return f"D{match.group(1)}" if match else ""


def fetch_ipeds(unitids: list[int], timeout: int) -> dict[int, dict[str, str]]:
    """Fill the four columns Scorecard does not publish, each pinned to its REPORTING_YEARS year."""
    ratio = ipeds_rows(f"ipeds/student-faculty-ratio/{REPORTING_YEARS['student_faculty']}", unitids, timeout)
    characteristics = ipeds_rows(
        f"ipeds/institutional-characteristics/{REPORTING_YEARS['housing']}", unitids, timeout
    )
    athletics = ipeds_rows(f"eada/institutional-characteristics/{REPORTING_YEARS['athletics']}", unitids, timeout)
    # All grant aid - federal, state, local, and institutional (type_of_aid 3) - which
    # excludes loans, since a loan does not reduce what a family pays. Population is
    # first-time, full-time, degree-seeking undergraduates, and the amount is an average
    # among students who received a grant, not across every student.
    aid = ipeds_rows(
        f"ipeds/sfa-ftft/{REPORTING_YEARS['aid']}",
        unitids,
        timeout,
        type_of_aid="3",
        ftpt="1",
        class_level="1",
        level_of_study="1",
        degree_seeking="1",
    )

    supplement: dict[int, dict[str, str]] = {}
    for unitid in unitids:
        eada = athletics.get(unitid, {})
        supplement[unitid] = {
            "STUFACR": ipeds_number(ratio.get(unitid, {}).get("student_faculty_ratio")),
            "housing_available": ipeds_housing(characteristics.get(unitid, {}).get("oncampus_housing")),
            "sports_division": athletics_division(
                eada.get("ath_classification_name"), eada.get("ath_classification_other")
            ),
            "GRANT_AMT": ipeds_number(aid.get(unitid, {}).get("average_amount")),
        }
    return supplement


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
    # STUFACR, GRANT_AMT, housing_available, and sports_division stay empty here: Scorecard
    # does not publish them, and main() fills them from fetch_ipeds().
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
    # Scorecard does not publish these; they stay empty here until fetch_ipeds() fills them.
    for column in ["STUFACR", "GRANT_AMT", "housing_available", "sports_division", *UNAVAILABLE_COLUMNS]:
        assert row[column] == "", f"{column} must not be invented from Scorecard fields"

    counts = dict(fill_report([row]))
    assert counts["UNITID"] == 1 and counts["MD_EARN_WNE_P10"] == 0

    # Online-only units are excluded, but only on a reported flag.
    assert is_campus({"school.online_only": 0}) and not is_campus({"school.online_only": 1})
    assert is_campus({}), "a missing flag must not exclude a school"

    # IPEDS negative codes are missing / not applicable / suppressed, never values.
    assert ipeds_number(18) == "18" and ipeds_number(21669.0) == "21669"
    assert ipeds_number(-1) == "" and ipeds_number(-3) == "" and ipeds_number(None) == ""
    assert ipeds_number(True) == "", "a boolean is not a count"
    assert ipeds_housing(1) == "true" and ipeds_housing(0) == "false"
    assert ipeds_housing(-1) == "" and ipeds_housing(None) == "", "unknown housing is not 'no'"

    # Every EADA classification present in the corpus, plus the edge cases.
    assert athletics_division("NCAA Division I-FBS", "") == "DI"
    assert athletics_division("NCAA Division I-FCS", "") == "DI"
    assert athletics_division("NCAA Division I without football", "") == "DI"
    assert athletics_division("NCAA Division II with football", "") == "DII"
    assert athletics_division("NCAA Division II without football", "") == "DII"
    assert athletics_division("NCAA Division III with football", "") == "DIII"
    assert athletics_division("NCAA Division III without football", "") == "DIII"
    assert athletics_division("Other", "NCAA DIII w/FB; M/W LAX DI") == "DIII", "primary division wins"
    assert athletics_division("NAIA Division I", "") == "NAIA"
    assert athletics_division("Other", "") == "" and athletics_division(None, None) == ""
    assert athletics_division("Other", "NJCAA") == "", "no recognisable division stays empty"

    # Transient failures retry; client errors do not. urlopen and sleep are swapped for
    # fakes so this stays offline and instant.
    class FakeResponse(io.BytesIO):
        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *exc: object) -> None:
            self.close()

    calls: list[str] = []
    real_urlopen, real_sleep = urllib.request.urlopen, time.sleep

    def flaky(url: str, timeout: int) -> FakeResponse:
        calls.append(url)
        if len(calls) == 1:
            raise TimeoutError("The read operation timed out")
        return FakeResponse(b'{"ok": true}')

    def client_error(url: str, timeout: int) -> FakeResponse:
        calls.append(url)
        raise urllib.error.HTTPError(url, 400, "Bad Request", {}, None)

    urllib.request.urlopen, time.sleep = flaky, lambda seconds: None
    try:
        assert urlopen_json("https://example.test/a", 1) == {"ok": True}
        assert len(calls) == 2, "one timeout, then success on the retry"

        calls.clear()
        urllib.request.urlopen = client_error
        try:
            urlopen_json("https://example.test/b", 1)
            raise AssertionError("a 400 must be raised, not swallowed")
        except urllib.error.HTTPError:
            assert len(calls) == 1, "a client error must not be retried"
    finally:
        urllib.request.urlopen, time.sleep = real_urlopen, real_sleep

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

    unitids = sorted(merged)
    print(f"  IPEDS supplement for {len(unitids)} schools")
    supplement = fetch_ipeds(unitids, args.timeout)
    rows = []
    for unitid in unitids:
        row = to_raw_row(merged[unitid])
        row.update(supplement[unitid])
        rows.append(row)

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
                "sources": {"scorecard": API_ROOT, "ipeds": IPEDS_ROOT},
                "selection_rule": {
                    "carnegie_basic": BASE_FILTERS["school.carnegie_basic"],
                    "ownership": BASE_FILTERS["school.ownership"],
                    "online_only": "excluded",
                    "per_slice": args.per_slice,
                    "slices": ["most_selective_by_admission_rate", "largest_by_undergraduate_enrollment"],
                },
                "unavailable_columns": UNAVAILABLE_COLUMNS,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote reporting-year manifest to {manifest}")


if __name__ == "__main__":
    sys.exit(main())
