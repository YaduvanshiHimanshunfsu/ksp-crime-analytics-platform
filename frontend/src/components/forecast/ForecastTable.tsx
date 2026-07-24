import React from "react";
import type { Forecast } from "../../types";

function riskColor(score: number) {
  if (score >= 85) return "#f16361";
  if (score >= 70) return "#f5b942";
  return "#45c9a3";
}

export default function ForecastTable({ forecasts, onSelectArea }: { forecasts: Forecast[]; onSelectArea: (area: string) => void }) {
  return (
    <article className="panel forecast-table">
      <div className="forecast-head">
        <span>Area</span>
        <span>Crime type</span>
        <span>Next 7 days</span>
        <span>Risk</span>
      </div>
      {forecasts.map((forecast) => (
        <button 
          className="forecast-row" 
          key={`${forecast.area}-${forecast.crime_head}`} 
          onClick={() => onSelectArea(forecast.area)}
        >
          <b>{forecast.area}<small>{forecast.district}</small></b>
          <span>{forecast.crime_head}</span>
          <span>{forecast.next_week_range[0]}–{forecast.next_week_range[1]} reports</span>
          <strong style={{ color: riskColor(forecast.risk_score) }}>{forecast.risk_score}</strong>
        </button>
      ))}
    </article>
  );
}
