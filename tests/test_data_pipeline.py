import csv
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "execution"))

from build_link_candidates import candidates
from generate_synthetic_data import make_cases
from validate_dataset import validate


def test_synthetic_generator_is_reproducible():
    rows_a = make_cases(7, date(2026, 1, 1), date(2026, 1, 5))
    rows_b = make_cases(7, date(2026, 1, 1), date(2026, 1, 5))
    assert rows_a == rows_b
    assert rows_a[0]["reported_source"] in {"victim_reported", "citizen_reported", "police_observed"}


def test_link_candidates_require_review():
    rows = [
        {"case_id": "1", "district": "Mysuru", "accused_name": "A. Kumar", "age_years": "28", "brief_facts": "Synthetic demonstration record: two-wheeler theft reported near X."},
        {"case_id": "2", "district": "Mangaluru", "accused_name": "A. Kumar", "age_years": "28", "brief_facts": "Synthetic demonstration record: two-wheeler theft reported near Y."},
    ]
    result = candidates(rows)
    assert result[0]["status"] == "candidate_review_required"
    assert result[0]["confidence"] >= 0.72


def test_validator_accepts_generated_data(tmp_path):
    rows = make_cases(7, date(2026, 1, 1), date(2026, 1, 3))
    path = tmp_path / "cases.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    assert validate(path) == []
