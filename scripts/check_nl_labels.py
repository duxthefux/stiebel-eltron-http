#!/usr/bin/env python3
"""Extract Dutch labels from ISG test data files."""

from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path(__file__).parent / "testdata"

def extract_labels(html_path: Path):
    """Extract labels from Dutch test file."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    labels = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                if label:
                    labels.append(label)
    return labels

if __name__ == "__main__":
    file_path = TESTDATA_DIR / "s_1_1_nl.html"
    labels = extract_labels(file_path)
    print(f"Dutch labels from s_1_1_nl.html:")
    for label in labels:
        print(f"  {label}")
