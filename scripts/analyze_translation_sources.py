"""Analyze what's in PARSING_TRANSLATIONS vs loaded from JSON."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.i18n.de import PARSING_TRANSLATIONS
from custom_components.stiebel_eltron_http.i18n import de

print("=" * 80)
print("ANALYSIS: PARSING_TRANSLATIONS vs JSON-loaded translations")
print("=" * 80)
print()

print(f"Total translations in de.TRANSLATIONS: {len(de.TRANSLATIONS)}")
print(f"Manually defined in PARSING_TRANSLATIONS: {len(PARSING_TRANSLATIONS)}")
print()

print("PARSING_TRANSLATIONS (manually defined - NOT in JSON):")
print("-" * 80)
for key in sorted(PARSING_TRANSLATIONS.keys(), key=lambda x: x.value):
    values = PARSING_TRANSLATIONS[key]
    print(f"  {key.name:40} → {values}")
print()

json_only = set(de.TRANSLATIONS.keys()) - set(PARSING_TRANSLATIONS.keys())
print(f"Loaded from JSON (sensor entity names): {len(json_only)}")
print("-" * 80)
for key in sorted(json_only, key=lambda x: x.value):
    values = de.TRANSLATIONS[key]
    print(f"  {key.name:40} → {values}")
print()

print("SUMMARY:")
print("-" * 80)
print(f"✓ PARSING_TRANSLATIONS = Section headings and parsing-specific strings")
print(f"✓ JSON-loaded = User-facing sensor entity names")
print(f"✓ Combined total: {len(de.TRANSLATIONS)} canonical keys")
