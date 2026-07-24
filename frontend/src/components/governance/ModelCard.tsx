import React, { useState, useEffect } from "react";
import { getModelCard, getCalibrationReport } from "../../api";
import type { ModelCard as ModelCardType, CalibrationReport } from "../../types";

export default function ModelCard() {
  const [modelCard, setModelCard] = useState<ModelCardType | null>(null);
  const [calibration, setCalibration] = useState<CalibrationReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    Promise.all([getModelCard(), getCalibrationReport()]).then(([modelRes, calibRes]) => {
      if (active) {
        if (!("error" in modelRes.data)) setModelCard(modelRes.data as ModelCardType);
        setCalibration(calibRes.data as CalibrationReport);
        setLoading(false);
      }
    }).catch(() => {
      if (active) setLoading(false);
    });
    return () => { active = false; };
  }, []);

  if (loading) return <div>Loading model metrics...</div>;
  if (!modelCard) return <div>Model metrics not found (offline).</div>;

  return (
    <article className="panel">
      <p className="eyebrow">MODEL CARD</p>
      <h3>{modelCard.model_version}</h3>
      <dl>
        <dt>Algorithm</dt>
        <dd>{modelCard.algorithm} ({modelCard.feature_count} features)</dd>
        <dt>Performance</dt>
        <dd>MAE: {modelCard.model_mae} ({modelCard.improvement_percent}% better than baseline)</dd>
        <dt>Training Split</dt>
        <dd>Before {modelCard.temporal_split} ({modelCard.train_rows} rows)</dd>
        <dt>Explainability</dt>
        <dd>{modelCard.explainability}</dd>
        <dt>Prohibited use</dt>
        <dd>{modelCard.prohibited_use}</dd>
      </dl>
      
      {calibration && calibration.status === "calibrated" && (
        <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <p className="eyebrow">CALIBRATION REPORT</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
            <div>
              <span style={{ display: 'block', fontSize: '0.75rem', color: '#8b949e' }}>Synthetic Size</span>
              <strong style={{ fontSize: '1.2rem', color: '#e6edf3' }}>{calibration.synthetic_total?.toLocaleString()}</strong>
            </div>
            <div>
              <span style={{ display: 'block', fontSize: '0.75rem', color: '#8b949e' }}>Geospatial Correlation</span>
              <strong style={{ fontSize: '1.2rem', color: '#45c9a3' }}>{(calibration.district_correlation ?? 0).toFixed(2)}</strong>
            </div>
          </div>
          <small style={{ color: '#8b949e', display: 'block', lineHeight: 1.4 }}>{calibration.interpretation}</small>
        </div>
      )}
    </article>
  );
}
