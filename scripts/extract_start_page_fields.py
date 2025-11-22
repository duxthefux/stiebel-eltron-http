"""Extract exact field names from s_1_0 (start page) for all 12 languages."""
from bs4 import BeautifulSoup
from pathlib import Path

# Fields to extract (search keywords)
field_keywords = {
    'BETRIEBSART': ['BETRIEB', 'OPERATION', 'MODE', 'FONCTIONNEMENT', 'BEDRIJF', 'MODALIT', 'DRIFT', 'SERVICIO', 'TRYB', 'PROVOZ', 'ÜZEM', 'KÄYTTÖ'],
}

fields_by_lang = {}

for html_file in sorted(Path('scripts/testdata').glob('s_1_0_*.html')):
    lang = html_file.stem.split('_')[-1]
    soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
    
    fields_by_lang[lang] = {}
    
    # Get all field names from first column
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            field_name = cells[0].get_text(strip=True)
            if field_name:
                # Check if it matches any field we're looking for
                for field_type, keywords in field_keywords.items():
                    for keyword in keywords:
                        if keyword.upper() in field_name.upper():
                            if field_type not in fields_by_lang[lang]:
                                fields_by_lang[lang][field_type] = field_name
                            break

# Print results
print("START PAGE FIELD NAMES BY LANGUAGE:")
print("="*80)

for field_type in sorted(field_keywords.keys()):
    print(f"\n{field_type}:")
    for lang in ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']:
        if lang in fields_by_lang and field_type in fields_by_lang[lang]:
            print(f'        "{fields_by_lang[lang][field_type]}",  # {lang}')
        else:
            print(f'        # {lang} - NOT FOUND')
