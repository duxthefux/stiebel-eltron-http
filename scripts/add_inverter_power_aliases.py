#!/usr/bin/env python3
"""Add INVERTER_POWER aliases to all language i18n files."""

from pathlib import Path

I18N_DIR = Path("custom_components/stiebel_eltron_http/i18n")

# These are the actual field names from test data
# Some devices still show "INVERTER POWER" in English, others have localized versions
INVERTER_POWER_FIELDS = {
    'cs': 'INVERTER POWER',  # Czech - still English in test data
    'da': 'INVERTER POWER',  # Danish - has both localized and English versions  
    'es': 'INVERTER POWER',  # Spanish - still English in test data
    'fi': 'INVERTER POWER',  # Finnish - still English in test data
    'fr': 'PUISS INVERTER',  # French - localized version
    'hu': 'INVERTER POWER',  # Hungarian - has both, using English for consistency
    'it': 'INVERTER POWER',  # Italian - has both, using English for consistency
    'nl': 'INVERTER POWER',  # Dutch - has both, using English for consistency
    'pl': 'INVERTER POWER',  # Polish - still English in test data
    'sv': 'INVERTER POWER',  # Swedish - still English in test data
}

# Update i18n files
for lang, field_name in INVERTER_POWER_FIELDS.items():
    file_path = I18N_DIR / f"{lang}.py"
    
    if not file_path.exists():
        print(f"⚠️  {lang}.py not found")
        continue
    
    content = file_path.read_text(encoding='utf-8')
    
    # Check if already has INVERTER_POWER
    if 'INVERTER_POWER' in content:
        print(f"✓ {lang}.py already has INVERTER_POWER")
        continue
    
    # Find the closing brace of PARSING_TRANSLATIONS
    marker = "}\n\n# Load from JSON"
    if marker not in content:
        print(f"⚠️  {lang}.py missing marker")
        continue
    
    # Add INVERTER_POWER before closing brace
    new_content = content.replace(
        marker,
        f'    CanonicalKey.INVERTER_POWER: [\n        "{field_name}",\n    ],\n{marker}'
    )
    
    file_path.write_text(new_content, encoding='utf-8')
    print(f"✓ Updated {lang}.py")

print("\nDone!")
