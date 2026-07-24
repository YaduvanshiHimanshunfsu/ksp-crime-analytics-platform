"""API for the KSP Drishti synthetic demonstration."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import app.services as analytics


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

app = FastAPI(title="KSP Drishti API", version="0.2.0", description="AI-Driven Crime Analytics & Visualization Platform — Synthetic-data challenge demonstration API")

# BUG-6 fix: include 127.0.0.1 and allow env-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AlertFeedback(BaseModel):
    useful: bool
    reason: str = Field(min_length=3, max_length=280)


class FrontendTelemetry(BaseModel):
    event: str = Field(min_length=3, max_length=80, pattern=r"^[a-z0-9_\-]+$")
    details: dict[str, str | int | float | bool] = Field(default_factory=dict)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data": "synthetic"}


@app.get("/api/v1/data-status")
def get_data_status():
    """Report available data sources and current data mode."""
    return analytics.data_status()

# ---------------------------------------------------------------------------
# Core analytics endpoints
# ---------------------------------------------------------------------------


@app.get("/api/v1/overview")
def get_overview(district: str | None = None, crime_head: str | None = None):
    return analytics.overview(district, crime_head)


@app.get("/api/v1/hotspots")
def get_hotspots(district: str | None = None, crime_head: str | None = None, limit: int = 50, offset: int = 0):
    return analytics.hotspots(district, crime_head, limit=limit, offset=offset)


@app.get("/api/v1/trends")
def get_trends(district: str | None = None, crime_head: str | None = None):
    return analytics.trends(district, crime_head)


@app.get("/api/v1/alerts")
def get_alerts(district: str | None = None, crime_head: str | None = None, limit: int = 50, offset: int = 0):
    return analytics.alerts(district, crime_head, limit=limit, offset=offset)


@app.get("/api/v1/risk-forecast")
def get_risk_forecast(district: str | None = None, crime_head: str | None = None):
    return analytics.risk_forecast(district, crime_head)


@app.get("/api/v1/model-card")
def get_model_card():
    import json
    from pathlib import Path
    try:
        metrics_path = Path("data/models/risk_model_metrics.json")
        if metrics_path.exists():
            metrics = json.loads(metrics_path.read_text())
            metrics["prohibited_use"] = "Individual risk scoring, arrest decisions, automated deployment"
            metrics["explainability"] = "SHAP TreeExplainer (per-prediction feature attribution)"
            metrics["data_sources"] = {
                "training": "Synthetic FIR-style demonstration data",
                "calibration": "Karnataka Police / OpenCity.in 2025 (official aggregate)"
            }
            return metrics
    except Exception:
        pass
    return {"error": "Model metrics not found. Train the model first."}


@app.get("/api/v1/calibration-report")
def get_calibration_report():
    return analytics.calibration_report()


@app.get("/api/v1/network")
def get_network():
    return analytics.network()


@app.get("/api/v1/case-links")
def get_case_links(limit: int = 50, offset: int = 0):
    return analytics.case_links(limit=limit, offset=offset)


@app.get("/api/v1/repeat-patterns")
def get_repeat_patterns():
    return analytics.repeat_patterns()


@app.get("/api/v1/correlations")
def get_correlations(district: str | None = None, crime_head: str | None = None):
    return analytics.correlations(district, crime_head)


@app.get("/api/v1/audit")
def get_audit():
    return analytics.audit_snapshot()


# ---------------------------------------------------------------------------
# District drilldown
# ---------------------------------------------------------------------------

@app.get("/api/v1/district-drilldown/{district}")
def get_district_drilldown(district: str):
    """Detailed station-level breakdown for a specific district."""
    return analytics.district_drilldown(district)


# ---------------------------------------------------------------------------
# Public aggregate data endpoints
# ---------------------------------------------------------------------------

@app.get("/api/v1/public-context/overview")
def get_public_overview():
    """Overview of public aggregate crime data availability."""
    return analytics.public_overview()


@app.get("/api/v1/public-context/trends")
def get_public_trends():
    """Monthly trends from public aggregate data."""
    return analytics.public_trends()


@app.get("/api/v1/public-context/districts")
def get_public_districts():
    """District-wise comparison from public data."""
    return analytics.public_district_comparison()


@app.get("/api/v1/district-benchmark")
def get_district_benchmark():
    """Real KSP 2025 district volumes."""
    return analytics.district_benchmark()


@app.get("/api/v1/district-trends")
def get_district_trends():
    """Multi-year district trend data."""
    return analytics.category_trend()


@app.get("/api/v1/public-context/state-summary")
def get_state_summary():
    """State-level totals with attribution."""
    return analytics.public_overview()


# ---------------------------------------------------------------------------
# Feedback & telemetry
# ---------------------------------------------------------------------------


@app.post("/api/v1/alerts/{alert_id}/feedback")
def submit_feedback(alert_id: str, feedback: AlertFeedback):
    if not alert_id.startswith("h3-demo-"):
        raise HTTPException(status_code=404, detail="Alert not found")
    return {
        "alert_id": alert_id,
        "stored": True,
        "message": "Feedback stored for review quality. It does not automatically retrain the forecast model.",
        "feedback": feedback.model_dump(),
    }


@app.post("/api/v1/telemetry")
def record_telemetry(telemetry: FrontendTelemetry) -> dict[str, Any]:
    return analytics.record_frontend_event(telemetry.event, telemetry.details)


# ---------------------------------------------------------------------------
# Cache management
# ---------------------------------------------------------------------------

@app.post("/api/v1/cache/invalidate")
def invalidate_cache():
    """Clear the analytics data cache (useful after data regeneration)."""
    analytics.invalidate_cache()
    return {"status": "cache_cleared"}
