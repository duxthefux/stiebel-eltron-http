"""Validation script to compare i18n translations against original mapping.py.

This script helps ensure that:
1. All German translations from mapping.py are captured in i18n/de.py
2. No incorrect translations are included
3. We can safely switch to the i18n structure later
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.mapping import (
    HEADER_ALIASES as ORIGINAL_ALIASES,
    CanonicalKey,
)
from custom_components.stiebel_eltron_http.i18n import de


def is_german(text):
    """Check if text is likely German."""
    # German-specific characters
    german_chars = ['Ä', 'Ö', 'Ü', 'ß', 'ä', 'ö', 'ü']
    
    # Check for special characters
    if any(char in text for char in german_chars):
        return True
    
    # German-specific words
    german_words = [
        'RAUM', 'TEMPERATUR', 'HEIZUNG', 'PROZESS', 'DATEN', 'WARMWASSER',
        'MENGE', 'WÄRME', 'STROM', 'VERBRAUCH', 'LEISTUNG', 'EFFIZIENZ',
        'BETRIEBSART', 'GESAMT', 'TAG', 'SUMME', 'IST', 'SOLL', 'RÜCKLAUF',
        'VORLAUF', 'FROSTSCHUTZ', 'AUSSEN', 'VERDICHTER', 'HEISSGAS',
        'VERFLÜSSIGER', 'ÖLSUMPF', 'DRUCK', 'NIEDER', 'HOCH', 'WASSER',
        'SPANNUNG', 'DREHZAHL', 'LÜFTER', 'VERDAMPFER', 'AUFNAHME', 'FEUCHTE'
    ]
    
    text_upper = text.upper()
    return any(word in text_upper for word in german_words)


def extract_german_from_mapping():
    """Extract all German translations from original mapping.py."""
    german_translations = {}
    
    for key, translations in ORIGINAL_ALIASES.items():
        german_values = [t for t in translations if is_german(t)]
        if german_values:
            german_translations[key] = german_values
    
    return german_translations


def compare_translations():
    """Compare i18n/de.py against mapping.py German translations."""
    print("=" * 80)
    print("VALIDATION: Comparing i18n/de.py against mapping.py")
    print("=" * 80)
    print()
    
    # Extract German from mapping.py
    mapping_german = extract_german_from_mapping()
    i18n_german = de.TRANSLATIONS
    
    # Find keys in mapping but not in i18n
    missing_keys = set(mapping_german.keys()) - set(i18n_german.keys())
    if missing_keys:
        print(f"⚠️  MISSING KEYS in i18n/de.py ({len(missing_keys)}):")
        for key in sorted(missing_keys):
            print(f"   - {key}: {mapping_german[key]}")
        print()
    else:
        print("✅ All German keys from mapping.py are in i18n/de.py")
        print()
    
    # Find keys in i18n but not in mapping
    extra_keys = set(i18n_german.keys()) - set(mapping_german.keys())
    if extra_keys:
        print(f"⚠️  EXTRA KEYS in i18n/de.py ({len(extra_keys)}):")
        for key in sorted(extra_keys):
            print(f"   - {key}: {i18n_german[key]}")
        print()
    else:
        print("✅ No extra keys in i18n/de.py")
        print()
    
    # Compare translations for common keys
    common_keys = set(mapping_german.keys()) & set(i18n_german.keys())
    
    missing_translations = {}
    extra_translations = {}
    
    for key in common_keys:
        mapping_set = set(mapping_german[key])
        i18n_set = set(i18n_german[key])
        
        missing = mapping_set - i18n_set
        if missing:
            missing_translations[key] = list(missing)
        
        extra = i18n_set - mapping_set
        if extra:
            extra_translations[key] = list(extra)
    
    if missing_translations:
        print(f"⚠️  MISSING TRANSLATIONS in i18n/de.py:")
        for key, translations in sorted(missing_translations.items()):
            print(f"   {key}:")
            for t in translations:
                print(f"      - {t}")
        print()
    else:
        print("✅ All German translations from mapping.py are in i18n/de.py")
        print()
    
    if extra_translations:
        print(f"⚠️  EXTRA TRANSLATIONS in i18n/de.py (possibly incorrect):")
        for key, translations in sorted(extra_translations.items()):
            print(f"   {key}:")
            for t in translations:
                print(f"      - {t}")
        print()
    else:
        print("✅ No extra translations in i18n/de.py")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY:")
    print(f"  Keys in mapping.py (German): {len(mapping_german)}")
    print(f"  Keys in i18n/de.py: {len(i18n_german)}")
    print(f"  Total German translations in mapping.py: {sum(len(v) for v in mapping_german.values())}")
    print(f"  Total translations in i18n/de.py: {sum(len(v) for v in i18n_german.values())}")
    
    if not missing_keys and not extra_keys and not missing_translations and not extra_translations:
        print("\n✅ PERFECT MATCH! i18n/de.py is identical to German translations in mapping.py")
        return 0
    else:
        print("\n⚠️  DIFFERENCES FOUND - review above")
        return 1


if __name__ == '__main__':
    sys.exit(compare_translations())
