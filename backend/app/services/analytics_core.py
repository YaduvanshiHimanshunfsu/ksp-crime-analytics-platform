from datetime import datetime, timezone
from typing import Any
import pandas as pd
import numpy as np

from .data_loader import load_cases, _scope


def overview(district: str | None = None, crime_head: str | None = None) -> dict[str, Any]:
    cases = _scope(load_cases(), district, crime_head)
    if cases.empty:
        return {
            "total_cases": 0, "last_28_days": 0, "change_percent": 0.0,
            "active_alerts": 0, "reported_source_share": 0.0,
            "latest_data_date": datetime.now(timezone.utc).date().isoformat(),
            "synthetic_notice": "Synthetic, schema-faithful demonstration data - not live police intelligence.",
        }
    latest = cases["incident_date"].max()
    recent_start = latest - pd.Timedelta(days=27)
    previous_start = latest - pd.Timedelta(days=55)
    current = int((cases["incident_date"] >= recent_start).sum())
    previous = int(((cases["incident_date"] >= previous_start) & (cases["incident_date"] < recent_start)).sum())
    change = round(((current - previous) / max(previous, 1)) * 100, 1)
    reported_share = round(float(cases["reported_source"].isin(["victim_reported", "citizen_reported"]).mean() * 100), 1)
    
    # Avoid double computation of hotspots (H-5)
    hs = hotspots(district, crime_head)
    active_alerts = 0
    if len(cases) > 0:
        supported_sources = cases["reported_source"].isin(["victim_reported", "citizen_reported"])
        source_share = float(supported_sources.mean())
        if source_share >= 0.75:
            active_alerts = sum(1 for h in hs[:8] if h["incidents_28d"] >= 7)
    
    return {
        "total_cases": int(len(cases)),
        "last_28_days": current,
        "change_percent": change,
        "active_alerts": active_alerts,
        "reported_source_share": reported_share,
        "latest_data_date": latest.date().isoformat(),
        "synthetic_notice": "Synthetic, schema-faithful demonstration data - not live police intelligence.",
    }


def hotspots(district: str | None = None, crime_head: str | None = None, limit: int = 30, offset: int = 0) -> list[dict[str, Any]]:
    cases = _scope(load_cases(), district, crime_head)
    if cases.empty:
        return []
    latest = cases["incident_date"].max()
    recent = cases[cases["incident_date"] >= latest - pd.Timedelta(days=55)].copy()
    recent["lat_cell"] = recent["latitude"].round(2)
    recent["lon_cell"] = recent["longitude"].round(2)
    recent["period"] = np.where(recent["incident_date"] >= latest - pd.Timedelta(days=27), "current", "previous")
    grouped = recent.groupby(["district", "station", "crime_head", "lat_cell", "lon_cell", "period"]).size().unstack(fill_value=0).reset_index()
    if "current" not in grouped:
        grouped["current"] = 0
    if "previous" not in grouped:
        grouped["previous"] = 0
    grouped["delta"] = grouped["current"] - grouped["previous"]
    grouped["risk_score"] = (grouped["current"] * 11 + grouped["delta"].clip(lower=0) * 9).clip(upper=99)
    result: list[dict[str, Any]] = []
    for row in grouped.sort_values(["risk_score", "current"], ascending=False).iloc[offset:offset+limit].reset_index().to_dict(orient="records"):
        result.append(
            {
                "id": f"h3-demo-{row['index']}",
                "district": row["district"],
                "station": row["station"],
                "crime_head": row["crime_head"],
                "latitude": float(row["lat_cell"]),
                "longitude": float(row["lon_cell"]),
                "incidents_28d": int(row["current"]),
                "change": int(row["delta"]),
                "risk_score": int(row["risk_score"]),
            }
        )
    return result


def trends(district: str | None = None, crime_head: str | None = None) -> list[dict[str, Any]]:
    cases = _scope(load_cases(), district, crime_head)
    if cases.empty:
        return []
    series = cases.set_index("incident_date").resample("W-MON").size().rename("incidents").tail(14).reset_index()
    baseline = series["incidents"].rolling(4, min_periods=2).mean().shift(1)
    series["expected"] = baseline.fillna(series["incidents"].mean()).round(1)
    series["anomaly"] = series["incidents"] > (series["expected"] * 1.35)
    return [
        {
            "week": row["incident_date"].date().isoformat(),
            "incidents": int(row["incidents"]),
            "expected": float(row["expected"]),
            "anomaly": bool(row["anomaly"]),
        }
        for _, row in series.iterrows()
    ]


def alerts(district: str | None = None, crime_head: str | None = None, limit: int = 8, offset: int = 0) -> list[dict[str, Any]]:
    cases = _scope(load_cases(), district, crime_head)
    if cases.empty:
        return []
    supported_sources = cases["reported_source"].isin(["victim_reported", "citizen_reported"])
    source_share = float(supported_sources.mean()) if len(cases) else 0.0
    result: list[dict[str, Any]] = []
    for hotspot in hotspots(district, crime_head)[offset:offset+limit]:
        confidence = "High" if hotspot["incidents_28d"] >= 7 and source_share >= 0.75 else "Review required"
        result.append(
            {
                "id": hotspot["id"],
                "title": f"{hotspot['crime_head']} pattern near {hotspot['station']}",
                "district": hotspot["district"],
                "risk_score": hotspot["risk_score"],
                "confidence": confidence,
                "reason": f"{hotspot['incidents_28d']} reports in 28 days; change of {hotspot['change']:+d} vs previous period.",
                "credibility": {
                    "reported_source_share": round(source_share * 100),
                    "geo_complete": 100,
                    "model_status": "advisory - analyst review required",
                },
            }
        )
    return result


def district_drilldown(district: str) -> dict[str, Any]:
    cases = _scope(load_cases(), district, None)
    if cases.empty:
        return {"district": district, "total_cases": 0, "stations": []}
    
    station_stats = []
    for station, group in cases.groupby("station"):
        station_stats.append({
            "station": station,
            "total_cases": len(group),
            "top_crime": group["crime_head"].value_counts().index[0] if not group.empty else "N/A",
            "recent_cases": len(group[group["incident_date"] >= group["incident_date"].max() - pd.Timedelta(days=28)])
        })
    
    return {
        "district": district,
        "total_cases": len(cases),
        "stations": sorted(station_stats, key=lambda x: x["total_cases"], reverse=True)
    }
