"""Chronological risk-model training for Google Colab or a local Python environment.

This deliberately uses reported incidents only and writes reproducible metadata.
GPU acceleration is not required for this compact tabular model.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Avoid joblib's physical-core probe warning in restricted or virtualised
# environments such as Colab and the hackathon workstation.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "2")

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import LabelEncoder
import math


FEATURES = [
    "lag_7", "lag_14", "lag_28",
    "rolling_7", "rolling_28", "ewm_14",
    "weekday", "is_weekend", "day_of_month",
    "month_sin", "month_cos",
    "festival_day", "rainfall_index",
    "crime_head_encoded", "district_encoded",
    "days_since_last",
]


def make_features(cases: pd.DataFrame) -> pd.DataFrame:
    cases["incident_date"] = pd.to_datetime(cases["incident_date"])
    reported = cases[cases["reported_source"].isin(["victim_reported", "citizen_reported"])].copy()
    # A precise coordinate is normally unique per FIR.  Training on those raw
    # points creates thousands of one-observation "cells".  Until a production
    # H3 index is configured, use the station service area as a stable spatial
    # unit; the dashboard can still render a finer visual grid.
    reported["cell"] = reported["district"].astype(str) + "::" + reported["station"].astype(str)
    grouped = (
        reported.groupby(["cell", "crime_head", "incident_date"], as_index=False)
        .agg(incident_count=("case_id", "count"), festival_day=("festival_day", "max"), rainfall_index=("rainfall_index", "mean"))
    )
    records: list[pd.DataFrame] = []
    for (cell, crime_head), group in grouped.groupby(["cell", "crime_head"]):
        index = pd.date_range(group["incident_date"].min(), group["incident_date"].max(), freq="D")
        daily = group.set_index("incident_date").reindex(index).fillna({"incident_count": 0, "festival_day": 0, "rainfall_index": 0})
        daily["cell"] = cell
        daily["crime_head"] = crime_head
        daily["lag_7"] = daily["incident_count"].shift(7)
        daily["lag_14"] = daily["incident_count"].shift(14)
        daily["lag_28"] = daily["incident_count"].shift(28)
        daily["rolling_7"] = daily["incident_count"].shift(1).rolling(7).mean()
        daily["rolling_28"] = daily["incident_count"].shift(1).rolling(28).mean()
        daily["ewm_14"] = daily["incident_count"].shift(1).ewm(span=14).mean()
        daily["weekday"] = daily.index.dayofweek
        daily["is_weekend"] = (daily.index.dayofweek >= 5).astype(int)
        daily["day_of_month"] = daily.index.day
        daily["month_sin"] = np.sin(2 * math.pi * daily.index.month / 12)
        daily["month_cos"] = np.cos(2 * math.pi * daily.index.month / 12)
        
        # Recency signal: time since last incident
        last_incident = daily["incident_count"].where(daily["incident_count"] > 0).dropna()
        if not last_incident.empty:
            # Reindex to full dates, forward fill, compute difference in days
            # fillna(30) handles the period before the first incident
            last_dates = pd.Series(last_incident.index, index=last_incident.index).reindex(daily.index).ffill()
            daily["days_since_last"] = (daily.index - last_dates).dt.days.fillna(30).clip(upper=30)
        else:
            daily["days_since_last"] = 30

        # Target: Total incidents in the NEXT 7 days (forward sum, not a backward leak).
        daily["target"] = daily["incident_count"].shift(-7).rolling(7).sum()
        records.append(daily.reset_index(names="date"))
    
    df = pd.concat(records, ignore_index=True)
    
    # Categorical encoders
    crime_le = LabelEncoder()
    df["crime_head_encoded"] = crime_le.fit_transform(df["crime_head"])
    
    # Extract district from cell (format is district::station)
    district_series = df["cell"].str.split("::").str[0]
    dist_le = LabelEncoder()
    df["district_encoded"] = dist_le.fit_transform(district_series)
    
    return df.dropna(subset=FEATURES + ["target"]), crime_le, dist_le


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "synthetic" / "cases.csv"))
    parser.add_argument("--model-out", default=str(PROJECT_ROOT / "data" / "models" / "risk_model.joblib"))
    parser.add_argument("--metrics-out", default=str(PROJECT_ROOT / "data" / "models" / "risk_model_metrics.json"))
    args = parser.parse_args()
    features, crime_le, dist_le = make_features(pd.read_csv(args.input))
    cutoff = pd.Timestamp(features["date"].quantile(0.80))
    train, test = features[features["date"] < cutoff], features[features["date"] >= cutoff]
    model = HistGradientBoostingRegressor(max_iter=180, learning_rate=0.06, l2_regularization=0.5, random_state=42)
    model.fit(train[FEATURES], train["target"])
    prediction = np.clip(model.predict(test[FEATURES]), 0, None)
    baseline = np.repeat(train["target"].mean(), len(test))
    metrics = {
        "model_version": "risk-hgb-v2",
        "algorithm": "HistGradientBoostingRegressor",
        "feature_count": len(FEATURES),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "temporal_split": str(cutoff.date()),
        "model_mae": round(float(mean_absolute_error(test["target"], prediction)), 4),
        "baseline_mae": round(float(mean_absolute_error(test["target"], baseline)), 4),
        "features": FEATURES,
        "warning": "Synthetic-data result only; not an operational crime forecast.",
    }
    metrics["improvement_percent"] = round((metrics["baseline_mae"] - metrics["model_mae"]) / metrics["baseline_mae"] * 100, 1)

    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "model": model,
        "features": FEATURES,
        "crime_le": crime_le,
        "dist_le": dist_le
    }, model_path)
    Path(args.metrics_out).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
