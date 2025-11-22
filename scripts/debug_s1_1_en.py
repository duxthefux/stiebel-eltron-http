"""Debug s_1_1_en extraction."""

import sys
sys.path.insert(0, '.')

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from pathlib import Path

client = StiebelEltronScrapingClient(host="test", session=None)
html = Path('scripts/testdata/s_1_1_en.html').read_text(encoding='utf-8')

print("Testing _extract_info_heatpump on s_1_1_en.html:")
print("=" * 80)

data = client._extract_info_heatpump(html)

print(f"\nTotal keys extracted: {len(data)}")
print("\nKeys related to heat/energy:")
for key in sorted(data.keys()):
    if 'heat' in key or 'dhw' in key or 'heating' in key or 'consumed' in key or 'produced' in key:
        print(f"  {key}: {data[key]}")

print("\nHas total_heat_produced?", 'total_heat_produced' in data)
print("Has total_dhw_produced?", 'total_dhw_produced' in data)
