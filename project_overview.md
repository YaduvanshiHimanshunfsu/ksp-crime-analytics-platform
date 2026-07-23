# KSP Crime Analytics Platform — Project Overview

---

## 3.2 ETL and Entity Resolution Pipeline

- **A pandas and GeoPandas ETL pipeline**: clean, normalize schema, standardize dates and crime heads across sources.
- **Entity resolution with Splink** (probabilistic record linkage) or the `recordlinkage` library: fuzzy match on name, age, father's name, and locality, producing match scores rather than brittle exact joins.
- **A canonical person store with an audit trail** of which raw records were merged, so an analyst can always inspect and override a merge (human-in-the-loop).
- **Output loaded into PostgreSQL with PostGIS** so downstream geo and analytical queries are fast.

---

## 3.3 Analytics Engine

Six analytical modules run over the resolved data. Each is deliberately built on classical, explainable methods, with no black-box deep learning, because every output must be defensible to an officer.

| Module | Method | Output |
|---|---|---|
| **Hotspots** | DBSCAN and KDE over geo-tagged incidents, per crime type per time window | Density surfaces and cluster labels on the map |
| **Trends and Anomalies** | STL decomposition and z-score flags per district/crime head | Trend lines with automatic anomaly markers |
| **Repeat Offenders** | Resolved-entity offense histories and recidivism scoring | Ranked offender lists with cross-district timelines |
| **Network and Link Analysis** | Co-accused and co-location graphs, Louvain community detection | Interactive offender-network graph |
| **Socio-economic Correlation** | Regression of crime rates against Census and calendar indicators | Correlation cards such as crime up near festivals and paydays |
| **Predictive Risk** | XGBoost per district by crime-type by week, time-based CV | Per-region risk scores with SHAP explanations |

---

## 3.4 Backend, API, and Governance Layer

A **FastAPI** service exposes analytics endpoints behind **JWT authentication** and **role-based access control (RBAC)**. Governance is not an add-on: every request is authenticated, authorized by role, row-filtered to the caller's jurisdiction, and written to a tamper-evident audit log.

- **FastAPI with JWT auth and RBAC dependency injection**, so an SHO sees only their district while SCRB HQ sees all.
- **Analytics endpoints** (hotspots, trends, network, risk, correlations) plus an alert-feed endpoint and a scheduled-brief generator.
- **Hash-chained audit log** recording user, role, endpoint, parameters, result hash, and timestamp — each entry chained to the previous so tampering is detectable.
- **A bias-audit endpoint** that runs disparate-impact checks on the risk model and surfaces them to admins.

---

## 3.5 Presentation Layer

A **React frontend** delivers a map-first, drillable experience: state map → district → station, with timelines, network graphs, an automated alert feed, and one-click PDF briefs. The design language is clean, government-appropriate, and legible on a projector during a live demo.

---

## 4. Self-Learning and Self-Correcting Backend

In a safety-critical policing context this must be done carefully: an uncontrolled self-updating model is exactly what creates the feedback loop described earlier. The design below gives genuine adaptivity while keeping a human in the loop and the whole process auditable.

### 4.1 Closed-Loop Retraining with Guardrails

- **Scheduled retraining**: the risk model retrains on a rolling window with strict time-based cross-validation, so it adapts to new patterns without leaking future data into the past.
- **Champion and challenger promotion**: a newly trained model is a *challenger* evaluated against the live *champion* on held-out recent data. It is promoted only if it beats the champion **and** passes the bias audit. Promotion is logged and reversible.
- **Drift detection**: monitor input-feature distributions and prediction distributions; when drift crosses a threshold, flag for retraining rather than silently continuing.

### 4.2 Feedback Capture That Avoids the Runaway Loop

The key insight from the predictive-policing literature is that training on *discovered* crime (where patrols happened to go) corrupts the model. The platform breaks this loop deliberately:

- Officers rate each alert or forecast as *useful* or *not*. This human feedback becomes a supervised signal for ranking, separate from raw incident counts.
- The risk model is weighted toward **victim-reported** and **citizen-reported** crime rather than patrol-discovered arrests, reducing the self-reinforcing signal.
- **A counterfactual check**: the bias audit continuously compares the predicted-risk distribution against protected-attribute and jurisdiction distributions and blocks promotion if disparate impact worsens.

> **Design Principle**
>
> Self-learning here means **human-supervised, audited, reversible adaptation**, never an autonomous model that decides where to send officers on its own. State this explicitly to the jury; it is the difference between naïve AI and responsible AI.

---

## 5. Interactive Frontend: Design and Screens

The frontend is the demo. Because the jury will judge much of the platform through what they see on screen, the interface is designed to be immediately legible, visually confident, and fast to drill through. The design system uses a clean government-appropriate palette (deep navy, slate, and a single accent), generous whitespace, a large map canvas, and consistent card components.

### 5.1 Stack

- **React** with TypeScript and a Vite build.
- **Mapping**: Leaflet or Kepler.gl for the geospatial canvas, with H3 hex-bin aggregation for smooth zoomed-out density.
- **Charts**: Recharts or Chart.js for trends and correlation cards.
- **Network graph**: Cytoscape.js for the offender-network view.
- **State and data**: React Query against the FastAPI endpoints, with role-aware routing.

### 5.2 Core Screens

| Screen | Purpose | Signature Element |
|---|---|---|
| **State Map** | Entry point, live state-wide picture | Choropleth plus hotspot layer; click a district to drill |
| **District Drilldown** | Local detail for SP and SHO | Station breakdown, trend sparklines, anomaly flags |
| **Offender Network** | Cross-district link analysis | Interactive graph, communities colour-coded |
| **Risk Forecast** | Where to deploy next week | Ranked regions with a SHAP *why* panel per score |
| **Trends** | Time-series exploration | STL trend and anomaly markers, crime-head filters |
| **Alert Feed** | Proactive notifications | Ranked alerts, one-click useful/not feedback |
| **Monthly Brief** | The ROI closer | One-click auto-generated PDF review |
| **Bias and Audit** | Governance and admin | Disparate-impact dashboard and audit-log viewer |

---

## 6. Wireframes

### 6.1 State Map (Landing Screen)

Reading top to bottom, the screen has a slim **top bar** carrying the KSP identity on the left, a global time-window and crime-head filter in the centre, and the role badge with user menu on the right. Below the top bar the screen divides into three columns:

- **Left rail** (narrow): layer toggles for hotspots, choropleth, and offender density, plus a live top-movers list of districts trending up.
- **Centre** (dominant): the Karnataka map canvas showing a choropleth with a hotspot heat layer; clicking any district drills into the District screen.
- **Right panel** (collapsible): state-wide summary cards for total incidents, week-over-week change, and active alerts.

### 6.2 Risk Forecast (The Trust Screen)

The screen splits left and right:

- **Left two-thirds**: ranked regions for the week ahead, each with a risk score and trend direction, sortable and filterable by crime head.
- **Right one-third**: the SHAP panel listing the top contributing factors in plain language (for example *festival proximity*, *recent payday*, *last-month trend*, *prior recidivism density*) with signed contributions.
- A **persistent banner** reminds the user that scores are advisory and human-reviewed, reinforcing the human-in-the-loop policy.

---

## 7. System Diagrams

### 7.1 End-to-End Data and Control Flow

The pipeline is a single upward flow from raw data to the officer's screen. Each stage below feeds the next:

1. **Sources**: public data (KSP monthly reviews, NCRB tables, Census indicators, festival/payday calendar) plus the synthetic FIR/arrest/disposition generator.
2. **ETL pipeline** (pandas & GeoPandas): clean → normalize → geo-tag.
3. **Entity resolution** (Splink or `recordlinkage`): fuzzy match on name, age, and father's name into canonical persons, with a merge audit and analyst override.
4. **Storage**: PostgreSQL with PostGIS as the single analytical store.
5. **Analytics engine**: hotspots, trends & anomalies, recidivism scoring, network & link analysis, socio-economic correlation, and predictive risk with SHAP.
6. **API**: FastAPI with JWT and RBAC row filters; every request is hash-chained into the audit log.
7. **Frontend**: the React map-first app — State Map → District → Station, plus Network, Risk, Trends, Alert Feed, Monthly Brief, and Bias/Audit.

### 7.2 Self-Learning Control Loop

The adaptivity loop is a closed cycle with a human checkpoint and two safety gates:

1. The live **champion model** produces alerts and risk scores shown to officers.
2. Officers rate each output as *useful* or *not*; this feedback flows into a **feedback store** alongside victim-reported weighting.
3. A **challenger model** retrains on a rolling window using time-based cross-validation, informed by the feedback store.
4. A **drift detector** watches feature and prediction distributions and triggers retraining when drift crosses a threshold.
5. The challenger is promoted to champion **only if** it beats the current champion **and** passes the bias audit; promotion is logged and reversible.

---

## 8. Folder and File Architecture

The repository is organized by layer, mirroring the architecture above. Each top-level directory maps to one responsibility, which keeps the codebase navigable for a team working in parallel.

```
crime-analytics-platform/
│
├── docker-compose.yml                     # postgres+postgis, backend, frontend, scheduler
├── README.md                              # setup, demo script, screenshots
│
├── etl/
│   ├── generators/
│   │   └── synthetic_fir.py               # calibrated synthetic FIR/arrest/disposition generator
│   ├── loaders/
│   │   ├── ksp_monthly.py                 # KSP monthly-review parser
│   │   ├── ncrb.py                        # NCRB crime-head tables
│   │   └── census.py                      # Census + festival/payday/rainfall calendar
│   ├── entity_resolution.py               # Splink / recordlinkage person dedup
│   └── pipeline.py                        # orchestrated ETL into PostgreSQL/PostGIS
│
├── analytics/
│   ├── hotspots.py                        # DBSCAN + KDE surfaces
│   ├── trends.py                          # STL + anomaly flags
│   ├── recidivism.py                      # repeat-offender scoring
│   ├── network.py                         # link analysis, Louvain communities
│   ├── correlation.py                     # socio-economic regressions
│   └── risk_model/
│       ├── train.py                       # XGBoost + time-based CV
│       ├── explain.py                     # SHAP values per prediction
│       ├── promote.py                     # champion/challenger promotion gate
│       ├── drift.py                       # feature/prediction drift detector
│       └── bias_audit.py                  # disparate-impact checks (signature module)
│
├── backend/app/
│   ├── main.py                            # FastAPI entry
│   ├── api/                               # auth, analytics, network, alerts, briefs, audit
│   ├── core/
│   │   ├── security.py                    # JWT, RBAC dependencies
│   │   └── audit.py                       # hash-chained audit log
│   ├── services/                          # brief generator (PDF), alert ranking, feedback store
│   └── models/                            # SQLAlchemy: crimes, persons, cases, users, audit, feedback
│
├── frontend/src/
│   ├── pages/                             # StateMap, DistrictDrilldown, OffenderNetwork,
│   │                                      # RiskForecast, Trends, AlertFeed, MonthlyBrief, BiasAudit
│   ├── components/                        # MapView, GraphView, ShapPanel, TrendChart, AlertCard
│   ├── hooks/                             # useAuth, useRole, data-fetch hooks
│   └── i18n/                              # EN / KN interface strings
│
├── eval/
│   ├── model_report.py                    # risk-model accuracy + calibration report
│   └── bias_report.py                     # disparate-impact report for the slide
│
└── docs/
    ├── methodology.md                     # synthetic-data calibration, model choices
    └── ethics_and_bias.md                 # bias mitigation, human-in-the-loop policy
```

---

## 9. Expected Output

At the end of the build the team ships a running, demonstrable platform plus a small set of documents that convert engineering into evidence. The concrete deliverables are:

- ✅ A **live web application** (Dockerized) with the eight screens in section 5, seeded with the calibrated synthetic dataset.
- ✅ **Cross-district offender resolution** demonstrated end-to-end: three seemingly separate local cases collapsed into one offender network on screen.
- ✅ A **predictive risk map** for the week ahead, with a SHAP *why* panel on every score.
- ✅ An **automated PDF monthly brief** generated with one click, replacing the manual review.
- ✅ An **alert feed** with officer feedback capture wired into the self-learning loop.
- ✅ A **bias-audit dashboard** and an `ethics_and_bias.md` document with an explicit human-in-the-loop policy.
- ✅ A **model report** with an accuracy and calibration number to put on the pitch slide.
- ✅ A `methodology.md` documenting the synthetic-data calibration, a judged deliverable in its own right.

---

## 10. Suggested Improvements and Advancements

The following go beyond the baseline brief. Each is chosen for high jury impact relative to build cost; most are additive modules that do not risk the core.

### 10.1 High-Impact, Low-Cost (Build These)

- **Kannada interface toggle (i18n)**: even without full NLP, a Kannada-labelled UI signals adoption-readiness to a Karnataka jury and is cheap to add.
- **A saved-clerical-hours counter**: quantify and display the estimated hours the automated brief saves per month — a concrete ROI number officers remember.
- **Natural-language query lite**: a small text-to-filter box (for example, *"show chain-snatching in Mysuru in the last three months"*) that maps to dashboard filters, borrowing Challenge 1's wow without its full complexity.
- **Confidence bands on every forecast**: show uncertainty, not just a point estimate. This reads as scientific honesty to a technical judge.

### 10.2 Ambitious (If Time Permits)

- **Offline or on-premise deployment mode**: police data cannot leave government infrastructure, so demonstrating a fully self-hosted mode is a strong credibility point.
- **Patrol-optimization suggestion**: given risk scores and available units, suggest a deployment plan, framed strictly as advisory and human-approved.
- **A what-if simulator**: let command staff simulate the effect of adding patrols to a district on projected risk.
- **Explainable anomaly narratives**: auto-generate a one-sentence plain-language explanation for each flagged anomaly.

### 10.3 Governance Advancements (Your Differentiator)

- Continuous **disparate-impact monitoring** with automatic promotion-blocking, as described in section 4.
- A **full audit-log export and verification tool** that proves the hash chain is intact.
- A **published model card** documenting intended use, limitations, and known failure modes.

---

## 11. Roadmap (5 Weeks)

Effort is sequenced by demo value, not by architectural order. The goal is to always have a demoable product and to finish the trust-building modules that disproportionately win with this jury.

| Week | Milestone | Why It Is Prioritized Here |
|---|---|---|
| **1** | Data, ETL, and entity resolution | Powers the headline cross-district demo; everything sits on this data |
| **2** | Hotspots and district drilldown map | The expected core; get it working, do not over-polish |
| **3** | Network analysis and recidivism scoring | The cross-district story becomes visual and interactive |
| **4** | Risk model, SHAP, and bias audit | The defensibility and trust anchor |
| **5** | Dashboard polish, alerts, PDF briefs, docs | The ROI closer, ethics doc, and demo rehearsal |

---

## 12. Risks and Mitigations

| Risk | Severity | Mitigation |
|---|---|---|
| Just-another-dashboard perception | 🔴 High | Lead with entity resolution, SHAP, and bias — not the map |
| Entity-resolution false merges | 🟡 Medium | Probabilistic scores with analyst override, never silent auto-merge |
| Predictive-policing bias feedback loop | 🔴 High | Victim-reported weighting, feedback signal, promotion-blocking audit |
| Synthetic data looks unrealistic | 🟡 Medium | Calibrate to NCRB and KSP distributions; document in `methodology.md` |
| Demo fails live | 🔴 High | Dockerized, seeded, rehearsed; screenshots as fallback in README |

---

## The One Thing to Rehearse

> **Feasibility is very high**, so you cannot win on the fact that *it works* — because everyone's will. **Rehearse the narrative** as hard as you build the code:
>
> 1. **Entity resolution** as the hook
> 2. **SHAP and bias** as the trust story
> 3. **The auto-generated brief** as the return-on-investment closer
