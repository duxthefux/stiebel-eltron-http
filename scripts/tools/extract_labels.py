#!/usr/bin/env python3
"""Extract section headers and labels from ISG test data files."""

from pathlib import Path
from bs4 import BeautifulSoup
import re

TESTDATA_DIR = Path(__file__).parent / "testdata"
LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "pl", "cs", "hu", "es", "fi", "da"]

def extract_labels(html_path: Path):
    """Extract section headers and table labels from an ISG HTML file."""
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    results = {
        "page_title": None,
        "sections": [],
        "table_labels": set(),
    }
    
    # Page title from sub_nav
    title_elem = soup.select_one("#sub_nav .left.main.sifr")
    if title_elem:
        results["page_title"] = title_elem.get_text(strip=True)
    
    # Section headers (typically h3 or similar)
    for h3 in soup.find_all("h3"):
        text = h3.get_text(strip=True)
        if text:
            results["sections"].append(text)
    
    # Table row labels (first column of tables)
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True)
                # Filter out empty labels and pure numbers
                if label and not re.match(r"^\d+$", label):
                    results["table_labels"].add(label)
    
    return results

def main():
    # Process each language for key pages
    pages = ["s_0_0", "s_1_0", "s_1_1", "s_1_8", "s_2_7"]
    
    for page in pages:
        print(f"\n{'='*80}")
        print(f"PAGE: {page}")
        print('='*80)
        
        for lang in LANGUAGES:
            file_path = TESTDATA_DIR / f"{page}_{lang}.html"
            if not file_path.exists():
                continue
            
            data = extract_labels(file_path)
            
            print(f"\n--- {lang.upper()} ---")
            if data["page_title"]:
                print(f"Title: {data['page_title']}")
            
            if data["sections"]:
                print(f"Sections ({len(data['sections'])}):")
                for section in data["sections"]:
                    print(f"  - {section}")
            
            if data["table_labels"]:
                # Show first 10 labels as sample
                labels = sorted(data["table_labels"])[:10]
                print(f"Sample labels ({len(data['table_labels'])} total):")
                for label in labels:
                    print(f"  - {label}")

if __name__ == "__main__":
    main()
