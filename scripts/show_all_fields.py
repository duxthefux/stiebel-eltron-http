from bs4 import BeautifulSoup

# Check all languages for fields with values that might be supplementary totals
for lang in ['de', 'en']:
    print(f"\n{lang.upper()} - All fields and values:")
    html = open(f'scripts/testdata/s_1_1_{lang}.html', encoding='utf-8').read()
    soup = BeautifulSoup(html, 'html.parser')
    
    tables = soup.find_all('table')
    for table_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                field = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                # Print all fields - we'll look for patterns
                print(f"  {field}: {value}")
        print()
