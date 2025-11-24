#!/usr/bin/env python3
"""Analyze complete structure of all test data pages to build position map."""

import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))

TESTDATA_DIR = Path(__file__).parent / "testdata"
TRANSLATIONS_DIR = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "translations"

def extract_fields_by_position(html_file: Path) -> list[dict]:
    """Extract all fields with their section name, maintaining order."""
    html = html_file.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    sections = []
    
    for table in soup.find_all("table", class_="info"):
        th = table.find("th")
        if not th:
            continue
        
        section_name = th.get_text(strip=True)
        fields = []
        
        for row in table.find_all("tr"):
            key_cells = row.find_all("td", class_="key")
            value_cells = row.find_all("td", class_="value")
            
            if key_cells and value_cells:
                field_name = key_cells[0].get_text(strip=True)
                field_value = value_cells[0].get_text(strip=True)
                if field_name:
                    fields.append((field_name, field_value))
        
        if fields:
            sections.append({'name': section_name, 'fields': fields})
    
    return sections

# Analyze all pages for German (reference)
print("GERMAN (DE) TEST DATA STRUCTURE")
print("=" * 100)

for page in ['s_1_0', 's_1_1', 's_1_8', 's_2_7']:
    de_file = TESTDATA_DIR / f"{page}_de.html"
    if not de_file.exists():
        continue
    
    print(f"\n{page}:")
    print("-" * 100)
    
    sections = extract_fields_by_position(de_file)
    
    for sec_idx, section in enumerate(sections):
        print(f"\n  Section {sec_idx}: {section['name']} ({len(section['fields'])} fields)")
        for field_idx, (field_name, value) in enumerate(section['fields']):
            print(f"    [{field_idx}] {field_name} = {value}")

# Load German translations to see which sensor keys we need
print("\n\n" + "=" * 100)
print("GERMAN SENSOR KEYS (from de.json)")
print("=" * 100)

de_json = TRANSLATIONS_DIR / "de.json"
with open(de_json, 'r', encoding='utf-8') as f:
    de_data = json.load(f)

sensors = de_data.get('entity', {}).get('sensor', {})
print(f"\nTotal: {len(sensors)} sensors")
print("\nSensor keys:")
for key in sorted(sensors.keys()):
    name = sensors[key].get('name', '')
    print(f"  {key}: {name}")
