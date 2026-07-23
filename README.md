# KSP Dṛṣṭi - Challenge 02 Prototype

KSP Dṛṣṭi is an evidence-aware crime analytics and visualisation prototype for the Karnataka State Police Datathon Challenge 02. It covers the required capabilities while keeping forecasting place-based, auditable, and human-reviewed.

## Challenge coverage

| Required capability | Implementation |
| --- | --- |
| Interactive dashboards and geospatial maps | React command map with H3-style risk cells |
| Crime hotspot detection | Recent-versus-prior 28-day hotspot scoring |
| District-level drilldowns | District and crime-type filters |
| Trend alerts and anomaly detection | Weekly trend line with expected baseline and anomaly flags |
| Network and link analysis | Cross-district CaseLink candidate graph |
| Repeat-offender tracking | Analyst-confirmed case-history timelines; no person risk score |
| Socio-economic/context correlation | Clearly caveated calendar, rainfall, and source-mix association cards |
| Predictive risk scoring | Weekly place/category ranges trained on reported incidents only |
| AI/ML pattern detection | Candidate entity linkage, anomaly detection, and optional count-model training |

## Safety and honesty rules

- The generated records are synthetic and schema-faithful. They are not real KSP findings.
- The forecast estimates reported incident volume by place and category, not an individual's likelihood of offending.
- Arrest, surrender, chargesheet, caste, religion, and employee data are excluded from forecast features.
- Entity links are candidates until an analyst confirms them.

## Exact project location

All project files are inside `E:\Competition\Datathon`.

## Quick start

Use Python 3.11+ and Node 20+.

Run the synthetic data pipeline, then create a virtual environment, install `backend/requirements.txt`, and start the API with `uvicorn app.main:app --app-dir backend --reload`.

In a second terminal, change to `E:\Competition\Datathon\frontend`, run `npm install`, then `npm run dev`.

Open http://localhost:5173. The API runs on http://localhost:8000.

## Model training: do we need it?

For the working prototype, no GPU training is required. The dashboard and analytics run from deterministic synthetic data.

For a real ML demonstration, train the compact risk model using `execution/train_risk_model.py` or `notebooks/ksp_drishti_colab.ipynb`. It uses CPU-friendly scikit-learn and should finish in minutes, not hours.

Use a T4 only if you later add a validated multilingual document/NLP module. Do not train a deep model simply because a GPU is available.

## Real-data acceptance criteria

1. Obtain explicit data-use approval.
2. Require at least 12 months of geotagged historical cases per usable category; 24 months is better.
3. Validate schema, date completeness, coordinate completeness, and lawful access.
4. Use time-ordered train/validation/test windows, never random splits.
5. Keep the model only if it improves on a seasonal baseline and publish its metrics/model card.

## Project map

- `directives/`: SOPs and guardrails.
- `execution/`: deterministic data generation, validation, linkage, and training.
- `backend/`: FastAPI analytics API.
- `frontend/`: React map-first dashboard.
- `data/`: synthetic records and optional exported model artifacts.
- `notebooks/`: Colab-ready training notebook.
- `tests/`: data-pipeline tests.

# ksp-crime-analytics-platform
