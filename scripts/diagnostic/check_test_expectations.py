#!/usr/bin/env python3
"""Simple test: extract all fields from all test HTML files and check sensor coverage."""

from pathlib import Path
from bs4 import BeautifulSoup
import re
import importlib.util
import sys

# Load const module
const_path = Path.cwd() / 'custom_components' / 'stiebel_eltron_http' / 'const.py'
spec = importlib.util.spec_from_file_location("const", const_path)
const = importlib.util.module_from_spec(spec)
spec.loader.exec_module(const)

# Get all sensor keys from sensor.py
sensor_path = Path.cwd() / 'custom_components' / 'stiebel_eltron_http' / 'sensor.py'
with open(sensor_path, 'r', encoding='utf-8') as f:
    sensor_content = f.read()

sensor_pattern = r'key=([A-Z_]+_KEY)'
sensor_keys_found = re.findall(sensor_pattern, sensor_content)
sensor_keys = {getattr(const, key_name) for key_name in sensor_keys_found if hasattr(const, key_name)}

print(f"✅ Found {len(sensor_keys)} sensors defined in sensor.py")

# Now let's see which test verifies extraction
test_path = Path.cwd() / 'tests'

# Look for tests that verify field extraction
test_files = [
    'test_values_not_none.py',  # Tests that values are extracted
]

for test_file in test_files:
    full_path = test_path / test_file
    if full_path.exists():
        print(f"\n📋 Checking {test_file}...")
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract all _KEY constants mentioned
        key_pattern = r'([A-Z_]+_KEY)'
        keys_in_test = re.findall(key_pattern, content)
        unique_keys = {getattr(const, key) for key in set(keys_in_test) if hasattr(const, key)}
        
        print(f"   Test references {len(unique_keys)} unique keys")
        
        # Check which ones have sensors
        with_sensors = unique_keys & sensor_keys
        without_sensors = unique_keys - sensor_keys
        
        print(f"   ✅ {len(with_sensors)} have sensors")
        if without_sensors:
            print(f"   ⚠️  {len(without_sensors)} mentioned in test but NO sensor:")
            for key in sorted(without_sensors):
                print(f"      - {key}")

print("\n" + "="*80)
print("CONCLUSION")
print("="*80)

# The real question: Are all the keys that get extracted by the scraper covered by sensors?
# Let's look at what test_values_not_none expects

test_values_path = Path.cwd() / 'tests' / 'test_values_not_none.py'
with open(test_values_path, 'r', encoding='utf-8') as f:
    test_content = f.read()

# Find the KEYS_TO_CHECK list
if 'KEYS_TO_CHECK' in test_content:
    # Extract the list
    match = re.search(r'KEYS_TO_CHECK\s*=\s*\[(.*?)\]', test_content, re.DOTALL)
    if match:
        keys_str = match.group(1)
        # Extract all KEY constants
        test_keys = re.findall(r'([A-Z_]+_KEY)', keys_str)
        expected_keys = {getattr(const, key) for key in test_keys if hasattr(const, key)}
        
        print(f"\ntest_values_not_none.py expects {len(expected_keys)} keys to be extracted")
        
        # Check sensor coverage
        covered = expected_keys & sensor_keys
        missing = expected_keys - sensor_keys
        
        print(f"✅ {len(covered)}/{len(expected_keys)} expected keys have sensors")
        
        if missing:
            print(f"\n❌ Keys expected to be extracted but WITHOUT sensors ({len(missing)}):")
            for key in sorted(missing):
                print(f"   - {key}")
        else:
            print("\n✅ PERFECT! All expected extraction keys have sensors!")
