#!/usr/bin/env python3
"""Extract s_2_7 diagnostic field translations from test HTML files."""

from pathlib import Path
import sys
import bs4
from collections import defaultdict

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

# Section keywords
CONTROLLER_KEYWORDS = ['REGLER', 'CONTROLLER', 'RÉGUL', 'REGUL', 'REGEL', 'REGOLAT', 
                       'STYRENHET', 'REGULAD', 'CONTROLADOR', 'STEROW', 'REGULAT', 'SZABÁLYOZ', 'SZABALYOZ',
                       'SZAB.', 'SÄÄTÖ', 'SAATO', 'SÄÄDIN', 'SAADIN', 'REGULATOR']

HEATPUMP_KEYWORDS = ['WÄRMEPUMPE', 'WARMEPUMPE', 'HEAT PUMP', 'POMPE', 'WARMTEPOMP',
                     'POMPA DI CALORE', 'VÄRMEPUMP', 'VARMEPUMP', 'BOMBA DE CALOR',
                     'POMPA CIEPLA', 'TEPELNÉ ČERPADLO', 'TEPELNE CERPADLO',
                     'HŐSZIVATTYÚ', 'HOSZTTYÚ', 'HÕSZIVATTYÚ', 'LÄMPÖPUMPPU', 'LAMPOPUMPPU', 'VARMEPUMPE']

FES_KEYWORDS = ['FES']

def find_section_table(soup, keywords):
    """Find a table with a header matching any of the keywords."""
    tables = soup.find_all('table')
    for table in tables:
        th = table.find('th')
        if th:
            header_text = th.get_text(strip=True).upper()
            for keyword in keywords:
                if keyword in header_text:
                    return table
    return None

def extract_field_by_position(table, position):
    """Extract field name at given position within table."""
    if not table:
        return None
    rows = table.find_all('tr')
    field_rows = [r for r in rows if r.find('td', class_='key')]
    if position < len(field_rows):
        key_cell = field_rows[position].find('td', class_='key')
        if key_cell:
            return key_cell.get_text(strip=True)
    return None

def main():
    print("Extracting from s_2_7 pages (Diagnostic info)...")
    print("=" * 70)
    
    testdata_dir = Path(__file__).parent / 'testdata'
    
    # Define fields and their positions
    # In CONTROLLER section:
    # Position 4 (last): SW-MATERIALNUMMER (controller)
    # In HEATPUMP section:
    # Position 4: SW-MATERIALNUMMER (heatpump)
    # Position 5: WP-TYP
    # Position 6: PARAMETERSATZ
    # Position 7: HP-ID
    # In FES section:
    # Position 4 (last): SW-MATERIALNUMMER (FES)
    
    fields = {
        'SOFTWARE_MATERIAL_NUMBER_CONTROLLER': {'section': 'CONTROLLER', 'position': 4},
        'SOFTWARE_MATERIAL_NUMBER_HEATPUMP': {'section': 'HEATPUMP', 'position': 4},
        'HEAT_PUMP_TYPE': {'section': 'HEATPUMP', 'position': 5},
        'PARAMETER_SET': {'section': 'HEATPUMP', 'position': 6},
        'HEAT_PUMP_ID': {'section': 'HEATPUMP', 'position': 7},
        'SOFTWARE_MATERIAL_NUMBER_FES': {'section': 'FES', 'position': 4},
    }
    
    results = defaultdict(dict)
    
    for lang in LANGUAGES:
        html_file = testdata_dir / f's_2_7_{lang}.html'
        if not html_file.exists():
            continue
            
        with open(html_file, 'r', encoding='utf-8') as f:
            soup = bs4.BeautifulSoup(f.read(), 'html.parser')
        
        # Extract from each section
        controller_table = find_section_table(soup, CONTROLLER_KEYWORDS)
        heatpump_table = find_section_table(soup, HEATPUMP_KEYWORDS)
        fes_table = find_section_table(soup, FES_KEYWORDS)
        
        # Extract each field
        for field_name, field_info in fields.items():
            if field_info['section'] == 'CONTROLLER':
                table = controller_table
            elif field_info['section'] == 'HEATPUMP':
                table = heatpump_table
            elif field_info['section'] == 'FES':
                table = fes_table
            else:
                continue
            
            value = extract_field_by_position(table, field_info['position'])
            if value:
                results[field_name][lang] = value
    
    # Print results
    print()
    print("=" * 70)
    print("EXTRACTION RESULTS - s_2_7 Fields")
    print("=" * 70)
    print()
    
    total_found = 0
    total_expected = 0
    
    for field_name in sorted(results.keys()):
        translations = results[field_name]
        found_count = len(translations)
        total_found += found_count
        total_expected += len(LANGUAGES)
        
        missing = [lang for lang in LANGUAGES if lang not in translations]
        
        print(f"{field_name}: {found_count}/{len(LANGUAGES)} languages found")
        if missing:
            print(f"  ⚠️ MISSING: {', '.join(missing)}")
        
        for lang in LANGUAGES:
            if lang in translations:
                print(f'  {lang}: "{translations[lang]}"')
        
        print()
        print("  # For HEADER_ALIASES:")
        print(f"  CanonicalKey.{field_name}: [")
        for lang in LANGUAGES:
            value = translations.get(lang, f"MISSING_{lang.upper()}")
            print(f'      "{value}",  # {lang}')
        print("  ],")
        print()
    
    print("=" * 70)
    print(f"Extraction complete. Found {len(results)} fields.")
    print()
    print(f"Total translations: {total_found}")
    print(f"Expected: {total_expected}")
    print(f"Missing: {total_expected - total_found}")

if __name__ == '__main__':
    main()
