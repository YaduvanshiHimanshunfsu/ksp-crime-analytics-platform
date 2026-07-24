import React from "react";
import type { DashboardData } from "../../hooks/useDashboardData";
import ModelCard from "./ModelCard";
import DataProvenance from "./DataProvenance";
import PDFExport from "../shared/PDFExport";

export default function GovernanceView({ data, district }: { data: DashboardData; district: string }) {
  return (
    <section className="workspace" id="governance-export-target">
      <div className="workspace-heading" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p className="eyebrow">GOVERNANCE AND AUDIT</p>
          <h2>Trust must be visible, not assumed</h2>
          <p>Access boundaries, model limitations, and analyst decisions are part of the product.</p>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span className="guardrail">On-premise ready</span>
          <PDFExport targetId="governance-export-target" filename="KSP_Drishti_Governance_Brief.pdf" />
        </div>
      </div>
      
      <div className="governance-grid">
        <ModelCard />
        
        <article className="panel">
          <p className="eyebrow">ROLE-BASED ACCESS</p>
          <div className="role-row">
            <b>SHO</b>
            <span>Own station analytics and assigned review queue</span>
          </div>
          <div className="role-row">
            <b>SP</b>
            <span>District aggregates and station drilldowns</span>
          </div>
          <div className="role-row">
            <b>SCRB HQ</b>
            <span>State-level aggregates and governance audit</span>
          </div>
        </article>
        
        <DataProvenance district={district} />
        
        <article className="panel">
          <p className="eyebrow">INTEGRITY LOG</p>
          <div className="hash-item"><span>GENESIS</span><b>→ 7a24f1a8…</b></div>
          <div className="hash-item"><span>Link review opened</span><b>→ cd9e52bf…</b></div>
          <div className="hash-item"><span>Alert viewed</span><b>→ 12f6a8c1…</b></div>
          <small>Demonstration of a verifiable event chain; production requires append-only storage.</small>
        </article>
      </div>
    </section>
  );
}
