#!/usr/bin/env python3
"""
Serve `web/` and POST /api/plan for live Module 5 replanning from the dashboard.

From repository root (after regenerating the HTML):

  PYTHONPATH=src python3 demos/demo_module4_web_ui.py
  PYTHONPATH=src python3 demos/dashboard_plan_server.py

Then open http://127.0.0.1:8765/module4_dashboard.html

Use the editable game-state controls and click **Refresh plan** (or enable auto-refresh).
"""

from __future__ import annotations

import argparse
import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
WEB_ROOT = REPO_ROOT / "web"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from module5.planner import PlanningInputError, generate_adaptive_plan


class DashboardPlanHandler(SimpleHTTPRequestHandler):
    """Static files from web/ plus JSON POST /api/plan."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, status: int, payload: object) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path != "/api/plan":
            self.send_error(404, "Not Found")
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body"})
            return
        try:
            plan = generate_adaptive_plan(
                data["game_state"],
                data["current_lineup"],
                data["bench_players"],
                data["offensive_scores"],
                data["defensive_scores"],
                innings_ahead=int(data.get("innings_ahead", 3)),
            )
        except KeyError as exc:
            self._send_json(400, {"error": f"Missing key: {exc}"})
            return
        except PlanningInputError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(200, plan)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dashboard static server + /api/plan")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address")
    parser.add_argument("--port", type=int, default=8765, help="Port")
    args = parser.parse_args()
    server = HTTPServer((args.host, args.port), DashboardPlanHandler)
    print(f"Serving {WEB_ROOT} at http://{args.host}:{args.port}/")
    print(f"Open http://{args.host}:{args.port}/module4_dashboard.html")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
