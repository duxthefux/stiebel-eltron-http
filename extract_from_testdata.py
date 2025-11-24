"""Extract field names from test HTML files for translation."""
import re
from pathlib import Path

langs = ['cs', 'da', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']
pages = ['s_1_0', 's_1_8', 's_2_7']  # System info, efficiency, energy consumed

# These are the German field names we know work
reference_patterns = {
    'dual_mode_temp_hzg': 'BIVALENZTEMPERATUR HZG',
    'dual_mode_temp_ww': 'BIVALENZTEMPERATUR WW',
    'room_temperature': 'RAUMTEMPERATUR',
    'room_humidity': 'RAUMFEUCHTE RELATIV',
}

# Extract all table rows with <td class="key">
def extract_fields(html_file):
    """Extract all field names from HTML."""
    content = html_file.read_text(encoding='utf-8')
    # Find all <td class="key">FIELD NAME</td>
    matches = re.findall(r'<td class="key">([^<]+)</td>', content)
    return [m.strip() for m in matches]

def find_similar_field(fields, patterns):
    """Find field matching any of the patterns."""
    for field in fields:
        for pattern in patterns:
            if re.search(pattern, field, re.IGNORECASE):
                return field
    return None

# Patterns to search for each sensor (case-insensitive, flexible matching)
search_patterns = {
    'dual_mode_temp_hzg': [r'BIVALENT.*HZG', r'BIVALENT.*TOPENI', r'BIVALENT.*RISCALDAMENTO', r'BIVALENT.*VERWARMING', r'BIVALENT.*CHAUFFAGE'],
    'dual_mode_temp_ww': [r'BIVALENT.*WW', r'BIVALENT.*TUV', r'BIVALENT.*ACS', r'BIVALENT.*ACQUA'],
}

results = {}

for lang in langs:
    results[lang] = {}
    all_fields = []
    
    # Collect fields from all test pages
    for page in pages:
        testfile = Path(f'scripts/testdata/{page}_{lang}.html')
        if testfile.exists():
            fields = extract_fields(testfile)
            all_fields.extend([(f, page) for f in fields])
    
    if not all_fields:
        continue
    
    print(f'\n{lang.upper()}:')
    print(f'Total fields found: {len(all_fields)}')
    
    for sensor_key, patterns in search_patterns.items():
        for field, page in all_fields:
            match = False
            for pattern in patterns:
                if re.search(pattern, field, re.IGNORECASE):
                    print(f'  {sensor_key}: "{field}" (from {page})')
                    results[lang][sensor_key] = field
                    match = True
                    break
            if match:
                break

# Also check for other common fields by exact match with variations
print('\n\n=== Searching for efficiency and produced fields in all pages ===')

for lang in langs:
    all_fields = []
    for page in pages:
        testfile = Path(f'scripts/testdata/{page}_{lang}.html')
        if testfile.exists():
            fields = extract_fields(testfile)
            all_fields.extend([(f, page) for f in fields])
    
    if not all_fields:
        continue
    
    # Look for efficiency/COP fields (various language patterns)
    efficiency_words = ['EFFI', 'COP', 'EFFICACITE', 'EFFICIENZA', 'WYDAJNO', 'ÚČINNOST']
    produced_words = ['ERZEUGT', 'PRODUCED', 'PRODUIT', 'PRODOTTO', 'GEPRODUCEERD', 'VYROBENO']
    
    eff_fields = [(f, p) for f, p in all_fields if any(w in f.upper() for w in efficiency_words)]
    prod_fields = [(f, p) for f, p in all_fields if any(w in f.upper() for w in produced_words)]
    
    if eff_fields or prod_fields:
        print(f'\n{lang.upper()}:')
        if eff_fields:
            for field, page in eff_fields:
                print(f'  [EFF] {field} (from {page})')
        if prod_fields:
            for field, page in prod_fields:
                print(f'  [PROD] {field} (from {page})')

print('\n\n=== JSON output for translations ===')
for lang, translations in results.items():
    if translations:
        print(f'\n{lang}:')
        for key, value in sorted(translations.items()):
            print(f'            "{key}": {{')
            print(f'                "name": "{value}"')
            print(f'            }},')
