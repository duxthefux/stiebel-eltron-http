#!/usr/bin/env python3
"""Collect all s_1_8 field names from all languages."""

from pathlib import Path
from bs4 import BeautifulSoup

LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

all_data = {}

for lang in LANGUAGES:
    html = BeautifulSoup(Path(f'scripts/testdata/s_1_8_{lang}.html').read_text(encoding='utf-8'), 'html.parser')
    fields = {}
    for table in html.find_all('table'):
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) >= 2:
                fname = tds[0].get_text(strip=True)
                fval = tds[1].get_text(strip=True)
                fields[fname] = fval
    all_data[lang] = fields

# Organize by pattern
patterns = {
    'heating_1_12m': {},
    'heating_1_24h': {},
    'heating_13_24m': {},
    'dhw_1_12m': {},
    'dhw_1_24h': {},
    'dhw_13_24m': {},
}

for lang, fields in all_data.items():
    for fname in fields.keys():
        fname_lower = fname.lower()
        # Heating patterns
        if ('heiz' in fname_lower or 'heat' in fname_lower or 'verwarmen' in fname_lower or 
            'risc' in fname_lower or 'uppvärm' in fname_lower or 'calef' in fname_lower or
            'ogrz' in fname_lower or 'topeni' in fname_lower or 'fût' in fname_lower or
            'chauff' in fname_lower or 'lämm' in fname_lower or 'varme' in fname_lower):
            if '1-12' in fname or '1–12' in fname:
                patterns['heating_1_12m'][lang] = fname
            elif '1-24' in fname or '1–24' in fname:
                patterns['heating_1_24h'][lang] = fname
            elif '13-24' in fname or '13–24' in fname:
                patterns['heating_13_24m'][lang] = fname
        # DHW patterns
        elif ('warmwasser' in fname_lower or 'dhw' in fname_lower or 'warm water' in fname_lower or
              'acqua calda' in fname_lower or 'varmvatten' in fname_lower or 'agua' in fname_lower or
              'ciepla woda' in fname_lower or 'tepla voda' in fname_lower or 'melegvíz' in fname_lower or
              'melegviz' in fname_lower or 'lämminv' in fname_lower or 'lamminv' in fname_lower or
              'varmt vand' in fname_lower or 'eau chaude' in fname_lower or 'ecs' in fname_lower):
            if '1-12' in fname or '1–12' in fname:
                patterns['dhw_1_12m'][lang] = fname
            elif '1-24' in fname or '1–24' in fname:
                patterns['dhw_1_24h'][lang] = fname
            elif '13-24' in fname or '13–24' in fname:
                patterns['dhw_13_24m'][lang] = fname

# Print results
for pattern_name, lang_map in patterns.items():
    print(f"\n{pattern_name.upper()}:")
    for lang in LANGUAGES:
        if lang in lang_map:
            print(f"  {lang}: {lang_map[lang]}")
        else:
            print(f"  {lang}: ❌ MISSING")
