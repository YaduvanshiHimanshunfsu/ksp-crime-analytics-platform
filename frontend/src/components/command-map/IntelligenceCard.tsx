import React, { useState } from "react";
import type { Alert } from "../../types";
import { submitAlertFeedback, logFrontendEvent } from "../../api";

function riskColor(score: number) {
  if (score >= 85) return "#f16361";
  if (score >= 70) return "#f5b942";
  return "#45c9a3";
}

export default function IntelligenceCard({ selectedAlert }: { selectedAlert: Alert | null }) {
  const [feedback, setFeedback] = useState<string>("");
  const confidence = selectedAlert?.confidence ?? "Review required";

  return (
    <>
      <div className="panel-title">
        <div>
          <p className="eyebrow">INTELLIGENCE CARD</p>
          <h3>{selectedAlert?.title ?? "Select a risk cell"}</h3>
        </div>
        <span className={`confidence ${confidence === "High" ? "high" : "review"}`}>{confidence}</span>
      </div>
      
      {selectedAlert && (
        <>
          <div className="score-row">
            <strong style={{ color: riskColor(selectedAlert.risk_score) }}>{selectedAlert.risk_score}</strong>
            <span>place risk<br />indicator</span>
          </div>
          <p className="alert-reason">{selectedAlert.reason}</p>
          
          <div className="credibility">
            <p className="eyebrow">DATA CREDIBILITY LENS</p>
            <div><span>Reported/citizen source</span><b>{selectedAlert.credibility.reported_source_share}%</b></div>
            <div><span>Geographic completeness</span><b>{selectedAlert.credibility.geo_complete}%</b></div>
            <div><span>Decision state</span><b>Human review</b></div>
          </div>
          
          <button 
            className="primary" 
            onClick={async () => { 
              const ok = await submitAlertFeedback(selectedAlert.id, true, "Marked useful from UI");
              setFeedback(ok ? "Feedback stored for review quality." : "Could not store feedback. Check connection.");
              logFrontendEvent("alert_marked_useful", { alert_id: selectedAlert.id }); 
            }}
          >
            Mark useful
          </button>
          
          {feedback && <p className="feedback">{feedback}</p>}
        </>
      )}
    </>
  );
}
