#!/usr/bin/env python3
"""Extract section names from ISG page for all languages.

Usage:
    python scripts/samples/extract_section_names.py s_1_9

This script extracts section names for all languages, which are needed for
the i18n translation files (used for parsing).

Example output:
    "en": {
        "section_0": "Section Name 1",
        "section_1": "Section Name 2"
    }

Section names are indexed starting from 0.
"""

import json
import sys
from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path(__file__).parent.parent / "testdata"
LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']


def extract_section_names(html_file: Path) -> dict[str, str]:
    """Extract section names indexed by position."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.find_all('table', class_='info')
    
    section_names = {}
    
    for idx, section in enumerate(sections):
        # Try multiple patterns for section headers
        section_name_tag = None
        
        # Pattern 1: <tr class="head"><td class="title">
        section_header = section.find('tr', class_='head')
        if section_header:
            section_name_tag = section_header.find('td', class_='title')
        
        # Pattern 2: <tr><th> (first row with th)
        if not section_name_tag:
            section_name_tag = section.find('th')
        
        if section_name_tag:
            section_name = section_name_tag.get_text(strip=True)
            section_names[f"section_{idx}"] = section_name
    
    return section_names


def extract_all_languages(page_name: str):
    """Extract section names for all languages."""
    all_sections = {}
    
    print(f"Extracting section names for {page_name}\n")
    
    for lang in LANGUAGES:
        html_file = TESTDATA_DIR / f"{page_name}_{lang}.html"
        
        if not html_file.exists():
            print(f"{lang}: Missing file (skip)")
            continue
        
        sections = extract_section_names(html_file)
        all_sections[lang] = sections
        
        print(f"{lang}: {len(sections)} sections")
        for key, name in sections.items():
            print(f"  {key}: {name}")
    
    # Save to file FIRST (before printing JSON which might fail on Windows)
    output_file = Path(__file__).parent.parent / f"extracted_{page_name}_sections.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_sections, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_file}")
    print("\n" + "=" * 60)
    print("Open the file to view the JSON output (for i18n files)")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_section_names.py <page_name>")
        print("Example: python extract_section_names.py s_1_9")
        sys.exit(1)
    
    page_name = sys.argv[1]
    extract_all_languages(page_name)
