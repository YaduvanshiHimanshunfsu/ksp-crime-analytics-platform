import React, { Component, useEffect, useMemo, useRef, useState } from "react";
import L from "leaflet";
import { loadDashboard, logFrontendEvent, getDistrictDrilldown } from "./api";
import KarnatakaMap from "./KarnatakaMap";
import type { Alert, Hotspot, Network, Trend, DistrictDrilldown } from "./types";

type DashboardData = Awaited<ReturnType<typeof loadDashboard>>;
type View = "Command map" | "CaseLink" | "Risk forecast" | "Governance";

const districts = ["All Karnataka", "Bengaluru Urban", "Mysuru", "Hubballi-Dharwad", "Mangaluru", "Kalaburagi"];
const crimeHeads = ["All crime heads", "Theft", "Burglary", "Cyber Fraud", "Assault", "Robbery"];

function riskColor(score: number) {
  if (score >= 85) return "#f16361";
  if (score >= 70) return "#f5b942";
  return "#45c9a3";
}

/* ── Error Boundary (BUG-13 fix) ── */
class ErrorBoundary extends Component<{ children: React.ReactNode }, { hasError: boolean; error: string }> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: "" };
  }
  static getDerivedStateFromError(err: Error) {
    return { hasError: true, error: err.message };
  }
  render() {
    if (this.state.hasError)
      return (
        <main className="error-boundary" style={{ padding: '2rem', color: '#f16361' }}>
          <div className="brand-mark" style={{ marginBottom: '1rem', width: '3rem', height: '3rem', fontSize: '2rem' }}>!</div>
          <h2>Something went wrong</h2>
          <p>{this.state.error}</p>
          <button className="primary" style={{ marginTop: '1rem', width: 'auto' }} onClick={() => window.location.reload()}>Reload dashboard</button>
        </main>
      );
    return this.props.children;
  }
}

function MetricCard({ label, value, note, tone = "default" }: { label: string; value: string; note: string; tone?: "default" | "attention" | "positive" }) {
  return <article className={`metric-card ${tone}`}><span>{label}</span><strong>{value}</strong><small>{note}</small></article>;
}

function TrendChart({ points }: { points: Trend[] }) {
  if (!points.length) return <div className="empty">No trend data is available for this filter.</div>;
  const max = Math.max(...points.flatMap((point) => [point.incidents, point.expected]), 1);
  const coordinates = points.map((point, index) => `${(index / Math.max(points.length - 1, 1)) * 100},${100 - (point.incidents / max) * 88}`).join(" ");
  const expected = points.map((point, index) => `${(index / Math.max(points.length - 1, 1)) * 100},${100 - (point.expected / max) * 88}`).join(" ");
  return <div className="trend-wrap"><svg className="trend-chart" viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Weekly reported incident trend">
    <line x1="0" y1="85" x2="100" y2="85" className="grid-line" /><line x1="0" y1="50" x2="100" y2="50" className="grid-line" />
    <polyline points={expected} className="expected-line" /><polyline points={coordinates} className="observed-line" />
    {points.map((point, index) => point.anomaly && <circle key={point.week} cx={(index / Math.max(points.length - 1, 1)) * 100} cy={100 - (point.incidents / max) * 88} r="2.4" className="anomaly-dot" />)}
  </svg><div className="chart-axis"><span>{points[0].week.slice(5)}</span><span>Latest week</span></div></div>;
}


function NetworkView({ network }: { network: Network }) {
  const position = (index: number) => {
    const angle = (index / Math.max(network.nodes.length, 1)) * Math.PI * 2 - Math.PI / 2;
    return { x: 270 + Math.cos(angle) * 180, y: 180 + Math.sin(angle) * 116 };
  };
  const lookup = Object.fromEntries(network.nodes.map((node, index) => [node.id, position(index)]));
  return <div className="network-wrap"><svg className="network-graph" viewBox="0 0 540 360" aria-label="Cross-district candidate link network">
    {network.edges.map((edge, index) => <line key={`${edge.source}-${edge.target}-${index}`} x1={lookup[edge.source]?.x} y1={lookup[edge.source]?.y} x2={lookup[edge.target]?.x} y2={lookup[edge.target]?.y} className="network-edge" />)}
    {network.nodes.map((node, index) => { const p = position(index); return <g key={node.id}><circle cx={p.x} cy={p.y} r="33" className="network-node" /><text x={p.x} y={p.y - 3} textAnchor="middle" className="network-label">{node.label}</text><text x={p.x} y={p.y + 14} textAnchor="middle" className="network-sub">{node.district.split(" ")[0]}</text></g>; })}
  </svg><p className="graph-caption">Edges are candidate links, not confirmed identities. Each requires analyst review.</p></div>;
}

function App() {
  const [district, setDistrict] = useState("All Karnataka");
  const [crimeHead, setCrimeHead] = useState("All crime heads");
  const [view, setView] = useState<View>("Command map");
  const [data, setData] = useState<DashboardData | null>(null);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [feedback, setFeedback] = useState<string>("");
  const [drilldown, setDrilldown] = useState<DistrictDrilldown | null>(null);

  useEffect(() => {
    loadDashboard(district, crimeHead).then((bundle) => { setData(bundle); setSelectedAlert(bundle.currentAlerts[0] ?? null); });
    logFrontendEvent("dashboard_filter_changed", { district, crime_head: crimeHead });
    
    if (district !== "All Karnataka") {
      getDistrictDrilldown(district).then(res => setDrilldown(res.data));
    } else {
      setDrilldown(null);
    }
  }, [district, crimeHead]);
  if (!data) return <main className="loading"><div className="loader" /> Loading KSP Dṛṣṭi…</main>;

  const confidence = selectedAlert?.confidence ?? "Review required";
  return <ErrorBoundary><main className="app-shell">
    <header className="topbar"><div className="brand"><div className="brand-mark">D</div><div><small>KARNATAKA STATE POLICE · SYNTHETIC DEMO</small><h1>KSP Dṛṣṭi</h1></div></div>
      <div className="topbar-actions"><span className="status-pill"><i /> analyst-reviewed intelligence</span><button className="profile">SP <span>⌄</span></button></div></header>
    {!data.isLive && <div className="offline-banner">Live backend disconnected. Showing offline mock data.</div>}
    <section className="notice"><b>Demonstration data only.</b> {data.summary.synthetic_notice}</section>
    <section className="controlbar"><div className="view-tabs">{(["Command map", "CaseLink", "Risk forecast", "Governance"] as View[]).map((item) => <button key={item} className={view === item ? "active" : ""} onClick={() => { setView(item); logFrontendEvent("view_changed", { view: item }); }}>{item}</button>)}</div>
      <div className="filters"><label>District<select value={district} onChange={(event) => setDistrict(event.target.value)}>{districts.map((item) => <option key={item}>{item}</option>)}</select></label><label>Crime type<select value={crimeHead} onChange={(event) => setCrimeHead(event.target.value)}>{crimeHeads.map((item) => <option key={item}>{item}</option>)}</select></label></div>
    </section>

    {view === "Command map" && <section className="dashboard-grid">
      <aside className="left-rail"><p className="eyebrow">STATE SITUATION</p><MetricCard label="Reported cases" value={data.summary.total_cases.toLocaleString()} note="selected synthetic dataset" /><MetricCard label="Last 28 days" value={data.summary.last_28_days.toString()} note={`${data.summary.change_percent >= 0 ? "+" : ""}${data.summary.change_percent}% vs prior 28 days`} tone={data.summary.change_percent > 0 ? "attention" : "positive"} /><MetricCard label="Active review alerts" value={data.summary.active_alerts.toString()} note="advisory only" />
        <div className="layer-control"><p className="eyebrow">MAP LAYERS</p><label><input type="checkbox" defaultChecked /> Credibility-scored hotspots</label><label><input type="checkbox" defaultChecked /> Trend anomalies</label><label><input type="checkbox" /> Reviewed case density</label></div></aside>
      <section className="map-column"><div className="section-heading"><div><p className="eyebrow">PLACE-BASED INTELLIGENCE</p><h2>Where reported patterns need attention</h2></div><span className="date-pill">Data through {data.summary.latest_data_date}</span></div><KarnatakaMap hotspots={data.mapHotspots} selected={selectedAlert} onSelectHotspot={(spot) => { setSelectedAlert(data.currentAlerts.find((alert) => alert.id === spot.id) ?? null); logFrontendEvent("hotspot_selected", { hotspot_id: spot.id, station: spot.station, district: spot.district }); }} onSelectDistrict={(dist) => { setDistrict(dist); logFrontendEvent("district_selected", { district: dist }); }} /><article className="panel trend-panel"><div className="panel-title"><div><p className="eyebrow">TREND AND ANOMALY DETECTION</p><h3>Weekly reported incidents</h3></div><span className="legend-line">Observed <i /> Expected</span></div><TrendChart points={data.chartTrends} /></article></section>
      <aside className="right-rail"><div className="panel-title"><div><p className="eyebrow">INTELLIGENCE CARD</p><h3>{selectedAlert?.title ?? "Select a risk cell"}</h3></div><span className={`confidence ${confidence === "High" ? "high" : "review"}`}>{confidence}</span></div>{selectedAlert && <><div className="score-row"><strong style={{ color: riskColor(selectedAlert.risk_score) }}>{selectedAlert.risk_score}</strong><span>place risk<br />indicator</span></div><p className="alert-reason">{selectedAlert.reason}</p><div className="credibility"><p className="eyebrow">DATA CREDIBILITY LENS</p><div><span>Reported/citizen source</span><b>{selectedAlert.credibility.reported_source_share}%</b></div><div><span>Geographic completeness</span><b>{selectedAlert.credibility.geo_complete}%</b></div><div><span>Decision state</span><b>Human review</b></div></div><button className="primary" onClick={() => { setFeedback("Marked useful - stored for alert-quality review."); logFrontendEvent("alert_marked_useful", { alert_id: selectedAlert.id }); }}>Mark useful</button>{feedback && <p className="feedback">{feedback}</p>}</>}
        {drilldown && (
          <div className="drilldown-panel">
            <p className="eyebrow" style={{ marginTop: "2rem" }}>DISTRICT DRILLDOWN</p>
            <h3 style={{ margin: "4px 0 16px 0", fontSize: "1.2rem", fontWeight: "600" }}>{drilldown.district}</h3>
            <div className="drilldown-list" style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
              {drilldown.stations.slice(0, 6).map(st => (
                <div key={st.station} className="drilldown-item" style={{ background: "rgba(255,255,255,0.04)", padding: "12px", borderRadius: "6px", borderLeft: "3px solid #165688" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
                    <b style={{ color: "#d2d8e0", fontSize: "1rem" }}>{st.station}</b>
                    <span style={{ background: "rgba(255,255,255,0.1)", padding: "2px 8px", borderRadius: "12px", fontSize: "0.85rem", color: "#a5b4cb" }}>{st.total_cases} cases</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", color: "#8b949e" }}>
                    <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: "60%" }}>Top: {st.top_crime}</span>
                    <span>Recent 28d: <strong>{st.recent_cases}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </aside>
    </section>}

    {view === "CaseLink" && <section className="workspace"><div className="workspace-heading"><div><p className="eyebrow">NETWORK AND LINK ANALYSIS</p><h2>Cross-station case evidence</h2><p>Candidate links are explainable and need an analyst decision before they become part of a case history.</p></div><span className="guardrail">No automatic merge</span></div><div className="case-grid"><article className="panel"><NetworkView network={data.currentNetwork} /></article><article className="panel review-panel"><p className="eyebrow">ANALYST REVIEW QUEUE</p>{data.currentLinks.slice(0, 4).map((link) => <div className="link-row" key={`${link.left_case_id}-${link.right_case_id}`}><div><b>Case {link.left_case_id} ↔ Case {link.right_case_id}</b><span>{link.left_district} · {link.right_district}</span></div><strong>{link.confidence}%</strong><small>Name {Math.round(link.name_similarity * 100)}% · age gap {link.age_gap} · MO {link.same_modus_operandi ? "matches" : "differs"}</small><div className="review-actions"><button>Confirm</button><button>Reject</button><button>Defer</button></div></div>)}</article></div><article className="panel repeat-panel"><div className="panel-title"><div><p className="eyebrow">REPEAT CASE-HISTORY TRACKING</p><h3>Reviewed entity timelines</h3></div><span className="guardrail">No person risk score</span></div>{data.patterns.map((pattern) => <div className="pattern-row" key={pattern.entity}><b>{pattern.entity}</b><span>{pattern.case_count} linked cases</span><span>{pattern.districts.join(" · ")}</span><span>{pattern.crime_heads.join(", ")}</span><small>Last seen {pattern.last_seen}</small></div>)}</article></section>}

    {view === "Risk forecast" && <section className="workspace"><div className="workspace-heading"><div><p className="eyebrow">PREDICTIVE RISK SCORING</p><h2>Forecast reported incident volume</h2><p>Forecasts are location/category estimates with ranges. They are not instructions to target a person or community.</p></div><span className="guardrail">Advisory only</span></div><div className="forecast-layout"><article className="panel forecast-table"><div className="forecast-head"><span>Area</span><span>Crime type</span><span>Next 7 days</span><span>Risk</span></div>{data.currentForecasts.map((forecast) => <button className="forecast-row" key={`${forecast.area}-${forecast.crime_head}`} onClick={() => setSelectedAlert(data.currentAlerts.find((alert) => alert.title.includes(forecast.area)) ?? null)}><b>{forecast.area}<small>{forecast.district}</small></b><span>{forecast.crime_head}</span><span>{forecast.next_week_range[0]}–{forecast.next_week_range[1]} reports</span><strong style={{ color: riskColor(forecast.risk_score) }}>{forecast.risk_score}</strong></button>)}</article><article className="panel explain-panel"><p className="eyebrow">FORECAST EXPLANATION</p><h3>What moved this estimate</h3><ol>{(data.currentForecasts[0]?.drivers ?? []).map((driver) => <li key={driver}>{driver}</li>)}</ol><div className="credibility"><p className="eyebrow">MODEL SAFEGUARDS</p><div><span>Prediction target</span><b>Reported incidents</b></div><div><span>Arrest/chargesheet features</span><b>Excluded</b></div><div><span>Confidence output</span><b>Range, not certainty</b></div></div></article></div><section className="correlation-section"><p className="eyebrow">SOCIO-ECONOMIC AND CONTEXTUAL ASSOCIATIONS</p>{data.currentCorrelations.map((item) => <article className="correlation-card" key={item.factor}><h3>{item.factor}</h3><p>{item.finding}</p><small>{item.caveat}</small></article>)}</section></section>}

    {view === "Governance" && <section className="workspace"><div className="workspace-heading"><div><p className="eyebrow">GOVERNANCE AND AUDIT</p><h2>Trust must be visible, not assumed</h2><p>Access boundaries, model limitations, and analyst decisions are part of the product.</p></div><span className="guardrail">On-premise ready</span></div><div className="governance-grid"><article className="panel"><p className="eyebrow">MODEL CARD</p><h3>risk-hgb-v1</h3><dl><dt>Purpose</dt><dd>Forecast reported incidents by place and crime category.</dd><dt>Prohibited use</dt><dd>Individual risk scoring, arrest decisions, automated deployment.</dd><dt>Training rule</dt><dd>Chronological splits; reported/citizen sources only.</dd><dt>Promotion rule</dt><dd>Human approval after baseline and calibration review.</dd></dl></article><article className="panel"><p className="eyebrow">ROLE-BASED ACCESS</p><div className="role-row"><b>SHO</b><span>Own station analytics and assigned review queue</span></div><div className="role-row"><b>SP</b><span>District aggregates and station drilldowns</span></div><div className="role-row"><b>SCRB HQ</b><span>State-level aggregates and governance audit</span></div></article><article className="panel"><p className="eyebrow">INTEGRITY LOG</p><div className="hash-item"><span>GENESIS</span><b>→ 7a24f1a8…</b></div><div className="hash-item"><span>Link review opened</span><b>→ cd9e52bf…</b></div><div className="hash-item"><span>Alert viewed</span><b>→ 12f6a8c1…</b></div><small>Demonstration of a verifiable event chain; production requires append-only storage.</small></article></div></section>}
  </main></ErrorBoundary>;
}

export default App;
