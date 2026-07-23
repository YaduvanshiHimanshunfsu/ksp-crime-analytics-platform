# KSP Sentinel: Crime Analytics Platform
## Project Overview & Problem Statement

**Developed for the Datathon organized by the Karnataka State Police (KSP) and Zoho.**

### 1. Introduction
KSP Sentinel is an end-to-end geospatial crime analytics and intelligence platform. Designed with trust and governance as first principles, the system ingests raw incident data and applies probabilistic entity resolution to build canonical offender networks.

### 2. Problem Statement
Law enforcement agencies generate massive amounts of data daily—FIRs, arrest records, court dispositions, and citizen reports. However, this data is often siloed, unstructured, and plagued by data-entry errors (e.g., misspelled names, inconsistent dates). 
Furthermore, traditional "predictive policing" models often create a runaway feedback loop: police patrol areas predicted to be high-risk, discover more crimes there (often minor offenses), which feeds back into the model to predict even higher risk in the same area, inadvertently baking systemic bias into the AI.

**The Challenge:**
1. Resolve duplicate and messy records into canonical person profiles without relying on brittle exact-string matching.
2. Deliver actionable, proactive intelligence (hotspots, predictive risks, offender networks) to station house officers (SHOs).
3. Break the runaway feedback loop and ensure AI outputs are explainable, audited, and strictly human-in-the-loop.

### 3. Elaboration & Project Goals
To solve these challenges, the platform aims to deliver the following core capabilities:
- **Geospatial Hotspot Mapping:** Live state-wide choropleths and heatmaps.
- **Probabilistic Entity Resolution:** Merging scattered records into unified offender profiles.
- **Explainable Predictive Risk:** Forecasting crime risk by district/week, with explicit plain-language explanations (via SHAP) for *why* the score was generated.
- **Cross-District Link Analysis:** Uncovering hidden syndicates using network graphs.
- **Governance & Auditing:** Tamper-evident hash-chained logs for every API request, and disparate-impact monitoring to prevent algorithmic bias.
- **Automated Reporting:** One-click PDF monthly briefs to save thousands of clerical hours.
