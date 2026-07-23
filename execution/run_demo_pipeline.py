"""Run the deterministic synthetic-data preparation workflow."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(script: str) -> None:
    print(f"\n==> {script}")
    subprocess.run([sys.executable, str(ROOT / "execution" / script)], cwd=ROOT, check=True)


def main() -> None:
    run("generate_synthetic_data.py")
    run("validate_dataset.py")
    run("build_link_candidates.py")
    print("\nDemo data pipeline completed. Optional model training requires backend/requirements.txt or Colab packages.")


if __name__ == "__main__":
    main()

