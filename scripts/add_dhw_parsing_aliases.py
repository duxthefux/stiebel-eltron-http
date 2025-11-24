#!/usr/bin/env python3
"""Add ACTUAL_TEMPERATURE and SET_TEMPERATURE parsing aliases to all lang.py files."""

from pathlib import Path

I18N_DIR = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "i18n"

# Field names from extract_parsing_aliases.py output
ALIASES = {
    'da': {
        'ACTUAL_TEMPERATURE': 'AKTUEL TEMPERATUR',
        'SET_TEMPERATURE': 'NOM. TEMPERATUR',
    },
    'es': {
        'ACTUAL_TEMPERATURE': 'TEMPERATURA REAL',
        'SET_TEMPERATURE': 'TEMPERATURA DE REFERENCIA',
    },
    'fi': {
        'ACTUAL_TEMPERATURE': 'TOSILÄMPÖT',
        'SET_TEMPERATURE': 'OHJELÄMPÖTILA',
    },
    'fr': {
        'ACTUAL_TEMPERATURE': 'TEMPERATURE REELLE',
        'SET_TEMPERATURE': 'TEMPÉRATURE DE CONSIGNE',
    },
    'it': {
        'ACTUAL_TEMPERATURE': 'TEMP EFFETTIVA',
        'SET_TEMPERATURE': 'TEMPERATURA NOMINALE',
    },
    'nl': {
        'ACTUAL_TEMPERATURE': 'ACTUELE TEMPERATUUR',
        'SET_TEMPERATURE': 'NOMINALE TEMPERATUUR',
    },
    'pl': {
        'ACTUAL_TEMPERATURE': 'TEMP RZECZYWISTA',
        'SET_TEMPERATURE': 'TEMPERATURA ZADANA',
    },
    'sv': {
        'ACTUAL_TEMPERATURE': 'AKT TEMPERATUR',
        'SET_TEMPERATURE': 'BÖRTEMPERATUR',
    },
}

def update_lang_file(lang: str):
    """Add ACTUAL_TEMPERATURE and SET_TEMPERATURE to a lang.py file."""
    lang_file = I18N_DIR / f"{lang}.py"
    
    if not lang_file.exists():
        print(f"Skipping {lang}: file not found")
        return
    
    content = lang_file.read_text(encoding='utf-8')
    
    # Check if already has ACTUAL_TEMPERATURE
    if 'CanonicalKey.ACTUAL_TEMPERATURE:' in content:
        print(f"Skipping {lang}: already has ACTUAL_TEMPERATURE")
        return
    
    aliases = ALIASES.get(lang)
    if not aliases:
        print(f"Skipping {lang}: no aliases defined")
        return
    
    # Find the line with EXTERNAL_ACTUAL_TEMPERATURE
    lines = content.split('\n')
    insert_idx = None
    
    for i, line in enumerate(lines):
        if 'CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE:' in line:
            # Insert before this line
            insert_idx = i
            break
    
    if insert_idx is None:
        print(f"ERROR {lang}: Could not find insertion point")
        return
    
    # Build the new lines to insert
    new_lines = [
        f"    # DHW section uses plain field names without prefix",
        f"    CanonicalKey.ACTUAL_TEMPERATURE: [",
        f"        \"{aliases['ACTUAL_TEMPERATURE']}\",  # DHW section field (unprefixed)",
        f"    ],",
        f"    CanonicalKey.SET_TEMPERATURE: [",
        f"        \"{aliases['SET_TEMPERATURE']}\",  # DHW section field (unprefixed)",
        f"    ],",
        f"    # External section - same field names but in different section",
    ]
    
    # Insert the new lines
    lines = lines[:insert_idx] + new_lines + lines[insert_idx:]
    
    # Write back
    lang_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✓ Updated {lang}.py")

def main():
    for lang in ALIASES.keys():
        update_lang_file(lang)

if __name__ == '__main__':
    main()
