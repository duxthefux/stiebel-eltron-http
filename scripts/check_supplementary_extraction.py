import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.abspath('custom_components'))

from stiebel_eltron_http.scraper import WPMScraper

scraper = WPMScraper()

for lang in ['de', 'en', 'fr']:
    html = open(f'scripts/testdata/s_1_1_{lang}.html', encoding='utf-8').read()
    result = scraper._extract_info_heatpump(html)
    
    supp_keys = [k for k in result.keys() if 'supplementary' in k]
    
    print(f'\n{lang.upper()} supplementary fields extracted:')
    if supp_keys:
        for k in supp_keys:
            print(f'  {k}: {result[k]}')
    else:
        print('  None')
