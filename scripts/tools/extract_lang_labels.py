#!/usr/bin/env python3
"""Extract labels from ISG test data for a specific language."""

import sys
from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path(__file__).parent / "testdata"

def extract_labels(lang_code: str):
    """Extract labels from test file for given language."""
    file_path = TESTDATA_DIR / f"s_1_1_{lang_code}.html"
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    labels = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                if label:
                    labels.append(label)
    
    print(f"{lang_code.upper()} labels from s_1_1_{lang_code}.html:")
    for label in labels:
        print(f"  {label}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_lang_labels.py <lang_code>")
        print("Example: python extract_lang_labels.py it")
        sys.exit(1)
    extract_labels(sys.argv[1])
