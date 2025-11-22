from bs4 import BeautifulSoup
from pathlib import Path

# Get unique section headers from all test data
sections = {}

for html_file in sorted(Path('scripts/testdata').glob('s_*.html')):
    if html_file.stem.startswith('_'):
        continue
    lang = html_file.stem.split('_')[-1]
    soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
    
    # Find all section headers (class='tabelle_head')
    for header in soup.find_all('td', class_='tabelle_head'):
        text = header.get_text(strip=True)
        if text and len(text) > 2:  # Skip short headers
            if text not in sections:
                sections[text] = []
            if lang not in sections[text]:
                sections[text].append(lang)

# Print sections sorted by language count
print("SECTION HEADERS FOUND IN TEST DATA:")
print("="*80)
for section, langs in sorted(sections.items(), key=lambda x: (len(x[1]), x[0]), reverse=True):
    print(f"{section:45} ({len(langs):2} langs): {', '.join(sorted(langs))}")
