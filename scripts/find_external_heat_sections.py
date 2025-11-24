from pathlib import Path
from bs4 import BeautifulSoup

testdata_dir = Path('scripts/testdata')

for html_file in sorted(testdata_dir.glob('s_1_0_*.html')):
    lang = html_file.stem.split('_')[-1].upper()
    html = html_file.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    for header in soup.find_all('th', class_='round-top'):
        text = header.get_text(strip=True)
        if 'EXTERN' in text.upper() or 'EXTERNAL' in text.upper():
            print(f"{lang}: {text}")
