"""Check what fields are in English s_1_8 testdata."""

from bs4 import BeautifulSoup
from pathlib import Path

html = Path('scripts/testdata/s_1_8_en.html').read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')

tables = soup.find_all('table', class_='info')

print("Energy/efficiency tables in s_1_8_en.html:")
print("=" * 80)

for table in tables:
    header = table.find('th')
    if not header:
        continue
    
    section_name = header.get_text(strip=True)
    if section_name in ['AMOUNT OF HEAT', 'POWER CONSUMPTION', 'EFFICIENCY']:
        print(f"\n{section_name}:")
        print("-" * 40)
        fields = table.find_all('td', class_='key')
        for field in fields:
            print(f"  {field.get_text(strip=True)}")
