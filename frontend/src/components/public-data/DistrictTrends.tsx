import React, { useState, useEffect } from "react";
import { getDistrictTrends } from "../../api";
import type { DistrictTrend } from "../../types";

export default function DistrictTrends({ district }: { district: string }) {
  const [trends, setTrends] = useState<DistrictTrend[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    getDistrictTrends(district).then(res => {
      if (active) {
        setTrends(res.data);
        setLoading(false);
      }
    }).catch(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, [district]);

  if (loading) return <div style={{ color: '#8b949e', fontSize: '0.85rem' }}>Loading trends...</div>;
  if (trends.length === 0) return <div style={{ color: '#8b949e', fontSize: '0.85rem' }}>No trend data available.</div>;

  const maxVal = Math.max(...trends.map(t => t.total_crimes), 1);

  return (
    <div className="district-trends">
      <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end', height: '60px', marginTop: '1rem' }}>
        {trends.map(t => (
          <div key={t.year} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
            <span style={{ fontSize: '0.75rem', color: '#e6edf3' }}>{t.total_crimes}</span>
            <div style={{ width: '100%', background: '#45c9a3', height: `${(t.total_crimes / maxVal) * 40}px`, borderRadius: '2px 2px 0 0' }} />
            <span style={{ fontSize: '0.75rem', color: '#8b949e' }}>{t.year}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
