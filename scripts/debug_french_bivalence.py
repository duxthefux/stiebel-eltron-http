#!/usr/bin/env python3
"""Debug French bivalence extraction."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient

# Read French HTML
html_content = Path('scripts/testdata/s_1_0_fr.html').read_text(encoding='utf-8')

# Create client and extract
client = StiebelEltronScrapingClient("dummy_host", "dummy_user", "dummy_pass")
result = client._extract_info_system(html_content)

print("Extracted fields from French s_1_0:")
for key, value in sorted(result.items()):
    print(f"  {key}: {value}")

print("\n" + "="*80)
print("Looking for bivalence fields:")
print("="*80)

from custom_components.stiebel_eltron_http.mapping import (
    BIVALENCE_TEMPERATURE_HEATING_KEY,
    BIVALENCE_TEMPERATURE_DHW_KEY,
)

if BIVALENCE_TEMPERATURE_HEATING_KEY in result:
    print(f"✅ Found {BIVALENCE_TEMPERATURE_HEATING_KEY}: {result[BIVALENCE_TEMPERATURE_HEATING_KEY]}")
else:
    print(f"❌ Missing {BIVALENCE_TEMPERATURE_HEATING_KEY}")

if BIVALENCE_TEMPERATURE_DHW_KEY in result:
    print(f"✅ Found {BIVALENCE_TEMPERATURE_DHW_KEY}: {result[BIVALENCE_TEMPERATURE_DHW_KEY]}")
else:
    print(f"❌ Missing {BIVALENCE_TEMPERATURE_DHW_KEY}")
