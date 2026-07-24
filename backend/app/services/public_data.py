from typing import Any
import pandas as pd
import os
from pathlib import Path

from .data_loader import PROJECT_ROOT, load_public_data

DISTRICT_2025_PATH = PROJECT_ROOT / "data" / "processed" / "karnataka_district_2025.csv"
DISTRICT_TRENDS_PATH = PROJECT_ROOT / "data" / "processed" / "karnataka_district_trends_2023_2025.csv"
# The default loader loads kaggle data for public_data, so we can still use load_public_data() for state trends

def district_benchmark() -> dict[str, Any]:
    """Return real KSP 2025 district volumes."""
    path = Path(os.getenv("DISTRICT_2025_PATH", str(DISTRICT_2025_PATH)))
    if not path.exists():
        return {"error": "Public data not processed. Run execution/process_public_data.py first.", "data": []}
    
    df = pd.read_csv(path)
    state_totals = df[["ipc_bns_crimes", "sll_crimes", "total_crimes"]].sum().to_dict()
    
    return {
        "source": "Karnataka Police / OpenCity.in",
        "year": 2025,
        "data_classification": "official_aggregate",
        "districts": df.to_dict(orient="records"),
        "state_total": {
            "ipc_bns_crimes": int(state_totals.get("ipc_bns_crimes", 0)),
            "sll_crimes": int(state_totals.get("sll_crimes", 0)),
            "total_crimes": int(state_totals.get("total_crimes", 0)),
        }
    }


def category_trend() -> dict[str, Any]:
    """Return multi-year district trend data."""
    path = Path(os.getenv("DISTRICT_TRENDS_PATH", str(DISTRICT_TRENDS_PATH)))
    if not path.exists():
        return {"error": "Public data not processed. Run execution/process_public_data.py first.", "data": []}
    
    df = pd.read_csv(path)
    return {
        "source": "OpenCity.in / Karnataka Police (2023-2025)",
        "districts": sorted(df["district_normalized"].unique().tolist()),
        "years": sorted(df["year"].unique().tolist()),
        "data": df.to_dict(orient="records")
    }


def public_overview() -> dict[str, Any]:
    """Overview of public aggregate crime data."""
    df = load_public_data()
    if df.empty:
        return {
            "available": False,
            "message": "No public aggregate data loaded. Download from Karnataka OGD or Kaggle and run import_public_aggregate.py.",
        }
    return {
        "available": True,
        "total_records": int(len(df)),
        "districts": sorted(df["district"].unique().tolist()) if "district" in df.columns else [],
        "date_range": {
            "start": str(df["period_start"].min().date()) if "period_start" in df.columns else "N/A",
            "end": str(df["period_start"].max().date()) if "period_start" in df.columns else "N/A",
        },
        "source": df["source"].iloc[0] if "source" in df.columns and len(df) > 0 else "Unknown",
        "granularity": "State" if "district" not in df.columns else "District",
    }


def public_trends() -> list[dict[str, Any]]:
    """Monthly trends from public aggregate data."""
    df = load_public_data()
    if df.empty or "period_start" not in df.columns:
        return []
    monthly = (
        df.groupby("period_start")["cases_reported"]
        .sum()
        .reset_index()
        .sort_values("period_start")
        .tail(24)
    )
    return [
        {
            "period": row["period_start"].strftime("%Y-%m"),
            "cases_reported": int(row["cases_reported"]),
            "source": "public_aggregate",
        }
        for _, row in monthly.iterrows()
    ]


def public_district_comparison() -> list[dict[str, Any]]:
    """District-wise comparison from public data."""
    df = load_public_data()
    if df.empty or "district" not in df.columns:
        return []
    comparison = (
        df.groupby("district")["cases_reported"]
        .sum()
        .reset_index()
        .sort_values("cases_reported", ascending=False)
    )
    return comparison.to_dict(orient="records")


def calibration_report() -> dict[str, Any]:
    """Compare synthetic data distribution to real KSP 2025 data."""
    from .data_loader import load_cases
    synthetic = load_cases()
    
    path = Path(os.getenv("DISTRICT_2025_PATH", str(DISTRICT_2025_PATH)))
    if not path.exists() or synthetic.empty:
        return {"status": "insufficient_data"}
        
    real = pd.read_csv(path)
    
    # Compare district proportions
    synth_dist = synthetic.groupby("district").size() / len(synthetic)
    real_dist = real.set_index("drishti_district")["total_crimes"]
    real_dist = real_dist / real_dist.sum()
    
    correlation = synth_dist.corr(real_dist)
    if pd.isna(correlation):
        correlation = 0.0
        
    return {
        "status": "calibrated",
        "synthetic_total": len(synthetic),
        "real_total_2025": int(real["total_crimes"].sum()),
        "scale_factor": round(real["total_crimes"].sum() / max(len(synthetic), 1), 2),
        "district_correlation": float(correlation),
        "interpretation": "Synthetic data represents a scaled-down simulation of the true distribution. A high correlation (>0.7) means the synthetic data matches the geographical spread of real crimes."
    }
