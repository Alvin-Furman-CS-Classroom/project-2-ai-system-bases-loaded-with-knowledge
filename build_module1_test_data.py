#!/usr/bin/env python3
"""
Builds aligned Module 1 test data using real 2025 stats.

Stages:
  1. Build Braves-only batting summary from:
       - test_data/defensive_stats.json
       - raw_data/2025_batting_braves.csv
  2. Build MLB pitching summary from:
       - raw_data/2025_pitching_mlb.csv
  3. Regenerate Module 1 test files:
       - test_data/matchup_stats.json / .csv
       - test_data/batter_vs_pitchers.json / .csv
       - test_data/matchups_matrix.json

Usage:
  python3 build_module1_test_data.py           # run all steps
  python3 build_module1_test_data.py batting   # only rebuild batting_stats_2025.csv
  python3 build_module1_test_data.py pitching  # only rebuild pitching_stats_2025.csv
  python3 build_module1_test_data.py tests     # only regenerate Module 1 test files
"""

import csv
import json
import os
from typing import Dict, List, Any


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFENSIVE_JSON_PATH = os.path.join(BASE_DIR, "test_data", "defensive_stats.json")
BRAVES_BATTING_CSV_PATH = os.path.join(BASE_DIR, "raw_data", "2025_batting_braves.csv")
MLB_PITCHING_CSV_PATH = os.path.join(BASE_DIR, "raw_data", "2025_pitching_mlb.csv")

BATTING_SUMMARY_PATH = os.path.join(BASE_DIR, "test_data", "batting_stats_2025.csv")
PITCHING_SUMMARY_PATH = os.path.join(BASE_DIR, "test_data", "pitching_stats_2025.csv")


def normalize_player_name(name: str) -> str:
    """
    Normalize a Baseball-Reference player name for matching.

    - Strip whitespace
    - Remove trailing '*' (left-handed) or '#' (switch) markers
    """
    if name is None:
        return ""
    name = name.strip()
    # Remove trailing handedness markers
    while name.endswith("*") or name.endswith("#"):
        name = name[:-1]
        name = name.rstrip()
    return name


def infer_batting_handedness(player_field: str) -> str:
    """
    Infer batter handedness from the Baseball-Reference Player field.

    Convention:
      - Trailing '*' → left-handed (L)
      - Trailing '#' → switch hitter (S)
      - Otherwise    → right-handed (R)
    """
    if not player_field:
        return "R"
    player_field = player_field.strip()
    if player_field.endswith("*"):
        return "L"
    if player_field.endswith("#"):
        return "S"
    return "R"


def infer_pitcher_handedness(player_field: str) -> str:
    """
    Infer pitcher handedness from the Baseball-Reference Player field.

    Convention:
      - Trailing '*' → left-handed pitcher (LHP)
      - Otherwise    → right-handed pitcher (RHP)
    """
    if not player_field:
        return "RHP"
    player_field = player_field.strip()
    if player_field.endswith("*"):
        return "LHP"
    return "RHP"


def build_batting_stats(
    defensive_json_path: str = DEFENSIVE_JSON_PATH,
    raw_batting_csv_path: str = BRAVES_BATTING_CSV_PATH,
    output_csv_path: str = BATTING_SUMMARY_PATH,
) -> None:
    """
    Build Braves-only batting summary aligned to defensive_stats.json.

    - Reads defensive_stats.json to get the player list.
    - Reads raw 2025 Braves batting CSV from Baseball-Reference.
    - Keeps only players that appear in BOTH (Braves players).
    - Writes test_data/batting_stats_2025.csv with:
        name, ba, k, obp, slg, hr, rbi, handedness
    """
    # Load defensive player names
    with open(defensive_json_path, "r", encoding="utf-8") as f:
        defensive_players = json.load(f)

    defensive_names = [p.get("name", "").strip() for p in defensive_players if p.get("name")]
    defensive_names_normalized = {normalize_player_name(n): n for n in defensive_names}

    # Index raw batting rows by normalized player name
    batting_index: Dict[str, Dict[str, str]] = {}
    with open(raw_batting_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            player_field = (row.get("Player") or "").strip()
            if not player_field:
                continue
            # Skip team totals or summary rows
            if player_field.startswith("Team Totals"):
                continue
            norm_name = normalize_player_name(player_field)
            if not norm_name:
                continue
            batting_index[norm_name] = row

    # Build batting summary only for players that are in both sets
    output_rows: List[Dict[str, Any]] = []
    missing_batting: List[str] = []

    for norm_name, original_name in defensive_names_normalized.items():
        row = batting_index.get(norm_name)
        if not row:
            # Player appears in defensive stats but not in Braves batting CSV.
            # Per user request, we only include Braves players, so skip.
            missing_batting.append(original_name)
            continue

        player_field = row.get("Player", "")
        handedness = infer_batting_handedness(player_field)

        def parse_float(key: str) -> float:
            val = (row.get(key) or "").strip()
            try:
                return float(val)
            except ValueError:
                return 0.0

        def parse_int(key: str) -> int:
            val = (row.get(key) or "").strip()
            try:
                return int(val)
            except ValueError:
                return 0

        ba = parse_float("BA")
        obp = parse_float("OBP")
        slg = parse_float("SLG")
        hr = parse_int("HR")
        rbi = parse_int("RBI")
        k = parse_int("SO")

        output_rows.append(
            {
                "name": original_name,  # keep name exactly as in defensive_stats.json
                "ba": ba,
                "k": k,
                "obp": obp,
                "slg": slg,
                "hr": hr,
                "rbi": rbi,
                "handedness": handedness,
            }
        )

    # Write summary CSV
    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "ba", "k", "obp", "slg", "hr", "rbi", "handedness"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in output_rows:
            writer.writerow(row)

    # Print a small report for visibility when run manually
    print(f"Wrote batting summary for {len(output_rows)} players to {output_csv_path}")
    if missing_batting:
        print("Players in defensive_stats.json with no Braves batting row (skipped):")
        for name in missing_batting:
            print(f"  - {name}")


def build_pitching_stats(
    raw_pitching_csv_path: str = MLB_PITCHING_CSV_PATH,
    output_csv_path: str = PITCHING_SUMMARY_PATH,
) -> None:
    """
    Build MLB pitching summary from raw Baseball-Reference CSV, with unique pitchers.

    - Reads raw_data/2025_pitching_mlb.csv
    - Extracts name, ERA, WHIP, K rate, walk rate, handedness
    - Normalizes player names and collapses multi-team rows (2TM, 3TM, etc.)
      so that each pitcher appears once.
    - Writes test_data/pitching_stats_2025.csv
    """
    pitchers: List[Dict[str, Any]] = []
    unique_pitchers: Dict[str, Dict[str, Any]] = {}  # Store unique pitchers by normalized name

    with open(raw_pitching_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            player_field = (row.get("Player") or "").strip()
            if not player_field:
                continue
            if player_field.startswith("Team Totals"):
                continue

            name = normalize_player_name(player_field)
            if not name:
                continue

            def parse_float(key: str) -> float:
                val = (row.get(key) or "").strip()
                try:
                    return float(val)
                except ValueError:
                    return 0.0

            def parse_int(key: str) -> int:
                val = (row.get(key) or "").strip()
                try:
                    return int(val)
                except ValueError:
                    return 0

            era = parse_float("ERA")
            whip = parse_float("WHIP")
            so = parse_int("SO")
            bb = parse_int("BB")
            bf = parse_int("BF")

            if bf > 0:
                k_rate = round(so / float(bf), 3)
                walk_rate = round(bb / float(bf), 3)
            else:
                k_rate = 0.0
                walk_rate = 0.0

            handedness = infer_pitcher_handedness(player_field)

            # Store or update the pitcher entry. This keeps the last row seen
            # for a given normalized name (collapsing 2TM/3TM duplicates).
            unique_pitchers[name] = {
                "name": name,
                "era": era,
                "whip": whip,
                "k_rate": k_rate,
                "walk_rate": walk_rate,
                "handedness": handedness,
            }

    pitchers = list(unique_pitchers.values())

    os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["name", "era", "whip", "k_rate", "walk_rate", "handedness"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in pitchers:
            writer.writerow(p)

    print(f"Wrote pitching summary for {len(pitchers)} pitchers to {output_csv_path}")


def _load_batters_from_summary(path: str) -> List[Dict[str, Any]]:
    """Load batters from batting_stats_2025.csv into dictionaries suitable for JSON test files."""
    batters: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            def parse_float(key: str) -> float:
                val = (row.get(key) or "").strip()
                try:
                    return float(val)
                except ValueError:
                    return 0.0

            def parse_int(key: str) -> int:
                val = (row.get(key) or "").strip()
                try:
                    return int(val)
                except ValueError:
                    return 0

            batters.append(
                {
                    "name": (row.get("name") or "").strip(),
                    "ba": parse_float("ba"),
                    "k": parse_int("k"),
                    "obp": parse_float("obp"),
                    "slg": parse_float("slg"),
                    "hr": parse_int("hr"),
                    "rbi": parse_int("rbi"),
                    "handedness": (row.get("handedness") or "").strip() or "R",
                }
            )
    return batters


def _load_pitchers_from_summary(path: str) -> List[Dict[str, Any]]:
    """Load pitchers from pitching_stats_2025.csv into dictionaries suitable for JSON test files."""
    pitchers: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            def parse_float(key: str) -> float:
                val = (row.get(key) or "").strip()
                try:
                    return float(val)
                except ValueError:
                    return 0.0

            pitchers.append(
                {
                    "name": (row.get("name") or "").strip(),
                    "era": parse_float("era"),
                    "whip": parse_float("whip"),
                    "k_rate": parse_float("k_rate"),
                    "walk_rate": parse_float("walk_rate"),
                    "handedness": (row.get("handedness") or "").strip() or "RHP",
                }
            )
    return pitchers


def build_module1_test_files(
    batting_summary_path: str = BATTING_SUMMARY_PATH,
    pitching_summary_path: str = PITCHING_SUMMARY_PATH,
    output_dir: str = os.path.join(BASE_DIR, "test_data"),
) -> None:
    """
    Regenerate Module 1 test data files from batting/pitching summaries.

    Creates:
      - matchup_stats.json / .csv
      - batter_vs_pitchers.json / .csv
      - matchups_matrix.json
    """
    batters = _load_batters_from_summary(batting_summary_path)
    pitchers = _load_pitchers_from_summary(pitching_summary_path)

    if not batters:
        raise RuntimeError("No batters found in batting summary.")
    if not pitchers:
        raise RuntimeError("No pitchers found in pitching summary.")

    os.makedirs(output_dir, exist_ok=True)

    # --- matchup_stats: many batters vs single pitcher ---
    # Use the first pitcher as the primary opponent
    primary_pitcher = pitchers[0]

    matchup_stats_data: Dict[str, Any] = {
        "batters": batters,  # all batters with defensive stats
        "pitcher": primary_pitcher,
    }

    matchup_json_path = os.path.join(output_dir, "matchup_stats.json")
    with open(matchup_json_path, "w", encoding="utf-8") as f:
        json.dump(matchup_stats_data, f, indent=2)

    matchup_csv_path = os.path.join(output_dir, "matchup_stats.csv")
    with open(matchup_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "type",
                "name",
                "ba",
                "k",
                "obp",
                "slg",
                "hr",
                "rbi",
                "handedness",
                "era",
                "whip",
                "k_rate",
                "walk_rate",
            ]
        )
        for b in batters:
            writer.writerow(
                [
                    "batter",
                    b["name"],
                    b["ba"],
                    b["k"],
                    b["obp"],
                    b["slg"],
                    b["hr"],
                    b["rbi"],
                    b["handedness"],
                    "",
                    "",
                    "",
                    "",
                ]
            )
        p = primary_pitcher
        writer.writerow(
            [
                "pitcher",
                p["name"],
                "",
                "",
                "",
                "",
                "",
                "",
                p["handedness"],
                p["era"],
                p["whip"],
                p["k_rate"],
                p["walk_rate"],
            ]
        )

    # --- batter_vs_pitchers: single Braves hitter vs multiple pitchers ---
    # Pick the batter with highest OBP as the "star" Braves hitter.
    star_batter = max(batters, key=lambda b: b.get("obp", 0.0))
    # Use all available pitchers as opponents
    opponent_pitchers = pitchers

    batter_vs_pitchers_data: Dict[str, Any] = {
        "batters": [star_batter],
        "pitchers": opponent_pitchers,
    }

    bvp_json_path = os.path.join(output_dir, "batter_vs_pitchers.json")
    with open(bvp_json_path, "w", encoding="utf-8") as f:
        json.dump(batter_vs_pitchers_data, f, indent=2)

    bvp_csv_path = os.path.join(output_dir, "batter_vs_pitchers.csv")
    with open(bvp_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "type",
                "name",
                "ba",
                "k",
                "obp",
                "slg",
                "hr",
                "rbi",
                "handedness",
                "era",
                "whip",
                "k_rate",
                "walk_rate",
            ]
        )
        b = star_batter
        writer.writerow(
            [
                "batter",
                b["name"],
                b["ba"],
                b["k"],
                b["obp"],
                b["slg"],
                b["hr"],
                b["rbi"],
                b["handedness"],
                "",
                "",
                "",
                "",
            ]
        )
        for p in opponent_pitchers:
            writer.writerow(
                [
                    "pitcher",
                    p["name"],
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    p["handedness"],
                    p["era"],
                    p["whip"],
                    p["k_rate"],
                    p["walk_rate"],
                ]
            )

    # --- matchups_matrix: multiple batters vs multiple pitchers ---
    matrix_batters = batters[:5] if len(batters) > 5 else batters
    # Include all pitchers in the matrix to maximize coverage from the provided dataset
    matrix_pitchers = pitchers

    matchups_matrix_data: Dict[str, Any] = {
        "batters": matrix_batters,
        "pitchers": matrix_pitchers,
    }

    matrix_json_path = os.path.join(output_dir, "matchups_matrix.json")
    with open(matrix_json_path, "w", encoding="utf-8") as f:
        json.dump(matchups_matrix_data, f, indent=2)

    print("Regenerated Module 1 test data files:")
    print(f"  - {matchup_json_path}")
    print(f"  - {matchup_csv_path}")
    print(f"  - {bvp_json_path}")
    print(f"  - {bvp_csv_path}")
    print(f"  - {matrix_json_path}")


def main() -> None:
    import sys

    args = sys.argv[1:]
    mode = args[0] if args else "all"

    if mode == "batting":
        build_batting_stats()
    elif mode == "pitching":
        build_pitching_stats()
    elif mode == "tests":
        build_module1_test_files()
    elif mode == "all":
        build_batting_stats()
        build_pitching_stats()
        build_module1_test_files()
    else:
        print("Usage:")
        print("  python3 build_module1_test_data.py           # run all steps")
        print("  python3 build_module1_test_data.py batting   # only rebuild batting_stats_2025.csv")
        print("  python3 build_module1_test_data.py pitching  # only rebuild pitching_stats_2025.csv")
        print("  python3 build_module1_test_data.py tests     # only regenerate Module 1 test files")


if __name__ == "__main__":
    main()

