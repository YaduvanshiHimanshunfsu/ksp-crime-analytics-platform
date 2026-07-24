import json
import logging
from datetime import datetime, timezone
from typing import Any
from .data_loader import PROJECT_ROOT

EVENT_LOG_PATH = PROJECT_ROOT / "logs" / "frontend_events.jsonl"
event_logger = logging.getLogger("ksp_drishti.frontend")

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
