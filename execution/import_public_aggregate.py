"""Import and standardise public aggregate crime data for KSP Drishti.

Supports Karnataka OGD and Kaggle datasets. Converts any source into
the standard `karnataka_monthly_aggregate.csv` format.

Usage:
    python execution/import_public_aggregate.py --input data/raw/karnataka_crime_review_2021_2024.csv
    python execution/import_public_aggregate.py --generate-sample
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "karnataka_monthly_aggregate.csv"

STANDARD_COLUMNS = [
    "period_start",
    "district",
    "crime_head",
    "cases_reported",
    "source_name",
    "source_url",
    "data_granularity",
    "data_classification",
]

# Karnataka district name normalisation
DISTRICT_ALIASES = {
    "bangalore": "Bengaluru Urban",
    "bangalore urban": "Bengaluru Urban",
    "bengaluru": "Bengaluru Urban",
    "bengaluru urban": "Bengaluru Urban",
    "mysore": "Mysuru",
    "mysuru": "Mysuru",
    "hubli": "Hubballi-Dharwad",
    "hubballi": "Hubballi-Dharwad",
    "hubli-dharwad": "Hubballi-Dharwad",
    "hubballi-dharwad": "Hubballi-Dharwad",
    "mangalore": "Mangaluru",
    "mangaluru": "Mangaluru",
    "gulbarga": "Kalaburagi",
    "kalaburagi": "Kalaburagi",
}

CRIME_HEAD_ALIASES = {
    "theft": "Theft",
    "burglary": "Burglary",
    "cyber crime": "Cyber Fraud",
    "cyber fraud": "Cyber Fraud",
    "assault": "Assault",
    "robbery": "Robbery",
    "murder": "Murder",
    "kidnapping": "Kidnapping",
    "cheating": "Cheating",
    "riots": "Riots",
}


def normalise_district(name: str) -> str:
    """Normalise district name to KSP Drishti standard."""
    return DISTRICT_ALIASES.get(name.strip().lower(), name.strip())


def normalise_crime_head(name: str) -> str:
    """Normalise crime category to KSP Drishti standard."""
    return CRIME_HEAD_ALIASES.get(name.strip().lower(), name.strip())


def generate_sample_data(output: Path) -> None:
    """Generate sample public aggregate data for demonstration.

    This simulates what real Karnataka OGD/Kaggle data would look like
    after standardisation.
    """
    import random

    rng = random.Random(42)
    districts = ["Bengaluru Urban", "Mysuru", "Hubballi-Dharwad", "Mangaluru", "Kalaburagi"]
    crime_heads = ["Theft", "Burglary", "Cyber Fraud", "Assault", "Robbery", "Murder", "Kidnapping", "Cheating"]

    # District crime rate multipliers (relative)
    district_rates = {
        "Bengaluru Urban": 3.2,
        "Mysuru": 1.5,
        "Hubballi-Dharwad": 1.2,
        "Mangaluru": 1.0,
        "Kalaburagi": 0.8,
    }

    rows = []
    for year in range(2021, 2025):
        for month in range(1, 13):
            for district in districts:
                rate = district_rates[district]
                for crime in crime_heads:
                    base = {"Theft": 45, "Burglary": 22, "Cyber Fraud": 18, "Assault": 15,
                            "Robbery": 10, "Murder": 3, "Kidnapping": 5, "Cheating": 8}.get(crime, 10)
                    # Add seasonal variation
                    seasonal = 1.15 if month in (6, 7, 8, 9) else 1.0
                    trend = 1.0 + (year - 2021) * 0.03  # slight upward trend
                    count = max(0, int(base * rate * seasonal * trend * rng.uniform(0.7, 1.3)))
                    rows.append({
                        "period_start": f"{year}-{month:02d}-01",
                        "district": district,
                        "crime_head": crime,
                        "cases_reported": count,
                        "source_name": "Karnataka Crime Review (Sample)",
                        "source_url": "https://data.gov.in/catalog/crime-review-karnataka",
                        "data_granularity": "monthly",
                        "data_classification": "public_aggregate_sample",
                    })

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=STANDARD_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} sample public aggregate records to {output}")


def import_csv(input_path: Path, output: Path, source_name: str, source_url: str) -> None:
    """Import and standardise a raw CSV into the standard format.

    Auto-detects common column names from Karnataka/Kaggle datasets.
    """
    with input_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        raw_fields = set(reader.fieldnames or [])
        rows = list(reader)

    if not rows:
        print("Input file is empty.")
        return

    # Auto-detect column mappings
    field_lower = {f.lower().strip(): f for f in raw_fields}

    # Try to find the date/period column
    date_candidates = ["period_start", "date", "month", "year_month", "period"]
    date_col = None
    for c in date_candidates:
        if c in field_lower:
            date_col = field_lower[c]
            break

    # Try to find district column
    district_candidates = ["district", "unit", "district_name", "police_district"]
    district_col = None
    for c in district_candidates:
        if c in field_lower:
            district_col = field_lower[c]
            break

    # Try to find crime head column
    crime_candidates = ["crime_head", "crime_type", "category", "ipc_category", "crime_category", "offence"]
    crime_col = None
    for c in crime_candidates:
        if c in field_lower:
            crime_col = field_lower[c]
            break

    # Try to find count column
    count_candidates = ["cases_reported", "count", "cases", "total", "number_of_cases", "case_count"]
    count_col = None
    for c in count_candidates:
        if c in field_lower:
            count_col = field_lower[c]
            break

    if not all([district_col, crime_col, count_col]):
        print(f"Could not auto-detect all required columns.")
        print(f"  Available columns: {sorted(raw_fields)}")
        print(f"  Detected: date={date_col}, district={district_col}, crime={crime_col}, count={count_col}")
        print("  Please map columns manually.")
        return

    # Check for year+month separate columns
    year_col = field_lower.get("year")
    month_col = field_lower.get("month")

    standardised = []
    for row in rows:
        # Build period_start
        if date_col and row.get(date_col):
            period = row[date_col]
        elif year_col and month_col and row.get(year_col) and row.get(month_col):
            period = f"{row[year_col]}-{int(row[month_col]):02d}-01"
        else:
            period = "2023-01-01"  # fallback

        standardised.append({
            "period_start": period,
            "district": normalise_district(row[district_col]),
            "crime_head": normalise_crime_head(row[crime_col]),
            "cases_reported": int(float(row[count_col])) if row.get(count_col) else 0,
            "source_name": source_name,
            "source_url": source_url,
            "data_granularity": "monthly",
            "data_classification": "public_aggregate",
        })

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=STANDARD_COLUMNS)
        writer.writeheader()
        writer.writerows(standardised)
    print(f"Standardised {len(standardised)} records from {input_path.name} → {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import and standardise public aggregate crime data")
    parser.add_argument("--input", help="Path to raw CSV file to import")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output path for standardised CSV")
    parser.add_argument("--source-name", default="Karnataka Crime Review", help="Name of the data source")
    parser.add_argument("--source-url", default="https://data.gov.in/catalog/crime-review-karnataka", help="URL of the data source")
    parser.add_argument("--generate-sample", action="store_true", help="Generate sample public aggregate data for demonstration")
    args = parser.parse_args()

    if args.generate_sample:
        generate_sample_data(Path(args.output))
    elif args.input:
        import_csv(Path(args.input), Path(args.output), args.source_name, args.source_url)
    else:
        print("Specify --input <csv_path> to import, or --generate-sample to create demo data.")
        parser.print_help()


if __name__ == "__main__":
    main()
