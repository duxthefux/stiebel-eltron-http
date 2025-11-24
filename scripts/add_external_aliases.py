#!/usr/bin/env python3
"""Add external temperature aliases to all i18n language files."""

from pathlib import Path

# Based on show_external_fields.py output, these are the exact field names
EXTERNAL_ALIASES = {
    'cs': {
        'actual': 'SKUTECNA TEPLOTA',
        'set': 'POŽADOVANÁ TEPLOTA',
    },
    'da': {
        'actual': 'AKTUEL TEMPERATUR',
        'set': 'NOM. TEMPERATUR',
    },
    'en': {
        'actual': 'ACTUAL TEMPERATURE',
        'set': 'SET TEMPERATURE',
    },
    'es': {
        'actual': 'TEMPERATURA REAL',
        'set': 'TEMPERATURA DE REFERENCIA',
    },
    'fr': {
        'actual': 'TEMPERATURE REELLE',  # Note: without accent in HTML
        'set': 'TEMPÉRATURE DE CONSIGNE',
    },
    'nl': {
        'actual': 'ACTUELE TEMPERATUUR',
        'set': 'NOMINALE TEMPERATUUR',
    },
    'pl': {
        'actual': 'TEMP RZECZYWISTA',
        'set': 'TEMPERATURA ZADANA',
    },
    'sv': {
        'actual': 'AKT TEMPERATUR',
        'set': 'BÖRTEMPERATUR',
    },
}

I18N_DIR = Path("custom_components/stiebel_eltron_http/i18n")

for lang, aliases in EXTERNAL_ALIASES.items():
    i18n_file = I18N_DIR / f"{lang}.py"
    
    if not i18n_file.exists():
        print(f"Skipping {lang}: file not found")
        continue
    
    content = i18n_file.read_text(encoding='utf-8')
    
    # Check if already has EXTERNAL_ACTUAL_TEMPERATURE
    if 'EXTERNAL_ACTUAL_TEMPERATURE' in content:
        print(f"Skipping {lang}: already has EXTERNAL_ACTUAL_TEMPERATURE")
        continue
    
    # Find the end of PARSING_TRANSLATIONS dict (before the closing brace)
    insert_marker = '}\n\n# Load from JSON'
    
    insertion = f'''    CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE: [
        "{aliases['actual']}",
    ],
    CanonicalKey.EXTERNAL_SET_TEMPERATURE: [
        "{aliases['set']}",
    ],
}}

# Load from JSON'''
    
    new_content = content.replace(insert_marker, insertion)
    
    if new_content != content:
        i18n_file.write_text(new_content, encoding='utf-8')
        print(f"✓ Updated {lang}.py")
    else:
        print(f"✗ Could not find insertion point in {lang}.py")

print("\nDone!")
