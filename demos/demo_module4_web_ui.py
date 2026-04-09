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

from demos.module4_pipeline_data import (
    compute_ui_bundle,
)
from module4.web_ui import write_lineup_dashboard_html


def main() -> None:
    bundle = compute_ui_bundle(seed=42)

    out = write_lineup_dashboard_html(
        bundle["batting_order"],
        bundle["assignment"],
        output_path=str(Path("web") / "module4_dashboard.html"),
        title="Module 4 + Module 5 Dashboard",
        module5_plan=bundle["module5_plan"],
        outfield_profiles=bundle["outfield_profiles"],
        outfield_profiles_predicted=bundle["outfield_profiles_predicted"],
        defensive_profiles=bundle["defensive_profiles"],
        offensive_profiles=bundle["offensive_profiles"],
        eligibility_profiles=bundle["eligibility_profiles"],
        pipeline_context=bundle["pipeline_context"],
    )
    print(f"Wrote dashboard: {out.resolve()}")


if __name__ == "__main__":
    main()
