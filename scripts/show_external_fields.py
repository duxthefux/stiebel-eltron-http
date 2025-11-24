#!/usr/bin/env python3
"""Show all fields in external heat source section."""

import sys
sys.path.insert(0, 'scripts')

from pathlib import Path
from map_translations_from_testdata import extract_fields_by_section, TESTDATA_DIR

LANGUAGES = ["cs", "da", "de", "en", "es", "fi", "fr", "hu", "it", "nl", "pl", "sv"]

print("External Heat Source Section Fields:")
print("=" * 80)

for lang in LANGUAGES:
    s_1_0 = TESTDATA_DIR / f"s_1_0_{lang}.html"
    if s_1_0.exists():
        sections = extract_fields_by_section(s_1_0)
        
        # Find external section
        external_fields = None
        for section_name, fields in sections.items():
            if any(kw in section_name.upper() for kw in ['EXTERN', 'EXTERNAL', 'EKSTERN', 'ESTERNO', 'EXTÉRIEUR', 'EXTERNI', 'ZEWN']):
                external_fields = fields
                print(f"\n{lang.upper()} - Section: {section_name}")
                for i, field in enumerate(fields[:6], 1):
                    print(f"  {i}. {field}")
                break
        
        if not external_fields:
            print(f"\n{lang.upper()}: NOT FOUND")

print("\n" + "=" * 80)
