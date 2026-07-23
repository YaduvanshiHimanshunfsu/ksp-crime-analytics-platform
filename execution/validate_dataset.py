"""Validate the approved, non-sensitive columns needed by the demo analytics."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "case_id", "crime_no", "registered_date", "incident_date", "district", "station",
    "crime_head", "latitude", "longitude", "reported_source", "case_status",
    "accused_name", "age_years", "festival_day", "rainfall_index",
    "literacy_index", "urbanization_index", "population_density",
}
ALLOWED_SOURCES = {"victim_reported", "citizen_reported", "police_observed"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED - fields
        if missing:
            return [f"Missing required columns: {', '.join(sorted(missing))}"]
        for line, row in enumerate(reader, start=2):
            try:
                date.fromisoformat(row["incident_date"])
                latitude, longitude = float(row["latitude"]), float(row["longitude"])
                if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
                    errors.append(f"Line {line}: invalid coordinate range")
                if row["reported_source"] not in ALLOWED_SOURCES:
                    errors.append(f"Line {line}: unknown reported_source")
                if int(row["age_years"]) < 0 or int(row["age_years"]) > 120:
                    errors.append(f"Line {line}: invalid age")
                float(row["literacy_index"])
                float(row["urbanization_index"])
                int(row["population_density"])
            except (ValueError, TypeError) as error:
                errors.append(f"Line {line}: {error}")
            if len(errors) >= 20:
                errors.append("Stopping after 20 validation errors")
                break
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "synthetic" / "cases.csv"))
    args = parser.parse_args()
    errors = validate(Path(args.input))
    if errors:
        raise SystemExit("Dataset validation failed:\n" + "\n".join(f"- {item}" for item in errors))
    print(f"Dataset validation passed: {args.input}")


if __name__ == "__main__":
    main()

