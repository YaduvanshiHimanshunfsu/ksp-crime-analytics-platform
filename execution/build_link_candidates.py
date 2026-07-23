"""Create explainable candidate entity links for analyst review."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def similarity(left: str, right: str) -> float:
    return round(SequenceMatcher(None, left.lower(), right.lower()).ratio(), 3)


def blocking_key(row: dict[str, str]) -> str:
    """Use initials and surname initial to avoid an expensive all-pairs comparison.

    This is only a candidate-generation rule. A record is never considered a
    confirmed identity solely because it shares this key.
    """
    tokens = [token.strip(".").lower() for token in row["accused_name"].split() if token.strip(".")]
    if not tokens or row["accused_name"].startswith("Synthetic Person"):
        return ""
    return f"{tokens[0][0]}:{tokens[-1][0]}:{int(row['age_years']) // 5}"


def candidates(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    blocks: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = blocking_key(row)
        if key:
            blocks[key].append(row)
    for block in blocks.values():
        for left, right in combinations(block, 2):
            if left["district"] == right["district"]:
                continue
            name_score = similarity(left["accused_name"], right["accused_name"])
            age_gap = abs(int(left["age_years"]) - int(right["age_years"]))
            same_mo = left["brief_facts"].split(" reported")[0] == right["brief_facts"].split(" reported")[0]
            score = round((name_score * 0.72) + (0.18 if age_gap <= 2 else 0) + (0.10 if same_mo else 0), 3)
            if score >= 0.72:
                output.append(
                    {
                        "left_case_id": left["case_id"],
                        "right_case_id": right["case_id"],
                        "left_name": left["accused_name"],
                        "right_name": right["accused_name"],
                        "left_district": left["district"],
                        "right_district": right["district"],
                        "confidence": score,
                        "name_similarity": name_score,
                        "age_gap": age_gap,
                        "same_modus_operandi": same_mo,
                        "status": "candidate_review_required",
                    }
                )
    return sorted(output, key=lambda item: float(item["confidence"]), reverse=True)[:80]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(PROJECT_ROOT / "data" / "synthetic" / "cases.csv"))
    parser.add_argument("--output", default=str(PROJECT_ROOT / "data" / "synthetic" / "link_candidates.csv"))
    args = parser.parse_args()
    with Path(args.input).open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    results = candidates(rows)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]) if results else ["status"])
        writer.writeheader()
        writer.writerows(results)
    print(f"Wrote {len(results)} analyst-review link candidates to {output}")


if __name__ == "__main__":
    main()
