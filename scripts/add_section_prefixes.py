#!/usr/bin/env python3
"""Add section prefixes to disambiguate duplicate sensor names.

When a language uses the same word for sensors in different sections,
we prefix the sensor name with the translated section name.
"""

import json
from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path(__file__).parent / "testdata"
TRANSLATIONS_DIR = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "translations"

# Map sensor keys to their (page, section_index) location
SENSOR_SECTION_MAP = {
    # s_1_0 Section 1: WARMWASSER (DHW)
    'dhw_temperature': ('s_1_0', 1),
    'dhw_set_temperature': ('s_1_0', 1),
    
    # s_1_0 Section 2: WÄRMEERZEUGER EXTERN (External heat source)
    'external_actual_temperature': ('s_1_0', 2),
    'external_set_temperature': ('s_1_0', 2),
    
    # s_1_8 Section 0: WÄRMEMENGE (Heat produced)
    'heat_produced_today': ('s_1_8', 0),
    'total_heat_produced': ('s_1_8', 0),
    'dhw_produced_today': ('s_1_8', 0),
    'total_dhw_produced': ('s_1_8', 0),
    
    # s_1_8 Section 1: STROMVERBRAUCH (Power consumption)
    'heating_consumed_today': ('s_1_8', 1),
    'total_heating_consumed': ('s_1_8', 1),
    'dhw_consumed_today': ('s_1_8', 1),
    'total_dhw_consumed': ('s_1_8', 1),
    
    # s_1_8 Section 2: EFFIZIENZ (Efficiency)
    'efficiency_heating_today': ('s_1_8', 2),
    'efficiency_heating_1_12m': ('s_1_8', 2),
    'efficiency_heating_13_24m': ('s_1_8', 2),
    'efficiency_dhw_today': ('s_1_8', 2),
    'efficiency_dhw_1_12m': ('s_1_8', 2),
    'efficiency_dhw_13_24m': ('s_1_8', 2),
}

def get_section_name(page: str, section_index: int, lang: str) -> str | None:
    """Extract section name from HTML test data."""
    html_file = TESTDATA_DIR / f"{page}_{lang}.html"
    if not html_file.exists():
        return None
    
    soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
    tables = soup.find_all('table', class_='info')
    
    if section_index >= len(tables):
        return None
    
    table = tables[section_index]
    section_header = table.find('th', class_='round-top')
    if section_header:
        return section_header.get_text(strip=True)
    
    return None

def add_prefixes_for_language(lang: str):
    """Add section prefixes to duplicate sensor names for a language."""
    json_file = TRANSLATIONS_DIR / f"{lang}.json"
    
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    
    sensors = data.get('entity', {}).get('sensor', {})
    updates = []
    
    # Process each sensor that might need a prefix
    for sensor_key, (page, section_index) in SENSOR_SECTION_MAP.items():
        if sensor_key not in sensors:
            continue
        
        current_name = sensors[sensor_key].get('name', '')
        
        # Get section name in this language
        section_name = get_section_name(page, section_index, lang)
        if not section_name:
            print(f"  WARNING: Could not find section name for {sensor_key}")
            continue
        
        # Check if we need to add prefix (i.e., name doesn't already start with section)
        if not current_name.upper().startswith(section_name.upper().split()[0]):
            # Prefix with section name
            new_name = f"{section_name} {current_name}"
            sensors[sensor_key]['name'] = new_name
            updates.append(f"  UPDATE {sensor_key}: {current_name} -> {new_name}")
    
    if updates:
        # Save updated JSON
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n{lang.upper()}:")
        for update in updates:
            print(update)
        print(f"  ✓ Saved: {len(updates)} prefixes added")
    else:
        print(f"{lang.upper()}: No updates needed")

def main():
    langs = ['cs', 'da', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']
    
    print("=" * 100)
    print("ADDING SECTION PREFIXES TO DISAMBIGUATE DUPLICATE NAMES")
    print("=" * 100)
    
    for lang in langs:
        add_prefixes_for_language(lang)
    
    print("\n" + "=" * 100)
    print("DONE!")
    print("=" * 100)

if __name__ == '__main__':
    main()
