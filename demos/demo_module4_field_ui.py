#!/usr/bin/env python3
"""
Demo: print a visual Module 4 dashboard in terminal.

Run from repo root:
  PYTHONPATH=src python3 demos/demo_module4_field_ui.py
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from demos.module4_pipeline_data import compute_module4_ui_inputs
from module4.field_ui import print_lineup_and_field


def main() -> None:
    batting_order, assignment = compute_module4_ui_inputs(seed=42)
    print_lineup_and_field(batting_order, assignment)


if __name__ == "__main__":
    main()
