"""Extract entity translations from testdata HTML files.

Parses testdata HTML files to extract field names and create translation
JSON files for Home Assistant with actual language-specific entity names.

The generated JSON files have sensors sorted alphabetically for easier diff review.
"""

import json
from pathlib import Path
from bs4 import BeautifulSoup
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.mapping import (
    CANONICAL_TO_CONST, 
    CanonicalKey,
    ENERGY_CONSUMED_MAP,
)
from custom_components.stiebel_eltron_http.const import (
    ROOM_TEMPERATURE_KEY, 
    ROOM_HUMIDITY_KEY, 
    DHW_TEMPERATURE_KEY,
)
from custom_components.stiebel_eltron_http.i18n import HEADER_ALIASES

# Language metadata
LANGUAGES = {
    'de': 'German',
    'en': 'English',
    'fr': 'French',
    'nl': 'Dutch',
    'it': 'Italian',
    'sv': 'Swedish',
    'es': 'Spanish',
    'pl': 'Polish',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'fi': 'Finnish',
    'da': 'Danish',
}


def extract_fields_from_html(html_path):
    """Extract all field names from an HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    fields = set()
    
    # Extract from table headers
    for th in soup.find_all('th'):
        text = th.get_text(strip=True)
        if text:
            fields.add(text)
    
    # Extract from table cells with class="key"
    for td in soup.find_all('td', class_='key'):
        text = td.get_text(strip=True)
        if text:
            fields.add(text)
    
    # Extract from h3 headings
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if text:
            fields.add(text)
    
    # Extract from navigation links
    for a in soup.find_all('a'):
        text = a.get_text(strip=True)
        if text and len(text) < 50:  # Reasonable length for field names
            fields.add(text)
    
    return fields


def find_translation_for_const(const_key, lang_fields, lang_code, canonical_to_const_map):
    """Find the translation for a const key in the language-specific fields."""
    # Find which canonical key(s) map to this const
    canonical_keys = []
    for can_key, const in canonical_to_const_map.items():
        if const == const_key:
            canonical_keys.append(can_key)
    
    if not canonical_keys:
        return None
    
    # Try each canonical key to find a match
    lang_fields_lower = {f.lower(): f for f in lang_fields}
    
    for canonical_key in canonical_keys:
        # Get all possible aliases for this canonical key
        aliases = HEADER_ALIASES.get(canonical_key, [])
        
        # Find which alias appears in the language fields (case-insensitive)
        for alias in aliases:
            if alias.lower() in lang_fields_lower:
                return lang_fields_lower[alias.lower()]
    
    return None


def create_translation_structure(lang_code, entity_names):
    """Create the translation JSON structure."""
    host_descriptions = {
        'de': "Der Hostname oder die IP-Adresse Ihres Stiebel Eltron ISG-Geräts.",
        'en': "The hostname or IP address of your Stiebel Eltron ISG device.",
        'fr': "Le nom d'hôte ou l'adresse IP de votre appareil Stiebel Eltron ISG.",
        'nl': "De hostnaam of het IP-adres van uw Stiebel Eltron ISG-apparaat.",
        'it': "Il nome host o l'indirizzo IP del tuo dispositivo Stiebel Eltron ISG.",
        'sv': "Värdnamnet eller IP-adressen för din Stiebel Eltron ISG-enhet.",
        'es': "El nombre de host o la dirección IP de su dispositivo Stiebel Eltron ISG.",
        'pl': "Nazwa hosta lub adres IP urządzenia Stiebel Eltron ISG.",
        'cs': "Název hostitele nebo IP adresa vašeho zařízení Stiebel Eltron ISG.",
        'hu': "A Stiebel Eltron ISG eszköz hosztneve vagy IP-címe.",
        'fi': "Stiebel Eltron ISG -laitteen isäntänimi tai IP-osoite.",
        'da': "Værtsnavnet eller IP-adressen på din Stiebel Eltron ISG-enhed.",
    }
    
    return {
        "config": {
            "step": {
                "user": {
                    "data": {
                        "host": "Host"
                    },
                    "data_description": {
                        "host": host_descriptions.get(lang_code, host_descriptions['en'])
                    }
                }
            },
            "error": {
                "cannot_connect": "[%key:common::config_flow::error::cannot_connect%]",
                "unknown": "[%key:common::config_flow::error::unknown%]"
            },
            "abort": {
                "already_configured": "[%key:common::config_flow::abort::already_configured_device%]",
                "cannot_connect": "[%key:common::config_flow::error::cannot_connect%]",
                "unknown": "[%key:common::config_flow::error::unknown%]"
            }
        },
        "title": "Stiebel Eltron ISG",
        "entity": {
            "sensor": {
                key: {"name": name}
                for key, name in entity_names.items()
                if key not in ['start_portal_ok', 'start_system_ok']
            },
            "binary_sensor": {
                "start_portal_ok": {"name": entity_names.get('start_portal_ok', 'Portal Connected')},
                "start_system_ok": {"name": entity_names.get('start_system_ok', 'System OK')}
            }
        }
    }


def main():
    """Generate all translation JSON files from testdata."""
    # Get paths
    root_dir = Path(__file__).parent.parent
    testdata_dir = root_dir / 'scripts' / 'testdata'
    translations_dir = root_dir / 'custom_components' / 'stiebel_eltron_http' / 'translations'
    translations_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("EXTRACTING ENTITY TRANSLATIONS FROM TESTDATA")
    print("=" * 80)
    print()
    
    # Build complete mapping including special cases
    # CANONICAL_TO_CONST has the main mappings
    canonical_to_const_expanded = dict(CANONICAL_TO_CONST)
    
    # Add special mappings that appear in scraper.py
    canonical_to_const_expanded[CanonicalKey.ACTUAL_TEMPERATURE_1] = ROOM_TEMPERATURE_KEY
    canonical_to_const_expanded[CanonicalKey.RELATIVE_HUMIDITY_1] = ROOM_HUMIDITY_KEY
    canonical_to_const_expanded[CanonicalKey.ACTUAL_TEMPERATURE] = DHW_TEMPERATURE_KEY
    
    # Also add consumed energy mappings
    canonical_to_const_expanded.update(ENERGY_CONSUMED_MAP)
    
    # Get all unique const keys we need to translate
    const_keys = set(canonical_to_const_expanded.values())
    
    for lang_code, lang_name in LANGUAGES.items():
        print(f"Processing {lang_name} ({lang_code})...")
        
        # Collect all fields from all testdata files for this language
        all_fields = set()
        testdata_files = list(testdata_dir.glob(f"*_{lang_code}.html"))
        
        for html_file in testdata_files:
            fields = extract_fields_from_html(html_file)
            all_fields.update(fields)
        
        print(f"  Found {len(all_fields)} unique fields in testdata")
        
        # Map const keys to translations
        entity_names = {}
        found_count = 0
        
        for const_key in const_keys:
            translation = find_translation_for_const(const_key, all_fields, lang_code, canonical_to_const_expanded)
            if translation:
                entity_names[const_key] = translation
                found_count += 1
        
        # Add special handling for binary sensors (Portal/System status)
        # These don't map through CANONICAL_TO_CONST but appear in start page
        if lang_code == 'de':
            entity_names['start_portal_ok'] = 'Portal verbunden'
            entity_names['start_system_ok'] = 'System OK'
        elif lang_code == 'en':
            entity_names['start_portal_ok'] = 'Portal Connected'
            entity_names['start_system_ok'] = 'System OK'
        else:
            # Use English as fallback
            entity_names['start_portal_ok'] = 'Portal Connected'
            entity_names['start_system_ok'] = 'System OK'
        
        print(f"  Matched {found_count}/{len(const_keys)} const keys to translations")
        
        # Create the translation structure
        translation = create_translation_structure(lang_code, entity_names)
        
        # Sort sensors alphabetically before writing
        from collections import OrderedDict
        if 'entity' in translation and 'sensor' in translation['entity']:
            sensors = translation['entity']['sensor']
            translation['entity']['sensor'] = OrderedDict(sorted(sensors.items()))
        
        if 'entity' in translation and 'binary_sensor' in translation['entity']:
            binary_sensors = translation['entity']['binary_sensor']
            translation['entity']['binary_sensor'] = OrderedDict(sorted(binary_sensors.items()))
        
        # Write to file
        output_file = translations_dir / f"{lang_code}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translation, f, indent=4, ensure_ascii=False)
            f.write('\n')  # Add trailing newline
        
        sensor_count = len(translation['entity']['sensor'])
        binary_sensor_count = len(translation['entity']['binary_sensor'])
        print(f"  ✓ Created {lang_code}.json (sorted)")
        print(f"    Sensors: {sensor_count}, Binary Sensors: {binary_sensor_count}")
        print()
    
    print("=" * 80)
    print(f"SUMMARY: Generated {len(LANGUAGES)} translation files from testdata")
    print("=" * 80)


if __name__ == '__main__':
    main()
