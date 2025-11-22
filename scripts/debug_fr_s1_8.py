from bs4 import BeautifulSoup

for lang in ['fr', 'nl']:
    html = open(f'scripts/testdata/s_1_8_{lang}.html', encoding='utf-8').read()
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    
    print(f'\n{lang.upper()} efficiency table:')
    eff_table = tables[2]
    rows = eff_table.find_all('tr')[1:]
    print(f'  Row count: {len(rows)}')
    for r in rows:
        cells = r.find_all('td')
        if len(cells) >= 2:
            field = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            print(f'    {field}: {value}')
