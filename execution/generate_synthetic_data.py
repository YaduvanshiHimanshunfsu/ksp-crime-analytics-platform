"""Generate a deterministic, schema-faithful synthetic FIR data set for the demo.

The output is explicitly synthetic. It is designed to exercise spatial analytics,
case-link review, repeat-pattern tracking and forecast evaluation - never to mimic
or disclose a real person.
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable


DISTRICTS = {
    "Bengaluru Urban": (12.9716, 77.5946),
    "Mysuru": (12.2958, 76.6394),
    "Hubballi-Dharwad": (15.3647, 75.1240),
    "Mangaluru": (12.9141, 74.8560),
    "Kalaburagi": (17.3297, 76.8343),
}

STATIONS = {
    "Bengaluru Urban": ["Ashok Nagar", "Jayanagar", "Yeshwanthpur"],
    "Mysuru": ["Nazarbad", "Vijayanagar", "Devaraja"],
    "Hubballi-Dharwad": ["Vidyanagar", "Suburban", "Dharwad Town"],
    "Mangaluru": ["Bunder", "Kankanady", "Ullal"],
    "Kalaburagi": ["Ashok Nagar KLB", "Gulbarga", "Sedam"],
}

CRIMES = {
    "Theft": {"weight": 0.37, "gravity": "Non-Heinous", "mo": "two-wheeler theft"},
    "Burglary": {"weight": 0.20, "gravity": "Non-Heinous", "mo": "house break-in"},
    "Cyber Fraud": {"weight": 0.16, "gravity": "Non-Heinous", "mo": "UPI impersonation"},
    "Assault": {"weight": 0.14, "gravity": "Heinous", "mo": "street altercation"},
    "Robbery": {"weight": 0.13, "gravity": "Heinous", "mo": "late-night snatching"},
}

ALIASES = [
    ("A. Kumar", "Arun Kumar", 28, "network-alpha"),
    ("Ramesh K.", "Ramesh Kumar", 31, "network-alpha"),
    ("S. Pasha", "Sameer Pasha", 27, "network-beta"),
    ("N. Shetty", "Naveen Shetty", 34, "network-gamma"),
]


def choose_weighted(rng: random.Random, values: dict[str, dict[str, object]]) -> str:
    labels = list(values)
    weights = [float(values[label]["weight"]) for label in labels]
    return rng.choices(labels, weights=weights, k=1)[0]


def incident_dates(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def make_cases(seed: int, start: date, end: date) -> list[dict[str, object]]:
    rng = random.Random(seed)
    rows: list[dict[str, object]] = []
    serial_by_station: Counter[tuple[str, int]] = Counter()
    case_id = 1

    for current in incident_dates(start, end):
        weekday_uplift = 1.22 if current.weekday() in (4, 5) else 1.0
        monsoon_uplift = 1.18 if current.month in (6, 7, 8, 9) else 1.0
        festival_uplift = 1.35 if (current.month, current.day) in {(10, 24), (11, 1), (12, 31)} else 1.0
        for district, (base_lat, base_lon) in DISTRICTS.items():
            base_cases = 2 if district == "Bengaluru Urban" else 1
            extra = 1 if rng.random() < 0.52 * weekday_uplift * monsoon_uplift else 0
            hotspot_extra = 1 if district == "Mysuru" and current.month in (5, 6) and rng.random() < 0.28 else 0
            for _ in range(base_cases + extra + hotspot_extra):
                station = rng.choice(STATIONS[district])
                crime = choose_weighted(rng, CRIMES)
                if district == "Mysuru" and current.month in (5, 6) and rng.random() < 0.45:
                    crime = "Theft"
                serial_key = (station, current.year)
                serial_by_station[serial_key] += 1
                alias_name, canonical_name, age, entity_key = rng.choice(ALIASES)
                is_linked = rng.random() < 0.18
                source = rng.choices(["victim_reported", "citizen_reported", "police_observed"], [0.62, 0.26, 0.12])[0]
                latitude = round(base_lat + rng.uniform(-0.042, 0.042), 6)
                longitude = round(base_lon + rng.uniform(-0.052, 0.052), 6)
                crime_meta = CRIMES[crime]
                rows.append(
                    {
                        "case_id": case_id,
                        "crime_no": f"1{case_id:04d}{(STATIONS[district].index(station)+1):04d}{current.year}{serial_by_station[serial_key]:05d}",
                        "registered_date": current.isoformat(),
                        "incident_date": current.isoformat(),
                        "district": district,
                        "station": station,
                        "crime_head": crime,
                        "gravity": crime_meta["gravity"],
                        "latitude": latitude,
                        "longitude": longitude,
                        "brief_facts": f"Synthetic demonstration record: {crime_meta['mo']} reported near {station}.",
                        "reported_source": source,
                        "case_status": rng.choices(["Under Investigation", "Charge Sheeted", "Closed"], [0.54, 0.28, 0.18])[0],
                        "accused_name": alias_name if is_linked else f"Synthetic Person {case_id:04d}",
                        "canonical_demo_entity": entity_key if is_linked else f"single-{case_id}",
                        "age_years": age if is_linked else rng.randint(20, 54),
                        "gender": "M" if rng.random() < 0.78 else "F",
                        "festival_day": int(festival_uplift > 1),
                        "rainfall_index": round(rng.uniform(0.2, 1.0) if current.month in (6, 7, 8, 9) else rng.uniform(0.0, 0.35), 2),
                    }
                )
                case_id += 1
    return rows


def write_csv(rows: list[dict[str, object]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="data/synthetic/cases.csv")
    parser.add_argument("--seed", type=int, default=20260723)
    parser.add_argument("--start", default="2025-07-01")
    parser.add_argument("--end", default="2026-07-22")
    args = parser.parse_args()
    rows = make_cases(args.seed, date.fromisoformat(args.start), date.fromisoformat(args.end))
    write_csv(rows, Path(args.output))
    print(f"Wrote {len(rows)} clearly synthetic FIR-style cases to {args.output}")


if __name__ == "__main__":
    main()

