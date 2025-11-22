#!/usr/bin/env python3
"""Debug VD field extraction for Dutch/Finnish/Danish."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient

client = StiebelEltronScrapingClient("dummy", "dummy", "dummy")

for lang in ['nl', 'fi', 'da']:
    print(f"\n{'='*80}")
    print(f"{lang.upper()}")
    print('='*80)
    
    html_path = Path(f'scripts/testdata/s_1_1_{lang}.html')
    html_content = html_path.read_text(encoding='utf-8')
    
    result = client._extract_info_heatpump(html_content)
    
    # Check for VD fields
    vd_fields = {k: v for k, v in result.items() if 'consumed' in k or 'heating' in k or 'dhw' in k}
    
    print("Extracted VD/consumed fields:")
    for key in sorted(vd_fields.keys()):
        print(f"  {key}: {vd_fields[key]}")
    
    # Check specifically for the missing ones
    missing = []
    for field in ['dhw_consumed_today', 'heating_consumed_today', 'total_dhw_consumed', 'total_heating_consumed']:
        if field not in result:
            missing.append(field)
    
    if missing:
        print(f"\nMissing fields: {', '.join(missing)}")
