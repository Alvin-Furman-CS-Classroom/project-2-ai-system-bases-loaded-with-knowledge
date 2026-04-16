"""
Script to clean and convert baseball-reference.com data to CSV format
"""

import csv
import re

# Raw data from user
raw_data = """Player,PO,E,Fld%,PB,SB,CS%,Pos,-9999
,,,,,,,,-9999
Matt Olson,1147,5,.996,,,,*3,olsonma02
Michael Harris II,402,1,.998,,,,*8/H,harrimi04
Ozzie Albies,205,2,.997,,,,*4,albieoz01
Nick Allen,158,6,.986,,,,*6/4H,allenni02
Austin Riley,55,11,.953,,,,5,rileyau01
Ronald Acuña Jr.,164,2,.988,,,,9/DH,acunaro01
Drake Baldwin,745,4,.995,3,88,13.7,2HD,baldwdr01
Jurickson Profar,164,1,.994,,,,7/D,profaju01
Sean Murphy,644,2,.997,2,57,29.6,2H/D,murphse01
Eli White,134,1,.993,,,,97H/D83,whiteel04
Nacho Alvarez Jr.,36,3,.978,,,,5/H,alvarna01
Alex Verdugo,88,2,.978,,,,7/H,verdual01
Ha-Seong Kim,31,0,1.000,,,,6/H,kimha01
Jarred Kelenic,32,2,.941,,,,9/H7D,kelenja01
Bryce Elder,15,0,1.000,,,,1,elderbr01
Chris Sale,7,1,.952,,,,1,salech01
Spencer Strider,9,2,.895,,,,1,stridsp01
Grant Holmes,20,1,.967,,,,1,holmegr01
Spencer Schwellenbach,19,1,.976,,,,1,schwesp01
Stuart Fairchild,33,0,1.000,,,,9H/D78,faircst01
Luke Williams,18,1,.974,,,,6H/15D,willilu01
Bryan De La Cruz,21,0,1.000,,,,7/H9D,delacbr01
Vidal Bruján,16,0,1.000,,,,6/H591,brujavi01
Orlando Arcia,7,0,1.000,,,,6/DH,arciaor01
Dylan Lee,7,0,1.000,,,,1,leedy01
Raisel Iglesias,2,0,1.000,,,,1,iglesra01
Joey Wentz,4,0,1.000,,,,1,wentzjo01
Pierce Johnson,7,0,1.000,,,,1,johnspi01
Hurston Waldrep,9,0,1.000,,,,1,waldrhu01
Aaron Bummer,3,2,.846,,,,1,bummeaa01
AJ Smith-Shawver,4,0,1.000,,,,/1,smithaj01
Jake Fraley,14,0,1.000,,,,/9H7D,fraleja01
Enyel De Los Santos,3,4,.636,,,,1,delosen01
Daysbel Hernández,2,0,1.000,,,,1,hernada03
Dylan Dodd,5,0,1.000,,,,1,dodddy01
Rafael Montero,5,0,1.000,,,,1,montera01
Sandy León,34,0,1.000,0,3,0.0,/2,leonsa01
Brett Wisely,6,0,1.000,,,,/4H,wiselbr01
Tyler Kinley,4,0,1.000,,,,1,kinlety01
Erick Fedde,2,0,1.000,,,,/1,feddeer01
Austin Cox,2,0,1.000,,,,1,coxau01
José Suarez,3,0,1.000,,,,/1,suarejo01
Scott Blewett,1,0,1.000,,,,1,blewesc01
Chadwick Tromp,17,0,1.000,0,4,0.0,/2,trompch01
Hunter Stratton,4,0,1.000,,,,1,strathu01
Carlos Carrasco,0,0,1.000,,,,/1,carraca01
Didier Fuentes,0,0,,,,,/1,fuentdi01
Dane Dunning,0,0,,,,,/1,dunnida01
Davis Daniel,0,0,,,,,/1,danieda01
Jonathan Ornelas,1,0,1.000,,,,/65,orneljo01
Jesse Chavez,0,0,1.000,,,,/1,chaveje01
Eddie Rosario,3,0,1.000,,,,/H9,rosared01
Cal Quantrill,0,0,,,,,/1,quantca01
Michael Petersen,0,0,,,,,/1,petermi01
Wander Suero,0,0,,,,,/1,suerowa01
Reynaldo López,0,0,1.000,,,,/1,lopezre01
John Brebbia,0,0,,,,,/1,brebbjo01
Connor Seabold,1,0,1.000,,,,/1,seaboco01
Zach Thompson,0,0,,,,,/1,thompza01
Rolddy Muñoz,0,0,,,,,/1,munozro02
Joel Payamps,0,0,,,,,/1,payamjo01
Alexis Díaz,0,0,1.000,,,,/1,diazal03
Hayden Harris,0,0,,,,,/1,harriha01
José Ruiz,0,0,,,,,/1,ruizjo01
Charlie Morton,0,0,,,,,/1,mortoch02
Nathan Wiles,0,0,,,,,/1,wilesna01
José Azócar,0,0,,,,,/H9D,azocajo01
Craig Kimbrel,0,0,1.000,,,,/1,kimbrcr01
Héctor Neris,0,0,,,,,/1,nerishe01
Kevin Herget,1,0,1.000,,,,/1,hergeke01
Infield Shifts,,,,,,,,-9999
Non-Shift Infield Positioning,,,,,,,,-9999
Outfield Positioning,,,,,,,,-9999
Team Totals,4314,54,.991,5,152,20.0,,-9999"""


def parse_position_code(pos_code):
    """
    Parse baseball-reference position code to our format.
    
    Position codes:
    1 = Pitcher (P) - we don't use this
    2 = Catcher (C)
    3 = First Base (1B)
    4 = Second Base (2B)
    5 = Third Base (3B)
    6 = Shortstop (SS)
    7 = Left Field (LF)
    8 = Center Field (CF)
    9 = Right Field (RF)
    H = Multiple positions
    D = Designated Hitter (we don't use this)
    
    Examples:
    *3 = Primary position 1B
    *8/H = Primary CF, also plays other positions
    2HD = Catcher, also plays other positions
    /2 = Backup catcher
    """
    if not pos_code or pos_code == '' or pos_code == '-9999':
        return []
    
    positions = []
    pos_code = pos_code.strip()
    
    # Remove asterisk (indicates primary position)
    pos_code = pos_code.replace('*', '')
    
    # Split by / to handle multiple position groups
    parts = pos_code.split('/')
    
    for part in parts:
        # Remove D (DH) and H (multiple) indicators
        part = part.replace('D', '').replace('H', '')
        
        # Extract position numbers
        for char in part:
            if char == '1':
                # Skip pitchers
                continue
            elif char == '2':
                if 'C' not in positions:
                    positions.append('C')
            elif char == '3':
                if '1B' not in positions:
                    positions.append('1B')
            elif char == '4':
                if '2B' not in positions:
                    positions.append('2B')
            elif char == '5':
                if '3B' not in positions:
                    positions.append('3B')
            elif char == '6':
                if 'SS' not in positions:
                    positions.append('SS')
            elif char == '7':
                if 'LF' not in positions:
                    positions.append('LF')
            elif char == '8':
                if 'CF' not in positions:
                    positions.append('CF')
            elif char == '9':
                if 'RF' not in positions:
                    positions.append('RF')
    
    return positions if positions else []


def convert_fielding_pct(fld_pct_str):
    """Convert fielding percentage string to decimal."""
    if not fld_pct_str or fld_pct_str == '':
        return ''
    try:
        # Remove any % sign and convert
        fld_pct_str = fld_pct_str.replace('%', '').strip()
        return float(fld_pct_str)
    except:
        return ''


def convert_cs_pct(cs_pct_str):
    """Convert caught stealing percentage string to decimal."""
    if not cs_pct_str or cs_pct_str == '':
        return ''
    try:
        # Remove any % sign and convert
        cs_pct_str = cs_pct_str.replace('%', '').strip()
        # Convert percentage to decimal and round to 3 decimal places
        return round(float(cs_pct_str) / 100.0, 3)
    except:
        return ''


def clean_data():
    """Clean and convert the raw data to CSV format."""
    lines = raw_data.strip().split('\n')
    
    # Skip header rows and empty rows
    data_rows = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith(',') or 'Stan' in line or 'additional' in line:
            continue
        if line.startswith('Player,PO'):
            continue  # Skip header
        if 'Shifts' in line or 'Positioning' in line or 'Team Totals' in line:
            continue  # Skip summary rows
        
        data_rows.append(line)
    
    # Parse and convert
    output_rows = []
    for row in data_rows:
        parts = row.split(',')
        if len(parts) < 8:
            continue
        
        player_name = parts[0].strip()
        if not player_name:
            continue
        
        po = parts[1].strip() if parts[1].strip() else '0'
        errors = parts[2].strip() if parts[2].strip() else '0'
        fld_pct = parts[3].strip()
        pb = parts[4].strip() if parts[4].strip() else ''
        sb = parts[5].strip()  # Stolen bases (not used)
        cs_pct = parts[6].strip()
        pos_code = parts[7].strip()
        
        # Skip players with no meaningful stats
        if po == '0' and errors == '0' and not fld_pct:
            continue
        
        # Convert fielding percentage
        fielding_pct = convert_fielding_pct(fld_pct)
        if not fielding_pct:
            continue  # Skip if no fielding percentage
        
        # Parse positions
        positions = parse_position_code(pos_code)
        if not positions:
            # If no positions found, skip this player
            continue
        
        # Convert caught stealing percentage
        caught_stealing_pct = convert_cs_pct(cs_pct)
        
        # Determine if catcher
        is_catcher = 'C' in positions
        
        # Build output row
        output_row = {
            'name': player_name,
            'fielding_pct': round(fielding_pct, 3) if fielding_pct else '',
            'errors': int(errors) if errors else 0,
            'putouts': int(po) if po else 0,
            'passed_balls': int(pb) if pb and is_catcher else '',
            'caught_stealing_pct': caught_stealing_pct if is_catcher and caught_stealing_pct else '',
            'positions': ','.join(positions)
        }
        
        output_rows.append(output_row)
    
    # Write to CSV
    output_file = 'cleaned_defensive_stats.csv'
    with open(output_file, 'w', newline='') as f:
        fieldnames = ['name', 'fielding_pct', 'errors', 'putouts', 'passed_balls', 'caught_stealing_pct', 'positions']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in output_rows:
            writer.writerow(row)
    
    print(f"Cleaned data written to: {output_file}")
    print(f"Total players processed: {len(output_rows)}")
    print("\nFirst few rows:")
    for i, row in enumerate(output_rows[:5]):
        print(f"  {i+1}. {row['name']}: {row['positions']} (Fld%: {row['fielding_pct']}, E: {row['errors']}, PO: {row['putouts']})")
    
    return output_file


if __name__ == "__main__":
    clean_data()
