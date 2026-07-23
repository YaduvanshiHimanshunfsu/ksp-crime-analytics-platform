"""API for the KSP Drishti synthetic demonstration."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services import analytics


logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

app = FastAPI(title="KSP Drishti API", version="0.1.0", description="Synthetic-data challenge demonstration API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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


@app.get("/api/v1/overview")
def get_overview(district: str | None = None, crime_head: str | None = None):
    return analytics.overview(district, crime_head)


@app.get("/api/v1/hotspots")
def get_hotspots(district: str | None = None, crime_head: str | None = None):
    return analytics.hotspots(district, crime_head)


@app.get("/api/v1/trends")
def get_trends(district: str | None = None, crime_head: str | None = None):
    return analytics.trends(district, crime_head)


@app.get("/api/v1/alerts")
def get_alerts(district: str | None = None, crime_head: str | None = None):
    return analytics.alerts(district, crime_head)


@app.get("/api/v1/risk-forecast")
def get_risk_forecast(district: str | None = None, crime_head: str | None = None):
    return analytics.risk_forecast(district, crime_head)


@app.get("/api/v1/network")
def get_network():
    return analytics.network()


@app.get("/api/v1/case-links")
def get_case_links():
    return analytics.case_links()


@app.get("/api/v1/repeat-patterns")
def get_repeat_patterns():
    return analytics.repeat_patterns()


@app.get("/api/v1/correlations")
def get_correlations(district: str | None = None, crime_head: str | None = None):
    return analytics.correlations(district, crime_head)


@app.get("/api/v1/audit")
def get_audit():
    return analytics.audit_snapshot()


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
