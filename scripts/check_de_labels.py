from bs4 import BeautifulSoup
import sys

file = sys.argv[1] if len(sys.argv) > 1 else 'scripts/testdata/s_1_1_da.html'
soup = BeautifulSoup(open(file, encoding='utf-8').read(), 'html.parser')

print(f"Analyzing {file}:")
print("\nTable headers:")
tables = soup.find_all('table')
for i, table in enumerate(tables, 1):
    headers = table.find_all('th')
    if headers:
        print(f"  Table {i}: {headers[0].get_text(strip=True)}")
    else:
        print(f"  Table {i}: (no header)")

print("\nAll row labels:")
rows = soup.find_all('tr')
for r in rows:
    key_cell = r.find('td', class_='key')
    if key_cell:
        print(f"  {key_cell.get_text(strip=True)}")
