#!/usr/bin/env python3
"""Check what headers exist in different language files."""

from pathlib import Path
from bs4 import BeautifulSoup

testdata = Path("scripts/testdata")

for lang in ["de", "en", "fr", "it", "nl", "es"]:
    file_path = testdata / f"s_1_1_{lang}.html"
    if not file_path.exists():
        continue
    
    html = file_path.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"\n=== {lang.upper()} (s_1_1_{lang}.html) ===")
    
    # Find the page title/header
    main_title = soup.select_one('#sub_nav .left.main.sifr')
    if main_title:
        print(f"  Page title: {main_title.get_text().strip()}")
    
    # Find calibration sections (these have the labels)
    sections = soup.select('.calibration.round h3.title')
    print(f"  Sections ({len(sections)}):")
    for s in sections[:8]:
        text = s.get_text().strip()
        if text:
            print(f"    - {text}")
