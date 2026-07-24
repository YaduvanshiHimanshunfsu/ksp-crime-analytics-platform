import hashlib
import pandas as pd
from typing import Any
from .data_loader import load_cases, _scope

def audit_snapshot() -> list[dict[str, str]]:
    records = [
        ("model-risk-hgb-v1", "Model evaluation reviewed", "synthetic-demo"),
        ("link-5-11", "Candidate link opened for analyst review", "demo-analyst"),
        ("alert-h3-demo-0", "Alert viewed", "district-supervisor"),
        ("data-import", "Public aggregate data imported", "data-pipeline"),
        ("cache-refresh", "Analytics cache refreshed", "system"),
    ]
    previous = "GENESIS"
    output = []
    for event_id, action, actor in records:
        entry_hash = hashlib.sha256(f"{previous}|{event_id}|{action}|{actor}".encode()).hexdigest()[:16]
        output.append({"event_id": event_id, "action": action, "actor": actor, "previous_hash": previous, "hash": entry_hash})
        previous = entry_hash
    return output


def correlations(district: str | None = None, crime_head: str | None = None) -> list[dict[str, Any]]:
    cases = _scope(load_cases(), district, crime_head)
    if cases.empty:
        return []
    festival = cases.groupby("festival_day").size()
    rainfall = cases.groupby(
        pd.cut(cases["rainfall_index"], [-0.1, 0.3, 0.7, 1.1]), observed=False
    ).size()
    festival_lift = round(((festival.get(1, 0) / max(festival.get(0, 1), 1)) * 100) - 100, 1)
    wet_count = int(rainfall.iloc[-1]) if len(rainfall) else 0

    urban = round(cases["urbanization_index"].mean(), 2) if "urbanization_index" in cases else 0.5
    lit = round(cases["literacy_index"].mean(), 2) if "literacy_index" in cases else 0.7
    pop = int(cases["population_density"].mean()) if "population_density" in cases else 1000

    return [
        {"factor": "Festival calendar", "finding": f"{festival_lift:+.1f}% observed count difference on configured calendar dates.", "caveat": "Association only; sample size and reporting effects apply."},
        {"factor": "High rainfall periods", "finding": f"{wet_count} synthetic cases fall in the high-rainfall band.", "caveat": "Not evidence that rainfall causes crime."},
        {"factor": "Data-source mix", "finding": f"{round(cases['reported_source'].isin(['victim_reported', 'citizen_reported']).mean() * 100)}% are reported/citizen-source records.", "caveat": "Police-observed events remain outside the risk-training target."},
        {"factor": "Urbanization", "finding": f"Average urbanization index of {urban} in affected areas.", "caveat": "Descriptive only."},
        {"factor": "Literacy & Population", "finding": f"Avg literacy {lit}, density {pop}/sq km.", "caveat": "Socio-economic context, not causality."},
    ]
