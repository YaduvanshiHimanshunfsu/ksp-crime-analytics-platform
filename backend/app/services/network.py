from typing import Any
from .data_loader import load_cases, load_links

def case_links(limit: int = 30, offset: int = 0) -> list[dict[str, Any]]:
    links = load_links()
    if links.empty:
        return []
    return links.iloc[offset:offset+limit].assign(confidence=lambda frame: (frame["confidence"] * 100).round(0).astype(int)).to_dict(orient="records")


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
        parts = entity.split('-')
        name = parts[-1].title() if len(parts) > 1 else entity.title()
        result.append(
            {
                "entity": f"Reviewed entity {name}",
                "case_count": int(len(group)),
                "districts": sorted(group["district"].unique().tolist()),
                "crime_heads": sorted(group["crime_head"].unique().tolist()),
                "last_seen": group["incident_date"].max().date().isoformat(),
                "status": "Case-history tracking after analyst confirmation",
            }
        )
    return sorted(result, key=lambda item: item["case_count"], reverse=True)
