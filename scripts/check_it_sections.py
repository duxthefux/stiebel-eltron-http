from bs4 import BeautifulSoup
from pathlib import Path

html = Path("scripts/testdata/s_1_1_it.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

print("Section headers (h3) in s_1_1_it.html:")
for h3 in soup.find_all('h3'):
    print(f"  {h3.get_text(strip=True)}")
