# Demo Script for Judges

Welcome to the KSP Dṛṣṭi demonstration. This script will walk you through the key features and ethical design decisions of our platform.

## Setup
1. Open a terminal and run the backend: `python run_ksp.py`
2. Open a second terminal, navigate to `frontend/`, and run the frontend: `npm run dev`
3. Open `http://localhost:5173` in your browser.

---

## 1. Command Map & Real Data Anchoring
*   **Action:** Look at the left rail under "STATE SITUATION" and "OFFICIAL KARNATAKA 2025 DATA".
*   **Talking Point:** "To avoid the pitfalls of biased open-source incident logs while still proving the system works, we use a hybrid data architecture. The granular hotspots on the map are 3.5 years of synthetic data. However, the benchmark panel on the left shows *real*, official Special & Local Laws (SLL) case counts for Karnataka districts from OpenCity.in. This anchors the simulation in reality."
*   **Action:** Click a hotspot on the map. Point out the "Intelligence Card" on the right.
*   **Talking Point:** "Notice the 'Data Credibility Lens'. The system explicitly tells the officer that this alert requires human review and highlights the data source breakdown."

## 2. CaseLink Analysis (Human-in-the-Loop)
*   **Action:** Click the "CaseLink" tab in the top control bar.
*   **Talking Point:** "This is our cross-district link analysis, powered by a D3 force-directed graph."
*   **Action:** Hover over or drag the nodes in the graph. Point to the 'Analyst Review Queue' on the right.
*   **Talking Point:** "Crucially, the system *never* merges case files automatically. It generates candidate links based on Modus Operandi and demographic similarities, but enforces a strict 'Human-in-the-Loop' policy. An analyst must confirm, reject, or defer the link."

## 3. Risk Forecasts (Explainable AI)
*   **Action:** Click the "Risk forecast" tab in the top control bar.
*   **Talking Point:** "Predictive policing is often criticized for being a 'black box'. We solve this using SHAP (SHapley Additive exPlanations)."
*   **Action:** Click on different rows in the Forecast Table and watch the SHAP Waterfall chart update on the right.
*   **Talking Point:** "For every risk score, the system visually breaks down *why* the score is what it is. For example, it might show that a recent 28-day lag increased the risk (+0.30), but a seasonal calendar pattern decreased the risk (-0.20). Furthermore, predictions are provided as *ranges* (e.g., 1-4 reports), not absolute certainties, and are strictly location-based, never person-based."

## 4. Governance & Trust
*   **Action:** Click the "Governance" tab.
*   **Talking Point:** "Trust in AI must be verifiable. Here we provide a transparent Model Card detailing the algorithm used, the training splits, and prohibited uses."
*   **Action:** Point out the "Data Provenance" section showing the 3-year district trend graph.
*   **Talking Point:** "This is again pulling from our real OpenCity.in dataset to provide context on statewide trends."
*   **Action:** Click the **"Export PDF Brief"** button in the top right.
*   **Talking Point:** "For audit purposes, administrators can instantly generate a PDF Governance Brief summarizing the current model state and data provenance, ensuring on-premise readiness."

---

*End of Demo.*
