#!/usr/bin/env python3
"""Add unprefixed field names as parsing aliases to i18n lang.py files.

The translation JSON has section-prefixed names for UI display, but the scraper
needs to find the unprefixed field names in the HTML.
"""

from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path(__file__).parent / "testdata"

# Map sensor keys to their (page, section_index, field_index) location
SENSORS_NEEDING_ALIASES = {
    # DHW section - plain "ACTUAL TEMPERATURE" / "SET TEMPERATURE" etc
    'dhw_temperature': ('s_1_0', 1, 0, 'ACTUAL_TEMPERATURE'),
    'dhw_set_temperature': ('s_1_0', 1, 1, 'SET_TEMPERATURE'),
    
    # External section already handled with EXTERNAL_ACTUAL_TEMPERATURE aliases
    # Efficiency section - plain "HEATING" / "DHW" field names
    'efficiency_heating_today': ('s_1_8', 2, 0, None),  # Field name varies by language
    'efficiency_heating_1_12m': ('s_1_8', 2, 1, None),
    'efficiency_heating_13_24m': ('s_1_8', 2, 2, None),
    'efficiency_dhw_today': ('s_1_8', 2, 3, None),
    'efficiency_dhw_1_12m': ('s_1_8', 2, 4, None),
    'efficiency_dhw_13_24m': ('s_1_8', 2, 5, None),
}

def extract_field_name(page: str, section_idx: int, field_idx: int, lang: str) -> str | None:
    """Extract field name from HTML at given position."""
    html_file = TESTDATA_DIR / f"{page}_{lang}.html"
    if not html_file.exists():
        return None
    
    soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
    tables = soup.find_all('table', class_='info')
    
    if section_idx >= len(tables):
        return None
    
    table = tables[section_idx]
    rows = table.find_all('tr')
    
    field_count = 0
    for row in rows:
        key_cell = row.find('td', class_='key')
        if key_cell:
            if field_count == field_idx:
                return key_cell.get_text(strip=True)
            field_count += 1
    
    return None

def main():
    langs = {
        'cs': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
        'da': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
        'es': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
        'fi': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
        'fr': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
        'hu': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
        'it': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
        'nl': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
        'pl': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
        'sv': 'CanonicalKey.ACTUAL_TEMPERATURE / SET_TEMPERATURE',
    }
    
    print("Unprefixed field names to add to lang.py files as PARSING_TRANSLATIONS:")
    print("=" * 100)
    
    for lang in langs:
        print(f"\n{lang.upper()}:")
        
        # DHW temperature
        dhw_temp = extract_field_name('s_1_0', 1, 0, lang)
        dhw_set = extract_field_name('s_1_0', 1, 1, lang)
        
        if dhw_temp:
            print(f"  CanonicalKey.ACTUAL_TEMPERATURE: [\"{dhw_temp}\"],  # DHW section field")
        if dhw_set:
            print(f"  CanonicalKey.SET_TEMPERATURE: [\"{dhw_set}\"],  # DHW section field")

if __name__ == '__main__':
    main()
