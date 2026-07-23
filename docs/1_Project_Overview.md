# KSP Drishti - Project Overview and Problem Statement

## Submission identity

**Project:** KSP Drishti - Evidence-Aware Crime Intelligence

**Competition:** Karnataka State Police and Zoho Datathon, Challenge 02 - AI-Driven Crime Analytics and Visualization Platform

**Team:** Himanshu Yadav and team

**Prototype status:** Working synthetic-data demonstration. It does not contain, infer, or expose real police intelligence.

## Official problem, in plain language

Current police information systems hold valuable FIR, case, arrest, legal-section, station, and case-status records. Their operational value is limited when data is fragmented across stations and converted manually into reports. Decision-makers need a modern system that turns those records into actionable intelligence.

Challenge 02 specifically asks for interactive dashboards and geospatial maps, hotspot detection, district drilldowns, trend alerts and anomaly detection, criminal network/link analysis, repeat-offender tracking, socio-economic correlation, predictive risk scoring, and AI/ML pattern detection.

The supplied FIR schema makes the opportunity concrete. `CaseMaster` contains dates, latitude/longitude, crime heads, station and status. Related tables contain accused mentions, victims, legal sections, arrest/surrender events, chargesheets, and the police-station hierarchy. The data is useful, but it is not automatically an intelligence product.

## Real operational pain points

1. **Fragmented case visibility:** Similar incidents in different stations appear unrelated when names, spelling, age, and location are recorded inconsistently.
2. **Slow manual reporting:** District and state reviews require staff to collate numbers and explain changes after they have already occurred.
3. **Map without context:** A heatmap alone cannot tell an officer whether activity is new, statistically unusual, data-complete, or driven by reporting/enforcement differences.
4. **Unsafe identity linkage:** The provided schema has accused name, age, and gender but no sufficiently strong universal identifier. Automatically merging people could create a harmful false connection.
5. **Predictive-policing feedback loops:** A model trained indiscriminately on arrest or patrol-discovered events can over-focus attention on previously policed places rather than estimate reported incident patterns.
6. **Trust and accountability:** Officers and senior reviewers need to inspect the evidence behind links and alerts, not accept black-box output.

## Our solution

KSP Drishti is a map-first, evidence-aware decision-support platform. It transforms approved FIR-style extracts into five connected intelligence experiences:

| Challenge capability | KSP Drishti implementation |
| --- | --- |
| Interactive dashboard and geospatial map | Command Map with district/crime filters and H3-style risk cells |
| Hotspot detection | 28-day recent-versus-prior incident scoring by station-area grid |
| District drilldown | District and crime-head controls applied to metrics, trends, hotspots, alerts, and associations |
| Trend alert and anomaly detection | Weekly observed-versus-expected series with anomaly flags |
| Network and link analysis | Cross-district CaseLink graph of explainable candidate links |
| Repeat tracking | Reviewed entity case-history timelines; no individual future-risk score |
| Socio-economic/context correlation | Clearly caveated calendar, rainfall, and source-mix association cards |
| Predictive risk scoring | Advisory next-week place/category ranges with evidence drivers |
| AI/ML pattern detection | Probabilistic candidate linkage, anomaly detection, and an optional chronological count model |

## Signature differentiator: the Data Credibility Lens

Most crime dashboards give a score and a heatmap. KSP Drishti also tells the user whether that score deserves attention.

For each alert, the dashboard presents:

- the place, crime category, trend, and advisory risk indicator;
- the percentage of victim/citizen-reported source events;
- geographic-data completeness;
- a confidence state: `High` or `Review required`;
- model drivers stated as model inputs, never causal claims;
- an explicit statement that the alert requires human review.

This makes the platform scientifically honest. It forecasts **reported incident volume by place and crime category**, not the probability that a person will offend.

## CaseLink: the evidence-first network workflow

The network module never silently creates a canonical person. It produces a candidate link only when multiple pieces of evidence support it:

- name similarity;
- age proximity;
- cross-district occurrence;
- similar modus-operandi text;
- a computed confidence score.

The analyst can confirm, reject, or defer the link. Until confirmed, every graph edge is visually and technically a candidate. The demonstration dataset includes a deliberate false-link review scenario so this safeguard is visible in the demo.

## Demonstration story

The best jury walkthrough is short and evidence-led:

1. Open the Command Map and show an elevated station-area cell with its 28-day trend.
2. Open the Intelligence Card and explain the reported-source share, data completeness, confidence, and advisory nature of the alert.
3. Switch to CaseLink and show seemingly separate cross-district cases connected as a candidate network.
4. Explain that analysts, not the model, confirm identity links.
5. Open Risk Forecast to show a next-week range and its inputs.
6. Open Governance to show prohibited uses, RBAC intent, audit-chain example, and human-review controls.

## Scope boundaries

KSP Drishti deliberately does **not** do the following:

- predict an individual's future criminality;
- automatically merge accused records;
- use caste, religion, employee health, arrests, surrender, or chargesheet results as risk-model features;
- issue automated patrol orders or arrest recommendations;
- claim that calendar/rainfall associations are causal;
- treat synthetic output as a real KSP finding.

## Success criteria

The prototype is successful when a reviewer can trace one output end-to-end:

`synthetic FIR-style record -> validated data -> hotspot/trend or candidate link -> explanation -> analyst review -> audit/terminal log`

The value proposition is not merely that a dashboard exists. It is that fragmented records become faster to inspect while the system remains explainable, auditable, and appropriately restrained.
