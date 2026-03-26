#!/usr/bin/env python3
"""
Demo: generate external browser UI for Module 4.

Run from repo root:
  PYTHONPATH=src python3 demos/demo_module4_web_ui.py
Then open the generated file path in your browser.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from demos.module4_pipeline_data import compute_module4_ui_inputs
from module4.web_ui import write_lineup_dashboard_html


def main() -> None:
    batting_order, assignment = compute_module4_ui_inputs(seed=42)

    out = write_lineup_dashboard_html(
        batting_order,
        assignment,
        output_path=str(Path("web") / "module4_dashboard.html"),
    )
    print(f"Wrote dashboard: {out.resolve()}")


if __name__ == "__main__":
    main()
