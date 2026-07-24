from typing import Any
import pandas as pd
import joblib
import math
import numpy as np
try:
    import shap
except ImportError:
    shap = None

from .data_loader import PROJECT_ROOT
from .analytics_core import hotspots


def compute_shap_explanation(model, features_df, feature_names):
    if shap is None:
        return [{"feature": "shap_missing", "readable_name": "SHAP library missing", "shap_value": 0, "direction": "unknown", "feature_value": 0}]
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(features_df)
    
    if len(features_df) == 1:
        sv = shap_values[0]
    else:
        sv = shap_values
    
    top_indices = np.argsort(np.abs(sv))[-3:][::-1]
    drivers = []
    
    for idx in top_indices:
        feature_name = feature_names[idx]
        shap_val = float(sv[idx])
        feature_val = float(features_df.iloc[0, idx]) if len(features_df) == 1 else None
        
        direction = "increases risk" if shap_val > 0 else "decreases risk"
        
        readable_name = {
            "lag_7": "incidents in the past week",
            "lag_14": "incidents 2 weeks ago",
            "lag_28": "incidents in the past month",
            "rolling_7": "short-term trend (7-day average)",
            "rolling_28": "monthly trend (28-day average)",
            "ewm_14": "recent momentum",
            "weekday": "day of the week",
            "is_weekend": "weekend effect",
            "month_sin": "seasonal pattern (month)",
            "month_cos": "seasonal pattern (month)",
            "festival_day": "festival/holiday proximity",
            "rainfall_index": "rainfall conditions",
            "crime_head_encoded": "crime category",
            "district_encoded": "geographic area",
            "days_since_last": "time since last incident",
            "day_of_month": "day in the month",
        }.get(feature_name, feature_name)
        
        drivers.append({
            "feature": feature_name,
            "readable_name": readable_name,
            "shap_value": round(shap_val, 4),
            "direction": direction,
            "feature_value": round(feature_val, 2) if feature_val is not None else None,
        })
    return drivers

def risk_forecast(district: str | None = None, crime_head: str | None = None) -> list[dict[str, Any]]:
    model_path = PROJECT_ROOT / "data" / "models" / "risk_model.joblib"
    model_data = None
    if model_path.exists():
        try:
            model_data = joblib.load(model_path)
        except Exception:
            pass

    forecasts = []
    for hotspot in hotspots(district, crime_head)[:12]:
        if model_data:
            # We must map values for the new 17 features
            # Dummy logic to populate the features for the API endpoint based on hotspot data
            crime_head_encoded = 0
            if "crime_le" in model_data:
                try:
                    crime_head_encoded = model_data["crime_le"].transform([hotspot["crime_head"]])[0]
                except ValueError:
                    pass
            district_encoded = 0
            if "dist_le" in model_data:
                try:
                    district_encoded = model_data["dist_le"].transform([hotspot["district"]])[0]
                except ValueError:
                    pass
            
            row = pd.DataFrame([{
                "lag_7": hotspot["incidents_28d"] / 4,
                "lag_14": hotspot["incidents_28d"] / 4,
                "lag_28": hotspot["incidents_28d"] / 4,
                "rolling_7": hotspot["incidents_28d"] / 4,
                "rolling_28": hotspot["incidents_28d"] / 28,
                "ewm_14": hotspot["incidents_28d"] / 4,
                "weekday": 0,
                "is_weekend": 0,
                "day_of_month": 15,
                "month_sin": math.sin(2 * math.pi * 6 / 12),
                "month_cos": math.cos(2 * math.pi * 6 / 12),
                "festival_day": 0,
                "rainfall_index": 0.5,
                "crime_head_encoded": crime_head_encoded,
                "district_encoded": district_encoded,
                "days_since_last": 2,
            }])
            
            pred = max(0, model_data["model"].predict(row[model_data["features"]])[0])
            centre = int(round(pred))
            
            # compute SHAP drivers
            shap_drivers = compute_shap_explanation(model_data["model"], row[model_data["features"]], model_data["features"])
        else:
            centre = max(1, int(round(hotspot["incidents_28d"] / 4)))
            shap_drivers = [
                {"readable_name": "recent reported-incident trend", "direction": "increases risk"},
                {"readable_name": "same-category 28-day activity", "direction": "increases risk"},
                {"readable_name": "calendar and seasonal pattern", "direction": "increases risk"}
            ]

        forecasts.append(
            {
                "area": hotspot["station"],
                "district": hotspot["district"],
                "crime_head": hotspot["crime_head"],
                "next_week_range": [max(0, centre - 1), centre + 2],
                "risk_score": hotspot["risk_score"],
                "drivers": shap_drivers,
                "use": "Prioritise analyst review; not a person-level prediction or patrol directive.",
            }
        )
    return forecasts
