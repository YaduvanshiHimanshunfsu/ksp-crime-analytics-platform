# KSP Dṛṣṭi: AI-Assisted Law Enforcement Intelligence

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![React 18](https://img.shields.io/badge/react-18-blue.svg)

KSP Dṛṣṭi is an advanced analytics and intelligence dashboard built for the Karnataka State Police. It demonstrates a responsible, transparent approach to predictive policing and case link analysis, prioritizing human-in-the-loop oversight and Explainable AI (XAI).

## Features

*   **Command Map:** Visualizes crime hotspots and trend anomalies. Features an overlay of real, official Karnataka 2025 data (from OpenCity.in) alongside granular synthetic incident data for demonstration.
*   **Risk Forecasts with SHAP:** Predicts incident volumes as ranges (not certainties) and explains every prediction using SHAP (SHapley Additive exPlanations) waterfall charts.
*   **CaseLink Network Analysis:** Uses `d3-force` and `networkx` to identify and visualize potential cross-district crime links (based on MO, age, and name similarity) for analyst review.
*   **Governance & Transparency:** Generates Model Cards, Calibration Reports, and downloadable PDF Governance Briefs to ensure trust is visible, not assumed.

## Getting Started

### Prerequisites

*   Python 3.10+
*   Node.js 18+

### 1. Data Pipeline & Backend Setup

Navigate to the project root:

```bash
# Install backend dependencies
python -m pip install -r requirements.txt

# Run the data pipeline (Generates 3.5 years of synthetic data and processes real public data)
python run_ksp.py --pipeline-only

# Start the FastAPI server
python run_ksp.py
```
*The backend will be available at `http://127.0.0.1:8000`.*

### 2. Frontend Setup

In a new terminal, navigate to the `frontend` directory:

```bash
cd frontend

# Install frontend dependencies
npm install

# Start the Vite development server
npm run dev
```
*The frontend dashboard will be available at `http://localhost:5173`.*

## Project Structure

*   `backend/app/`: The FastAPI application, organized by domain (`routers/`, `services/`, `models/`).
*   `frontend/src/`: The React application.
    *   `components/`: Modular UI grouped by domain (`command-map`, `forecast`, `caselink`, `governance`, `public-data`).
    *   `hooks/`: Data fetching and state management (`useDashboardData.ts`).
*   `execution/`: Data pipeline scripts for generating synthetic data (`generate_synthetic_data.py`) and processing real datasets (`process_public_data.py`).
*   `Dataset/`: Raw and processed data, including the real OpenCity.in SLL dataset.

## Ethical Design Principles

1.  **Advisory Only:** Forecasts and link candidates never execute automated actions. They strictly queue for human review.
2.  **No Person-Level Targeting:** Risk scores apply to geographic locations and incident categories, not individuals.
3.  **Explainability:** Black-box models are unacceptable in law enforcement; SHAP values are required for all forecasts.

## License

This project is licensed under the MIT License.
