#!/usr/bin/env python3
"""Verify consistent structure across all language versions of an ISG page.

Usage:
    python scripts/samples/verify_structure_consistency.py s_1_9

This script checks that all language versions of a page have the same structure:
- Same number of sections
- Same number of fields in each section

This is important because the structure-based extraction assumes all languages
have identical structure (same device, same firmware).
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path(__file__).parent.parent / "testdata"
LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']


def get_structure(html_file: Path) -> list[int]:
    """Get page structure as list of field counts per section."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.find_all('table', class_='info')
    
    return [len(section.find_all('tr')[1:]) for section in sections]


def verify_consistency(page_name: str):
    """Verify all language versions have identical structure."""
    structures = {}
    
    print(f"Verifying structure consistency for {page_name} across all languages\n")
    
    for lang in LANGUAGES:
        html_file = TESTDATA_DIR / f"{page_name}_{lang}.html"
        
        if not html_file.exists():
            print(f"{lang.upper()}: ⚠️  Missing file")
            continue
        
        structure = get_structure(html_file)
        structures[lang] = structure
        
        print(f"{lang.upper()}: {len(structure)} sections")
        for idx, field_count in enumerate(structure):
            print(f"  Section {idx}: {field_count} fields")
    
    # Check if all structures are identical
    print("\n" + "=" * 60)
    if len(set(str(s) for s in structures.values())) == 1:
        print("SUCCESS: All languages have IDENTICAL structure!")
    else:
        print("ERROR: Languages have DIFFERENT structures!")
        print("\nDifferences found:")
        reference = structures[LANGUAGES[0]]
        for lang, structure in structures.items():
            if structure != reference:
                print(f"  {lang}: {structure} != {reference}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_structure_consistency.py <page_name>")
        print("Example: python verify_structure_consistency.py s_1_9")
        sys.exit(1)
    
    page_name = sys.argv[1]
    verify_consistency(page_name)
