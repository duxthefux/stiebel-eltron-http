#!/usr/bin/env python3
"""Extract ALL field translations from test HTML files to complete HEADER_ALIASES."""

import bs4
from pathlib import Path
from collections import defaultdict

# Languages to check
LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

# Section header keywords by language (uppercase)
HEATING_KEYWORDS = ['HEIZUNG', 'HEATING', 'CHAUFFAGE', 'VERWARMING', 'RISCALDAMENTO', 
                    'UPPVÄRMNING', 'CALEFACCIÓN', 'OGRZEWANIE', 'TOPENI', 'FŰTÉS', 
                    'LÄMMITYS', 'OPVARMNING']

DHW_KEYWORDS = ['WARMWASSER', 'HOT WATER', 'EAU CHAUDE', 'WARMWATER', 'ACQUA CALDA',
                'VARMVATTEN', 'AGUA CALIENTE', 'CIEPŁA WODA', 'TEPLA VODA', 'MELEGVÍZ',
                'LÄMMIN VESI', 'VARMT VAND']

ELECTRIC_KEYWORDS = ['ELEKTRISCHER', 'ELECTRIC', 'ÉLECTRIQUE', 'ELEKTRISCHE', 'ELETTRICO',
                     'ELEKTRISK', 'ELÉCTRICO', 'ELEKTRYCZNY', 'ELEKTRICKÝ', 'ELEKTROMOS',
                     'SÄHKÖINEN', 'ELEKTRISK']

def find_section_table(soup, keywords):
    """Find a table with a header matching any of the keywords."""
    tables = soup.find_all('table')
    for table in tables:
        th = table.find('th')
        if th:
            header_text = th.get_text().upper()
            if any(kw in header_text for kw in keywords):
                return table
    return None

def extract_field(table, pattern_parts):
    """
    Extract a field value from a table based on pattern parts.
    pattern_parts: list of strings that should ALL appear in the field name (case insensitive)
    Returns the field name or None.
    """
    if not table:
        return None
    
    rows = table.find_all('tr')
    for row in rows:
        key_cell = row.find('td', class_='key')
        if key_cell:
            key_text = key_cell.get_text(strip=True)
            key_upper = key_text.upper()
            # All parts must be present
            if all(part.upper() in key_upper for part in pattern_parts):
                return key_text
    return None

# Dictionary to store results: {field_name: {lang: translation}}
results = defaultdict(dict)

# Define fields to extract from s_1_0 HEATING section
heating_fields = {
    'TARGET_TEMPERATURE_HK1': [['SOLL', 'HK', '1'], ['SET', 'HK', '1'], ['CONSIGNE', 'CC1'], 
                                ['GEVRAAGDE', 'HK', '1'], ['SETPOINT', 'HK', '1'], 
                                ['ÖNSKAD', 'HK', '1'], ['CONSIGNA', 'HK', '1'], 
                                ['ZADANA', 'HK', '1'], ['POZADOVANA', 'HK', '1'], 
                                ['KÍVÁNT', 'HK', '1'], ['OHJE', 'HK', '1'], 
                                ['ØNSKET', 'HK', '1']],
    
    'ACTUAL_TEMPERATURE_HK1': [['IST', 'HK', '1'], ['ACTUAL', 'HK', '1'], ['RÉELLE', 'CC', '1'], 
                                ['ACTUELE', 'HK', '1'], ['EFFETTIVA', 'HK', '1'], 
                                ['AKT', 'HK', '1'], ['REAL', 'HK', '1'], 
                                ['RZECZYWISTA', 'HK', '1'], ['SKUTECNA', 'HK', '1'], 
                                ['TÉNYLEGES', 'HK', '1'], ['TOSI', 'HK', '1'], 
                                ['AKTUEL', 'HK', '1']],
    
    'BUFFER_TARGET_TEMPERATURE': [['SOLL', 'PUFFER'], ['SET', 'BUFFER'], ['CONSIGNE', 'TAMPON'], 
                                   ['GEVRAAGDE', 'BUFFER'], ['SETPOINT', 'BUFFER'], 
                                   ['ÖNSKAD', 'BUFFERT'], ['CONSIGNA', 'ACUMULADOR'], 
                                   ['ZADANA', 'BUFOR'], ['POZADOVANA', 'AKUMUL'], 
                                   ['KÍVÁNT', 'PUFFER'], ['OHJE', 'PUSKURI'], 
                                   ['ØNSKET', 'BUFFER']],
    
    'BUFFER_ACTUAL_TEMPERATURE': [['IST', 'PUFFER'], ['ACTUAL', 'BUFFER'], ['RÉELLE', 'TAMPON'], 
                                   ['ACTUELE', 'BUFFER'], ['EFFETTIVA', 'BUFFER'], 
                                   ['AKT', 'BUFFERT'], ['REAL', 'ACUMULADOR'], 
                                   ['RZECZYWISTA', 'BUFOR'], ['SKUT', 'AKUMUL'], 
                                   ['TÉNYLEGES', 'PUFFER'], ['TOSI', 'PUSKURI'], 
                                   ['AKTUEL', 'BUFFER']],
}

# Define fields to extract from s_1_0 DHW section
dhw_fields = {
    'TARGET_TEMPERATURE_DHW': [['SOLL'], ['SET'], ['CONSIGNE'], ['GEVRAAGDE'], ['SETPOINT'], 
                                ['ÖNSKAD'], ['CONSIGNA'], ['ZADANA'], ['POZADOVANA'], 
                                ['KÍVÁNT'], ['OHJE'], ['ØNSKET']],
}

# Define fields to extract from s_1_0 ELECTRIC REHEATING section
electric_fields = {
    'BIVALENCE_TEMPERATURE_HEATING': [['BIVALENZ', 'HEIZ'], ['BIVALENCE', 'HEAT'], 
                                       ['BIVALENCE', 'CHAUFF'], ['BIVALENTIE', 'VERW'], 
                                       ['BIVALENZA', 'RISC'], ['BIVALENS', 'UPPV'], 
                                       ['BIVALENCIA', 'CALEF'], ['BIWALEN', 'OGRZ'], 
                                       ['BIVALENCE', 'TOPEN'], ['BIVALENCIA', 'FŰTÉS'], 
                                       ['BIVALENSSI', 'LÄMM'], ['BIVALENS', 'OPVARM']],
    
    'BIVALENCE_TEMPERATURE_DHW': [['BIVALENZ', 'WARM'], ['BIVALENCE', 'WATER'], 
                                   ['BIVALENCE', 'EAU'], ['BIVALENTIE', 'WATER'], 
                                   ['BIVALENZA', 'ACQUA'], ['BIVALENS', 'VARMV'], 
                                   ['BIVALENCIA', 'AGUA'], ['BIWALEN', 'WODA'], 
                                   ['BIVALENCE', 'VODA'], ['BIVALENCIA', 'VÍZ'], 
                                   ['BIVALENSSI', 'VESI'], ['BIVALENS', 'VAND']],
    
    'LOWER_LIMIT_HEATING': [['GRENZ', 'HEIZ'], ['LIMIT', 'HEAT'], ['LIMITE', 'CHAUFF'], 
                             ['GRENS', 'VERW'], ['LIMITE', 'RISC'], ['GRÄNS', 'UPPV'], 
                             ['LÍMITE', 'CALEF'], ['GRANICA', 'OGRZ'], ['LIMIT', 'TOPEN'], 
                             ['HATÁR', 'FŰTÉS'], ['RAJA', 'LÄMM'], ['GRÆNSE', 'OPVARM']],
    
    'LOWER_LIMIT_DHW': [['GRENZ', 'WARM'], ['LIMIT', 'WATER'], ['LIMITE', 'EAU'], 
                         ['GRENS', 'WATER'], ['LIMITE', 'ACQUA'], ['GRÄNS', 'VARMV'], 
                         ['LÍMITE', 'AGUA'], ['GRANICA', 'WODA'], ['LIMIT', 'VODA'], 
                         ['HATÁR', 'VÍZ'], ['RAJA', 'VESI'], ['GRÆNSE', 'VAND']],
}

print("Extracting translations from s_1_0 pages...")
print("=" * 70)

# Extract from HEATING section
for lang in LANGUAGES:
    html_file = Path(f'scripts/testdata/s_1_0_{lang}.html')
    if not html_file.exists():
        print(f"⚠️  Missing: s_1_0_{lang}.html")
        continue
    
    text = html_file.read_text(encoding='utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')
    
    # Find HEATING section
    heating_table = find_section_table(soup, HEATING_KEYWORDS)
    if heating_table:
        for field_name, patterns in heating_fields.items():
            # Try each pattern (one per language typically)
            for pattern in patterns:
                translation = extract_field(heating_table, pattern)
                if translation:
                    results[field_name][lang] = translation
                    break
    
    # Find DHW section
    dhw_table = find_section_table(soup, DHW_KEYWORDS)
    if dhw_table:
        for field_name, patterns in dhw_fields.items():
            for pattern in patterns:
                translation = extract_field(dhw_table, pattern)
                if translation:
                    results[field_name][lang] = translation
                    break
    
    # Find ELECTRIC REHEATING section
    electric_table = find_section_table(soup, ELECTRIC_KEYWORDS)
    if electric_table:
        for field_name, patterns in electric_fields.items():
            for pattern in patterns:
                translation = extract_field(electric_table, pattern)
                if translation:
                    results[field_name][lang] = translation
                    break

# Print results
for field_name in sorted(results.keys()):
    translations = results[field_name]
    print(f"\n{field_name}: {len(translations)}/12 languages found")
    for lang in LANGUAGES:
        if lang in translations:
            print(f"  {lang}: \"{translations[lang]}\"")
        else:
            print(f"  {lang}: ❌ MISSING")
    
    # Format for HEADER_ALIASES
    if translations:
        print(f"\n  # For HEADER_ALIASES:")
        print(f"  CanonicalKey.{field_name}: [")
        for lang in LANGUAGES:
            if lang in translations:
                print(f"      \"{translations[lang]}\",  # {lang}")
        print(f"  ],")

print("\n" + "=" * 70)
print(f"Extraction complete. Found {len(results)} fields.")
