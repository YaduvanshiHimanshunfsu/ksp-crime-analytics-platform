# KSP Dṛṣṭi: Competition Submission

**KSP Dṛṣṭi** is a demonstration of how AI and analytics *should* be deployed in law enforcement: transparently, ethically, and with strict guardrails. It uses a hybrid data architecture designed specifically for the constraints of public hackathons and ethical data handling.

## The Data Approach

Instead of relying on a single, flawed open-source dataset, KSP Dṛṣṭi fuses two distinct sources:

1.  **Synthetic Incident Data:** A 3.5-year synthetic dataset generated to faithfully mimic the *schema and statistical distributions* of real crime data (using the OpenCity.in schema). This allows us to safely demonstrate granular tracking, predictive modeling, and link analysis without compromising PII or relying on biased public logs.
2.  **Real Official KSP Aggregate Data (2023-2025):** We overlay real, aggregated SLL cases from the Karnataka OpenCity.in dataset to provide a true, district-level benchmark. 

This hybrid approach ensures the application demonstrates full capabilities while remaining grounded in verifiable reality.

## Key Technical Features

*   **Explainable AI (XAI) with SHAP:** Risk forecasts are not black boxes. Every forecast is accompanied by a SHAP waterfall chart, visually explaining *exactly* which features (e.g., seasonal patterns vs. recent 28-day lags) drove the score up or down.
*   **Force-Directed Network Graphs (D3):** CaseLink analysis uses `d3-force` to visualize candidate links between cross-district crimes, mapping modus operandi and entity similarities.
*   **Human-in-the-Loop Design:** The system is explicitly advisory. Candidate links do not automatically merge; they queue for analyst review. Forecasts are presented as ranges, not certainties. Alerts feature a "Mark Useful" button to track model performance via human feedback.
*   **Governance & Audit:** Built-in PDF generation (`html2pdf`) for downloading Governance Briefs, model calibration reports, and data provenance logs.

## Architecture

*   **Frontend:** React (Vite), completely modularized. Uses standard CSS variables and zero bloated UI frameworks. Visualizations powered by `d3-force` and custom SVG charts.
*   **Backend:** FastAPI (Python). Modular architecture separating ML inference, network analysis, and public data ingestion.
*   **Data Science:** SHAP for model explainability, networkx for link candidate generation, scikit-learn for synthetic baseline generation.

## Integrity First

We have intentionally stripped out all "buzzwords" that are not actually implemented (e.g., no fake PostGIS claims, no fake JWT auth layers). What you see is exactly what is running: a robust, well-architected prototype focused on ethics and transparency in predictive policing.
