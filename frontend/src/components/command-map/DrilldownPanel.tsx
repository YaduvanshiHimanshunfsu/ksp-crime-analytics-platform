import React from "react";
import type { DistrictDrilldown } from "../../types";

export default function DrilldownPanel({ drilldown }: { drilldown: DistrictDrilldown | null }) {
  if (!drilldown) return null;

  return (
    <div className="drilldown-panel">
      <p className="eyebrow" style={{ marginTop: "2rem" }}>DISTRICT DRILLDOWN</p>
      <h3 style={{ margin: "4px 0 16px 0", fontSize: "1.2rem", fontWeight: "600" }}>{drilldown.district}</h3>
      <div className="drilldown-list" style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {drilldown.stations.slice(0, 6).map(st => (
          <div key={st.station} className="drilldown-item" style={{ background: "rgba(255,255,255,0.04)", padding: "12px", borderRadius: "6px", borderLeft: "3px solid #165688" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
              <b style={{ color: "#d2d8e0", fontSize: "1rem" }}>{st.station}</b>
              <span style={{ background: "rgba(255,255,255,0.1)", padding: "2px 8px", borderRadius: "12px", fontSize: "0.85rem", color: "#a5b4cb" }}>{st.total_cases} cases</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "#8b949e" }}>
              <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "60%" }}>Top: {st.top_crime}</span>
              <span>Recent 28d: <strong>{st.recent_cases}</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
