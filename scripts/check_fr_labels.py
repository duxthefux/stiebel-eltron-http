from pathlib import Path
from bs4 import BeautifulSoup

html = Path('scripts/testdata/s_1_1_fr.html').read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all('table')

print("French labels from s_1_1_fr.html:")
for table in tables:
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            if label:
                print(f"  {label}")
