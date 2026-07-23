# Technical Architecture & Setup

### 1. Technology Stack
- **Database:** PostgreSQL 15+ with PostGIS (for spatial querying and indexing).
- **Backend Framework:** FastAPI (Python 3.11+) with JWT Auth & RBAC.
- **Frontend Framework:** React 18+ (TypeScript) with Vite, React Query.
- **Data & ML Libraries:** pandas, GeoPandas, scikit-learn, XGBoost, SHAP, Splink (probabilistic linkage), networkx, statsmodels.
- **Visualizations:** Leaflet/Kepler.gl (Maps), Recharts (Time-series), Cytoscape.js (Networks).

### 2. Folder Architecture
```text
crime-analytics-platform/
├── docker-compose.yml                     # postgres+postgis, backend, frontend, scheduler
├── README.md                              # setup, demo script, screenshots
├── docs/                                  # Project documentation
├── etl/
│   ├── generators/synthetic_fir.py        # Calibrated synthetic FIR generator
│   ├── loaders/                           # KSP, NCRB, and Census data parsers
│   ├── entity_resolution.py               # Splink probabilistic deduplication
│   └── pipeline.py                        # ETL orchestration to PostGIS
├── analytics/
│   ├── hotspots.py                        # DBSCAN + KDE surfaces
│   ├── trends.py                          # STL + anomaly flags
│   ├── recidivism.py                      # Repeat-offender scoring
│   ├── network.py                         # Link analysis, Louvain communities
│   ├── correlation.py                     # Socio-economic regressions
│   └── risk_model/
│       ├── train.py                       # XGBoost + time-based CV
│       ├── explain.py                     # SHAP explanations
│       └── bias_audit.py                  # Disparate-impact checks
├── backend/app/
│   ├── main.py                            # FastAPI entry
│   ├── api/                               # Routers for auth, analytics, alerts, audit
│   ├── core/security.py                   # JWT & RBAC
│   └── models/                            # SQLAlchemy models
├── frontend/src/
│   ├── pages/                             # Map, Drilldown, Network, Trends, Audit
│   └── components/                        # UI Components
└── eval/                                  # Model accuracy and bias reports
```

### 3. Core Technical Concepts & Methods
- **Entity Resolution:** Instead of basic string matching, we use **Splink** (Jaro-Winkler for names, Levenshtein for locality). This assigns a match probability. Scores >85% auto-merge, 70-85% require human review.
- **Predictive Risk Modeling:** Uses an **XGBoost Regressor** trained on rolling time-windows. Crucially, **SHAP (SHapley Additive exPlanations)** extracts human-readable reasons (e.g., "Proximity to Payday", "Recent Anomalous Spike") for every prediction.
- **Hotspot Clustering:** Uses **DBSCAN** for unsupervised clustering of incident coordinates, smoothed by **Gaussian KDE** to render actionable density surfaces on the frontend map.
- **Tamper-Evident Logs:** Every API request writes an audit log. Each log's hash incorporates the hash of the *previous* log entry, creating a blockchain-like chain.

### 4. How to Use & Run Locally
1. **Prerequisites:** Docker, Docker Compose, Node.js, Python 3.11+.
2. **Setup Environment Variables:** Copy `.env.example` to `.env` and fill in DB credentials and JWT secrets.
3. **Boot Infrastructure:** Run `docker-compose up -d db` to start PostGIS.
4. **Generate Synthetic Data:** Run `python etl/generators/synthetic_fir.py` to seed the database.
5. **Run ETL & Resolution:** Execute `python etl/pipeline.py`.
6. **Start Services:** 
   - Backend: `cd backend && uvicorn app.main:app --reload`
   - Frontend: `cd frontend && npm run dev`
7. **Access UI:** Open `http://localhost:5173` in your browser.
