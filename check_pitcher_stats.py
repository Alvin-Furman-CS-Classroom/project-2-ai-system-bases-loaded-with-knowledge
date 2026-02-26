#!/usr/bin/env python3
"""
Detect pitchers with no games played (or placeholder stats) in Module 1 test data.

A pitcher is considered to have "no games" if:
- All of ERA, WHIP, K_rate, walk_rate are 0, or
- Three or more of those stats are 0 (likely missing/placeholder data), or
- ERA is 0 (possible no innings / tiny sample).

Run from repo root:
  python3 check_pitcher_stats.py
"""

import csv
import json
import sys
from pathlib import Path


def _is_zero(value) -> bool:
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return True
    try:
        return float(value) == 0
    except (ValueError, TypeError):
        return True


def _check_pitcher(name: str, era, whip, k_rate, walk_rate) -> tuple:
    """Return (category, description) or (None, '') if stats look normal."""
    era_z = _is_zero(era)
    whip_z = _is_zero(whip)
    k_z = _is_zero(k_rate)
    walk_z = _is_zero(walk_rate)
    zeros = sum([era_z, whip_z, k_z, walk_z])

    if zeros == 4:
        return ("no_games", "all four stats are 0 (no games played)")
    if zeros >= 3:
        return ("likely_no_games", f"{zeros}/4 stats are 0 (placeholder/missing data)")
    if era_z:
        return ("suspicious", "ERA = 0 (no innings or tiny sample)")
    return (None, "")


def check_csv(file_path: Path) -> list:
    """Check a CSV with columns name, era, whip, k_rate, walk_rate, handedness."""
    results = []
    with open(file_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            if not name:
                continue
            cat, desc = _check_pitcher(
                name,
                row.get("era"),
                row.get("whip"),
                row.get("k_rate"),
                row.get("walk_rate"),
            )
            if cat:
                results.append((cat, name, desc))
    return results


def check_json_pitchers(file_path: Path) -> list:
    """Check pitchers in a JSON file (pitcher object or pitchers array)."""
    results = []
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    pitchers_data = data.get("pitchers") or (
        [data["pitcher"]] if data.get("pitcher") else []
    )
    for p in pitchers_data:
        name = (p.get("name") or "").strip() or "(no name)"
        cat, desc = _check_pitcher(
            name,
            p.get("era"),
            p.get("whip"),
            p.get("k_rate"),
            p.get("walk_rate"),
        )
        if cat:
            results.append((cat, name, desc))
    return results


def main():
    repo = Path(__file__).resolve().parent
    test_data = repo / "test_data"

    all_findings = []

    # pitching_stats_2025.csv
    csv_path = test_data / "pitching_stats_2025.csv"
    if csv_path.exists():
        for cat, name, desc in check_csv(csv_path):
            all_findings.append((csv_path.name, cat, name, desc))

    # JSON files with pitchers
    for jname in ("matchup_stats.json", "batter_vs_pitchers.json", "matchups_matrix.json"):
        jpath = test_data / jname
        if not jpath.exists():
            continue
        try:
            for cat, name, desc in check_json_pitchers(jpath):
                all_findings.append((jpath.name, cat, name, desc))
        except Exception as e:
            print("Warning: could not check {}: {}".format(jpath, e), file=sys.stderr)

    # Report by file
    by_file = {}
    for path, cat, name, desc in all_findings:
        by_file.setdefault(path, []).append((cat, name, desc))

    print("Pitchers with no games played or placeholder stats")
    print("=" * 60)
    for path in sorted(by_file.keys()):
        entries = by_file[path]
        print("\n{}".format(path))
        for cat, name, desc in entries:
            labels = {
                "no_games": "NO GAMES (all zeros)",
                "likely_no_games": "LIKELY NO GAMES (3+ zeros)",
                "suspicious": "SUSPICIOUS (ERA=0)",
            }
            label = labels.get(cat, cat)
            print("  - {}: {}".format(name, label))
            print("    {}".format(desc))
    if not all_findings:
        print("None found. All pitchers have non-zero stats.")
    else:
        print("\n" + "=" * 60)
        print("Total: {} pitcher(s) flagged.".format(len(all_findings)))
    return 0 if not all_findings else 1


if __name__ == "__main__":
    sys.exit(main())
