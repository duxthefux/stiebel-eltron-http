#!/usr/bin/env python3
"""Extract field name translations from test HTML files by parsing like the scraper does."""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import json

# Set UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

TESTDATA_DIR = Path(__file__).parent / "testdata"

def extract_field_names(html_file: Path):
    """Extract all field names from HTML file organized by section."""
    html = html_file.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    results = {}
    current_section = None
    
    for table in soup.find_all("table", class_="info"):
        # Get section name from table header
        th = table.find("th")
        if th:
            section_name = th.get_text(strip=True)
            current_section = section_name
            results[section_name] = []
        
        # Extract all field names (first column of each row)
        for row in table.find_all("tr"):
            cells = row.find_all("td", class_="key")
            if cells:
                field_name = cells[0].get_text(strip=True)
                if field_name and current_section:
                    results[current_section].append(field_name)
    
    return results

def main():
    """Extract translations for all languages."""
    langs = ['cs', 'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']
    pages = ['s_1_0', 's_1_8', 's_2_7']
    
    # Sensors we're looking for
    target_sensors = {
        'dual_mode_temp_hzg': 'Dual mode temperature HZG',
        'dual_mode_temp_ww': 'Dual mode temperature WW',
        'efficiency_dhw_today': 'DHW efficiency 1-24h',
        'efficiency_dhw_1_12m': 'DHW efficiency 1-12M',
        'efficiency_dhw_13_24m': 'DHW efficiency 13-24M',
        'efficiency_heating_today': 'Heating efficiency 1-24h',
        'efficiency_heating_1_12m': 'Heating efficiency 1-12M',
        'efficiency_heating_13_24m': 'Heating efficiency 13-24M',
        'room_temperature': 'Room temperature',
        'room_humidity': 'Room humidity',
        'dhw_produced_today': 'DHW heat produced 1-24h',
        'total_dhw_produced': 'DHW heat produced 1-12M',
        'heat_produced_today': 'Heating heat produced 1-24h',
        'total_heat_produced': 'Heating heat produced 1-12M',
    }
    
    print("=" * 80)
    print("EXTRACTING FIELD NAMES FROM TEST HTML FILES")
    print("=" * 80)
    
    # First, show what German has
    print("\n### GERMAN REFERENCE (de) ###")
    for page in pages:
        file_path = TESTDATA_DIR / f"{page}_de.html"
        if file_path.exists():
            sections = extract_field_names(file_path)
            for section, fields in sections.items():
                if fields:
                    print(f"\n[{page}] Section: {section}")
                    for field in fields:
                        print(f"  - {field}")
    
    # Now extract for each language
    all_translations = {}
    
    for lang in langs:
        if lang == 'de' or lang == 'en':  # Skip German and English, already done
            continue
        
        print(f"\n\n### {lang.upper()} ###")
        all_translations[lang] = {}
        
        for page in pages:
            file_path = TESTDATA_DIR / f"{page}_{lang}.html"
            if not file_path.exists():
                continue
            
            sections = extract_field_names(file_path)
            for section, fields in sections.items():
                if fields:
                    print(f"\n[{page}] Section: {section}")
                    for field in fields:
                        print(f"  - {field}")
    
    print("\n\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)

if __name__ == "__main__":
    main()
