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


def process_district_trends_2023_to_2025() -> Path:
    """Process multi-year district trends from OpenCity.in data."""
    records = []

    # 1. 2023 Data
    src_2023 = DATASET_ROOT / "OpenCity.in Karnataka Crime Data 2025/2023/ffce2bf3-1202-489d-8af5-f156c2e9b793.csv"
    if src_2023.exists():
        df_23 = pd.read_csv(src_2023)
        df_23 = df_23[df_23["Districts"].str.strip().str.lower() != "total"].copy()
        for _, row in df_23.iterrows():
            dist = row["Districts"]
            records.append({"district_raw": dist, "year": 2023, "crime_head": "Total IPC", "cases_reported": int(row["IPC Cases"])})
            records.append({"district_raw": dist, "year": 2023, "crime_head": "Total SLL", "cases_reported": int(row["SLL Cases"])})

    # 2. 2024 Data
    src_2024 = DATASET_ROOT / "OpenCity.in Karnataka Crime Data 2025/2024/district wise.csv"
    if src_2024.exists():
        df_24 = pd.read_csv(src_2024)
        df_24 = df_24[df_24["Sl No"].notna() & (df_24["DISTRICT/UNITS"] != "STATE")].copy()
        map_24 = {
            "THEFT": "Theft", "BURGLARY-DAY": "Burglary", "BURGLARY-NIGHT": "Burglary",
            "CYBER CRIME": "Cyber Fraud", "CASES OF HURT": "Assault", "ROBBERY": "Robbery",
            "MURDER": "Murder"
        }
        cols = [c for c in df_24.columns if c not in ("Sl No", "DISTRICT/UNITS")]
        for _, row in df_24.iterrows():
            dist = row["DISTRICT/UNITS"]
            for c in cols:
                val = row[c]
                if pd.isna(val): val = 0
                ch = map_24.get(str(c).strip(), str(c).strip().title())
                records.append({"district_raw": dist, "year": 2024, "crime_head": ch, "cases_reported": int(val)})

    # 3. 2025 Data
    src_2025 = DATASET_ROOT / "OpenCity.in Karnataka Crime Data 2025/ka-district-wise-2025.csv"
    if src_2025.exists():
        df_25 = pd.read_csv(src_2025)
        df_25.columns = ["sl_no", "district_unit", "ipc_bns_crimes", "sll_crimes"]
        df_25 = df_25[df_25["sl_no"].notna() & (df_25["district_unit"] != "STATE")].copy()
        for _, row in df_25.iterrows():
            dist = row["district_unit"]
            val_ipc = pd.to_numeric(row["ipc_bns_crimes"], errors="coerce")
            val_sll = pd.to_numeric(row["sll_crimes"], errors="coerce")
            records.append({"district_raw": dist, "year": 2025, "crime_head": "Total IPC", "cases_reported": int(val_ipc) if not pd.isna(val_ipc) else 0})
            records.append({"district_raw": dist, "year": 2025, "crime_head": "Total SLL", "cases_reported": int(val_sll) if not pd.isna(val_sll) else 0})

    if not records:
        print("WARNING: No data for 2023-2025 trends")
        return None

    df = pd.DataFrame(records)
    
    def normalize_district(d):
        d_title = str(d).strip().title()
        # Fallback to existing mapping logic
        if d_title in DISTRICT_NORM:
            return DISTRICT_NORM[d_title]
        # Also try exact match just in case
        if d in DISTRICT_NORM:
            return DISTRICT_NORM[d]
        return d_title

    df["district_normalized"] = df["district_raw"].apply(normalize_district)
    df["data_source"] = "OpenCity.in / Karnataka Police (2023-2025)"
    df["data_classification"] = "official_aggregate"
    
    df = df.groupby(["district_normalized", "year", "crime_head", "data_source", "data_classification"], as_index=False)["cases_reported"].sum()
    
    out = PROCESSED_DIR / "karnataka_district_trends_2023_2025.csv"
    df.to_csv(out, index=False)
    print(f"[trends]   Wrote {len(df)} trend records -> {out}")
    return out


def main() -> None:
    print("Processing public datasets for KSP Drishti...")
    out1 = process_district_data()
    out2 = process_kaggle_trends()
    out3 = process_district_trends_2023_to_2025()

    print("\nSummary:")
    if out1:
        d = pd.read_csv(out1)
        print(f"  District 2025: {len(d)} units, total IPC = {d['ipc_bns_crimes'].sum():,}")
    if out2:
        t = pd.read_csv(out2)
        print(f"  Category trends: {len(t)} monthly records, years = {sorted(t['period_start'].str[:4].unique())}")
    if out3:
        td = pd.read_csv(out3)
        print(f"  District trends: {len(td)} records, years = {sorted(td['year'].unique())}")
    print("\nDone. Re-start the backend to serve updated public-context endpoints.")


if __name__ == "__main__":
    main()
