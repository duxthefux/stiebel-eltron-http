from bs4 import BeautifulSoup
import glob

for file in glob.glob('scripts/testdata/*_de.html'):
    soup = BeautifulSoup(open(file, encoding='utf-8').read(), 'html.parser')
    fields = [td.get_text(strip=True) for td in soup.find_all('td', class_='spalte1')]
    nhz_fields = [f for f in fields if 'NHZ' in f]
    
    if nhz_fields:
        print(f'{file}:')
        for f in nhz_fields:
            print(f'  {f}')
        print()
