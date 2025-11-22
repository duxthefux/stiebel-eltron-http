#!/usr/bin/env python3
"""Find missing field translations in s_1_1 HTML files."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient

# Fields missing in specific languages on s_1_1
MISSING_FIELDS = [
    ('frost_protection_temperature', ['fr']),
    ('inverter_current', ['cs', 'es', 'fr', 'hu']),
    ('dhw_consumed_today', ['da', 'fi', 'nl']),
    ('heating_consumed_today', ['da', 'fi', 'nl']),
    ('total_dhw_consumed', ['da', 'fi', 'nl']),
    ('total_heating_consumed', ['da', 'fi', 'nl']),
]

client = StiebelEltronScrapingClient("dummy", "dummy", "dummy")

for field_name, missing_langs in MISSING_FIELDS:
    print(f"\n{'='*80}")
    print(f"{field_name}")
    print('='*80)
    
    for lang in missing_langs:
        html_path = Path(f'scripts/testdata/s_1_1_{lang}.html')
        html_content = html_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Get all field names from tables
        all_fields = []
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                tds = row.find_all('td')
                if len(tds) >= 2:
                    fname = tds[0].get_text(strip=True)
                    fval = tds[1].get_text(strip=True)
                    all_fields.append((fname, fval))
        
        # Try extraction
        result = client._extract_info_heatpump(html_content)
        
        if field_name in result:
            print(f"{lang}: ✅ {result[field_name]}")
        else:
            print(f"{lang}: ❌ NOT FOUND - searching HTML...")
            
            # Search for likely candidates
            keywords_map = {
                'frost_protection_temperature': ['frost', 'gel', 'antigel', 'vorst', 'gelo', 'fagy', 'jää'],
                'inverter_current': ['inverter', 'strom', 'current', 'courant', 'corriente', 'proud'],
                'dhw_consumed_today': ['warmwasser', 'dhw', 'water', 'eau', 'agua', 'verbrauch', 'consume', 'heute', 'today', 'hoy'],
                'heating_consumed_today': ['heizung', 'heating', 'chauffage', 'verwarming', 'calef', 'verbrauch', 'consume', 'heute', 'today'],
                'total_dhw_consumed': ['warmwasser', 'dhw', 'water', 'totaal', 'total', 'gesamt', 'verbrauch', 'consume'],
                'total_heating_consumed': ['heizung', 'heating', 'chauffage', 'verwarming', 'calef', 'totaal', 'total', 'gesamt', 'verbrauch'],
            }
            
            keywords = keywords_map.get(field_name, [])
            matches = [(f, v) for f, v in all_fields if any(k.lower() in f.lower() for k in keywords)]
            
            if matches:
                print(f"  Possible matches:")
                for fname, fval in matches[:5]:
                    print(f"    {fname} = {fval}")
