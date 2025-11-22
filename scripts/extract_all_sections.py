"""Extract all exact field names and sections from test data organized by language."""
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict

# Collect all unique strings by type
fields_by_lang = defaultdict(set)
sections_by_lang = defaultdict(set)

for html_file in sorted(Path('scripts/testdata').glob('s_*.html')):
    if html_file.stem.startswith('_'):
        continue
    
    lang = html_file.stem.split('_')[-1]
    soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
    
    # Get all table headers (section names)
    for th in soup.find_all('th'):
        text = th.get_text(strip=True)
        if text and len(text) > 2:
            sections_by_lang[lang].add(text)
    
    # Get all field names from rows
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            field_name = cells[0].get_text(strip=True)
            if field_name and len(field_name) > 2:
                fields_by_lang[lang].add(field_name)

# Print sections organized by language
print("SECTION HEADERS BY LANGUAGE:")
print("="*80)
for lang in ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']:
    if lang in sections_by_lang:
        print(f"\n{lang.upper()}:")
        for section in sorted(sections_by_lang[lang]):
            print(f"  {section}")

# Find sections that appear in all languages (likely section headers we need)
all_sections = {}
for lang in ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']:
    for section in sections_by_lang.get(lang, []):
        if section not in all_sections:
            all_sections[section] = []
        all_sections[section].append(lang)

print("\n" + "="*80)
print("SECTIONS WITH 12-LANGUAGE COVERAGE (likely canonical sections):")
print("="*80)
for section, langs in sorted(all_sections.items(), key=lambda x: len(x[1]), reverse=True):
    if len(langs) == 12:
        print(f"{section:50} ALL 12 LANGS")
