"""Chronological risk-model training for Google Colab or a local Python environment.

This deliberately uses reported incidents only and writes reproducible metadata.
GPU acceleration is not required for this compact tabular model.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

# Avoid joblib's physical-core probe warning in restricted or virtualised
# environments such as Colab and the hackathon workstation.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "2")

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error


FEATURES = ["lag_7", "lag_14", "lag_28", "rolling_28", "weekday", "month", "festival_day", "rainfall_index"]


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
        daily["rolling_28"] = daily["incident_count"].shift(1).rolling(28).mean()
        daily["weekday"] = daily.index.dayofweek
        daily["month"] = daily.index.month
        daily["target"] = daily["incident_count"].shift(-7).rolling(7).sum()
        records.append(daily.reset_index(names="date"))
    return pd.concat(records, ignore_index=True).dropna(subset=FEATURES + ["target"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/synthetic/cases.csv")
    parser.add_argument("--model-out", default="data/models/risk_model.joblib")
    parser.add_argument("--metrics-out", default="data/models/risk_model_metrics.json")
    args = parser.parse_args()
    features = make_features(pd.read_csv(args.input))
    cutoff = features["date"].quantile(0.80)
    train, test = features[features["date"] < cutoff], features[features["date"] >= cutoff]
    model = HistGradientBoostingRegressor(max_iter=180, learning_rate=0.06, l2_regularization=0.5, random_state=42)
    model.fit(train[FEATURES], train["target"])
    prediction = np.clip(model.predict(test[FEATURES]), 0, None)
    baseline = np.repeat(train["target"].mean(), len(test))
    metrics = {
        "model_version": "risk-hgb-v1",
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "temporal_split": str(cutoff.date()),
        "model_mae": round(float(mean_absolute_error(test["target"], prediction)), 4),
        "baseline_mae": round(float(mean_absolute_error(test["target"], baseline)), 4),
        "features": FEATURES,
        "warning": "Synthetic-data result only; not an operational crime forecast.",
    }
    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES}, model_path)
    Path(args.metrics_out).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
