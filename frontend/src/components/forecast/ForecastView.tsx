import React, { useState } from "react";
import type { DashboardData } from "../../hooks/useDashboardData";
import ForecastTable from "./ForecastTable";
import ShapWaterfall from "./ShapWaterfall";
import CorrelationCards from "./CorrelationCards";

export default function ForecastView({ data }: { data: DashboardData }) {
  const [selectedArea, setSelectedArea] = useState<string | null>(
    data.currentForecasts.length > 0 ? data.currentForecasts[0].area : null
  );

  const selectedForecast = data.currentForecasts.find(f => f.area === selectedArea) ?? data.currentForecasts[0];

  return (
    <section className="workspace">
      <div className="workspace-heading">
        <div>
          <p className="eyebrow">PREDICTIVE RISK SCORING</p>
          <h2>Forecast reported incident volume</h2>
          <p>Forecasts are location/category estimates with ranges. They are not instructions to target a person or community.</p>
        </div>
        <span className="guardrail">Advisory only</span>
      </div>
      
      <div className="forecast-layout">
        <ForecastTable 
          forecasts={data.currentForecasts} 
          onSelectArea={setSelectedArea} 
        />
        
        <article className="panel explain-panel">
          <p className="eyebrow">FORECAST EXPLANATION</p>
          <h3>What moved this estimate</h3>
          <p style={{ color: '#8b949e', fontSize: '0.85rem', marginBottom: '1rem' }}>
            Showing top SHAP drivers for {selectedForecast?.area} ({selectedForecast?.crime_head})
          </p>
          
          <ShapWaterfall drivers={selectedForecast?.drivers ?? []} />
          
          <div className="credibility" style={{ marginTop: '2rem' }}>
            <p className="eyebrow">MODEL SAFEGUARDS</p>
            <div><span>Prediction target</span><b>Reported incidents</b></div>
            <div><span>Arrest/chargesheet features</span><b>Excluded</b></div>
            <div><span>Confidence output</span><b>Range, not certainty</b></div>
          </div>
        </article>
      </div>
      
      <CorrelationCards correlations={data.currentCorrelations} />
    </section>
  );
}
