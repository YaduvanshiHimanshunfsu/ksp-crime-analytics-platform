"""Data loading and caching utility for KSP Drishti analytics."""

import functools
import os
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CASE_PATH = PROJECT_ROOT / "data" / "synthetic" / "cases.csv"
DEFAULT_LINK_PATH = PROJECT_ROOT / "data" / "synthetic" / "link_candidates.csv"
DEFAULT_PUBLIC_PATH = PROJECT_ROOT / "data" / "processed" / "karnataka_category_trends_2021_2024.csv"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "data" / "models" / "risk_model.joblib"


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Synthetic demo data missing at {path}. Run execution/generate_synthetic_data.py first.")
    return pd.read_csv(path)


@functools.lru_cache(maxsize=1)
def load_cases() -> pd.DataFrame:
    path = Path(os.getenv("DATA_PATH", str(DEFAULT_CASE_PATH)))
    if not path.exists():
        return pd.DataFrame()
    cases = _read_csv(path)
    if not cases.empty:
        cases["incident_date"] = pd.to_datetime(cases["incident_date"])
    return cases


@functools.lru_cache(maxsize=1)
def load_links() -> pd.DataFrame:
    path = Path(os.getenv("LINK_PATH", str(DEFAULT_LINK_PATH)))
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@functools.lru_cache(maxsize=1)
def load_public_data() -> pd.DataFrame:
    """Load public aggregate crime data if available."""
    path = Path(os.getenv("PUBLIC_DATA_PATH", str(DEFAULT_PUBLIC_PATH)))
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    if "period_start" in df.columns:
        df["period_start"] = pd.to_datetime(df["period_start"])
    return df


def invalidate_cache():
    """Clear the data loader caches."""
    load_cases.cache_clear()
    load_links.cache_clear()
    load_public_data.cache_clear()


def data_status() -> dict[str, str]:
    """Return the status of the loaded data."""
    cases = load_cases()
    if cases.empty:
        return {"status": "error", "message": "No case data loaded"}
    return {
        "status": "ok",
        "cases_count": str(len(cases)),
        "latest_incident": str(cases["incident_date"].max().date())
    }


def _scope(cases: pd.DataFrame, district: str | None, crime_head: str | None) -> pd.DataFrame:
    """Scope the dataframe by district and crime head.
    Note: Returns a reference/slice, downstream functions should not modify the result.
    """
    scoped = cases
    if district and district != "All Karnataka":
        scoped = scoped[scoped["district"] == district]
    if crime_head and crime_head != "All crime heads":
        scoped = scoped[scoped["crime_head"] == crime_head]
    return scoped
