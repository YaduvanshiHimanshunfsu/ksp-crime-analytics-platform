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


def test_synthetic_generator_has_socioeconomic_fields():
    """Verify new socio-economic fields are present in generated data."""
    rows = make_cases(42, date(2026, 1, 1), date(2026, 1, 3))
    assert len(rows) > 0
    for row in rows[:5]:
        assert "literacy_index" in row
        assert "urbanization_index" in row
        assert "population_density" in row
        assert 0 <= row["literacy_index"] <= 1
        assert 0 <= row["urbanization_index"] <= 1
        assert row["population_density"] > 0


def test_synthetic_generator_covers_all_districts():
    """Every district should appear in generated data."""
    rows = make_cases(7, date(2026, 1, 1), date(2026, 1, 10))
    districts = {row["district"] for row in rows}
    expected = {"Bengaluru Urban", "Mysuru", "Hubballi-Dharwad", "Mangaluru", "Kalaburagi"}
    assert districts == expected


def test_link_candidates_require_review():
    rows = [
        {"case_id": "1", "district": "Mysuru", "accused_name": "A. Kumar", "age_years": "28", "brief_facts": "Synthetic demonstration record: two-wheeler theft reported near X."},
        {"case_id": "2", "district": "Mangaluru", "accused_name": "A. Kumar", "age_years": "28", "brief_facts": "Synthetic demonstration record: two-wheeler theft reported near Y."},
    ]
    result = candidates(rows)
    assert result[0]["status"] == "candidate_review_required"
    assert result[0]["confidence"] >= 0.72


def test_link_candidates_skip_same_district():
    """Candidates within the same district should be filtered out."""
    rows = [
        {"case_id": "1", "district": "Mysuru", "accused_name": "A. Kumar", "age_years": "28", "brief_facts": "Synthetic demonstration record: two-wheeler theft reported near X."},
        {"case_id": "2", "district": "Mysuru", "accused_name": "A. Kumar", "age_years": "28", "brief_facts": "Synthetic demonstration record: two-wheeler theft reported near Y."},
    ]
    result = candidates(rows)
    assert len(result) == 0


def test_validator_accepts_generated_data(tmp_path):
    rows = make_cases(7, date(2026, 1, 1), date(2026, 1, 3))
    path = tmp_path / "cases.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    assert validate(path) == []


def test_validator_rejects_bad_coordinates(tmp_path):
    """Validator should catch out-of-range coordinates."""
    rows = make_cases(7, date(2026, 1, 1), date(2026, 1, 2))
    rows[0]["latitude"] = 999  # invalid
    path = tmp_path / "cases.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    errors = validate(path)
    assert any("invalid coordinate" in e for e in errors)


def test_validator_rejects_bad_source(tmp_path):
    """Validator should catch unknown reported_source values."""
    rows = make_cases(7, date(2026, 1, 1), date(2026, 1, 2))
    rows[0]["reported_source"] = "invalid_source"
    path = tmp_path / "cases.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    errors = validate(path)
    assert any("unknown reported_source" in e for e in errors)
