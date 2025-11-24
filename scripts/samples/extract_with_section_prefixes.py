#!/usr/bin/env python3
"""Extract field names WITH section prefixes from ISG page for all languages.

Usage:
    python scripts/samples/extract_with_section_prefixes.py s_1_9

This script extracts field names with section prefixes ready for JSON translation files.
This is the RECOMMENDED approach because it maintains section context.

Example output:
    "en": {
        "Section Name Field 1": "Field 1",
        "Section Name Field 2": "Field 2"
    }

The section prefix is automatically prepended to each field name to provide context.
"""

import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path(__file__).parent.parent / "testdata"
LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']


def extract_translations_with_prefixes(html_file: Path) -> dict[str, str]:
    """Extract field names with section prefixes from HTML."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.find_all('table', class_='info')
    
    translations = {}
    
    for section in sections:
        # Get section name - try multiple patterns
        section_name_tag = None
        
        # Pattern 1: <tr class="head"><td class="title">
        section_header = section.find('tr', class_='head')
        if section_header:
            section_name_tag = section_header.find('td', class_='title')
        
        # Pattern 2: <tr><th> (first row with th)
        if not section_name_tag:
            section_name_tag = section.find('th')
        
        if not section_name_tag:
            continue
        
        section_name = section_name_tag.get_text(strip=True)
        
        # Get all field rows (skip header row)
        all_rows = section.find_all('tr')
        field_rows = [row for row in all_rows if not row.find('th')]  # Skip rows with <th>
        
        for row in field_rows:
            # Try both 'name' and 'key' classes (different ISG versions use different classes)
            name_tag = row.find('td', class_='name')
            if not name_tag:
                name_tag = row.find('td', class_='key')
            
            if name_tag:
                field_name = name_tag.get_text(strip=True)
                
                # Create prefixed key: "Section Name Field Name"
                prefixed_key = f"{section_name} {field_name}"
                translations[prefixed_key] = field_name
    
    return translations


def extract_all_languages(page_name: str):
    """Extract translations for all languages with section prefixes."""
    all_translations = {}
    
    print(f"Extracting translations with section prefixes for {page_name}\n")
    
    for lang in LANGUAGES:
        html_file = TESTDATA_DIR / f"{page_name}_{lang}.html"
        
        if not html_file.exists():
            print(f"{lang}: Missing file (skip)")
            continue
        
        translations = extract_translations_with_prefixes(html_file)
        all_translations[lang] = translations
        
        print(f"{lang}: {len(translations)} fields extracted")
    
    # Save to file FIRST (before trying to print which might fail on Windows)
    output_file = Path(__file__).parent.parent / f"extracted_{page_name}_translations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_translations, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_file}")
    print("\n" + "=" * 60)
    print("Open the file to view the JSON output (ready to paste into translation files)")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_with_section_prefixes.py <page_name>")
        print("Example: python extract_with_section_prefixes.py s_1_9")
        sys.exit(1)
    
    page_name = sys.argv[1]
    extract_all_languages(page_name)
