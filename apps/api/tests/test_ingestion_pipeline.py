from pathlib import Path

from ingestion.college_data import (
    IngestionMetadata,
    ProductSchoolRecord,
    normalize_records,
    read_raw_csv,
    validate_records,
    write_seed_csv,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "public_college_snapshot.csv"
METADATA = IngestionMetadata(
    source_name="college_scorecard_fixture",
    source_year=2024,
    data_version="fixture-v1",
    imported_at="2026-05-20T00:00:00Z",
)


def test_successful_import_on_small_fixture() -> None:
    raw_rows = read_raw_csv(FIXTURE_PATH)
    records = normalize_records(raw_rows, METADATA)
    report = validate_records(records)

    assert report.ok
    assert [record.unitid for record in records] == [100001, 100002]
    assert records[0].source_name == "college_scorecard_fixture"
    assert records[0].data_version == "fixture-v1"


def test_normalization_maps_public_source_fields() -> None:
    records = normalize_records(read_raw_csv(FIXTURE_PATH), METADATA)
    public_school = records[0]

    assert public_school.name == "Example Public University"
    assert public_school.state == "CA"
    assert public_school.region == "West"
    assert public_school.type == "Public"
    assert public_school.setting == "Urban"
    assert public_school.net_price == 18500
    assert public_school.top_majors == ["Business", "Computer Science"]


def test_missing_values_remain_none_and_warn_for_confidence_inputs() -> None:
    records = normalize_records(read_raw_csv(FIXTURE_PATH), METADATA)
    missing_school = records[1]
    report = validate_records(records)

    assert missing_school.acceptance_rate is None
    assert missing_school.retention_rate is None
    assert missing_school.net_price == 29500
    assert missing_school.debt_median is None
    assert missing_school.repayment_rate is None
    assert any("unavailable ranking inputs" in warning for warning in report.warnings)


def test_validation_failures_include_range_and_duplicate_errors() -> None:
    records = [
        ProductSchoolRecord(
            unitid=1,
            name="Bad Rate University",
            city="Nowhere",
            state="C",
            region="Unknown",
            type="Public",
            setting="Urban",
            acceptance_rate=1.4,
            source_name="fixture",
            source_year=2024,
            data_version="bad",
            imported_at="2026-05-20T00:00:00Z",
        ),
        ProductSchoolRecord(
            unitid=1,
            name="Duplicate University",
            city="Nowhere",
            state="CA",
            region="West",
            type="Public",
            setting="Urban",
            net_price=-1,
            source_name="fixture",
            source_year=2024,
            data_version="bad",
            imported_at="2026-05-20T00:00:00Z",
        ),
    ]

    report = validate_records(records)

    assert not report.ok
    assert any("state must be a two-letter code" in error for error in report.errors)
    assert any("acceptance_rate must be between 0 and 1" in error for error in report.errors)
    assert any("duplicate unitid" in error for error in report.errors)
    assert any("net_price must be nonnegative" in error for error in report.errors)


def test_seed_output_is_deterministic(tmp_path: Path) -> None:
    records = normalize_records(reversed(read_raw_csv(FIXTURE_PATH)), METADATA)
    first_output = tmp_path / "first.csv"
    second_output = tmp_path / "second.csv"

    write_seed_csv(records, first_output)
    write_seed_csv(records, second_output)

    assert first_output.read_text(encoding="utf-8") == second_output.read_text(encoding="utf-8")
    assert first_output.read_text(encoding="utf-8").splitlines()[0].endswith("refreshed_at")
