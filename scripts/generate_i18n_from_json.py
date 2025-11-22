"""Generate i18n Python files from translation JSON files.

This script reads the translation JSON files and generates corresponding
Python files in the i18n package, ensuring consistency between JSON and Python.
"""

import json
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.mapping import CANONICAL_TO_CONST, ENERGY_CONSUMED_MAP, CanonicalKey
from custom_components.stiebel_eltron_http.const import (
    ROOM_TEMPERATURE_KEY,
    ROOM_HUMIDITY_KEY,
    DHW_TEMPERATURE_KEY,
)

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


def build_reverse_mapping():
    """Build reverse mapping from const keys to canonical keys."""
    # Build complete mapping
    canonical_to_const_expanded = dict(CANONICAL_TO_CONST)
    canonical_to_const_expanded[CanonicalKey.ACTUAL_TEMPERATURE_1] = ROOM_TEMPERATURE_KEY
    canonical_to_const_expanded[CanonicalKey.RELATIVE_HUMIDITY_1] = ROOM_HUMIDITY_KEY
    canonical_to_const_expanded[CanonicalKey.ACTUAL_TEMPERATURE] = DHW_TEMPERATURE_KEY
    canonical_to_const_expanded.update(ENERGY_CONSUMED_MAP)
    
    # Reverse it: const_key -> list of canonical keys
    const_to_canonical = {}
    for canonical_key, const_key in canonical_to_const_expanded.items():
        if const_key not in const_to_canonical:
            const_to_canonical[const_key] = []
        const_to_canonical[const_key].append(canonical_key)
    
    return const_to_canonical


def generate_python_file(lang_code, lang_name, json_data, const_to_canonical):
    """Generate Python i18n file content from JSON translation data."""
    lines = [
        f'"""{lang_name} ({lang_code}) translations.',
        '',
        'Generated from translations JSON file.',
        'Contains field names as they appear in the ISG web interface.',
        '"""',
        '',
        'from .canonical_keys import CanonicalKey',
        '',
        '',
        'TRANSLATIONS: dict[CanonicalKey, list[str]] = {',
    ]
    
    # Get sensor translations from JSON
    sensors = json_data.get('entity', {}).get('sensor', {})
    
    # Build translations dict: canonical_key -> [translation]
    translations = {}
    
    for const_key, sensor_data in sensors.items():
        translation_text = sensor_data.get('name')
        if not translation_text:
            continue
        
        # Find canonical key(s) for this const key
        canonical_keys = const_to_canonical.get(const_key, [])
        
        for canonical_key in canonical_keys:
            if canonical_key not in translations:
                translations[canonical_key] = []
            if translation_text not in translations[canonical_key]:
                translations[canonical_key].append(translation_text)
    
    # Sort by canonical key name for consistent output
    for canonical_key in sorted(translations.keys(), key=lambda k: k.value):
        values = translations[canonical_key]
        lines.append(f'    CanonicalKey.{canonical_key.name}: [')
        for value in sorted(values):
            # Escape quotes and backslashes
            escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
            lines.append(f'        "{escaped_value}",')
        lines.append('    ],')
    
    lines.append('}')
    
    return '\n'.join(lines) + '\n', len(translations)


def main():
    """Generate i18n Python files from translation JSON files."""
    # Get paths
    root_dir = Path(__file__).parent.parent
    translations_dir = root_dir / 'custom_components' / 'stiebel_eltron_http' / 'translations'
    i18n_dir = root_dir / 'custom_components' / 'stiebel_eltron_http' / 'i18n'
    
    print("=" * 80)
    print("GENERATING I18N PYTHON FILES FROM TRANSLATION JSON")
    print("=" * 80)
    print()
    
    # Build reverse mapping
    const_to_canonical = build_reverse_mapping()
    
    total_translations = 0
    
    for lang_code, lang_name in LANGUAGES.items():
        print(f"Processing {lang_name} ({lang_code})...")
        
        # Read JSON file
        json_file = translations_dir / f"{lang_code}.json"
        if not json_file.exists():
            print(f"  ⚠ Skipping - {json_file.name} not found")
            continue
        
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Generate Python file
        python_content, num_keys = generate_python_file(lang_code, lang_name, json_data, const_to_canonical)
        
        # Write to i18n directory
        output_file = i18n_dir / f"{lang_code}.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(python_content)
        
        print(f"  ✓ Generated {lang_code}.py with {num_keys} canonical keys")
        total_translations += num_keys
    
    print()
    print("=" * 80)
    print(f"SUMMARY: Generated {len(LANGUAGES)} Python files with {total_translations} total keys")
    print("=" * 80)
    print()
    print("Note: Run extract_all_languages.py to also extract from testdata HTML files")
    print("      for complete coverage of all field variations.")


if __name__ == '__main__':
    main()
