from __future__ import annotations

import argparse
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

from ingestion.college_data import (
    IngestionMetadata,
    normalize_records,
    read_raw_csv,
    run_pipeline,
    utc_timestamp,
    validate_records,
    write_seed_csv,
)


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RAW_PATH = ROOT / "data" / "raw" / "college_snapshot.csv"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "processed" / "schools_ingested.csv"


def build_metadata(args: argparse.Namespace, refreshed: bool = False) -> IngestionMetadata:
    timestamp = args.imported_at or utc_timestamp()
    return IngestionMetadata(
        source_name=args.source_name,
        source_year=args.source_year,
        data_version=args.data_version,
        imported_at=timestamp,
        refreshed_at=timestamp if refreshed else args.refreshed_at,
    )


def load_records(args: argparse.Namespace, refreshed: bool = False):
    return normalize_records(read_raw_csv(Path(args.raw_file)), build_metadata(args, refreshed=refreshed))


def print_report(report) -> None:
    for warning in report.warnings:
        print(f"WARNING: {warning}")
    for error in report.errors:
        print(f"ERROR: {error}")
    print("Validation passed" if report.ok else "Validation failed")


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--raw-file", default=str(DEFAULT_RAW_PATH))
    parser.add_argument("--output-file", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--source-name", default="public_college_snapshot")
    parser.add_argument("--source-year", type=int, required=True)
    parser.add_argument("--data-version", required=True)
    parser.add_argument("--imported-at")
    parser.add_argument("--refreshed-at")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V2.1 college data ingestion pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("import", "validate", "seed", "refresh"):
        add_common_args(subparsers.add_parser(command))
    args = parser.parse_args()

    raw_path = Path(args.raw_file)
    output_path = Path(args.output_file)

    if args.command == "import":
        records = load_records(args)
        print(f"Imported {len(records)} raw records from {raw_path}")
        return

    if args.command == "validate":
        report = validate_records(load_records(args))
        print_report(report)
        raise SystemExit(0 if report.ok else 1)

    if args.command == "seed":
        records = load_records(args)
        report = validate_records(records)
        print_report(report)
        if not report.ok:
            raise SystemExit(1)
        write_seed_csv(records, output_path)
        print(f"Wrote seed output to {output_path}")
        return

    report = run_pipeline(raw_path, output_path, build_metadata(args, refreshed=True))
    print_report(report)
    if not report.ok:
        raise SystemExit(1)
    print(f"Refreshed seed output at {output_path}")


if __name__ == "__main__":
    main()
