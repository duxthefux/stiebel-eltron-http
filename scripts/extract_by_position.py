from bs4 import BeautifulSoup#!/usr/bin/env python3

"""

# First, get all field names from German to establish positionsExtract ALL field translations from test HTML files.

html_de = open('scripts/testdata/s_1_1_de.html', encoding='utf-8').read()This version extracts by inspecting actual field positions rather than pattern matching.

soup_de = BeautifulSoup(html_de, 'html.parser')"""

fields_de = [td.get_text(strip=True) for td in soup_de.find_all('td', class_='spalte1')]

import sys

# Find positions of NHZ HEIZEN SUMME and NHZ WARMWASSER SUMMEimport bs4

nhz_heating_pos = Nonefrom pathlib import Path

nhz_dhw_pos = Nonefrom collections import defaultdict



for i, field in enumerate(fields_de):# Ensure UTF-8 output

    if field == "NHZ HEIZEN SUMME":if sys.stdout.encoding != 'utf-8':

        nhz_heating_pos = i    sys.stdout.reconfigure(encoding='utf-8')

    elif field == "NHZ WARMWASSER SUMME":

        nhz_dhw_pos = i# Languages to check

LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

print(f"German NHZ HEIZEN SUMME at position: {nhz_heating_pos}")

print(f"German NHZ WARMWASSER SUMME at position: {nhz_dhw_pos}")# Section header keywords (use simple substring matching, case-insensitive)

# Just need to identify the section, not match perfectly

if nhz_heating_pos is None or nhz_dhw_pos is None:HEATING_KEYWORDS = ['HEIZ', 'HEAT', 'CHAUFF', 'VERW', 'RISC', 'UPPV', 'CALEF', 'OGRZ', 

    print("\nERROR: Could not find NHZ fields in German test data!")                    'TOPEN', 'FŰT', 'FÛT', 'LÄMM', 'OPVARM', 'VARME']

else:

    print("\n" + "="*80)DHW_KEYWORDS = ['WARMW', 'WARM W', 'HOT W', 'DHW', 'EAU CH', 'ACQUA', 'VARMV', 'AGUA CA', 

    print("EXACT FIELD NAMES AT THESE POSITIONS IN ALL LANGUAGES:")                'CIEPŁA', 'CIEPLA', 'TEPLA', 'MELEGV', 'LÄMMIN', 'VARMT V']

    print("="*80)

    ELECTRIC_KEYWORDS = ['ELEKTR', 'ELECTRIC', 'ÉLECTR', 'ELETTR', 'ELÉCTRI', 'ELEKTRICKÝ', 'EFTEROPVARM', 

    for lang in ['de','en','fr','nl','it','sv','es','pl','cs','hu','fi','da']:                     'RESISTANCE', 'JÄLKILÄMM', 'SÄHK']

        html = open(f'scripts/testdata/s_1_1_{lang}.html', encoding='utf-8').read()

        soup = BeautifulSoup(html, 'html.parser')def find_section_table(soup, keywords):

        fields = [td.get_text(strip=True) for td in soup.find_all('td', class_='spalte1')]    """Find a table with a header matching any of the keywords."""

            tables = soup.find_all('table')

        heating_field = fields[nhz_heating_pos] if nhz_heating_pos < len(fields) else "MISSING"    for table in tables:

        dhw_field = fields[nhz_dhw_pos] if nhz_dhw_pos < len(fields) else "MISSING"        th = table.find('th')

                if th:

        print(f'\n{lang}:')            header_text = th.get_text().upper()

        print(f'  Heating: "{heating_field}"')            if any(kw.upper() in header_text for kw in keywords):

        print(f'  DHW: "{dhw_field}"')                return table

    return None

def get_field_by_index(table, index):
    """Get the field name at a specific index in the table."""
    if not table:
        return None
    rows = table.find_all('tr')
    field_index = 0
    for row in rows:
        key_cell = row.find('td', class_='key')
        if key_cell:
            if field_index == index:
                return key_cell.get_text(strip=True)
            field_index += 1
    return None

# Dictionary to store results
results = defaultdict(dict)

# Field positions in s_1_0 HEATING section (0-indexed)
heating_positions = {
    # index: canonical_key
    1: 'ACTUAL_TEMPERATURE_HK1',  # Position 1 (after outdoor temp)
    2: 'TARGET_TEMPERATURE_HK1',   # Position 2
    4: 'BUFFER_ACTUAL_TEMPERATURE', # Position 4
    5: 'BUFFER_TARGET_TEMPERATURE', # Position 5
}

# Field positions in s_1_0 DHW section (0-indexed)
dhw_positions = {
    # index: canonical_key
    1: 'TARGET_TEMPERATURE_DHW',  # Position 1 (after actual temp)
}

# Field positions in s_1_0 ELECTRIC REHEATING section (0-indexed)
electric_positions = {
    # index: canonical_key
    0: 'BIVALENCE_TEMPERATURE_HEATING',  # Position 0
    1: 'LOWER_LIMIT_HEATING',             # Position 1
    2: 'BIVALENCE_TEMPERATURE_DHW',       # Position 2
    3: 'LOWER_LIMIT_DHW',                 # Position 3
}

print("Extracting translations from s_1_0 pages by field position...")
print("=" * 70)

for lang in LANGUAGES:
    html_file = Path(f'scripts/testdata/s_1_0_{lang}.html')
    if not html_file.exists():
        print(f"⚠️  Missing: s_1_0_{lang}.html")
        continue
    
    text = html_file.read_text(encoding='utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')
    
    # Extract from HEATING section
    heating_table = find_section_table(soup, HEATING_KEYWORDS)
    if heating_table:
        for index, canonical_key in heating_positions.items():
            field_name = get_field_by_index(heating_table, index)
            if field_name:
                results[canonical_key][lang] = field_name
    
    # Extract from DHW section
    dhw_table = find_section_table(soup, DHW_KEYWORDS)
    if dhw_table:
        for index, canonical_key in dhw_positions.items():
            field_name = get_field_by_index(dhw_table, index)
            if field_name:
                results[canonical_key][lang] = field_name
    
    # Extract from ELECTRIC REHEATING section
    electric_table = find_section_table(soup, ELECTRIC_KEYWORDS)
    if electric_table:
        for index, canonical_key in electric_positions.items():
            field_name = get_field_by_index(electric_table, index)
            if field_name:
                results[canonical_key][lang] = field_name

# Print results
for canonical_key in sorted(results.keys()):
    translations = results[canonical_key]
    missing_count = 12 - len(translations)
    
    print(f"\n{canonical_key}: {len(translations)}/12 languages found")
    if missing_count > 0:
        missing_langs = [lang for lang in LANGUAGES if lang not in translations]
        print(f"  ❌ MISSING: {', '.join(missing_langs)}")
    
    for lang in LANGUAGES:
        if lang in translations:
            print(f"  {lang}: \"{translations[lang]}\"")
    
    # Format for HEADER_ALIASES
    if translations:
        print(f"\n  # For HEADER_ALIASES (add to mapping.py):")
        print(f"  CanonicalKey.{canonical_key}: [")
        for lang in LANGUAGES:
            if lang in translations:
                print(f"      \"{translations[lang]}\",  # {lang}")
        print(f"  ],")

print("\n" + "=" * 70)
print(f"Extraction complete. Found {len(results)} fields.")
print(f"\nTotal translations: {sum(len(t) for t in results.values())}")
print(f"Expected: {len(results) * 12}")
print(f"Missing: {len(results) * 12 - sum(len(t) for t in results.values())}")
