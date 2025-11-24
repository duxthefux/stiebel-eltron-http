#!/usr/bin/env python3
"""Check section name in Hungarian HTML."""
from bs4 import BeautifulSoup

html_file = "scripts/testdata/s_1_1_hu.html"

with open(html_file, 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
sections = soup.find_all('table', class_='info')

print(f"Found {len(sections)} sections\n")
for i, section in enumerate(sections):
    header = section.find('th')
    if header:
        section_name = header.get_text(strip=True)
        print(f"Section {i}: '{section_name}'")
    else:
        print(f"Section {i}: No header")
