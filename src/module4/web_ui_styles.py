"""
Stylesheet for the Module 4 lineup dashboard (generated layout).
"""

from __future__ import annotations

from pathlib import Path


def get_dashboard_css() -> str:
    """Return embedded CSS for the dashboard page."""
    css_path = Path(__file__).with_name("dashboard.css")
    return css_path.read_text(encoding="utf-8")
