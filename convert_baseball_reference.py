"""
Helper script to convert baseball-reference.com data to CSV format
for Module 2: Defensive Performance Analysis

Usage:
1. Copy your data from baseball-reference.com
2. Paste it into a text file or provide it directly
3. Run this script to convert it to the required CSV format
"""

import csv
from typing import List, Dict, Any


def create_csv_template(output_file: str = "defensive_stats_template.csv"):
    """
    Create a CSV template file with the required columns.
    
    Args:
        output_file: Name of the output CSV file
    """
    headers = [
        "name",
        "fielding_pct",
        "errors",
        "putouts",
        "passed_balls",
        "caught_stealing_pct",
        "positions"
    ]
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        # Add example row
        writer.writerow([
            "Example Player",
            "0.950",
            "5",
            "150",
            "",
            "",
            "1B,LF"
        ])
        writer.writerow([
            "Example Catcher",
            "0.980",
            "2",
            "200",
            "3",
            "0.350",
            "C"
        ])
    
    print(f"Template created: {output_file}")
    print("\nFill in the template with your baseball-reference data:")
    print("- name: Player name")
    print("- fielding_pct: Fielding percentage (as decimal, e.g., 0.950 for 95%)")
    print("- errors: Number of errors")
    print("- putouts: Number of putouts")
    print("- passed_balls: Only for catchers (leave empty for others)")
    print("- caught_stealing_pct: Only for catchers (leave empty for others)")
    print("- positions: Comma-separated list (e.g., '1B,LF' or 'C')")


def convert_from_dict_list(players_data: List[Dict[str, Any]], output_file: str = "defensive_stats.csv"):
    """
    Convert a list of player dictionaries to CSV format.
    
    Args:
        players_data: List of dictionaries with player data
        output_file: Name of the output CSV file
        
    Example players_data:
    [
        {
            "name": "John Doe",
            "fielding_pct": 0.950,
            "errors": 5,
            "putouts": 150,
            "positions": ["1B", "LF"]
        },
        {
            "name": "Jane Smith",
            "fielding_pct": 0.980,
            "errors": 2,
            "putouts": 200,
            "passed_balls": 3,
            "caught_stealing_pct": 0.350,
            "positions": ["C"]
        }
    ]
    """
    headers = [
        "name",
        "fielding_pct",
        "errors",
        "putouts",
        "passed_balls",
        "caught_stealing_pct",
        "positions"
    ]
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        
        for player in players_data:
            row = {
                "name": player.get("name", ""),
                "fielding_pct": player.get("fielding_pct", ""),
                "errors": player.get("errors", ""),
                "putouts": player.get("putouts", ""),
                "passed_balls": player.get("passed_balls", ""),
                "caught_stealing_pct": player.get("caught_stealing_pct", ""),
                "positions": ",".join(player.get("positions", [])) if isinstance(player.get("positions"), list) else player.get("positions", "")
            }
            writer.writerow(row)
    
    print(f"CSV file created: {output_file}")


def help_with_baseball_reference_fields():
    """
    Print help information about mapping baseball-reference.com fields
    to our CSV format.
    """
    print("=" * 70)
    print("Baseball-Reference.com Field Mapping Guide")
    print("=" * 70)
    print()
    print("Required Fields Mapping:")
    print("-" * 70)
    print("CSV Field          | Baseball-Reference Field")
    print("-" * 70)
    print("name              | Player name")
    print("fielding_pct      | Fld% (convert percentage to decimal)")
    print("                  |   Example: 95.0% → 0.950")
    print("errors            | E (Errors)")
    print("putouts           | PO (Putouts)")
    print("positions         | Position(s) - you'll need to list these")
    print()
    print("Catcher-Specific Fields:")
    print("-" * 70)
    print("passed_balls      | PB (Passed Balls) - only for catchers")
    print("caught_stealing_ | CS% (Caught Stealing %) - convert to decimal")
    print("  pct             |   Example: 35.0% → 0.350")
    print()
    print("Position Codes:")
    print("-" * 70)
    print("C  = Catcher")
    print("1B = First Base")
    print("2B = Second Base")
    print("3B = Third Base")
    print("SS = Shortstop")
    print("LF = Left Field")
    print("CF = Center Field")
    print("RF = Right Field")
    print()
    print("Tips:")
    print("- Fielding percentage: Divide by 100 (95.0% = 0.950)")
    print("- Caught stealing %: Divide by 100 (35.0% = 0.350)")
    print("- Positions: Use comma-separated list (e.g., '1B,LF')")
    print("- Leave catcher fields empty for non-catchers")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "template":
            create_csv_template()
        elif sys.argv[1] == "help":
            help_with_baseball_reference_fields()
        else:
            print("Usage:")
            print("  python convert_baseball_reference.py template  - Create CSV template")
            print("  python convert_baseball_reference.py help      - Show field mapping guide")
    else:
        print("Baseball-Reference to CSV Converter")
        print("=" * 50)
        print()
        print("Options:")
        print("1. Create template: python convert_baseball_reference.py template")
        print("2. Show help:       python convert_baseball_reference.py help")
        print()
        print("Or use the convert_from_dict_list() function programmatically")
