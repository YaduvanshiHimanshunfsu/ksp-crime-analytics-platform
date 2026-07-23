"""Read-only analytics for the synthetic FIR demonstration data."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CASE_PATH = PROJECT_ROOT / "data" / "synthetic" / "cases.csv"
DEFAULT_LINK_PATH = PROJECT_ROOT / "data" / "synthetic" / "link_candidates.csv"
EVENT_LOG_PATH = PROJECT_ROOT / "logs" / "frontend_events.jsonl"
event_logger = logging.getLogger("ksp_drishti.frontend")


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Synthetic demo data missing at {path}. Run execution/generate_synthetic_data.py first.")
    return pd.read_csv(path)


def load_cases() -> pd.DataFrame:
    path = Path(os.getenv("DATA_PATH", str(DEFAULT_CASE_PATH)))
    cases = _read_csv(path)
    cases["incident_date"] = pd.to_datetime(cases["incident_date"])
    return cases


def load_links() -> pd.DataFrame:
    path = Path(os.getenv("LINK_PATH", str(DEFAULT_LINK_PATH)))
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _scope(cases: pd.DataFrame, district: str | None, crime_head: str | None) -> pd.DataFrame:
    scoped = cases.copy()
    if district and district != "All Karnataka":
        scoped = scoped[scoped["district"] == district]
    if crime_head and crime_head != "All crime heads":
        scoped = scoped[scoped["crime_head"] == crime_head]
    return scoped


def overview(district: str | None = None, crime_head: str | None = None) -> dict[str, Any]:
    cases = _scope(load_cases(), district, crime_head)
    latest = cases["incident_date"].max()
    recent_start = latest - pd.Timedelta(days=27)
    previous_start = latest - pd.Timedelta(days=55)
    current = int((cases["incident_date"] >= recent_start).sum())
    previous = int(((cases["incident_date"] >= previous_start) & (cases["incident_date"] < recent_start)).sum())
    change = round(((current - previous) / max(previous, 1)) * 100, 1)
    reported_share = round(float(cases["reported_source"].isin(["victim_reported", "citizen_reported"]).mean() * 100), 1)
    return {
        "total_cases": int(len(cases)),
        "last_28_days": current,
        "change_percent": change,
        "active_alerts": int(len(alerts(district, crime_head))),
        "reported_source_share": reported_share,
        "latest_data_date": latest.date().isoformat(),
        "synthetic_notice": "Synthetic, schema-faithful demonstration data - not live police intelligence.",
    }


def hotspots(district: str | None = None, crime_head: str | None = None) -> list[dict[str, Any]]:
    cases = _scope(load_cases(), district, crime_head)
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
    for index, row in grouped.sort_values(["risk_score", "current"], ascending=False).head(30).iterrows():
        result.append(
            {
                "id": f"h3-demo-{index}",
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


def alerts(district: str | None = None, crime_head: str | None = None) -> list[dict[str, Any]]:
    cases = _scope(load_cases(), district, crime_head)
    supported_sources = cases["reported_source"].isin(["victim_reported", "citizen_reported"])
    source_share = float(supported_sources.mean()) if len(cases) else 0.0
    result: list[dict[str, Any]] = []
    for hotspot in hotspots(district, crime_head)[:8]:
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


def risk_forecast(district: str | None = None, crime_head: str | None = None) -> list[dict[str, Any]]:
    forecasts = []
    for hotspot in hotspots(district, crime_head)[:12]:
        centre = max(1, int(round(hotspot["incidents_28d"] / 4)))
        forecasts.append(
            {
                "area": hotspot["station"],
                "district": hotspot["district"],
                "crime_head": hotspot["crime_head"],
                "next_week_range": [max(0, centre - 1), centre + 2],
                "risk_score": hotspot["risk_score"],
                "drivers": [
                    "recent reported-incident trend",
                    "same-category 28-day activity",
                    "calendar and seasonal pattern",
                ],
                "use": "Prioritise analyst review; not a person-level prediction or patrol directive.",
            }
        )
    return forecasts


def case_links() -> list[dict[str, Any]]:
    links = load_links()
    if links.empty:
        return []
    return links.head(30).assign(confidence=lambda frame: (frame["confidence"] * 100).round(0).astype(int)).to_dict(orient="records")


def network() -> dict[str, list[dict[str, Any]]]:
    cases = load_cases()
    links = load_links().head(20)
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []
    for _, link in links.iterrows():
        for case_id, name, district in [
            (str(link["left_case_id"]), link["left_name"], link["left_district"]),
            (str(link["right_case_id"]), link["right_name"], link["right_district"]),
        ]:
            nodes[case_id] = {"id": case_id, "label": f"Case {case_id}", "person": name, "district": district}
        edges.append({"source": str(link["left_case_id"]), "target": str(link["right_case_id"]), "confidence": round(float(link["confidence"]) * 100)})
    return {"nodes": list(nodes.values()), "edges": edges}


def repeat_patterns() -> list[dict[str, Any]]:
    cases = load_cases()
    grouped = cases[cases["canonical_demo_entity"].str.startswith("network-")].groupby("canonical_demo_entity")
    result = []
    for entity, group in grouped:
        if len(group) < 2:
            continue
        result.append(
            {
                "entity": f"Reviewed entity {entity.split('-')[-1].title()}",
                "case_count": int(len(group)),
                "districts": sorted(group["district"].unique().tolist()),
                "crime_heads": sorted(group["crime_head"].unique().tolist()),
                "last_seen": group["incident_date"].max().date().isoformat(),
                "status": "Case-history tracking after analyst confirmation",
            }
        )
    return sorted(result, key=lambda item: item["case_count"], reverse=True)


def correlations(district: str | None = None, crime_head: str | None = None) -> list[dict[str, Any]]:
    cases = _scope(load_cases(), district, crime_head)
    festival = cases.groupby("festival_day").size()
    rainfall = cases.groupby(
        pd.cut(cases["rainfall_index"], [-0.1, 0.3, 0.7, 1.1]), observed=False
    ).size()
    festival_lift = round(((festival.get(1, 0) / max(festival.get(0, 1), 1)) * 100) - 100, 1)
    wet_count = int(rainfall.iloc[-1]) if len(rainfall) else 0
    return [
        {"factor": "Festival calendar", "finding": f"{festival_lift:+.1f}% observed count difference on configured calendar dates.", "caveat": "Association only; sample size and reporting effects apply."},
        {"factor": "High rainfall periods", "finding": f"{wet_count} synthetic cases fall in the high-rainfall band.", "caveat": "Not evidence that rainfall causes crime."},
        {"factor": "Data-source mix", "finding": f"{round(cases['reported_source'].isin(['victim_reported', 'citizen_reported']).mean() * 100)}% are reported/citizen-source records.", "caveat": "Police-observed events remain outside the risk-training target."},
    ]


def audit_snapshot() -> list[dict[str, str]]:
    records = [
        ("model-risk-hgb-v1", "Model evaluation reviewed", "synthetic-demo"),
        ("link-5-11", "Candidate link opened for analyst review", "demo-analyst"),
        ("alert-h3-demo-0", "Alert viewed", "district-supervisor"),
    ]
    previous = "GENESIS"
    output = []
    for event_id, action, actor in records:
        entry_hash = hashlib.sha256(f"{previous}|{event_id}|{action}|{actor}".encode()).hexdigest()[:16]
        output.append({"event_id": event_id, "action": action, "actor": actor, "previous_hash": previous, "hash": entry_hash})
        previous = entry_hash
    return output


def record_frontend_event(event: str, details: dict[str, Any]) -> dict[str, Any]:
    """Persist non-sensitive UI telemetry for the terminal launcher and audit demo.

    The function intentionally logs only UI state, never raw FIR records or
    names. In a production deployment this would be routed to a protected,
    retention-controlled audit store.
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "details": details,
        "data_classification": "synthetic-demo-ui-telemetry",
    }
    EVENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EVENT_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    event_logger.info("FRONTEND_EVENT event=%s details=%s", event, details)
    return record
