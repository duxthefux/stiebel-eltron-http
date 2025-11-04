from bs4 import BeautifulSoup
from pathlib import Path

html = Path("scripts/testdata/s_1_1_it.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

# Check for section headers - they might be in table cells
print("Looking for table structure...")
for table in soup.find_all('table'):
    rows = table.find_all('tr')
    print(f"\nTable with {len(rows)} rows")
    for i, row in enumerate(rows[:10]):  # Show first 10 rows
        cells = row.find_all(['td', 'th'])
        if cells:
            print(f"  Row {i}: {[cell.get_text(strip=True) for cell in cells]}")
    if len(rows) > 10:
        print(f"  ... ({len(rows) - 10} more rows)")
