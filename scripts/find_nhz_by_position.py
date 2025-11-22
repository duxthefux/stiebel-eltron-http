from bs4 import BeautifulSoup

# Get all fields from all languages
all_fields_by_lang = {}

for lang in ['de','en','fr','nl','it','sv','es','pl','cs','hu','fi','da']:
    html = open(f'scripts/testdata/s_1_1_{lang}.html', encoding='utf-8').read()
    soup = BeautifulSoup(html, 'html.parser')
    
    fields = [td.get_text(strip=True) for td in soup.find_all('td', class_='spalte1')]
    all_fields_by_lang[lang] = fields

# Get German fields first to identify the pattern
de_fields = all_fields_by_lang['de']
print("German fields containing 'NHZ' or 'SUMME':")
for f in de_fields:
    if 'NHZ' in f or ('SUMME' in f and 'VD' not in f):
        print(f'  {f}')

print("\n" + "="*80)

# Now check if similar patterns exist in other languages by position
# Find the positions of NHZ fields in German
nhz_positions = []
for i, f in enumerate(de_fields):
    if 'NHZ' in f:
        nhz_positions.append(i)
        print(f"\nGerman position {i}: {f}")

# Check what's at those positions in other languages
for pos in nhz_positions:
    print(f"\nPosition {pos} across languages:")
    for lang in ['de','en','fr','nl','it','sv','es','pl','cs','hu','fi','da']:
        fields = all_fields_by_lang[lang]
        if pos < len(fields):
            print(f'  {lang}: {fields[pos]}')
