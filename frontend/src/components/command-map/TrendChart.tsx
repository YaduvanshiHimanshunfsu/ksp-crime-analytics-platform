import React from "react";
import type { Trend } from "../../types";

export default function TrendChart({ points }: { points: Trend[] }) {
  if (!points.length) return <div className="empty">No trend data is available for this filter.</div>;
  const max = Math.max(...points.flatMap((point) => [point.incidents, point.expected]), 1);
  const coordinates = points.map((point, index) => `${(index / Math.max(points.length - 1, 1)) * 100},${100 - (point.incidents / max) * 88}`).join(" ");
  const expected = points.map((point, index) => `${(index / Math.max(points.length - 1, 1)) * 100},${100 - (point.expected / max) * 88}`).join(" ");
  
  return (
    <div className="trend-wrap">
      <svg className="trend-chart" viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Weekly reported incident trend">
        <line x1="0" y1="85" x2="100" y2="85" className="grid-line" />
        <line x1="0" y1="50" x2="100" y2="50" className="grid-line" />
        <polyline points={expected} className="expected-line" />
        <polyline points={coordinates} className="observed-line" />
        {points.map((point, index) => point.anomaly && (
          <circle key={point.week} cx={(index / Math.max(points.length - 1, 1)) * 100} cy={100 - (point.incidents / max) * 88} r="2.4" className="anomaly-dot" />
        ))}
      </svg>
      <div className="chart-axis">
        <span>{points[0].week.slice(5)}</span>
        <span>Latest week</span>
      </div>
    </div>
  );
}
