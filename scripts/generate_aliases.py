#!/usr/bin/env python3
"""Generate HEADER_ALIASES code from manual translations."""

from manual_translations import MANUAL_TRANSLATIONS

print("="*80)
print("HEADER_ALIASES ENTRIES TO ADD TO mapping.py")
print("="*80)
print()

for field_name in sorted(MANUAL_TRANSLATIONS.keys()):
    translations = MANUAL_TRANSLATIONS[field_name]
    
    print(f"    CanonicalKey.{field_name}: [")
    
    # Order: de, en, fr, nl, it, sv, es, pl, cs, hu, fi, da
    for lang in ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']:
        if lang in translations:
            print(f'        "{translations[lang]}",')
    
    print("    ],")
    print()
