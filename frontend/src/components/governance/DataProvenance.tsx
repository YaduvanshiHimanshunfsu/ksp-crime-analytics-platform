import React from "react";
import DistrictTrends from "../public-data/DistrictTrends";

export default function DataProvenance({ district }: { district: string }) {
  return (
    <article className="panel">
      <p className="eyebrow">DATA PROVENANCE</p>
      <h3>Public Data Context</h3>
      <p style={{ fontSize: '0.85rem', color: '#8b949e', marginBottom: '1rem' }}>
        The system uses aggregated historical SLL cases from Karnataka OpenCity.in data as a real-world baseline.
      </p>
      
      <div style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '6px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <b style={{ color: '#e6edf3' }}>{district === "All Karnataka" ? "Statewide" : district} Trends</b>
          <span style={{ fontSize: '0.75rem', padding: '2px 6px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px' }}>Real Data</span>
        </div>
        <DistrictTrends district={district} />
      </div>
    </article>
  );
}
