from pathlib import Path
from bs4 import BeautifulSoup

testdata_dir = Path('scripts/testdata')

for html_file in sorted(testdata_dir.glob('s_1_0_*.html')):
    lang = html_file.stem.split('_')[-1].upper()
    html = html_file.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get all section headers
    headers = [h.get_text(strip=True) for h in soup.find_all('th', class_='round-top')]
    
    # Check if there's an external heat source section
    external_section = None
    for h in headers:
        if any(word in h.upper() for word in ['EXTERN', 'EXTERNAL', 'ESTERNO', 'ESTERN', 'EST ']):
            external_section = h
            break
    
    if external_section:
        print(f"{lang}: {external_section}")
    else:
        print(f"{lang}: NOT FOUND")
