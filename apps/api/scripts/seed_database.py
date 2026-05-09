import argparse
import csv
import os
from pathlib import Path

import psycopg


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SEED_PATH = ROOT / "data" / "seed" / "schools_seed.csv"
DEFAULT_DATABASE_URL = "postgresql://college:college@localhost:5432/college_exploration"


def nullable_int(value: str) -> int | None:
    return int(value) if value else None


def nullable_float(value: str) -> float | None:
    return float(value) if value else None


def split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def seed_school(conn: psycopg.Connection, row: dict[str, str]) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO schools (
                unitid, name, city, state, region, type, setting,
                undergraduate_enrollment, acceptance_rate, latitude, longitude,
                source_name, source_year
            )
            VALUES (
                %(unitid)s, %(name)s, %(city)s, %(state)s, %(region)s, %(type)s, %(setting)s,
                %(undergraduate_enrollment)s, %(acceptance_rate)s, %(latitude)s, %(longitude)s,
                'synthetic_v1_seed', 2026
            )
            ON CONFLICT (unitid) DO UPDATE SET
                name = EXCLUDED.name,
                city = EXCLUDED.city,
                state = EXCLUDED.state,
                region = EXCLUDED.region,
                type = EXCLUDED.type,
                setting = EXCLUDED.setting,
                undergraduate_enrollment = EXCLUDED.undergraduate_enrollment,
                acceptance_rate = EXCLUDED.acceptance_rate,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                source_name = EXCLUDED.source_name,
                source_year = EXCLUDED.source_year,
                updated_at = now()
            RETURNING id
            """,
            {
                "unitid": int(row["unitid"]),
                "name": row["name"],
                "city": row["city"],
                "state": row["state"],
                "region": row["region"],
                "type": row["type"],
                "setting": row["setting"],
                "undergraduate_enrollment": nullable_int(row["undergraduate_enrollment"]),
                "acceptance_rate": nullable_float(row["acceptance_rate"]),
                "latitude": nullable_float(row["latitude"]),
                "longitude": nullable_float(row["longitude"]),
            },
        )
        school_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO school_academics (
                school_id, top_majors, graduation_rate, retention_rate, student_faculty_ratio
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (school_id) DO UPDATE SET
                top_majors = EXCLUDED.top_majors,
                graduation_rate = EXCLUDED.graduation_rate,
                retention_rate = EXCLUDED.retention_rate,
                student_faculty_ratio = EXCLUDED.student_faculty_ratio
            """,
            (
                school_id,
                split_list(row["top_majors"]),
                nullable_float(row["graduation_rate"]),
                nullable_float(row["retention_rate"]),
                nullable_float(row["student_faculty_ratio"]),
            ),
        )

        cur.execute(
            """
            INSERT INTO school_costs (
                school_id, tuition_in_state, tuition_out_state, net_price, average_aid, debt_median
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (school_id) DO UPDATE SET
                tuition_in_state = EXCLUDED.tuition_in_state,
                tuition_out_state = EXCLUDED.tuition_out_state,
                net_price = EXCLUDED.net_price,
                average_aid = EXCLUDED.average_aid,
                debt_median = EXCLUDED.debt_median
            """,
            (
                school_id,
                nullable_int(row["tuition_in_state"]),
                nullable_int(row["tuition_out_state"]),
                nullable_int(row["net_price"]),
                nullable_int(row["average_aid"]),
                nullable_int(row["debt_median"]),
            ),
        )

        cur.execute(
            """
            INSERT INTO school_outcomes (school_id, median_earnings, repayment_rate)
            VALUES (%s, %s, %s)
            ON CONFLICT (school_id) DO UPDATE SET
                median_earnings = EXCLUDED.median_earnings,
                repayment_rate = EXCLUDED.repayment_rate
            """,
            (
                school_id,
                nullable_int(row["median_earnings"]),
                nullable_float(row["repayment_rate"]),
            ),
        )

        cur.execute(
            """
            INSERT INTO school_campus_life (
                school_id, housing_available, sports_division, greek_life_rate, culture_tags
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (school_id) DO UPDATE SET
                housing_available = EXCLUDED.housing_available,
                sports_division = EXCLUDED.sports_division,
                greek_life_rate = EXCLUDED.greek_life_rate,
                culture_tags = EXCLUDED.culture_tags
            """,
            (
                school_id,
                row["housing_available"].lower() == "true" if row["housing_available"] else None,
                row["sports_division"] or None,
                nullable_float(row["greek_life_rate"]),
                split_list(row["culture_tags"]),
            ),
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Load deterministic V1.2 seed data.")
    parser.add_argument("--seed-file", default=str(DEFAULT_SEED_PATH))
    parser.add_argument("--reset", action="store_true", help="Clear seeded school data before loading.")
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    database_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    seed_path = Path(args.seed_file)

    with psycopg.connect(database_url) as conn:
        if args.reset:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    TRUNCATE
                        comparison_schools,
                        saved_schools,
                        school_campus_life,
                        school_outcomes,
                        school_costs,
                        school_academics,
                        schools
                    RESTART IDENTITY CASCADE
                    """
                )

        with seed_path.open(newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                seed_school(conn, row)

    print(f"Seeded schools from {seed_path}")


if __name__ == "__main__":
    main()
