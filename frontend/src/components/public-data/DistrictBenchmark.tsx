import React, { useState, useEffect } from "react";
import { getDistrictBenchmark } from "../../api";
import type { DistrictBenchmark as DistrictBenchmarkType } from "../../types";

export default function DistrictBenchmark() {
  const [benchmarks, setBenchmarks] = useState<DistrictBenchmarkType[]>([]);

  useEffect(() => {
    let active = true;
    getDistrictBenchmark().then(res => {
      if (active) setBenchmarks(res.data);
    });
    return () => { active = false; };
  }, []);

  if (benchmarks.length === 0) return null;

  const maxCases = Math.max(...benchmarks.map(b => b.cases_reported), 1);

  return (
    <article className="panel district-benchmark-panel" style={{ marginTop: '1rem' }}>
      <p className="eyebrow" style={{ color: '#45c9a3' }}>OFFICIAL KARNATAKA 2025 DATA</p>
      <h3 style={{ margin: '4px 0 12px' }}>Real KSP Volumes</h3>
      <div className="benchmark-list" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {benchmarks.slice(0, 5).map(b => (
          <div key={b.district} className="benchmark-row" style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: '#e6edf3' }}>
              <span>{b.district}</span>
              <span>{b.cases_reported.toLocaleString()}</span>
            </div>
            <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px' }}>
              <div style={{ width: `${(b.cases_reported / maxCases) * 100}%`, height: '100%', background: '#165688', borderRadius: '3px' }} />
            </div>
          </div>
        ))}
      </div>
      <small style={{ display: 'block', marginTop: '12px', color: '#656d76', fontSize: '0.75rem' }}>Source: OpenCity.in SLL aggregate</small>
    </article>
  );
}
