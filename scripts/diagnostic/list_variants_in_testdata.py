"""List all variants that are in test data and show which language they belong to."""

from pathlib import Path
from bs4 import BeautifulSoup
import re

# Extract all variants from mapping.py
mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
content = mapping_file.read_text(encoding='utf-8')

variant_pattern = r'"(.+?)",\s*#\s*variant'
variants = set(re.findall(variant_pattern, content))

# Extract fields by language
LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]
testdata_dir = Path("scripts/testdata")

fields_by_lang = {}
for lang in LANGUAGES:
    fields_by_lang[lang] = set()
    for page in ["s_1_0", "s_1_1", "s_2_7"]:
        file_path = testdata_dir / f"{page}_{lang}.html"
        if file_path.exists():
            soup = BeautifulSoup(file_path.read_text(encoding='utf-8'), 'html.parser')
            for row in soup.find_all('tr'):
                key_cell = row.find('td', class_='key')
                if key_cell:
                    field_name = key_cell.get_text(strip=True)
                    if field_name:
                        fields_by_lang[lang].add(field_name)

# Find variants that are in test data
variants_with_langs = []
for variant in sorted(variants):
    langs = [lang for lang in LANGUAGES if variant in fields_by_lang[lang]]
    if langs:
        variants_with_langs.append((variant, langs))

print(f"Found {len(variants_with_langs)} variants that are in test data:\n")
for variant, langs in variants_with_langs:
    lang_str = ", ".join(langs)
    print(f'"{variant}",  # {lang_str}')
