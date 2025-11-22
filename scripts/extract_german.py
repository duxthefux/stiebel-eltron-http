"""Extract German translations from mapping.py to de.py."""

import re
from pathlib import Path

# German-specific characters and patterns
GERMAN_INDICATORS = ['Ä', 'Ö', 'Ü', 'ß', 'ä', 'ö', 'ü']
GERMAN_WORDS = [
    'RAUM', 'TEMPERATUR', 'HEIZUNG', 'PROZESS', 'DATEN', 'WARMWASSER',
    'MENGE', 'WÄRME', 'STROM', 'VERBRAUCH', 'LEISTUNG', 'EFFIZIENZ',
    'BETRIEBSART', 'GESAMT', 'TAG', 'SUMME', 'IST', 'SOLL', 'RÜCKLAUF',
    'VORLAUF', 'FROSTSCHUTZ', 'AUSSEN', 'VERDICHTER', 'HEISSGAS',
    'VERFLÜSSIGER', 'ÖLSUMPF', 'DRUCK', 'NIEDER', 'HOCH', 'WASSER',
    'SPANNUNG', 'DREHZAHL', 'LÜFTER', 'VERDAMPFER', 'AUFNAHME'
]

def is_german(text):
    """Check if text is likely German."""
    text_upper = text.upper()
    
    # Check for German-specific characters (strong indicator)
    for char in GERMAN_INDICATORS:
        if char in text:
            return True
    
    # Check for German words (must match whole words to avoid false positives)
    words_in_text = text_upper.replace('-', ' ').replace('.', ' ').split()
    for word in GERMAN_WORDS:
        if word in words_in_text or any(w.startswith(word) for w in words_in_text):
            # Make sure it's not also English
            english_indicators = ['TEMPERATURE', 'HEATING', 'PROCESS', 'DATA', 'CONSUMPTION', 'EFFICIENCY', 'OPERATION', 'MODE']
            if not any(eng in text_upper for eng in english_indicators):
                return True
    
    return False

def extract_german_translations():
    """Extract German translations from mapping.py."""
    mapping_path = Path(__file__).parent.parent / 'custom_components' / 'stiebel_eltron_http' / 'mapping.py'
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract HEADER_ALIASES dict
    match = re.search(r'HEADER_ALIASES:.*?= \{(.*?)\n\}', content, re.DOTALL)
    if not match:
        raise ValueError("Could not find HEADER_ALIASES")
    
    aliases_content = match.group(1)
    
    # Parse each CanonicalKey entry
    german_translations = {}
    key_pattern = r'CanonicalKey\.(\w+):\s*\[(.*?)\]'
    
    for key_match in re.finditer(key_pattern, aliases_content, re.DOTALL):
        canonical_key = key_match.group(1)
        values_str = key_match.group(2)
        
        # Extract German translations
        german_values = []
        value_pattern = r'"([^"]+)"'
        for value_match in re.finditer(value_pattern, values_str):
            translation = value_match.group(1)
            if is_german(translation):
                german_values.append(translation)
        
        if german_values:
            german_translations[canonical_key] = german_values
    
    return german_translations

def generate_de_file(translations):
    """Generate de.py file content."""
    lines = [
        '"""German (de) translations."""',
        '',
        'from .canonical_keys import CanonicalKey',
        '',
        '',
        '# German translations for canonical keys',
        'TRANSLATIONS: dict[CanonicalKey, list[str]] = {'
    ]
    
    for key in sorted(translations.keys()):
        values = translations[key]
        lines.append(f'    CanonicalKey.{key}: [')
        for value in values:
            lines.append(f'        "{value}",')
        lines.append('    ],')
    
    lines.append('}')
    lines.append('')
    
    return '\n'.join(lines)

if __name__ == '__main__':
    translations = extract_german_translations()
    print(f"Found {len(translations)} keys with German translations")
    print(f"Total German translations: {sum(len(v) for v in translations.values())}")
    print("\nSample keys:")
    for key in sorted(translations.keys())[:5]:
        print(f"  {key}: {len(translations[key])} translations")
    
    # Generate de.py content
    content = generate_de_file(translations)
    output_path = Path(__file__).parent.parent / 'custom_components' / 'stiebel_eltron_http' / 'i18n' / 'de.py'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nCreated {output_path}")
