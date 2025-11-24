#!/usr/bin/env python3
"""Analyze structure of a new ISG page.

Usage:
    python scripts/samples/analyze_page_structure.py scripts/testdata/s_1_9_de.html

This script examines the HTML structure of an ISG page and shows:
- Number of sections
- Section names
- Field positions and names
- Field values
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup


def analyze_structure(html_file: Path):
    """Analyze and display the structure of an ISG HTML page."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    sections = soup.find_all('table', class_='info')

    print(f"Found {len(sections)} sections in {html_file.name}\n")

    for section_idx, section in enumerate(sections):
        header = section.find('th')
        section_name = header.get_text(strip=True) if header else "No header"
        print(f"Section {section_idx}: '{section_name}'")
        
        rows = section.find_all('tr')[1:]  # Skip header row
        for field_idx, row in enumerate(rows[:12]):  # Show first 12 fields
            cells = row.find_all('td')
            if len(cells) >= 2:
                field_name = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                print(f"  [{field_idx}] {field_name} = {value}")
        
        if len(rows) > 12:
            print(f"  ... ({len(rows)} total fields)")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_page_structure.py <html_file>")
        print("Example: python analyze_page_structure.py scripts/testdata/s_1_9_de.html")
        sys.exit(1)
    
    html_file = Path(sys.argv[1])
    if not html_file.exists():
        print(f"Error: File not found: {html_file}")
        sys.exit(1)
    
    analyze_structure(html_file)
