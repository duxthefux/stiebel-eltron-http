#!/usr/bin/env python3
"""Check which sections bivalence fields are in."""

from pathlib import Path
from bs4 import BeautifulSoup

print("=== GERMAN (de) ===")
html = BeautifulSoup(Path('scripts/testdata/s_1_0_de.html').read_text(encoding='utf-8'), 'html.parser')

# Find all tables
tables = html.find_all('table')
print(f"Found {len(tables)} tables\n")

for i, table in enumerate(tables):
    print(f"=== TABLE {i} ===")
    
    # Look for section header
    header_rows = table.find_all('tr', class_='head')
    if header_rows:
        for hr in header_rows:
            print(f"SECTION HEADER: {hr.get_text(strip=True)}")
    else:
        print("NO SECTION HEADER")
    
    # Find all rows with data
    data_rows = [row for row in table.find_all('tr') if 'head' not in row.get('class', [])]
    
    # Look for bivalence fields
    for row in data_rows:
        tds = row.find_all('td')
        if len(tds) >= 2:
            field_name = tds[0].get_text(strip=True)
            if 'BIVALENZ' in field_name:
                field_value = tds[1].get_text(strip=True)
                print(f"  FIELD: {field_name} = {field_value}")
    
    print()

print("\n" + "="*80 + "\n")
print("=== FRENCH (fr) ===")
html = BeautifulSoup(Path('scripts/testdata/s_1_0_fr.html').read_text(encoding='utf-8'), 'html.parser')

# Find all tables
tables = html.find_all('table')
print(f"Found {len(tables)} tables\n")

for i, table in enumerate(tables):
    print(f"=== TABLE {i} ===")
    
    # Look for section header
    header_rows = table.find_all('tr', class_='head')
    if header_rows:
        for hr in header_rows:
            print(f"SECTION HEADER: {hr.get_text(strip=True)}")
    else:
        print("NO SECTION HEADER")
    
    # Find all rows with data
    data_rows = [row for row in table.find_all('tr') if 'head' not in row.get('class', [])]
    
    # Look for bivalence fields
    for row in data_rows:
        tds = row.find_all('td')
        if len(tds) >= 2:
            field_name = tds[0].get_text(strip=True)
            if 'BIVALENCE' in field_name or 'CHAUFFAGE' in field_name or 'ECS' in field_name:
                field_value = tds[1].get_text(strip=True)
                print(f"  FIELD: {field_name} = {field_value}")
    
    print()

