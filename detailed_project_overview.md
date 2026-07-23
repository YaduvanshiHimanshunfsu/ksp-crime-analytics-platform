# KSP Crime Analytics Platform — Detailed Project Overview & Master Architecture

This document expands on the initial project overview to provide comprehensive technical specifications, data models, algorithm details, API contracts, and an alignment with the Agent 3-Layer Architecture.

---

## 1. Architecture Overview & Tech Stack

**Data & Storage Layer:**
- **Database:** PostgreSQL 15+ with PostGIS extension for spatial querying.
- **ORM:** SQLAlchemy for relational mapping, GeoAlchemy2 for spatial types.
- **Cache (Optional):** Redis for caching frequent map tiles or heavy analytical queries.

**Backend & API Layer:**
- **Framework:** FastAPI (Python 3.11+) for high-performance async endpoints.
- **Security:** JWT (JSON Web Tokens) with Role-Based Access Control (RBAC). Hash-chained audit logging for all mutations and sensitive reads.
- **ML/Analytics:** pandas, GeoPandas, scikit-learn, XGBoost, SHAP, networkx, Splink.

**Frontend & Presentation Layer:**
- **Framework:** React 18+ with TypeScript, Vite build system.
- **State Management:** React Query for API data caching and synchronization.
- **Visualization:** Leaflet/Kepler.gl (Maps), Recharts (Trends), Cytoscape.js (Networks).

---

## 2. Agent Instruction Alignment (3-Layer Architecture)

As per the `agent_instruction.md`, this project will be built using the 3-Layer Architecture to ensure deterministic execution:

1. **`directives/` (Layer 1):** We will create specific Markdown SOPs for each module (e.g., `directives/etl_pipeline.md`, `directives/train_risk_model.md`, `directives/setup_fastapi.md`).
2. **Orchestration (Layer 2):** The AI Agent will read these directives to manage the build process intelligently.
3. **`execution/` (Layer 3):** Python scripts will be created for discrete tasks (e.g., `execution/run_splink_resolution.py`, `execution/train_xgboost.py`, `execution/generate_synthetic_fir.py`).

---

## 3. Detailed Data Models (PostgreSQL/PostGIS)

### 3.1 Raw Incident Store (`incidents`)
- `incident_id` (UUID, Primary Key)
- `crime_head` (String, Standardized e.g., 'Burglary', 'Assault')
- `reported_date` (Timestamp)
- `location` (Geometry/Point, PostGIS)
- `district_id`, `station_id` (Foreign Keys)
- `status` (String)

### 3.2 Canonical Person Store (`persons`)
- `person_id` (UUID, Primary Key)
- `canonical_name` (String)
- `age_range` (String)
- `father_name` (String)
- `risk_score` (Float)
- `is_repeat_offender` (Boolean)

### 3.3 Entity Resolution Audit (`resolution_audit`)
- `merge_id` (UUID)
- `canonical_person_id` (UUID)
- `raw_record_id` (UUID)
- `match_score` (Float)
- `analyst_override` (Boolean)

### 3.4 Audit Log (`system_audit_log`)
- `log_id` (UUID, Primary Key)
- `user_id`, `role` (String)
- `endpoint_accessed` (String)
- `query_params` (JSONB)
- `timestamp` (Timestamp)
- `previous_hash` (String) - For tamper-evident hash chaining.

---

## 4. ETL and Entity Resolution Pipeline (Detailed)

**1. Data Ingestion & Standardization:**
- Standardize varying date formats across KSP and NCRB datasets.
- Map local crime definitions to standardized `crime_heads`.

**2. Probabilistic Record Linkage (Splink):**
- **Blocking Rules:** Block on `district_id` or first 3 letters of `name` to reduce Cartesian products.
- **Comparisons:** 
  - Jaro-Winkler similarity on `name` and `father_name`.
  - Levenshtein distance on `locality`.
  - Numeric distance on `age`.
- **Thresholding:** Matches with probability > 0.85 auto-merge; 0.70-0.85 flagged for human review.

---

## 5. Analytics Engine (Detailed Methods)

| Module | Technical Implementation | Explainability / Output |
|---|---|---|
| **Hotspots** | `sklearn.cluster.DBSCAN` (eps=500m, min_samples=5). `scipy.stats.gaussian_kde` for density surfaces. | Hex-bin or heatmaps rendered on frontend. |
| **Trends & Anomalies** | `statsmodels.tsa.seasonal.STL`. Z-score > 2.5 on the residual component triggers an anomaly flag. | Clean trendline with red dots for anomalies. |
| **Recidivism** | Simple weighted scoring based on frequency and recency of past offenses. | Ranked list with sparklines of past activity. |
| **Network Analysis** | `networkx.algorithms.community.louvain_communities` on a graph where edges = co-accused in same FIR. | Force-directed Cytoscape graph. |
| **Correlations** | `statsmodels.api.OLS` (Ordinary Least Squares) regressing crime counts against categorical calendar events. | Plain text insights (e.g., "+15% during Payday"). |
| **Predictive Risk** | `xgboost.XGBRegressor`. Features: rolling 7/14/30 day counts, seasonality, socio-economics. | `shap.TreeExplainer` providing top 3 driving factors per region. |

---

## 6. Backend API & Governance (Detailed Contracts)

**Authentication:**
- `POST /api/auth/login`: Issues JWT with role claims (e.g., `role: 'SHO'`, `district_id: 'D01'`).

**RBAC Dependency (FastAPI):**
```python
# Example pseudo-code for jurisdiction filtering
def get_jurisdiction_filter(user: User = Depends(get_current_user)):
    if user.role == "SHO":
        return {"district_id": user.district_id}
    elif user.role == "HQ":
        return {} # Access all
```

**Key Endpoints:**
- `GET /api/v1/analytics/hotspots?crime_head=X&time_window=Y`
- `GET /api/v1/analytics/risk-forecasts`
- `POST /api/v1/feedback/alerts/{alert_id}` (Officer rates alert as useful/not useful)
- `GET /api/v1/audit/bias-report` (Admin only)

---

## 7. Self-Learning & Drift Control (MLOps)

To prevent the "runaway feedback loop" in predictive policing:

1. **Feedback Integration:** When officers rate alerts (`useful`=1, `not useful`=0), this is appended to the training set as sample weights, prioritizing verified signals over raw arrest counts.
2. **Drift Detection:** Calculate Population Stability Index (PSI) on incoming feature distributions. If PSI > 0.2, trigger a warning for model drift.
3. **Champion/Challenger Gate:** 
   - New model trains weekly.
   - Evaluated on precision/recall for the last 14 days.
   - **Bias Check:** Must ensure false positive rates across different demographic proxies (e.g., socio-economic zones) do not exceed a 1.25 disparate impact ratio.
   - If conditions met -> Automate promotion, log to hash-chain.

---

## 8. Frontend Implementation Details

**Component Architecture:**
- `<AppRouter>`
  - `<StateMapDashboard>`: Leaflet map + GeoJSON choropleth.
  - `<DistrictDrilldown id={districtId}>`: Recharts time-series + local hotspots.
  - `<RiskForecastPanel>`: Renders the XGBoost scores alongside `<ShapExplanationCard>`.
  - `<OffenderNetworkGraph>`: Cytoscape instance with Louvain communities color-coded.
  - `<GovernanceAuditView>`: Table view of the hash-chained logs and bias metrics.

**State Management:**
- `react-query` used for all API fetches with a 5-minute stale time.
- Zustand or React Context for global UI state (e.g., global date range filter, selected crime head).

---

## 9. Next Steps / Execution Plan

To execute this architecture deterministically (following `agent_instruction.md`), we should initialize the following:

1. **Create Directives:** Write specific SOPs into the `directives/` folder (e.g., `setup_postgres_postgis.md`, `build_splink_pipeline.md`).
2. **Scaffold `execution/`:** Create the base Python scripts and `docker-compose.yml`.
3. **Generate Synthetic Data:** Execute a script to build a highly realistic, calibrated synthetic dataset to power the UI before real data is connected.
