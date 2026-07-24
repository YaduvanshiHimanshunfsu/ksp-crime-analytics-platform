import React from "react";
import type { DashboardData } from "../../hooks/useDashboardData";
import NetworkGraph from "./NetworkGraph";
import ReviewQueue from "./ReviewQueue";
import RepeatPatterns from "./RepeatPatterns";

export default function CaseLinkView({ data }: { data: DashboardData }) {
  return (
    <section className="workspace">
      <div className="workspace-heading">
        <div>
          <p className="eyebrow">NETWORK AND LINK ANALYSIS</p>
          <h2>Cross-station case evidence</h2>
          <p>Candidate links are explainable and need an analyst decision before they become part of a case history.</p>
        </div>
        <span className="guardrail">No automatic merge</span>
      </div>
      
      <div className="case-grid">
        <article className="panel">
          <NetworkGraph network={data.currentNetwork} />
        </article>
        
        <article className="panel review-panel">
          <p className="eyebrow">ANALYST REVIEW QUEUE</p>
          <ReviewQueue links={data.currentLinks} />
        </article>
      </div>
      
      <article className="panel repeat-panel">
        <div className="panel-title">
          <div>
            <p className="eyebrow">REPEAT CASE-HISTORY TRACKING</p>
            <h3>Reviewed entity timelines</h3>
          </div>
          <span className="guardrail">No person risk score</span>
        </div>
        <RepeatPatterns patterns={data.patterns} />
      </article>
    </section>
  );
}
