#!/usr/bin/env python3
"""
Script to scrape 2025 Atlanta Braves statistics from Baseball Reference
and create test data files for Module 1.
"""

import json
import csv
import urllib.request
import ssl
import re
from html.parser import HTMLParser
from typing import List, Dict, Optional

# Disable SSL verification for scraping (not recommended for production)
ssl._create_default_https_context = ssl._create_unverified_context


def fetch_page(url: str) -> str:
    """Fetch HTML content from URL."""
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching page: {e}")
        return ""


def extract_table_data(html: str, table_id: str) -> List[Dict]:
    """Extract data from an HTML table by ID."""
    # Find the table
    table_pattern = rf'<table[^>]*id="{table_id}"[^>]*>(.*?)</table>'
    table_match = re.search(table_pattern, html, re.DOTALL | re.IGNORECASE)
    
    if not table_match:
        return []
    
    table_html = table_match.group(1)
    rows = []
    
    # Extract table rows
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    row_matches = re.finditer(row_pattern, table_html, re.DOTALL | re.IGNORECASE)
    
    headers = []
    for i, row_match in enumerate(row_matches):
        row_html = row_match.group(1)
        
        # Extract cells
        cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
        cells = re.findall(cell_pattern, row_html, re.DOTALL | re.IGNORECASE)
        
        # Clean cell content
        cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
        cells = [cell for cell in cells if cell]  # Remove empty cells
        
        if i == 0 and 'th' in row_html.lower():
            # This is the header row
            headers = cells
        elif cells:
            # This is a data row
            if headers:
                row_dict = {}
                for j, cell in enumerate(cells):
                    if j < len(headers):
                        row_dict[headers[j]] = cell
                rows.append(row_dict)
            else:
                # No headers, use index
                rows.append(cells)
    
    return rows


def parse_batter_stats(row: Dict) -> Optional[Dict]:
    """Parse batter statistics from a table row."""
    try:
        # Extract name (usually in first column or has data-stat="player")
        name = row.get('Name', row.get('Player', ''))
        if not name or name == 'Name' or name == 'Player':
            return None
        
        # Clean name (remove HTML entities, extra spaces)
        name = re.sub(r'&[^;]+;', '', name).strip()
        name = re.sub(r'\s+', ' ', name)
        
        # Extract stats - Baseball Reference uses data-stat attributes
        # We'll try to extract from text content
        ba = float(row.get('BA', row.get('Batting Avg', '0'))) if row.get('BA') or row.get('Batting Avg') else None
        obp = float(row.get('OBP', '0')) if row.get('OBP') else None
        slg = float(row.get('SLG', '0')) if row.get('SLG') else None
        hr = int(row.get('HR', '0')) if row.get('HR') else None
        rbi = int(row.get('RBI', '0')) if row.get('RBI') else None
        k = int(row.get('SO', row.get('K', '0'))) if row.get('SO') or row.get('K') else None
        
        # Handedness - might need to look up separately or estimate
        # For now, we'll need to handle this manually or skip
        handedness = row.get('Bats', 'R')  # Default to R if not found
        
        if ba is None or obp is None or slg is None:
            return None
        
        return {
            'name': name,
            'ba': ba,
            'k': k or 0,
            'obp': obp,
            'slg': slg,
            'hr': hr or 0,
            'rbi': rbi or 0,
            'handedness': handedness
        }
    except (ValueError, KeyError) as e:
        return None


def parse_pitcher_stats(row: Dict) -> Optional[Dict]:
    """Parse pitcher statistics from a table row."""
    try:
        name = row.get('Name', row.get('Player', ''))
        if not name or name == 'Name' or name == 'Player':
            return None
        
        name = re.sub(r'&[^;]+;', '', name).strip()
        name = re.sub(r'\s+', ' ', name)
        
        era = float(row.get('ERA', '0')) if row.get('ERA') else None
        whip = float(row.get('WHIP', '0')) if row.get('WHIP') else None
        
        # K rate and walk rate might need calculation from IP and stats
        so = int(row.get('SO', row.get('K', '0'))) if row.get('SO') or row.get('K') else 0
        bb = int(row.get('BB', '0')) if row.get('BB') else 0
        ip = float(row.get('IP', '0')) if row.get('IP') else 0
        
        # Calculate rates (approximate)
        k_rate = (so / (ip * 3 + so + bb)) if (ip * 3 + so + bb) > 0 else 0.0
        walk_rate = (bb / (ip * 3 + so + bb)) if (ip * 3 + so + bb) > 0 else 0.0
        
        handedness = row.get('Throws', 'RHP')
        if handedness and handedness not in ['LHP', 'RHP']:
            handedness = 'RHP' if 'R' in str(handedness).upper() else 'LHP'
        
        if era is None or whip is None:
            return None
        
        return {
            'name': name,
            'era': era,
            'whip': whip,
            'k_rate': round(k_rate, 3),
            'handedness': handedness,
            'walk_rate': round(walk_rate, 3)
        }
    except (ValueError, KeyError) as e:
        return None


def main():
    """Main function to scrape and create test data."""
    url = "https://www.baseball-reference.com/teams/ATL/2025.shtml"
    
    print("Fetching data from Baseball Reference...")
    html = fetch_page(url)
    
    if not html:
        print("Failed to fetch page. Creating sample data based on typical MLB stats instead.")
        create_sample_data()
        return
    
    print("Parsing HTML...")
    
    # Try to find batting and pitching tables
    # Baseball Reference uses specific table IDs
    batters = []
    pitchers = []
    
    # Look for standard batting table
    batting_rows = extract_table_data(html, 'team_batting')
    if not batting_rows:
        # Try alternative table IDs
        for table_id in ['batting_standard', 'batting', 'team_batting_standard']:
            batting_rows = extract_table_data(html, table_id)
            if batting_rows:
                break
    
    # Look for pitching table
    pitching_rows = extract_table_data(html, 'team_pitching')
    if not pitching_rows:
        for table_id in ['pitching_standard', 'pitching', 'team_pitching_standard']:
            pitching_rows = extract_table_data(html, table_id)
            if pitching_rows:
                break
    
    # Parse batter stats
    print("Parsing batter statistics...")
    for row in batting_rows[:15]:  # Limit to top 15 batters
        batter = parse_batter_stats(row)
        if batter:
            batters.append(batter)
    
    # Parse pitcher stats
    print("Parsing pitcher statistics...")
    for row in pitching_rows[:10]:  # Limit to top 10 pitchers
        pitcher = parse_pitcher_stats(row)
        if pitcher:
            pitchers.append(pitcher)
    
    if not batters or not pitchers:
        print("Could not extract sufficient data. Creating sample data instead.")
        create_sample_data()
        return
    
    # Create test data files
    print(f"Found {len(batters)} batters and {len(pitchers)} pitchers")
    create_test_files(batters, pitchers)


def create_sample_data():
    """Create sample test data based on realistic MLB statistics."""
    # Sample batters (based on typical 2025 Braves lineup)
    batters = [
        {'name': 'Ronald Acuña Jr.', 'ba': 0.337, 'k': 84, 'obp': 0.416, 'slg': 0.596, 'hr': 41, 'rbi': 106, 'handedness': 'R'},
        {'name': 'Ozzie Albies', 'ba': 0.274, 'k': 98, 'obp': 0.336, 'slg': 0.513, 'hr': 33, 'rbi': 109, 'handedness': 'S'},
        {'name': 'Austin Riley', 'ba': 0.282, 'k': 142, 'obp': 0.345, 'slg': 0.516, 'hr': 37, 'rbi': 97, 'handedness': 'R'},
        {'name': 'Matt Olson', 'ba': 0.283, 'k': 167, 'obp': 0.389, 'slg': 0.604, 'hr': 54, 'rbi': 139, 'handedness': 'L'},
        {'name': 'Marcell Ozuna', 'ba': 0.274, 'k': 144, 'obp': 0.346, 'slg': 0.558, 'hr': 40, 'rbi': 100, 'handedness': 'R'},
        {'name': 'Michael Harris II', 'ba': 0.293, 'k': 131, 'obp': 0.331, 'slg': 0.477, 'hr': 18, 'rbi': 57, 'handedness': 'L'},
        {'name': 'Orlando Arcia', 'ba': 0.264, 'k': 108, 'obp': 0.321, 'slg': 0.420, 'hr': 17, 'rbi': 57, 'handedness': 'R'},
        {'name': 'Sean Murphy', 'ba': 0.251, 'k': 124, 'obp': 0.365, 'slg': 0.478, 'hr': 21, 'rbi': 68, 'handedness': 'R'},
    ]
    
    # Sample pitchers (based on typical 2025 Braves rotation)
    pitchers = [
        {'name': 'Spencer Strider', 'era': 3.86, 'whip': 1.09, 'k_rate': 0.37, 'handedness': 'RHP', 'walk_rate': 0.07},
        {'name': 'Max Fried', 'era': 3.20, 'whip': 1.13, 'k_rate': 0.24, 'handedness': 'LHP', 'walk_rate': 0.06},
        {'name': 'Charlie Morton', 'era': 3.64, 'whip': 1.27, 'k_rate': 0.25, 'handedness': 'RHP', 'walk_rate': 0.09},
        {'name': 'Bryce Elder', 'era': 3.81, 'whip': 1.28, 'k_rate': 0.20, 'handedness': 'RHP', 'walk_rate': 0.08},
    ]
    
    create_test_files(batters, pitchers)


def create_test_files(batters: List[Dict], pitchers: List[Dict]):
    """Create JSON and CSV test data files."""
    # Create matchup_stats format (multiple batters, one pitcher)
    matchup_data = {
        'batters': batters[:5],  # Top 5 batters
        'pitcher': pitchers[0] if pitchers else {}
    }
    
    # Create batter_vs_pitchers format (one batter, multiple pitchers)
    batter_vs_pitchers_data = {
        'batters': [batters[0]] if batters else [],
        'pitchers': pitchers[:4] if len(pitchers) >= 4 else pitchers
    }
    
    # Create matchups_matrix format (multiple batters, multiple pitchers)
    matchups_matrix_data = {
        'batters': batters[:3] if len(batters) >= 3 else batters,
        'pitchers': pitchers[:3] if len(pitchers) >= 3 else pitchers
    }
    
    # Write JSON files
    print("Creating JSON test files...")
    with open('test_data/braves_matchup_stats.json', 'w') as f:
        json.dump(matchup_data, f, indent=2)
    
    with open('test_data/braves_batter_vs_pitchers.json', 'w') as f:
        json.dump(batter_vs_pitchers_data, f, indent=2)
    
    with open('test_data/braves_matchups_matrix.json', 'w') as f:
        json.dump(matchups_matrix_data, f, indent=2)
    
    # Write CSV files
    print("Creating CSV test files...")
    # matchup_stats.csv
    with open('test_data/braves_matchup_stats.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['type', 'name', 'ba', 'k', 'obp', 'slg', 'hr', 'rbi', 'handedness', 'era', 'whip', 'k_rate', 'walk_rate'])
        for batter in matchup_data['batters']:
            writer.writerow(['batter', batter['name'], batter['ba'], batter['k'], batter['obp'], 
                           batter['slg'], batter['hr'], batter['rbi'], batter['handedness'], '', '', '', ''])
        if matchup_data['pitcher']:
            p = matchup_data['pitcher']
            writer.writerow(['pitcher', p['name'], '', '', '', '', '', '', p['handedness'], 
                           p['era'], p['whip'], p['k_rate'], p['walk_rate']])
    
    # batter_vs_pitchers.csv
    with open('test_data/braves_batter_vs_pitchers.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['type', 'name', 'ba', 'k', 'obp', 'slg', 'hr', 'rbi', 'handedness', 'era', 'whip', 'k_rate', 'walk_rate'])
        for batter in batter_vs_pitchers_data['batters']:
            writer.writerow(['batter', batter['name'], batter['ba'], batter['k'], batter['obp'], 
                           batter['slg'], batter['hr'], batter['rbi'], batter['handedness'], '', '', '', ''])
        for pitcher in batter_vs_pitchers_data['pitchers']:
            writer.writerow(['pitcher', pitcher['name'], '', '', '', '', '', '', pitcher['handedness'], 
                           pitcher['era'], pitcher['whip'], pitcher['k_rate'], pitcher['walk_rate']])
    
    print("Test data files created successfully!")
    print(f"  - test_data/braves_matchup_stats.json")
    print(f"  - test_data/braves_matchup_stats.csv")
    print(f"  - test_data/braves_batter_vs_pitchers.json")
    print(f"  - test_data/braves_batter_vs_pitchers.csv")
    print(f"  - test_data/braves_matchups_matrix.json")


if __name__ == '__main__':
    main()
