#!/usr/bin/env python3
"""Extract field names using the same parsing structure as scraper.py."""

from pathlib import Path
from bs4 import BeautifulSoup
import sys
import os

# Add parent directory to path to import from custom_components
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.i18n.canonical_keys import CanonicalKey
from custom_components.stiebel_eltron_http.i18n import get_aliases

TESTDATA_DIR = Path("scripts/testdata")
LANGUAGES = ["cs", "da", "de", "en", "es", "fi", "fr", "hu", "it", "nl", "pl", "sv"]

def extract_field_name_for_canonical_key(soup, canonical_key: CanonicalKey, section_context: CanonicalKey | None = None) -> str | None:
    """Extract the actual field name used for a canonical key in a given language.
    
    This mimics what parse_process_data_table does, but instead of extracting values,
    we extract the field name itself.
    """
    # Get all possible aliases for this canonical key
    aliases = get_aliases(canonical_key)
    if not aliases:
        return None
    
    # Find all tables
    tables = soup.find_all('table', class_='info')
    
    for table in tables:
        # Check if we're in the right section context
        if section_context:
            # Get section title from <th class="round-top">
            section_header = table.find('th', class_='round-top')
            if section_header:
                section_title = section_header.get_text(strip=True)
                # Check if this section matches our context
                section_aliases = get_aliases(section_context)
                if not any(alias.upper() in section_title.upper() for alias in section_aliases):
                    continue  # Not the right section
        
        # Look for field name in this table
        rows = table.find_all('tr')
        for row in rows:
            key_cell = row.find('td', class_='key')
            if key_cell:
                field_name = key_cell.get_text(strip=True)
                # Check if this field name matches any of the aliases
                for alias in aliases:
                    if alias.upper() == field_name.upper():
                        return field_name
    
    return None

def extract_external_fields(lang: str) -> dict[str, str]:
    """Extract all external heat source fields for a language."""
    file_path = TESTDATA_DIR / f"s_1_0_{lang}.html"
    
    if not file_path.exists():
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Extract field names for each canonical key in the external section
    external_keys = {
        'external_actual_temperature': CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE,
        'external_set_temperature': CanonicalKey.EXTERNAL_SET_TEMPERATURE,
        'dual_mode_temp_hzg': CanonicalKey.DUAL_MODE_TEMP_HZG,
        'dual_mode_temp_ww': CanonicalKey.DUAL_MODE_TEMP_WW,
        'lower_limit_hzg': CanonicalKey.LOWER_LIMIT_HZG,
        'lower_limit_ww': CanonicalKey.LOWER_LIMIT_WW,
    }
    
    mapping = {}
    for sensor_key, canonical_key in external_keys.items():
        field_name = extract_field_name_for_canonical_key(
            soup,
            canonical_key,
            section_context=CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION
        )
        if field_name:
            mapping[sensor_key] = field_name
    
    return mapping

print("Extracting external heat source field names using parsing structure:")
print("=" * 80)

for lang in LANGUAGES:
    print(f"\n{lang.upper()}:")
    mapping = extract_external_fields(lang)
    
    if mapping:
        for sensor_key, field_name in mapping.items():
            print(f"  {sensor_key}: {field_name}")
    else:
        print("  No external section found")

print("\n" + "=" * 80)
