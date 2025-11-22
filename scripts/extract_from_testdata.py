"""Create language files directly from test data HTML files."""

from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict

# Test data directory
test_data_dir = Path("tests/test_data")

# Language info
LANG_INFO = {
    "de": "German",
    "en": "English", 
    "fr": "French",
    "nl": "Dutch",
    "it": "Italian",
    "sv": "Swedish",
    "es": "Spanish",
    "pl": "Polish",
    "cs": "Czech",
    "hu": "Hungarian",
    "fi": "Finnish",
    "da": "Danish",
}

# Canonical keys mapping (field name -> canonical key name)
# Based on known mappings
FIELD_TO_CANONICAL = {
    # Sections
    "RAUMTEMPERATUR": "ROOM_TEMPERATURE_SECTION",
    "ROOM TEMPERATURE": "ROOM_TEMPERATURE_SECTION",
    "HEIZUNG": "HEATING_SECTION",
    "HEATING": "HEATING_SECTION",
    "PROZESSDATEN": "PROCESS_DATA_SECTION",
    "PROCESS DATA": "PROCESS_DATA_SECTION",
    "WARMWASSER": "DHW_SECTION",
    "DHW": "DHW_SECTION",
    "ELEKTRISCHE NACHERWÄRMUNG": "ELECTRIC_REHEATING_SECTION",
    "ELECTRIC BOOSTER HEATER": "ELECTRIC_REHEATING_SECTION",
    "WÄRMEMENGE": "AMOUNT_OF_HEAT_SECTION",
    "AMOUNT OF HEAT": "AMOUNT_OF_HEAT_SECTION",
    "LEISTUNGSAUFNAHME": "POWER_CONSUMPTION_SECTION",
    "STROMVERBRAUCH": "POWER_CONSUMPTION_SECTION",
    "POWER CONSUMPTION": "POWER_CONSUMPTION_SECTION",
    "EFFIZIENZ": "EFFICIENCY_SECTION",
    "EFFICIENCY": "EFFICIENCY_SECTION",
    "LAUFZEIT": "RUNTIME_SECTION",
    "RUNTIME": "RUNTIME_SECTION",
    "STARTS": "STARTS_SECTION",
    "ISG": "ISG_SECTION",
    
    # Start page
    "FESTWERTBETRIEB": "START_BETRIEBSART",
    "BETRIEBSART": "START_BETRIEBSART",
    "FIXED VALUE OPERATION": "START_BETRIEBSART",
    "OPERATING MODE": "START_BETRIEBSART",
    
    # Temperatures
    "AUSSENTEMPERATUR": "OUTSIDE_TEMPERATURE",
    "OUTSIDE TEMPERATURE": "OUTSIDE_TEMPERATURE",
    "RÜCKLAUFTEMPERATUR": "RETURN_TEMPERATURE",
    "RETURN TEMPERATURE": "RETURN_TEMPERATURE",
    "VORLAUFTEMPERATUR": "SUPPLY_TEMPERATURE",
    "FLOW TEMPERATURE": "SUPPLY_TEMPERATURE",
    "ISTTEMPERATUR HK 1": "ACTUAL_TEMPERATURE_HK1",
    "ACTUAL TEMPERATURE HK 1": "ACTUAL_TEMPERATURE_HK1",
    "SOLLTEMPERATUR HK 1": "TARGET_TEMPERATURE_HK1",
    "SET TEMPERATURE HK 1": "TARGET_TEMPERATURE_HK1",
    "SOLLTEMPERATUR": "TARGET_TEMPERATURE_DHW",
    "SET TEMPERATURE": "TARGET_TEMPERATURE_DHW",
    
    # More fields can be added as needed
}

# Collect translations by language
by_lang = {lang: defaultdict(list) for lang in LANG_INFO}

# Process each test HTML file
for html_file in sorted(test_data_dir.glob("*.html")):
    # Extract language from filename (e.g., s_1_0_de.html -> de)
    parts = html_file.stem.split('_')
    if len(parts) >= 4:
        lang = parts[-1]
        if lang in LANG_INFO:
            print(f"Processing {html_file.name}...")
            
            soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
            
            # Extract section headings (h1, h2, h3)
            for heading in soup.find_all(['h1', 'h2', 'h3']):
                text = heading.get_text(strip=True)
                if text and text in FIELD_TO_CANONICAL:
                    canonical = FIELD_TO_CANONICAL[text]
                    if text not in by_lang[lang][canonical]:
                        by_lang[lang][canonical].append(text)
            
            # Extract field names (from tables)
            for td in soup.find_all('td'):
                text = td.get_text(strip=True)
                # Remove values in parentheses like (45.5)
                text = text.split('(')[0].strip()
                if text and text in FIELD_TO_CANONICAL:
                    canonical = FIELD_TO_CANONICAL[text]
                    if text not in by_lang[lang][canonical]:
                        by_lang[lang][canonical].append(text)

# For now, let's just create a minimal de.py with what we extracted
print("\nExtracting German translations...")

# Write German file
de_trans = by_lang['de']
lines = [
    '"""Translation mappings for DE (German)."""',
    '',
    'from .canonical_keys import CanonicalKey',
    '',
    '',
    'TRANSLATIONS_DE = {',
]

for canonical in sorted(de_trans.keys()):
    values = de_trans[canonical]
    if len(values) == 1:
        lines.append(f'    CanonicalKey.{canonical}: "{values[0]}",')
    else:
        vals_str = ', '.join(f'"{v}"' for v in values)
        lines.append(f'    CanonicalKey.{canonical}: [{vals_str}],')

lines.append('}')
lines.append('')

output_file = Path("custom_components/stiebel_eltron_http/i18n/de.py")
output_file.write_text('\n'.join(lines), encoding='utf-8')

print(f"✓ Created de.py with {len(de_trans)} keys from test data")
print(f"  Keys: {list(de_trans.keys())}")
