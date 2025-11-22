#!/usr/bin/env python3#!/usr/bin/env python3

"""Extract all missing translations by checking actual HTML content.""""""Extract missing translations from test data files."""



from pathlib import Pathfrom pathlib import Path

import sysfrom bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))import re



from bs4 import BeautifulSouptestdata_dir = Path(__file__).parent / 'testdata'

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient

def extract_all_fields_with_context(lang_code, pages):

LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']    """Extract all field names with their section context."""

    sections_and_fields = {}

# Fields to check on s_1_1    

S1_1_FIELDS_TO_CHECK = [    for page in pages:

    ('frost_protection_temperature', ['fr']),        filepath = testdata_dir / f'{page}_{lang_code}.html'

    ('inverter_current', ['cs', 'es', 'fr', 'hu']),        if not filepath.exists():

    ('dhw_consumed_today', ['da', 'fi', 'nl']),            continue

    ('heating_consumed_today', ['da', 'fi', 'nl']),        

    ('total_dhw_consumed', ['da', 'fi', 'nl']),        soup = BeautifulSoup(filepath.read_text(encoding='utf-8'), 'html.parser')

    ('total_heating_consumed', ['da', 'fi', 'nl']),        

]        current_section = None

        for table in soup.find_all('table', class_='info'):

def extract_all_fields(html_path, lang):            # Get section name from th

    """Extract all fields from HTML and return as dict."""            th = table.find('th')

    html_content = Path(html_path).read_text(encoding='utf-8')            if th:

    soup = BeautifulSoup(html_content, 'html.parser')                current_section = th.get_text(strip=True)

                    if current_section not in sections_and_fields:

    # Get all tables                    sections_and_fields[current_section] = []

    all_tables = soup.find_all('table')            

                # Get fields in this table

    # Collect all field names            for row in table.find_all('tr'):

    all_fields = {}                key_cell = row.find('td', class_='key')

    for table in all_tables:                if key_cell and not key_cell.get('colspan'):

        all_rows = table.find_all('tr')                    field_name = key_cell.get_text(strip=True)

        for row in all_rows:                    if current_section:

            tds = row.find_all('td')                        sections_and_fields[current_section].append(field_name)

            if len(tds) >= 2:    

                field_name = tds[0].get_text(strip=True)    return sections_and_fields

                field_value = tds[1].get_text(strip=True)

                all_fields[field_name] = field_valuedef find_field(fields, *patterns):

        """Find a field matching all patterns."""

    return all_fields    for field in fields:

        field_upper = field.upper()

print("="*80)        if all(p.upper() in field_upper for p in patterns):

print("EXTRACTING MISSING TRANSLATIONS FROM s_1_1")            return field

print("="*80)    return None



client = StiebelEltronScrapingClient("dummy", "dummy", "dummy")# Languages to process

languages = ['en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

for field_name, missing_langs in S1_1_FIELDS_TO_CHECK:

    print(f"\n{'='*80}")# Exact German field names (our reference)

    print(f"Field: {field_name}")GERMAN_VALUES = {

    print(f"Missing languages: {', '.join(missing_langs)}")    'TARGET_TEMPERATURE_HK1': 'SOLLTEMPERATUR HK 1',

    print('='*80)    'ACTUAL_TEMPERATURE_HK1': 'ISTTEMPERATUR HK 1',

        'TARGET_TEMPERATURE_DHW': 'SOLLTEMPERATUR',  # In DHW section

    # First, get the field from German which should work    'BUFFER_ACTUAL_TEMPERATURE': 'PUFFERISTTEMPERATUR',

    working_lang = 'de'    'BUFFER_TARGET_TEMPERATURE': 'PUFFERSOLLTEMPERATUR',

    html_path = f'scripts/testdata/s_1_1_{working_lang}.html'    'BIVALENCE_TEMPERATURE_HEATING': 'BIVALENZTEMPERATUR HZG',

    html_content = Path(html_path).read_text(encoding='utf-8')    'LOWER_LIMIT_HEATING': 'UNTERE EINSATZGRENZE HZG',

    result = client._extract_info_heatpump(html_content)    'BIVALENCE_TEMPERATURE_DHW': 'BIVALENZTEMPERATUR WW',

        'LOWER_LIMIT_DHW': 'UNTERE EINSATZGRENZE WW',

    if field_name in result:    'ELECTRIC_REHEATING_SECTION': 'ELEKTRISCHE NACHERWÄRMUNG',

        print(f"✅ Field exists in {working_lang}: {result[field_name]}")    'FIXED_VALUE_MODE': 'FESTWERTBETRIEB',

    else:    'RUNTIME_COMPRESSOR_HEATING': 'VD HEIZEN',

        print(f"❌ Field NOT in {working_lang} extraction!")    'RUNTIME_COMPRESSOR_DHW': 'VD WARMWASSER',

        continue    'RUNTIME_COMPRESSOR_DEFROST': 'VD ABTAUEN',

        'RUNTIME_SUPPLEMENTARY_HEATER_1': 'NHZ 1',

    # Now check each missing language    'RUNTIME_SUPPLEMENTARY_HEATER_2': 'NHZ 2',

    for lang in missing_langs:    'RUNTIME_SUPPLEMENTARY_HEATER_TOTAL': 'NHZ 1/2',

        html_path = f'scripts/testdata/s_1_1_{lang}.html'    'DEFROST_TIME': 'ZEIT ABTAUEN',

            'DEFROST_STARTS': 'STARTS ABTAUEN',

        # Get all fields from HTML    'COMPRESSOR_STARTS': 'STARTS VD',

        all_fields = extract_all_fields(html_path, lang)    'TOTAL_SUPPLEMENTARY_HEATING': 'NHZ HEIZEN SUMME',

            'TOTAL_SUPPLEMENTARY_DHW': 'NHZ WARMWASSER SUMME',

        # Try extraction    'HEAT_PUMP_TYPE': 'WP-TYP',

        html_content = Path(html_path).read_text(encoding='utf-8')    'HEAT_PUMP_ID': 'HP-ID',

        result = client._extract_info_heatpump(html_content)    'PARAMETER_SET': 'PARAMETERSATZ',

            'SOFTWARE_MATERIAL_NUMBER': 'SW-MATERIALNUMMER',  # Same field in 3 sections

        print(f"\n{lang.upper()}:")}

        if field_name in result:

            print(f"  ✅ Extracted: {result[field_name]}")# Exact match lookups (case-insensitive)

        else:# These are fields that have exact known names across languages

            print(f"  ❌ NOT extracted")EXACT_MATCHES = {

            # Show some field names from HTML that might match    'RUNTIME_SUPPLEMENTARY_HEATER_1': 'NHZ 1',

            print(f"  Available fields in HTML ({len(all_fields)} total):")    'RUNTIME_SUPPLEMENTARY_HEATER_2': 'NHZ 2',

            # Look for keywords related to the field    'RUNTIME_SUPPLEMENTARY_HEATER_TOTAL': 'NHZ 1/2',

            keywords = {    'HEAT_PUMP_ID': 'HP-ID',

                'frost_protection_temperature': ['frost', 'gel', 'anti', 'protection', 'schutz'],}

                'inverter_current': ['inverter', 'current', 'strom', 'courant', 'intensidad', 'corriente'],

                'dhw_consumed_today': ['warmwasser', 'warm water', 'dhw', 'eau chaude', 'consumed', 'verbrauch', 'heute', 'today', 'vandaag'],# Fields we need to find using pattern matching

                'heating_consumed_today': ['heating', 'heizung', 'chauffage', 'verbrauch', 'consumed', 'heute', 'today', 'vandaag'],# Each field has multiple pattern groups - try each in order

                'total_dhw_consumed': ['warmwasser', 'warm water', 'dhw', 'eau chaude', 'total', 'gesamt', 'verbrauch', 'totaal'],fields_to_find = {

                'total_heating_consumed': ['heating', 'heizung', 'chauffage', 'total', 'gesamt', 'verbrauch', 'totaal'],    # s=1,0 fields (HEATING section)

            }    'TARGET_TEMPERATURE_HK1': [

                    ('SET', 'TEMP', 'HK', '1'),

            relevant_keywords = keywords.get(field_name, [])        ('SOLL', 'HK', '1'),

            matching = []        ('CONSIGNE', 'CC1'),  # French: CONSIGNE TEMP. CC1

            for fname, fval in all_fields.items():        ('CONSIGNE', 'CC', '1'),

                fname_lower = fname.lower()    ],

                if any(kw in fname_lower for kw in relevant_keywords):    'ACTUAL_TEMPERATURE_HK1': [

                    matching.append((fname, fval))        ('ACTUAL', 'TEMP', 'HK', '1'),

                    ('IST', 'HK', '1'),

            if matching:        ('REELL', 'CC', '1'),  # French: TEMPERATURE REELLE CC 1

                print(f"  Matching fields (showing first 10):")        ('RZECZ', 'HK'),  # Polish: TEMP RZECZYWISTA HK 1

                for fname, fval in matching[:10]:    ],

                    print(f"    {fname}: {fval}")    

            else:    # TARGET_TEMPERATURE_DHW is "SET TEMPERATURE" in DHW section - needs context

                print(f"  No matches for keywords: {relevant_keywords}")    'TARGET_TEMPERATURE_DHW': None,  # Will extract using section context

    
    # s=1,0 fields (other sections)
    'BUFFER_ACTUAL_TEMPERATURE': [
        ('ACTUAL', 'BUFFER'),
        ('PUFFER', 'IST'),
        ('TAMPON', 'REELL'),
    ],
    'BUFFER_TARGET_TEMPERATURE': [
        ('SET', 'BUFFER'),
        ('PUFFER', 'SOLL'),
        ('TAMPON', 'CONSIGNE'),
    ],
    'BIVALENCE_TEMPERATURE_HEATING': [
        ('DUAL', 'HZG'),
        ('BIVAL', 'HZG'),
        ('BIMOD', 'RISC'),
        ('BIVALENCE', 'CHAUFFAGE'),  # French: TEMP. BIVALENCE CHAUFFAGE
    ],
    'LOWER_LIMIT_HEATING': [
        ('LOWER', 'HZG'),
        ('UNTERE', 'HZG'),
        ('LIMITE', 'INF', 'CHAUFFAGE'),  # French: LIMITE INF. CHAUFFAGE
        ('LIMITE', 'OPERATIVO', 'INF', 'HZG'),  # Italian
    ],
    'BIVALENCE_TEMPERATURE_DHW': [
        ('DUAL', 'WW'),
        ('BIVAL', 'WW'),
        ('BIMOD', 'WW'),
        ('DUE', 'FONTI', 'WW'),
        ('BIVALENCE', 'ECS'),  # French: TEMP. BIVALENCE ECS
    ],
    'LOWER_LIMIT_DHW': [
        ('LOWER', 'WW'),
        ('UNTERE', 'WW'),
        ('LIMITE', 'INF', 'ECS'),  # French: LIMITE INF. ECS
        ('LIMITE', 'OPERATIVO', 'INF', 'WW'),  # Italian
    ],
    'ELECTRIC_REHEATING_SECTION': [
        ('ELECTRIC', 'BOOSTER'),
        ('ELEKTRISCHE', 'NACHERW'),
        ('RESISTANCE', 'ELEC'),  # French: RESISTANCE ELEC D'APPOINT
        ('ELECTR', 'BIJVERW'),  # Dutch
    ],
    'FIXED_VALUE_MODE': [
        ('FIXED', 'VALUE'),
        ('FESTWERT'),
        ('CONSIGNE', 'FIXE'),  # French: MODE CONSIGNE FIXE
        ('VALEUR', 'FIXE'),
    ],
    
    # s=1,1 runtime fields
    'RUNTIME_COMPRESSOR_HEATING': [
        ('VD', 'HEAT', 'DAY'),
        ('VD', 'HEIZ'),
        ('COMP', 'CHAUFFAGE'),  # French: COMP. CHAUFFAGE (in DURÉE FONCTIONNEMENT)
        ('COMP', 'VERW'),  # Dutch
    ],
    'RUNTIME_COMPRESSOR_DHW': [
        ('VD', 'DHW'),
        ('VD', 'WARM'),
        ('COMP', 'ECS'),  # French: COMP. ECS
        ('COMP', 'ACS'),  # Other languages
    ],
    'RUNTIME_COMPRESSOR_DEFROST': [
        ('VD', 'DEFROST'),
        ('VD', 'ABTAU'),
        ('COMP', 'DEGIVRAGE'),  # French: COMP. DEGIVRAGE
        ('COMP', 'DEGEL'),
        ('COMP', 'SBRIN'),
    ],
    'DEFROST_TIME': [
        ('DEFROST', 'TIME'),
        ('ZEIT', 'ABTAU'),
        ('DUREE', 'DEGIVRAGE'),  # French: DUREE DEGIVRAGE
        ('TEMPO', 'SBRIN'),
    ],
    'DEFROST_STARTS': [
        ('DEFROST', 'STARTS'),
        ('STARTS', 'ABTAU'),
        ('DEMARRAGE', 'DEGIVRAGE'),  # French: DEMARRAGE DEGIVRAGE
        ('DEMARR', 'DEGEL'),
    ],
    'COMPRESSOR_STARTS': [
        ('COMPRESSOR',),  # Just "COMPRESSOR" in STARTS section
        ('VD',),  # "VD" in STARTS section (not in RUNTIME section)
        ('COMPRESSEUR',),  # French: COMPRESSEUR (in DÉMARRAGES)
    ],
    'TOTAL_SUPPLEMENTARY_HEATING': [
        ('NHZ', 'HEAT', 'TOTAL'),
        ('NHZ', 'HEIZ', 'SUMME'),
        ('ELEM', 'CH', 'NUIT', 'TOTAL'),  # French: ELEM. CH. NUIT TOTAL
        ('RISCALD', 'SUPPL', 'ELETTRICO'),
    ],
    'TOTAL_SUPPLEMENTARY_DHW': [
        ('NHZ', 'DHW', 'TOTAL'),
        ('NHZ', 'WARM', 'SUMME'),
        ('EL', 'CH', 'EAU', 'TOTAL'),  # French: EL. CH. EAU N. TOTAL
        ('ELEM', 'ECS', 'TOTAL'),
    ],
    
    # s=2,7 diagnostic fields
    'HEAT_PUMP_TYPE': [
        ('WP-TYP',),
        ('HP-TYPE',),
        ('HP', 'TYPE'),
    ],
    'PARAMETER_SET': [
        ('PARAMETERSET',),
        ('PARAMETERSATZ',),
        ('JEU', 'PARAMETRES'),  # French: JEU DE PARAMETRES
        ('ENSEMBLE', 'PARAM'),
    ],
    'SOFTWARE_MATERIAL_NUMBER': [
        ('SW', 'MATERIAL', 'NUMBER'),
        ('SW-MATERIAL'),
        ('REFERENCE', 'PIECE', 'LOGICIEL'),  # French: RÉFÉRENCE PIÈCE LOGICIEL
        ('MATERIEL', 'SW'),
    ],
}

# Extract translations
print("Extracting translations from test data...\n")

all_translations = {}

for lang in languages:
    print(f"Processing {lang}...")
    
    # Get all fields with section context for this language
    s_1_0_data = extract_all_fields_with_context(lang, ['s_1_0'])
    s_1_1_data = extract_all_fields_with_context(lang, ['s_1_1'])
    s_2_7_data = extract_all_fields_with_context(lang, ['s_2_7'])
    
    # Combine all fields from all sections for pattern matching
    all_fields = []
    for sections in [s_1_0_data, s_1_1_data, s_2_7_data]:
        for fields in sections.values():
            all_fields.extend(fields)
    
    lang_trans = {}
    
    # Handle exact matches first
    for field_name, exact_value in EXACT_MATCHES.items():
        if exact_value in all_fields:
            lang_trans[field_name] = exact_value
    
    # Handle TARGET_TEMPERATURE_DHW separately (needs section context - "SET TEMPERATURE" in DHW section)
    for section_name, fields in s_1_0_data.items():
        section_upper = section_upper = section_name.upper()
        if 'DHW' in section_upper or 'WW' in section_upper or 'ECS' in section_upper or 'ACS' in section_upper:
            # This is the DHW section
            for field in fields:
                field_upper = field.upper()
                if ('SET' in field_upper or 'SOLL' in field_upper or 'CONSIGNE' in field_upper) and \
                   ('TEMP' in field_upper or 'TEMPERATUR' in field_upper):
                    # Don't match if it has HK in it (that's the heating circuit)
                    if 'HK' not in field_upper:
                        lang_trans['TARGET_TEMPERATURE_DHW'] = field
                        break
    
    # Handle COMPRESSOR_STARTS separately (needs section context - just "COMPRESSOR" or "VD" in STARTS section)
    for section_name, fields in s_1_1_data.items():
        section_upper = section_name.upper()
        if 'STARTS' in section_upper:
            for field in fields:
                field_upper = field.upper()
                # Match "COMPRESSOR" or "VD" but not "DEFROST"
                if (field_upper == 'COMPRESSOR' or field_upper == 'VD' or 'COMP' in field_upper) and \
                   'DEFROST' not in field_upper and 'ABTAU' not in field_upper and 'DEGEL' not in field_upper:
                    lang_trans['COMPRESSOR_STARTS'] = field
                    break
    
    # Handle all other fields using pattern matching
    for field_name, pattern_groups in fields_to_find.items():
        if field_name in lang_trans:
            continue  # Already found
        if field_name in EXACT_MATCHES:
            continue  # Was exact match
        if pattern_groups is None:
            continue  # Handled separately above
        
        found = None
        for patterns in pattern_groups:
            found = find_field(all_fields, *patterns)
            if found:
                break
        
        if found:
            lang_trans[field_name] = found
        else:
            print(f"  WARNING: Could not find {field_name} for {lang}")
    
    all_translations[lang] = lang_trans

print("\n" + "="*80)
print("EXTRACTED TRANSLATIONS")
print("="*80)

# Print results in a format ready to add to mapping.py
for lang in languages:
    print(f"\n# {lang.upper()}:")
    for field_name in sorted(fields_to_find.keys()):
        if field_name in all_translations[lang]:
            value = all_translations[lang][field_name]
            print(f'# {field_name}: "{value}"')

print("\n" + "="*80)
print("GENERATING mapping.py UPDATE CODE")
print("="*80)

# All unique field names we're handling
all_field_names = set(GERMAN_VALUES.keys())
all_field_names.update(EXACT_MATCHES.keys())
all_field_names = sorted(all_field_names)

# Generate the actual code to add
for field_name in all_field_names:
    print(f"\n    # {field_name}")
    values = []
    
    # Add German value
    if field_name in GERMAN_VALUES:
        values.append(f'        "{GERMAN_VALUES[field_name]}"')
    
    # Add other language values
    for lang in ['en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']:
        if field_name in all_translations.get(lang, {}):
            values.append(f'        "{all_translations[lang][field_name]}"')
    
    if values:
        print('    CanonicalKey.' + field_name + ': [')
        print(',\n'.join(values))
        print('    ],')
    else:
        print(f'    # WARNING: No translations found for {field_name}')