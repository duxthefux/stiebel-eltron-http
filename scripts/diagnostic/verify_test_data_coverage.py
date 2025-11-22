#!/usr/bin/env python3
"""Verify that all fields from test data have corresponding sensors."""

from pathlib import Path
import sys

# Add parent directory to path to import helpers
sys.path.insert(0, str(Path(__file__).parent.parent))

from script_helpers import find_test_data_files, parse_html_file
import importlib.util

# Load const module
const_path = Path.cwd() / 'custom_components' / 'stiebel_eltron_http' / 'const.py'
spec = importlib.util.spec_from_file_location("const", const_path)
const = importlib.util.module_from_spec(spec)
spec.loader.exec_module(const)

# Get all sensor keys from sensor.py
sensor_path = Path.cwd() / 'custom_components' / 'stiebel_eltron_http' / 'sensor.py'
with open(sensor_path, 'r', encoding='utf-8') as f:
    sensor_content = f.read()

import re
sensor_pattern = r'key=([A-Z_]+_KEY)'
sensor_keys_found = re.findall(sensor_pattern, sensor_content)
sensor_keys = {getattr(const, key_name) for key_name in sensor_keys_found if hasattr(const, key_name)}

print(f"Total sensors defined: {len(sensor_keys)}")
print(f"Sensors: {sorted(sensor_keys)}\n")

# Run the actual scraper on test data
print("="*80)
print("RUNNING SCRAPER ON TEST DATA")
print("="*80)

# Import the scraper - need to set up the environment
sys.path.insert(0, str(Path.cwd() / 'custom_components' / 'stiebel_eltron_http'))

# Mock the homeassistant module
import sys
import types

# Create mock homeassistant module structure
homeassistant = types.ModuleType('homeassistant')
homeassistant.core = types.ModuleType('homeassistant.core')
homeassistant.helpers = types.ModuleType('homeassistant.helpers')

sys.modules['homeassistant'] = homeassistant
sys.modules['homeassistant.core'] = homeassistant.core
sys.modules['homeassistant.helpers'] = homeassistant.helpers
sys.modules['homeassistant.helpers.aiohttp_client'] = types.ModuleType('homeassistant.helpers.aiohttp_client')

# Now import scraper
from scraper import StiebelEltronHTTPScraper

# Find test files
test_files = find_test_data_files()
print(f"Found {len(test_files)} test files")

# Extract data from one test file
for test_file in test_files[:1]:  # Just check first one
    print(f"\nProcessing: {test_file.name}")
    
    html_content = test_file.read_text(encoding='utf-8')
    parsed_sections = parse_html_file(html_content)
    
    # Create scraper instance
    scraper = StiebelEltronHTTPScraper(None, None, None)  # type: ignore
    
    # Extract data from all sections
    all_data = {}
    for section_name, section_soup in parsed_sections.items():
        if section_name == 's_1_0':
            data = scraper._extract_info_temperatures(section_soup)
        elif section_name == 's_1_1':
            data = scraper._extract_info_statistics(section_soup)
        elif section_name == 's_2_7':
            data = scraper._extract_info_parameter(section_soup)
        else:
            continue
        
        all_data.update(data)
    
    print(f"\nExtracted {len(all_data)} fields:")
    for key in sorted(all_data.keys()):
        has_sensor = '✅' if key in sensor_keys else '❌'
        print(f"  {has_sensor} {key}: {all_data[key]}")
    
    # Check coverage
    extracted_keys = set(all_data.keys())
    
    # Keys extracted but without sensors
    missing_sensors = extracted_keys - sensor_keys
    if missing_sensors:
        print(f"\n⚠️  Extracted fields WITHOUT sensors ({len(missing_sensors)}):")
        for key in sorted(missing_sensors):
            print(f"  - {key}")
    else:
        print("\n✅ All extracted fields have sensors!")
    
    # Sensors without extracted data (might be device-specific)
    extra_sensors = sensor_keys - extracted_keys
    if extra_sensors:
        print(f"\n📋 Sensors NOT extracted from this test file ({len(extra_sensors)}):")
        print("   (May be device-specific or from other pages)")
        for key in sorted(extra_sensors):
            print(f"  - {key}")
    
    break  # Only process first file for now

print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total sensors defined: {len(sensor_keys)}")
print(f"Fields extracted from test: {len(extracted_keys)}")
print(f"Coverage: {len(extracted_keys & sensor_keys)}/{len(extracted_keys)} extracted fields have sensors")
