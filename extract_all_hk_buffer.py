from pathlib import Path
from bs4 import BeautifulSoup

testdata_dir = Path('scripts/testdata')

langs = ['fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

for lang in langs:
    html_file = testdata_dir / f's_1_0_{lang}.html'
    if not html_file.exists():
        continue
    
    html = html_file.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    rows = soup.find_all('tr')
    
    fields = {}
    
    for row in rows:
        key_cell = row.find('td', class_='key')
        if key_cell:
            key_text = key_cell.get_text(strip=True)
            
            if 'HK 1' in key_text:
                if 'HK 1' not in fields:
                    fields['HK 1'] = []
                fields['HK 1'].append(key_text)
            elif 'HK 2' in key_text:
                if 'HK 2' not in fields:
                    fields['HK 2'] = []
                fields['HK 2'].append(key_text)
            
            key_upper = key_text.upper()
            if any(word in key_upper for word in ['BUFFER', 'PUFFER', 'TAMPONE', 'BALLON', 'BUFOR', 'ZÁSOBNÍK', 'PUSKURI']):
                if 'BUFFER' not in fields:
                    fields['BUFFER'] = []
                fields['BUFFER'].append(key_text)
    
    if fields:
        print(f"\n{lang.upper()}:")
        for category, field_list in fields.items():
            print(f"  {category}:")
            for field in field_list:
                print(f"    - {field}")
