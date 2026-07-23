# KSP Drishti - Technical Architecture and Operating Guide

## Architecture at a glance

```text
Synthetic FIR-style CSV or approved extract
                  |
                  v
  execution/generate_synthetic_data.py
  execution/validate_dataset.py
  execution/build_link_candidates.py
                  |
                  v
        data/synthetic/*.csv
                  |
                  v
 FastAPI analytics service on port 8000
  - hotspots, trends, alerts, forecast
  - CaseLink, network, repeat patterns
  - contextual associations and audit snapshot
  - non-sensitive frontend telemetry endpoint
                  |
                  v
 React + TypeScript dashboard on port 5173
  - Command Map
  - CaseLink
  - Risk Forecast
  - Governance
                  |
                  v
 logs/ksp_runtime_*.log and logs/frontend_events.jsonl
```

## Stack used in the current repository

| Layer | Technology | Why it is used |
| --- | --- | --- |
| Synthetic data, validation, linkage, training | Python 3.11+, standard library, pandas, NumPy, scikit-learn, joblib | Deterministic data processing and compact tabular modelling |
| API | FastAPI, Pydantic, Uvicorn | Typed, documented endpoints with a small deployment footprint |
| Analytics | pandas and NumPy | Grouped time series, trend comparisons, hotspot calculations, source-mix checks |
| Optional risk model | `HistGradientBoostingRegressor` | CPU-friendly non-linear tabular model; no GPU is required |
| Frontend | React, TypeScript, Vite | Fast, typed, interactive dashboard development |
| Visualisation | Native SVG and CSS | No map API key or external tile dependency for the demo |
| Packaging | Docker Compose, Dockerfiles, pnpm lockfile | Reproducible local or containerised setup |
| Operations | `run_ksp.py`, Python logging, JSONL event log | One launcher, terminal visibility, and traceable demo actions |

The repository intentionally does not depend on a GPU, cloud database, proprietary LLM, or external map API. That makes the prototype dependable for a live hackathon demo.

## Repository structure

```text
E:\Competition\Datathon
├── run_ksp.py                     # Single interactive launcher
├── README.md                      # Quick-start guide
├── docker-compose.yml             # Optional container setup
├── docs/
│   ├── 1_Project_Overview.md
│   ├── 2_Technical_Architecture.md
│   └── 3_Layer_Wise_Implementation.md
├── directives/                    # Build and training SOPs
├── execution/                     # Deterministic Python workflows
│   ├── generate_synthetic_data.py
│   ├── validate_dataset.py
│   ├── build_link_candidates.py
│   ├── train_risk_model.py
│   └── run_demo_pipeline.py
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py                # FastAPI routes and telemetry contract
│       └── services/analytics.py  # Read-only analytics and event persistence
├── frontend/
│   ├── package.json
│   ├── src/App.tsx                # Dashboard views and interactions
│   ├── src/api.ts                 # API and frontend-event client
│   ├── src/mockData.ts            # Offline fallback for UI resilience
│   ├── src/types.ts
│   └── src/styles.css
├── data/
│   ├── synthetic/                 # Generated, git-ignored demo CSV files
│   └── models/                    # Generated model and metrics, git-ignored
├── notebooks/ksp_drishti_colab.ipynb
├── logs/                          # Generated runtime and UI-action logs
└── tests/test_data_pipeline.py
```

## Data contract

The generated `cases.csv` is schema-faithful to the supplied FIR ER diagram but uses only the fields needed by the prototype. Important columns include:

| Column | Use |
| --- | --- |
| `case_id`, `crime_no` | Synthetic case identity and traceability |
| `registered_date`, `incident_date` | Time-series and temporal training features |
| `district`, `station` | Drilldown, station-area aggregation, future RBAC scope |
| `crime_head`, `gravity`, `case_status` | Category filters and case context |
| `latitude`, `longitude` | Visual grid/hotspot positioning |
| `brief_facts` | Synthetic modus-operandi cue for CaseLink |
| `reported_source` | Separates victim/citizen sources from police-observed events |
| `accused_name`, `age_years` | Candidate-link inputs only; never used as a person risk score |
| `festival_day`, `rainfall_index` | Contextual feature and association demonstration |

Fields such as caste, religion, employee health, court outcome, and chargesheet outcome are excluded from the model contract.

## API contract

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Service health and dataset classification |
| `GET /api/v1/overview` | KPI cards and synthetic-data notice |
| `GET /api/v1/hotspots` | Recent-versus-prior area/category hotspots |
| `GET /api/v1/trends` | Weekly observed and expected counts with anomaly flags |
| `GET /api/v1/alerts` | Credibility-scored advisory intelligence cards |
| `GET /api/v1/risk-forecast` | Next-week place/category ranges and drivers |
| `GET /api/v1/network` | Candidate CaseLink graph nodes and edges |
| `GET /api/v1/case-links` | Analyst-review candidate list |
| `GET /api/v1/repeat-patterns` | Reviewed entity case-history summaries |
| `GET /api/v1/correlations` | Caveated contextual associations |
| `GET /api/v1/audit` | Demonstration integrity-chain snapshot |
| `POST /api/v1/alerts/{id}/feedback` | Alert review feedback; does not auto-retrain |
| `POST /api/v1/telemetry` | Non-sensitive UI action log for the launcher terminal |

All frontend communication has an offline mock-data fallback so the dashboard remains visually present if the API is temporarily unavailable. A live demo should use the API.

## Algorithms implemented

### Hotspot score

The API groups recent events by district, station, crime head, and rounded map cell. It compares current 28-day incidents with the preceding 28 days, then produces a bounded advisory score. This is an explainable operational score, not a calibrated probability.

### Trend and anomaly detection

The API resamples filtered data weekly. A trailing four-week expected level is compared with observed incident volume. A week is flagged where observed volume exceeds 135% of expected volume. This simple baseline is intentionally transparent for the hackathon demo.

### CaseLink candidate generation

To avoid expensive all-pairs matching, the candidate generator uses an explainable blocking key based on name initials and an age bucket. It then scores candidates using:

- name similarity via `difflib.SequenceMatcher`;
- age proximity;
- same synthetic modus operandi;
- cross-district condition.

The output is always `candidate_review_required`. It is not a confirmed canonical identity.

### Risk-model training

`execution/train_risk_model.py` trains on station service area, crime head, and date. It retains only victim-reported and citizen-reported records, builds lag and rolling features, and splits chronologically at the 80th percentile of dates.

Features: `lag_7`, `lag_14`, `lag_28`, `rolling_28`, weekday, month, festival day, and rainfall index.

The model is accepted only if its held-out MAE improves on a baseline. Generated metrics are written to `data/models/risk_model_metrics.json` and must always be labelled synthetic-data-only.

## How to run

### Recommended single-command method

From PowerShell:

```powershell
cd E:\Competition\Datathon
python run_ksp.py
```

If Windows cannot resolve `python`, use the project virtual-environment interpreter after its first setup:

```powershell
.\.venv\Scripts\python.exe run_ksp.py
```

The launcher prints the project briefing, asks before dependency installation, generates and validates synthetic data, optionally trains the model, starts both services, opens the dashboard, and streams service/UI logs in the terminal. Press `Ctrl+C` to stop both services safely.

Useful launcher options:

```powershell
python run_ksp.py --train
python run_ksp.py --prepare-only
python run_ksp.py --non-interactive --no-browser
```

Optional developer verification:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

### Manual method

1. Create and activate a Python virtual environment.
2. Install `backend/requirements.txt`.
3. Run `python execution/run_demo_pipeline.py`.
4. Optionally run `python execution/train_risk_model.py`.
5. Start FastAPI with `python -m uvicorn app.main:app --app-dir backend --reload`.
6. In another terminal, run `pnpm --dir frontend install` and `pnpm --dir frontend dev`.
7. Open `http://localhost:5173` and API documentation at `http://localhost:8000/docs`.

## Container method

After generating `data/synthetic/cases.csv` and `link_candidates.csv`, run `docker compose up --build`. The backend is exposed on port 8000 and the frontend on port 5173.

## Production migration notes

The prototype is not a production police system. Production work requires approved data access, PostGIS, stronger identity identifiers, formal security review, authoritative RBAC, immutable audit storage, model monitoring, retention controls, and a verified deployment environment. The code is structured so those additions can replace the synthetic input without changing the core product story.
