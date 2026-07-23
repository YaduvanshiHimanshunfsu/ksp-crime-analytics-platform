# Build the KSP Drishti prototype

## Goal

Produce a locally runnable, synthetic-data prototype for Challenge 02 that visibly covers all requested capabilities without presenting synthetic findings as real police intelligence.

## Inputs

- The supplied FIR ER diagram.
- `execution/generate_synthetic_data.py` for deterministic, schema-faithful cases.
- `execution/build_link_candidates.py` for analyst-review entity links.

## Procedure

1. Generate synthetic data with a fixed seed.
2. Validate the data before running analytics.
3. Start the FastAPI service; it must serve the Challenge 02 API endpoints.
4. Start the React dashboard and verify each tab renders with the API unavailable fallback disabled only after backend testing.
5. Mark all screens and reports as synthetic demonstration data.

## Guardrails

- Never score an individual person as a future offender.
- Do not use caste, religion, employee health, arrest outcome, or chargesheet outcome as forecast features.
- Show candidate entity links as unconfirmed until an analyst accepts them.
- Forecast reported incident volume at location/category level only.

