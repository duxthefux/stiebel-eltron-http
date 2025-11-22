#!/usr/bin/env python3
"""Comprehensive check: all fields from test data are extracted and have sensors."""

from pathlib import Path
from bs4 import BeautifulSoup
import sys
import importlib.util

# Load const.py
const_path = Path.cwd() / 'custom_components' / 'stiebel_eltron_http' / 'const.py'
spec = importlib.util.spec_from_file_location("const", const_path)
const = importlib.util.module_from_spec(spec)
spec.loader.exec_module(const)

# Add const to sys.modules so it can be imported
sys.modules['const'] = const

# Load mapping.py
mapping_path = Path.cwd() / 'custom_components' / 'stiebel_eltron_http' / 'mapping.py'
with open(mapping_path, 'r', encoding='utf-8') as f:
    mapping_content = f.read()
    # Replace relative imports
    mapping_content = mapping_content.replace('from .const import', 'from const import')
    mapping_content = mapping_content.replace('from .dedupe import', 'from dedupe import')

# Execute mapping module
mapping_globals = {'__builtins__': __builtins__}
exec(mapping_content, mapping_globals)

CANONICAL_TO_CONST = mapping_globals['CANONICAL_TO_CONST']
ENERGY_CONSUMED_MAP = mapping_globals['ENERGY_CONSUMED_MAP']

# Collect all _KEY constants
all_keys = set()
for name in dir(const):
    if name.endswith('_KEY') and not name.startswith('_'):
        all_keys.add(getattr(const, name))

print(f"Total _KEY constants defined: {len(all_keys)}")

# Collect all keys that should have sensors (exclude internal/meta keys)
EXCLUDED_FROM_SENSORS = {
    getattr(const, 'MAC_ADDRESS_KEY'),
    getattr(const, 'FIXED_VALUE_MODE_KEY'),
}

sensor_keys = all_keys - EXCLUDED_FROM_SENSORS
print(f"Keys that should have sensors: {len(sensor_keys)}")

# Check which keys are in CANONICAL_TO_CONST
mapped_keys = set(CANONICAL_TO_CONST.values())
print(f"Keys in CANONICAL_TO_CONST: {len(mapped_keys)}")

# Check ENERGY_CONSUMED_MAP
energy_map_keys = set(ENERGY_CONSUMED_MAP.values())
print(f"Keys in ENERGY_CONSUMED_MAP: {len(energy_map_keys)}")

# Total extractable keys
extractable = mapped_keys | energy_map_keys
print(f"Total extractable keys: {len(extractable)}")

# Find keys not mapped for extraction
not_extractable = sensor_keys - extractable
if not_extractable:
    print(f"\n⚠️  Keys defined but NOT extractable ({len(not_extractable)}):")
    for key in sorted(not_extractable):
        print(f"  - {key}")
else:
    print("\n✅ All sensor keys are extractable!")

# Now check sensors - extract sensor keys from ENTITY_DESCRIPTIONS
print("\n" + "="*80)
print("CHECKING SENSOR DEFINITIONS")
print("="*80)

# Load sensor.py and extract sensor keys
sensor_path = Path.cwd() / 'custom_components' / 'stiebel_eltron_http' / 'sensor.py'
with open(sensor_path, 'r', encoding='utf-8') as f:
    sensor_content = f.read()

# Parse sensor keys from key=CONSTANT_KEY pattern
import re
sensor_pattern = r'key=([A-Z_]+_KEY)'
sensor_keys_found = re.findall(sensor_pattern, sensor_content)
sensor_set = {getattr(const, key_name) for key_name in sensor_keys_found if hasattr(const, key_name)}

print(f"Total sensors defined: {len(sensor_set)}")

# Check coverage
missing_sensors = sensor_keys - sensor_set
if missing_sensors:
    print(f"\n⚠️  Keys without sensors ({len(missing_sensors)}):")
    for key in sorted(missing_sensors):
        print(f"  - {key}")
else:
    print("\n✅ All keys have sensors!")

extra_sensors = sensor_set - all_keys
if extra_sensors:
    print(f"\n⚠️  Sensors for non-existent keys ({len(extra_sensors)}):")
    for key in sorted(extra_sensors):
        print(f"  - {key}")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total _KEY constants: {len(all_keys)}")
print(f"Excluded from sensors: {len(EXCLUDED_FROM_SENSORS)} (MAC_ADDRESS, FIXED_VALUE_MODE)")
print(f"Should have sensors: {len(sensor_keys)}")
print(f"Actually have sensors: {len(sensor_set)}")
print(f"Extractable (CANONICAL_TO_CONST): {len(mapped_keys)}")
print(f"Extractable (ENERGY_CONSUMED_MAP): {len(energy_map_keys)}")
print(f"Total extractable: {len(extractable)}")

if not missing_sensors and not not_extractable:
    print("\n✅ PERFECT COVERAGE: All fields are extractable and have sensors!")
else:
    print(f"\n❌ Issues found: {len(not_extractable)} not extractable, {len(missing_sensors)} missing sensors")
