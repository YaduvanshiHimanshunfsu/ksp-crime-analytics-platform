"""Process public datasets into standardised formats for KSP Drishti.

Sources:
  1. Dataset/OpenCity.in Karnataka Crime Data 2025/ka-district-wise-2025.csv
     → data/processed/karnataka_district_2025.csv

  2. Dataset/Kaggle/CRIME_REVIEW_2021_TO_2024_KARNATAKA_CLEAN.csv
     → data/processed/karnataka_category_trends_2021_2024.csv

Run:
    python execution/process_public_data.py
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = PROJECT_ROOT / "Dataset"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

# Month abbreviation → integer
MONTH_MAP = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4,
    "MAY": 5, "JUN": 6, "JUL": 7, "AUG": 8,
    "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

# Mapping Kaggle MAJOR HEAD prefixes → KSP Drishti crime_head names
CRIME_HEAD_MAP = {
    "THEFT": "Theft",
    "BURGLARY - NIGHT": "Burglary",
    "BURGLARY - DAY": "Burglary",
    "Robbery": "Robbery",
    "CASES OF HURT": "Assault",
    "Cyber Crime": "Cyber Fraud",
    "ASSAULT": "Assault",
}

# Normalise district/unit names to match Drishti's 5 demo districts
DISTRICT_NORM = {
    "Bengaluru City": "Bengaluru Urban",
    "Bengaluru Dist": "Bengaluru Urban",
    "Bengaluru South": "Bengaluru Urban",
    "Mysuru City": "Mysuru",
    "Mysuru Dist": "Mysuru",
    "Hubballi Dharwad City": "Hubballi-Dharwad",
    "Mangaluru City": "Mangaluru",
    "Kalaburagi City": "Kalaburagi",
    "Kalaburagi": "Kalaburagi",
}


def process_district_data() -> Path:
    """Process OpenCity.in district-wise 2025 data."""
    src = DATASET_ROOT / "OpenCity.in Karnataka Crime Data 2025" / "ka-district-wise-2025.csv"
    if not src.exists():
        print(f"WARNING: {src} not found — skipping district data")
        return None

    df = pd.read_csv(src)
    df.columns = ["sl_no", "district_unit", "ipc_bns_crimes", "sll_crimes"]

    # Remove section header rows and STATE total
    df = df[df["sl_no"].notna() & (df["district_unit"] != "STATE")].copy()
    df["sl_no"] = df["sl_no"].astype(int)
    df["ipc_bns_crimes"] = pd.to_numeric(df["ipc_bns_crimes"], errors="coerce").fillna(0).astype(int)
    df["sll_crimes"] = pd.to_numeric(df["sll_crimes"], errors="coerce").fillna(0).astype(int)
    df["total_crimes"] = df["ipc_bns_crimes"] + df["sll_crimes"]
    df["drishti_district"] = df["district_unit"].map(DISTRICT_NORM).fillna("Other")
    df["year"] = 2025
    df["source"] = "Karnataka Police / OpenCity.in"
    df["data_classification"] = "official_aggregate"
    df["licence"] = "Open Government Data (India)"

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "karnataka_district_2025.csv"
    df.to_csv(out, index=False)
    print(f"[district] Wrote {len(df)} rows -> {out}")
    return out


def map_crime_head(major_head: str) -> str:
    """Map Kaggle MAJOR HEAD to Drishti crime_head."""
    for prefix, mapped in CRIME_HEAD_MAP.items():
        if str(major_head).startswith(prefix):
            return mapped
    return "Other IPC"


def process_kaggle_trends() -> Path:
    """Process Kaggle Karnataka 2021-2024 into monthly state-level trends."""
    src = DATASET_ROOT / "Kaggle" / "CRIME_REVIEW_2021_TO_2024_KARNATAKA_CLEAN.csv"
    if not src.exists():
        print(f"WARNING: {src} not found — skipping Kaggle trends")
        return None

    df = pd.read_csv(src, encoding="latin1")

    # Convert month to numeric
    df["month_num"] = df["Month"].str.strip().map(MONTH_MAP)
    df = df[df["month_num"].notna()]  # Drop any unmapped months
    df["period_start"] = pd.to_datetime(
        df["Year"].astype(str) + "-" + df["month_num"].astype(int).astype(str) + "-01"
    )

    # Map to Drishti crime heads
    df["crime_head"] = df["MAJOR HEAD"].apply(map_crime_head)

    # Use 'During the current month' as the count
    df["cases_monthly"] = pd.to_numeric(df["During the current month"], errors="coerce").fillna(0)

    # Aggregate: state-level monthly count per mapped crime head
    monthly = (
        df.groupby(["period_start", "crime_head"])
        .agg(cases_reported=("cases_monthly", "sum"))
        .reset_index()
    )

    monthly["geography"] = "Karnataka (State)"
    monthly["source"] = "Kaggle: Karnataka Crime Review 2021-2024 (Aayush Rokade)"
    monthly["source_url"] = "https://www.kaggle.com/datasets/aayushrokade/crime-review-of-karnataka-2021-2024"
    monthly["data_classification"] = "public_aggregate"
    monthly["licence"] = "CC0 (Kaggle)"

    # Sort by period
    monthly = monthly.sort_values(["crime_head", "period_start"]).reset_index(drop=True)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out = PROCESSED_DIR / "karnataka_category_trends_2021_2024.csv"
    monthly.to_csv(out, index=False)
    print(f"[kaggle]   Wrote {len(monthly)} monthly records -> {out}")
    return out


def main() -> None:
    print("Processing public datasets for KSP Drishti...")
    out1 = process_district_data()
    out2 = process_kaggle_trends()

    print("\nSummary:")
    if out1:
        d = pd.read_csv(out1)
        print(f"  District 2025: {len(d)} units, total IPC = {d['ipc_bns_crimes'].sum():,}")
    if out2:
        t = pd.read_csv(out2)
        print(f"  Category trends: {len(t)} monthly records, years = {sorted(t['period_start'].str[:4].unique())}")
    print("\nDone. Re-start the backend to serve updated public-context endpoints.")


if __name__ == "__main__":
    main()
