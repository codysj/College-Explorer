from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


SEED_COLUMNS = [
    "unitid",
    "name",
    "city",
    "state",
    "region",
    "type",
    "setting",
    "undergraduate_enrollment",
    "acceptance_rate",
    "latitude",
    "longitude",
    "top_majors",
    "graduation_rate",
    "retention_rate",
    "student_faculty_ratio",
    "tuition_in_state",
    "tuition_out_state",
    "net_price",
    "average_aid",
    "debt_median",
    "median_earnings",
    "repayment_rate",
    "housing_available",
    "sports_division",
    "greek_life_rate",
    "culture_tags",
    "source_name",
    "source_year",
    "data_version",
    "imported_at",
    "refreshed_at",
]

MISSING_TOKENS = {"", "null", "none", "nan", "privacy suppressed", "privacysuppressed"}

STATE_REGIONS = {
    "CT": "Northeast",
    "ME": "Northeast",
    "MA": "Northeast",
    "NH": "Northeast",
    "NJ": "Northeast",
    "NY": "Northeast",
    "PA": "Northeast",
    "RI": "Northeast",
    "VT": "Northeast",
    "AL": "South",
    "AR": "South",
    "DE": "South",
    "FL": "South",
    "GA": "South",
    "KY": "South",
    "LA": "South",
    "MD": "South",
    "MS": "South",
    "NC": "South",
    "OK": "South",
    "SC": "South",
    "TN": "South",
    "TX": "South",
    "VA": "South",
    "WV": "South",
    "IA": "Midwest",
    "IL": "Midwest",
    "IN": "Midwest",
    "KS": "Midwest",
    "MI": "Midwest",
    "MN": "Midwest",
    "MO": "Midwest",
    "ND": "Midwest",
    "NE": "Midwest",
    "OH": "Midwest",
    "SD": "Midwest",
    "WI": "Midwest",
    "AZ": "West",
    "CA": "West",
    "CO": "Mountain",
    "ID": "Mountain",
    "MT": "Mountain",
    "NM": "Mountain",
    "NV": "West",
    "OR": "West",
    "UT": "Mountain",
    "WA": "West",
    "WY": "Mountain",
}

CONTROL_TYPES = {
    "1": "Public",
    "2": "Private",
    "3": "Private",
    "public": "Public",
    "private": "Private",
    "private nonprofit": "Private",
    "private for-profit": "Private",
}

LOCALE_SETTINGS = {
    "11": "Urban",
    "12": "Urban",
    "13": "Urban",
    "21": "Suburban",
    "22": "Suburban",
    "23": "Suburban",
    "31": "Town",
    "32": "Town",
    "33": "Town",
    "41": "Rural",
    "42": "Rural",
    "43": "Rural",
}


@dataclass(frozen=True)
class IngestionMetadata:
    source_name: str
    source_year: int
    data_version: str
    imported_at: str
    refreshed_at: str | None = None


@dataclass(frozen=True)
class ProductSchoolRecord:
    unitid: int
    name: str
    city: str
    state: str
    region: str
    type: str
    setting: str
    undergraduate_enrollment: int | None = None
    acceptance_rate: float | None = None
    latitude: float | None = None
    longitude: float | None = None
    top_majors: list[str] = field(default_factory=list)
    graduation_rate: float | None = None
    retention_rate: float | None = None
    student_faculty_ratio: float | None = None
    tuition_in_state: int | None = None
    tuition_out_state: int | None = None
    net_price: int | None = None
    average_aid: int | None = None
    debt_median: int | None = None
    median_earnings: int | None = None
    repayment_rate: float | None = None
    housing_available: bool | None = None
    sports_division: str | None = None
    greek_life_rate: float | None = None
    culture_tags: list[str] = field(default_factory=list)
    source_name: str = ""
    source_year: int = 0
    data_version: str = ""
    imported_at: str = ""
    refreshed_at: str | None = None

    def seed_row(self) -> dict[str, str]:
        return {
            "unitid": str(self.unitid),
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "region": self.region,
            "type": self.type,
            "setting": self.setting,
            "undergraduate_enrollment": format_optional(self.undergraduate_enrollment),
            "acceptance_rate": format_optional(self.acceptance_rate, 4),
            "latitude": format_optional(self.latitude, 6),
            "longitude": format_optional(self.longitude, 6),
            "top_majors": "|".join(self.top_majors),
            "graduation_rate": format_optional(self.graduation_rate, 4),
            "retention_rate": format_optional(self.retention_rate, 4),
            "student_faculty_ratio": format_optional(self.student_faculty_ratio, 1),
            "tuition_in_state": format_optional(self.tuition_in_state),
            "tuition_out_state": format_optional(self.tuition_out_state),
            "net_price": format_optional(self.net_price),
            "average_aid": format_optional(self.average_aid),
            "debt_median": format_optional(self.debt_median),
            "median_earnings": format_optional(self.median_earnings),
            "repayment_rate": format_optional(self.repayment_rate, 4),
            "housing_available": "" if self.housing_available is None else str(self.housing_available).lower(),
            "sports_division": self.sports_division or "",
            "greek_life_rate": format_optional(self.greek_life_rate, 4),
            "culture_tags": "|".join(self.culture_tags),
            "source_name": self.source_name,
            "source_year": str(self.source_year),
            "data_version": self.data_version,
            "imported_at": self.imported_at,
            "refreshed_at": self.refreshed_at or "",
        }


@dataclass(frozen=True)
class ValidationReport:
    errors: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.errors


def utc_timestamp() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_raw_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def normalize_records(raw_rows: Iterable[dict[str, str]], metadata: IngestionMetadata) -> list[ProductSchoolRecord]:
    records = [normalize_record(row, metadata) for row in raw_rows]
    return sorted(records, key=lambda record: record.unitid)


def normalize_record(row: dict[str, str], metadata: IngestionMetadata) -> ProductSchoolRecord:
    state = (text_value(pick(row, "state", "STABBR")) or "").upper()
    school_type = normalize_type(pick(row, "type", "CONTROL"))
    setting = normalize_setting(pick(row, "setting", "LOCALE"))
    region = text_value(pick(row, "region")) or STATE_REGIONS.get(state) or "Unknown"
    top_majors = list_value(pick(row, "top_majors", "programs.cip_4_digit.title", "majors"))
    culture_tags = list_value(pick(row, "culture_tags"))
    net_price = int_value(pick(row, "net_price", "NPT4_PUB", "NPT4_PRIV"))

    return ProductSchoolRecord(
        unitid=required_int(pick(row, "unitid", "UNITID"), "unitid"),
        name=required_text(pick(row, "name", "INSTNM"), "name"),
        city=required_text(pick(row, "city", "CITY"), "city"),
        state=required_text(state, "state"),
        region=region,
        type=school_type,
        setting=setting,
        undergraduate_enrollment=int_value(pick(row, "undergraduate_enrollment", "UGDS")),
        acceptance_rate=rate_value(pick(row, "acceptance_rate", "ADM_RATE")),
        latitude=float_value(pick(row, "latitude", "LATITUDE")),
        longitude=float_value(pick(row, "longitude", "LONGITUDE")),
        top_majors=top_majors,
        graduation_rate=rate_value(pick(row, "graduation_rate", "C150_4")),
        retention_rate=rate_value(pick(row, "retention_rate", "RET_FT4")),
        student_faculty_ratio=float_value(pick(row, "student_faculty_ratio", "STUFACR")),
        tuition_in_state=int_value(pick(row, "tuition_in_state", "TUITIONFEE_IN")),
        tuition_out_state=int_value(pick(row, "tuition_out_state", "TUITIONFEE_OUT")),
        net_price=net_price,
        average_aid=int_value(pick(row, "average_aid", "GRANT_AMT")),
        debt_median=int_value(pick(row, "debt_median", "DEBT_MDN")),
        median_earnings=int_value(pick(row, "median_earnings", "MD_EARN_WNE_P10")),
        repayment_rate=rate_value(pick(row, "repayment_rate", "RPY_3YR_RT")),
        housing_available=bool_value(pick(row, "housing_available")),
        sports_division=text_value(pick(row, "sports_division")),
        greek_life_rate=rate_value(pick(row, "greek_life_rate")),
        culture_tags=culture_tags,
        source_name=metadata.source_name,
        source_year=metadata.source_year,
        data_version=metadata.data_version,
        imported_at=metadata.imported_at,
        refreshed_at=metadata.refreshed_at,
    )


def validate_records(records: Iterable[ProductSchoolRecord]) -> ValidationReport:
    errors: list[str] = []
    warnings: list[str] = []
    unitids: set[int] = set()
    records_list = list(records)
    for index, record in enumerate(records_list, start=1):
        label = f"row {index} unitid {record.unitid}"
        if record.unitid in unitids:
            errors.append(f"{label}: duplicate unitid")
        unitids.add(record.unitid)
        if len(record.state) != 2:
            errors.append(f"{label}: state must be a two-letter code")
        if record.region == "Unknown":
            warnings.append(f"{label}: region unavailable")
        for field_name in ("acceptance_rate", "graduation_rate", "retention_rate", "repayment_rate", "greek_life_rate"):
            value = getattr(record, field_name)
            if value is not None and not 0 <= value <= 1:
                errors.append(f"{label}: {field_name} must be between 0 and 1")
        for field_name in (
            "undergraduate_enrollment",
            "tuition_in_state",
            "tuition_out_state",
            "net_price",
            "average_aid",
            "debt_median",
            "median_earnings",
        ):
            value = getattr(record, field_name)
            if value is not None and value < 0:
                errors.append(f"{label}: {field_name} must be nonnegative")
        missing_scoring_fields = [
            name
            for name in ("acceptance_rate", "graduation_rate", "net_price", "median_earnings", "repayment_rate")
            if getattr(record, name) is None
        ]
        if missing_scoring_fields:
            warnings.append(f"{label}: unavailable ranking inputs: {', '.join(missing_scoring_fields)}")
    if not records_list:
        errors.append("snapshot contains no records")
    return ValidationReport(errors=errors, warnings=warnings)


def write_seed_csv(records: Iterable[ProductSchoolRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [record.seed_row() for record in sorted(records, key=lambda record: record.unitid)]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=SEED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def run_pipeline(raw_path: Path, output_path: Path, metadata: IngestionMetadata) -> ValidationReport:
    records = normalize_records(read_raw_csv(raw_path), metadata)
    report = validate_records(records)
    if report.ok:
        write_seed_csv(records, output_path)
    return report


def pick(row: dict[str, str], *keys: str) -> str | None:
    lower_lookup = {key.lower(): key for key in row}
    for key in keys:
        actual_key = key if key in row else lower_lookup.get(key.lower())
        if actual_key is None:
            continue
        value = row.get(actual_key)
        if text_value(value) is not None:
            return value
    return None


def is_missing(value: str | None) -> bool:
    return value is None or value.strip().lower() in MISSING_TOKENS


def text_value(value: str | None) -> str | None:
    if is_missing(value):
        return None
    return value.strip()


def required_text(value: str | None, field_name: str) -> str:
    text = text_value(value)
    if text is None:
        raise ValueError(f"{field_name} is required")
    return text


def required_int(value: str | None, field_name: str) -> int:
    parsed = int_value(value)
    if parsed is None:
        raise ValueError(f"{field_name} is required")
    return parsed


def int_value(value: str | None) -> int | None:
    text = text_value(value)
    return int(float(text)) if text is not None else None


def float_value(value: str | None) -> float | None:
    text = text_value(value)
    return float(text) if text is not None else None


def rate_value(value: str | None) -> float | None:
    return float_value(value)


def bool_value(value: str | None) -> bool | None:
    text = text_value(value)
    if text is None:
        return None
    lowered = text.lower()
    if lowered in {"true", "t", "1", "yes", "y"}:
        return True
    if lowered in {"false", "f", "0", "no", "n"}:
        return False
    raise ValueError(f"invalid boolean value: {value}")


def list_value(value: str | None) -> list[str]:
    text = text_value(value)
    if text is None:
        return []
    delimiter = "|" if "|" in text else ";"
    return sorted({item.strip() for item in text.split(delimiter) if item.strip()})


def normalize_type(value: str | None) -> str:
    text = text_value(value)
    if text is None:
        return "Unknown"
    return CONTROL_TYPES.get(text.lower(), text)


def normalize_setting(value: str | None) -> str:
    text = text_value(value)
    if text is None:
        return "Unknown"
    return LOCALE_SETTINGS.get(text, text)


def format_optional(value: int | float | None, decimals: int | None = None) -> str:
    if value is None:
        return ""
    if decimals is None:
        return str(value)
    return f"{value:.{decimals}f}"

