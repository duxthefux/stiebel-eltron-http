"""Convert all language files to use dynamic JSON loading like de.py."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.mapping import CanonicalKey
from custom_components.stiebel_eltron_http.i18n.json_loader import load_translations_from_json

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


def extract_parsing_translations(lang_code: str) -> dict:
    """Extract PARSING_TRANSLATIONS by comparing existing file with JSON-loaded."""
    # Import the existing language module
    module_name = f'custom_components.stiebel_eltron_http.i18n.{lang_code}'
    if module_name in sys.modules:
        del sys.modules[module_name]
    
    lang_module = __import__(module_name, fromlist=['TRANSLATIONS'])
    existing_translations = lang_module.TRANSLATIONS
    
    # Load what would come from JSON
    json_translations = load_translations_from_json(lang_code, None)
    
    # Find keys that are NOT in JSON (these are parsing-specific)
    parsing_keys = set(existing_translations.keys()) - set(json_translations.keys())
    
    parsing_translations = {}
    for key in sorted(parsing_keys, key=lambda k: k.value):
        parsing_translations[key] = existing_translations[key]
    
    return parsing_translations


def generate_language_file(lang_code: str, lang_name: str) -> str:
    """Generate the new language file content."""
    print(f"Processing {lang_name} ({lang_code})...")
    
    # Extract parsing translations
    parsing_translations = extract_parsing_translations(lang_code)
    
    lines = [
        f'""""{lang_name} ({lang_code}) translations.',
        '',
        'Combines entity names from translations/{lang_code}.json with parsing-specific strings.',
        'This ensures both user-facing entity names and ISG web interface field names are recognized.',
        '"""',
        '',
        'from .canonical_keys import CanonicalKey',
        'from .json_loader import load_translations_from_json',
        '',
        '',
    ]
    
    if parsing_translations:
        lines.extend([
            '# Parsing-specific translations for HTML scraping',
            '# Section headings and field variations needed for parsing but not mapped to sensors',
            'PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {',
        ])
        
        for canonical_key, values in parsing_translations.items():
            lines.append(f'    CanonicalKey.{canonical_key.name}: [')
            for value in values:
                # Escape quotes and backslashes
                escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
                lines.append(f'        "{escaped_value}",')
            lines.append('    ],')
        
        lines.extend([
            '}',
            '',
            f'# Load from JSON and merge with parsing translations',
            f"TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('{lang_code}', PARSING_TRANSLATIONS)",
        ])
    else:
        lines.extend([
            '# No parsing-specific translations needed for this language',
            '# All translations loaded from JSON',
            f"TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('{lang_code}')",
        ])
    
    print(f"  ✓ {len(parsing_translations)} parsing translations")
    
    return '\n'.join(lines) + '\n'


def main():
    """Convert all language files."""
    i18n_dir = Path(__file__).parent.parent / 'custom_components' / 'stiebel_eltron_http' / 'i18n'
    
    print("=" * 80)
    print("CONVERTING LANGUAGE FILES TO DYNAMIC JSON LOADING")
    print("=" * 80)
    print()
    
    # Skip de.py as it's already converted
    for lang_code, lang_name in LANGUAGES.items():
        if lang_code == 'de':
            print(f"Skipping {lang_name} ({lang_code}) - already converted")
            continue
        
        try:
            content = generate_language_file(lang_code, lang_name)
            
            output_file = i18n_dir / f"{lang_code}.py"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"  ✓ Written to {lang_code}.py")
            print()
        except Exception as e:
            print(f"  ✗ Error: {e}")
            print()
    
    print("=" * 80)
    print("CONVERSION COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
