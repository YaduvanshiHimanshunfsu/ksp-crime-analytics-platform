# Layer-Wise Implementation & Datasets

### 1. The Agentic 3-Layer Architecture
This platform is built and managed using a highly reliable 3-Layer architecture designed for AI agent collaboration, mitigating error compounding through determinism:

1. **Layer 1: Directives (Intent)**: Markdown SOPs living in `directives/` that dictate business rules and intended workflows (e.g., `directives/etl_pipeline.md`).
2. **Layer 2: Orchestration (Decision Making)**: Intelligent routing by the AI agent mapping human intent to execution tools, checking for errors, and self-annealing broken scripts.
3. **Layer 3: Execution (Deterministic Code)**: Python scripts in `execution/` that reliably perform data transformations, API calls, and DB transactions. 

### 2. Application Layers
#### A. Data Ingestion & ETL Layer
- **Libraries**: `pandas`, `geopandas`, `splink`.
- **Function**: Standardizes schema across sources, geocodes locations, and resolves scattered identity records into a Canonical Person Store. Features a human-in-the-loop audit trail for merged records, ensuring accountability.

#### B. Analytics Engine Layer
- **Libraries**: `scikit-learn`, `xgboost`, `shap`, `networkx`, `statsmodels`.
- **Modules**:
  - **Trends & Anomalies**: STL Decomposition over time-series data.
  - **Offender Networks**: Louvain community detection on co-accused graphs.
  - **Socio-Economic Correlation**: OLS Regressions linking crime to census/payday data.
  - **Predictive Risk**: XGBoost with SHAP explaining the forecast.

#### C. API & Governance Layer
- **Libraries**: `FastAPI`, `SQLAlchemy`, `PyJWT`.
- **Function**: Exposes analytics endpoints. Injects Role-Based Access Control (RBAC) to row-filter data (e.g., an SHO only sees their district while HQ sees the state). Implements the tamper-evident, hash-chained audit log.

#### D. Presentation Layer
- **Libraries**: `React`, `Vite`, `React Query`, `Leaflet` / `Kepler.gl`, `Recharts`, `Cytoscape.js`.
- **Function**: A map-first dashboard designed for a live projector demo. Screens include State Map, District Drilldown, Risk Forecast, Offender Networks, and automated PDF Brief Generators.

### 3. Datasets & Data Acquisition
Since raw policing data is highly confidential, this project relies on a rigorously calibrated synthetic data generation pipeline for the Datathon.

**Data Sources & Generators:**
1. **KSP Monthly Reviews & NCRB Tables**: Used as the statistical baseline to calibrate our generative distributions.
2. **Synthetic FIR/Arrest Generator**: A Python script (`execution/synthetic_fir.py`) that generates millions of rows of realistic tabular data (Dates, Crime Heads, Modus Operandi, Lat/Lng bounds per district) reflecting the real world.
3. **Census & Calendar Data**: Real socio-economic indicators, public holidays, paydays, and festival calendars are joined against the synthetic incidents to provide the ML models with real-world correlating features.

**Data Bias Mitigation & Self-Learning:**
To stop the AI from generating a "runaway feedback loop", the platform:
- Explicitly weights the training of the predictive model toward **citizen-reported** and **victim-reported** incidents rather than patrol-discovered incidents.
- Uses a continuous **disparate-impact monitoring** endpoint that ensures model updates (Challenger vs Champion) are blocked if they exacerbate bias across mapped jurisdictions.
