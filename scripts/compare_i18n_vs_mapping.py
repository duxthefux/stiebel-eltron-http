"""Compare i18n package against original mapping.py.

This script validates that the i18n package provides the same translations
as the original mapping.py for all testdata fields.
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http import mapping
from custom_components.stiebel_eltron_http import i18n

def main():
    print("=" * 80)
    print("COMPARING i18n PACKAGE vs mapping.py")
    print("=" * 80)
    print()
    
    # Get all keys from both
    mapping_keys = set(mapping.HEADER_ALIASES.keys())
    i18n_keys = set(i18n.HEADER_ALIASES.keys())
    
    print(f"Keys in mapping.py:     {len(mapping_keys)}")
    print(f"Keys in i18n package:   {len(i18n_keys)}")
    print()
    
    # Count total translations
    mapping_total = sum(len(v) for v in mapping.HEADER_ALIASES.values())
    i18n_total = sum(len(v) for v in i18n.HEADER_ALIASES.values())
    
    print(f"Total translations in mapping.py:   {mapping_total}")
    print(f"Total translations in i18n package: {i18n_total}")
    print()
    
    # Check for missing or extra keys
    missing_keys = mapping_keys - i18n_keys
    extra_keys = i18n_keys - mapping_keys
    
    if missing_keys:
        print(f"⚠️  MISSING KEYS in i18n ({len(missing_keys)}):")
        for key in sorted(missing_keys):
            print(f"   - {key}")
        print()
    
    if extra_keys:
        print(f"⚠️  EXTRA KEYS in i18n ({len(extra_keys)}):")
        for key in sorted(extra_keys):
            print(f"   - {key}")
        print()
    
    # For common keys, check translation coverage
    common_keys = mapping_keys & i18n_keys
    
    missing_translations = {}
    extra_translations = {}
    
    for key in sorted(common_keys):
        mapping_trans = set(mapping.HEADER_ALIASES[key])
        i18n_trans = set(i18n.HEADER_ALIASES[key])
        
        missing = mapping_trans - i18n_trans
        extra = i18n_trans - mapping_trans
        
        if missing:
            missing_translations[key] = missing
        
        if extra:
            extra_translations[key] = extra
    
    if missing_translations:
        print(f"⚠️  MISSING TRANSLATIONS (fields in mapping.py but not in i18n):")
        print(f"   {len(missing_translations)} keys affected")
        print()
        for key in sorted(missing_translations.keys()):
            print(f"   {key}:")
            for trans in sorted(missing_translations[key]):
                print(f"      - {trans}")
        print()
    
    if extra_translations:
        print(f"⚠️  EXTRA TRANSLATIONS (fields in i18n but not in mapping.py):")
        print(f"   {len(extra_translations)} keys affected")
        print()
        for key in sorted(extra_translations.keys()):
            print(f"   {key}:")
            for trans in sorted(extra_translations[key]):
                print(f"      - {trans}")
        print()
    
    # Final verdict
    print("=" * 80)
    if not missing_keys and not extra_keys and not missing_translations and not extra_translations:
        print("✅ PERFECT MATCH - i18n package matches mapping.py exactly!")
    elif not missing_keys and not missing_translations:
        print("✅ COMPLETE COVERAGE - All mapping.py translations present in i18n")
        print("   (i18n has some extra translations not in mapping.py)")
    else:
        print("⚠️  DIFFERENCES FOUND - See details above")
    print("=" * 80)

if __name__ == "__main__":
    main()
