# KSP Drishti - Layer-Wise Solution, Dataset, and Library Guide

## Why this project uses layers

The supplied workspace follows a three-layer operating model. KSP Drishti uses that model to keep policy, orchestration, and deterministic data work separate.

```text
Layer 1: Directives       What the system is permitted to do
Layer 2: Orchestration    When and in what order tasks are run
Layer 3: Execution        Deterministic code that generates, validates, links, trains, and serves
```

This separation matters for policing analytics. A model or dashboard must not silently invent a data policy; the policy must be visible before the code runs.

## Layer 1 - Directives and governance rules

Files:

- `directives/build_demo.md`
- `directives/train_risk_model.md`

Rules encoded in these SOPs:

- all demonstration output is explicitly synthetic;
- only reported/citizen-source incidents are training targets;
- caste, religion, employee health, arrests, surrender, and chargesheets are excluded from risk features;
- candidate entity links require analyst review;
- the forecast is place/category decision support, not a person-level prediction;
- chronological validation is mandatory; random train/test splits are prohibited.

## Layer 2 - Orchestration

The orchestration path is implemented in `run_ksp.py` and `execution/run_demo_pipeline.py`.

### `run_ksp.py`

This is the single entry point for a demo operator. It:

1. prints the project identity, objective, capabilities, and guardrails;
2. asks approval before installing dependencies;
3. creates a local `.venv` inside the project when needed;
4. prepares synthetic data and optionally trains the model;
5. starts FastAPI, waits for health, starts the React dashboard, and opens it;
6. streams backend/frontend service output into the terminal;
7. saves runtime output under `logs/ksp_runtime_<timestamp>.log`;
8. stops child processes safely on `Ctrl+C`.

The frontend also posts non-sensitive telemetry events for filter changes, view changes, hotspot selection, and alert-feedback actions. The API writes them to `logs/frontend_events.jsonl`; the backend service output makes them visible in the launcher terminal.

### `execution/run_demo_pipeline.py`

This deterministic preparation runner executes the data layer in the correct order:

1. generate synthetic FIR-style records;
2. validate required columns, dates, coordinates, source types, and age range;
3. generate candidate CaseLink pairs.

## Layer 3 - Deterministic execution

| Script | Purpose | Output |
| --- | --- | --- |
| `generate_synthetic_data.py` | Generates reproducible synthetic FIR-style cases using a fixed seed | `data/synthetic/cases.csv` |
| `validate_dataset.py` | Rejects missing columns, invalid dates/coordinates, unknown sources, invalid ages | Terminal validation result |
| `build_link_candidates.py` | Generates explainable cross-district candidate links | `data/synthetic/link_candidates.csv` |
| `train_risk_model.py` | Builds chronological station-area/category risk-model features and trains the compact model | `data/models/risk_model.joblib`, metrics JSON |
| `run_demo_pipeline.py` | Runs generation, validation, and linkage in sequence | All synthetic data artefacts |

## Application-layer design

### 1. Data layer

The supplied police ER diagram is the schema reference. The demonstration focuses on the following conceptual relationships:

```text
CaseMaster
  -> incident dates, registered date, location, station, crime head, status
  -> Accused mention
  -> Victim / complainant context
  -> Act and section association
  -> Arrest / charge-sheet case progression
  -> Unit -> District -> State hierarchy
```

The synthetic generator creates five Karnataka district anchors, three stations per district, five crime heads, multiple source types, case statuses, geographic coordinates, contextual variables, and deliberately repeated aliases. It seeds a credible demo narrative without impersonating real individuals.

### 2. Entity and link-analysis layer

The prototype uses standard-library fuzzy matching because it is easy to inspect in a hackathon demo. For a production-scale source, replace or supplement it with Splink and approved strong identifiers.

Current candidate score:

```text
0.72 * name similarity
+ 0.18 when age difference is at most two years
+ 0.10 when modus operandi matches
```

Only scores at or above 0.72 enter the review queue. The output status remains `candidate_review_required` even at a high score. This is a deliberate safety property.

### 3. Analytics layer

| Module | Current method | Human-readable output |
| --- | --- | --- |
| Hotspots | Current-versus-prior 28-day count score in station-area cells | Map cell, recent count, change, advisory score |
| Trends | Weekly resampling and four-week rolling expected level | Observed/expected line and anomaly marker |
| Alerts | Hotspot ranking plus source-completeness/credibility rules | Intelligence card with confidence and reason |
| CaseLink network | Candidate links rendered as a graph | Nodes, edges, evidence fields, review status |
| Repeat patterns | Count and timeline of reviewed synthetic entity keys | Cross-district case-history summary |
| Context | Descriptive festival, rainfall, and source-mix comparisons | Association cards with non-causal caveats |
| Forecast | Range based on place/category activity, optional trained model artefact | Next-week reported-incident range and model drivers |

### 4. API and logging layer

FastAPI exposes read-only analytics endpoints and two intentional writes:

- alert feedback, which is stored as review-quality input and never automatically retrains the model;
- frontend telemetry, which contains UI-state fields only and is persisted as JSONL for the demo terminal log.

Production replacement requirements:

- JWT/OIDC identity verification;
- server-side district/station data filtering;
- encrypted, append-only audit storage;
- protected PII and evidence access;
- retention policy and security review.

### 5. Presentation layer

The React dashboard is structured as four focused views:

1. **Command Map:** KPIs, filters, H3-style visual cells, trend chart, and Data Credibility Lens.
2. **CaseLink:** Cross-district candidate graph, review queue, and case-history tracking.
3. **Risk Forecast:** Advisory ranges, input drivers, and contextual association cards.
4. **Governance:** Model card, role intent, and integrity-log demonstration.

## Libraries and what each contributes

| Library or tool | Purpose |
| --- | --- |
| `pandas` | CSV ingestion, grouping, date handling, feature engineering |
| `numpy` | Numeric operations in analytics and modelling |
| `scikit-learn` | CPU-friendly histogram gradient boosting regressor and metrics |
| `joblib` | Model serialisation |
| `FastAPI` | Typed API service and auto-generated docs |
| `Pydantic` | Validates feedback and telemetry payloads |
| `Uvicorn` | Local ASGI server |
| `React` | Interactive dashboard state and views |
| `TypeScript` | Frontend type safety |
| `Vite` | Fast local development and production build |
| `Docker Compose` | Optional reproducible multi-service deployment |

## Dataset strategy and acquisition path

### Prototype data

The application runs on `data/synthetic/cases.csv`, generated locally and ignored by Git. It is suitable for submission screenshots, feature testing, and demo rehearsal.

### Public contextual calibration

For a refined demo, use official KSP monthly review aggregates, NCRB aggregates, a documented holiday calendar, and publicly available weather/rainfall data to calibrate distributions. Clearly cite the source and distinguish public aggregates from confidential case-level data.

### Authorised real-data migration

Only after formal KSP approval:

1. create a read-only extract/adapter for authorised fields;
2. map the FIR schema to the documented data contract;
3. run validation and data-quality reporting before analytics;
4. restrict raw records and names to authorised roles;
5. require at least 12 months of sufficiently complete geotagged history; 24 months is preferred;
6. train with chronological splits and compare against a baseline;
7. document performance, uncertainty, limitations, and approval status in a model card.

## Google Colab training guidance

The included `notebooks/ksp_drishti_colab.ipynb` can train the model in minutes using CPU. A T4 GPU is not useful for this compact tabular model. Use a GPU only for a separately validated multilingual NLP module, and never upload confidential FIR/PII data to public Colab without written authorisation.

The training acceptance rule is simple: retain the model only if held-out chronological MAE improves on the baseline. The resulting metrics must remain labelled as synthetic-data-only unless the real-data governance process is complete.

## What makes the solution responsible

KSP Drishti does not claim to predict crime in an absolute sense. It makes limited, inspectable statements about patterns in **reported records**. It separates model output from human operational decisions, highlights uncertainty and data quality, and treats identity linkage as an analyst-reviewed evidence task. Those choices are not cosmetic; they are the core of the product’s credibility.
