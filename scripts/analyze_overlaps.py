"""Analyze overlapping aliases and classify them as OK or problematic"""
import re
from pathlib import Path
from collections import defaultdict

# Read the mapping.py file
mapping_file = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "mapping.py"
content = mapping_file.read_text(encoding='utf-8')

# Extract HEADER_ALIASES dictionary
match = re.search(r'HEADER_ALIASES:\s*dict\[CanonicalKey,\s*list\[str\]\]\s*=\s*\{(.*?)\n}', content, re.DOTALL)
if not match:
    print("Could not find HEADER_ALIASES in mapping.py")
    exit(1)

dict_content = match.group(1)

# Parse the aliases
pattern = r'CanonicalKey\.(\w+):\s*\[(.*?)\],'
matches = re.findall(pattern, dict_content, re.DOTALL)

# Build alias -> keys mapping
alias_to_keys = defaultdict(list)

for canonical_key, aliases_str in matches:
    alias_pattern = r'"([^"\\]*(?:\\.[^"\\]*)*)"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\''
    alias_matches = re.findall(alias_pattern, aliases_str)
    aliases = [match[0] or match[1] for match in alias_matches if match[0] or match[1]]
    
    for alias in aliases:
        if alias:
            normalized = alias.lower().strip()
            alias_to_keys[normalized].append(canonical_key)

# Find overlaps
overlaps = {alias: keys for alias, keys in alias_to_keys.items() if len(keys) > 1}

# Categorize overlaps
section_keys = ['ROOM_TEMPERATURE_SECTION', 'HEATING_SECTION', 'PROCESS_DATA_SECTION', 
                'DHW_SECTION', 'AMOUNT_OF_HEAT_SECTION', 'POWER_CONSUMPTION_SECTION',
                'EFFICIENCY_SECTION', 'ISG_SECTION']

row_value_keys = ['VD_HEATING_TOTAL', 'VD_HEATING_DAY', 'VD_DHW_TOTAL', 'VD_DHW_DAY',
                  'VD_HEATING_SUM', 'NHZ_HEATING_SUM', 'NHZ_DHW_SUM']

temperature_keys = ['ACTUAL_TEMPERATURE_1', 'ACTUAL_TEMPERATURE']

contextual_ok = []
generic_abbrev = []
real_conflicts = []

for alias, keys in sorted(overlaps.items()):
    # Check if it's a generic abbreviation (single letter or short suffix)
    if len(alias) <= 2 or alias in ['godz.', 'mies.']:
        generic_abbrev.append((alias, keys))
    # Check if it's section vs row value (different contexts)
    elif any(k in section_keys for k in keys) and any(k in row_value_keys for k in keys):
        contextual_ok.append((alias, keys))
    # Check for temperature conflicts (both are row values, similar usage)
    elif set(keys).issubset(set(temperature_keys)):
        real_conflicts.append((alias, keys))
    # Check for VD_HEATING conflicts
    elif 'VD_HEATING_TOTAL' in keys and 'VD_HEATING_SUM' in keys:
        real_conflicts.append((alias, keys))
    # Check for section vs section (ambiguous)
    elif all(k in section_keys for k in keys):
        real_conflicts.append((alias, keys))
    else:
        # Unknown pattern - flag as potential conflict
        real_conflicts.append((alias, keys))

print("=" * 80)
print("OVERLAP ANALYSIS REPORT")
print("=" * 80)

print(f"\n✓ CONTEXTUAL OK ({len(contextual_ok)} overlaps)")
print("-" * 80)
print("These are OK because they appear in different contexts:")
print("- Section keys are matched against table HEADERS (<th>)")
print("- Row value keys are matched against table ROW LABELS (<td>)")
print()
for alias, keys in contextual_ok:
    sections = [k for k in keys if k in section_keys]
    rows = [k for k in keys if k in row_value_keys]
    print(f'  "{alias}"')
    print(f'    Section headers: {", ".join(sections)}')
    print(f'    Row labels: {", ".join(rows)}')
    print()

print(f"\n⚠️  GENERIC ABBREVIATIONS ({len(generic_abbrev)} overlaps)")
print("-" * 80)
print("These are fragments of longer labels and should NOT be standalone aliases:")
print("They likely got added by mistake (e.g., 'm' from 'HEATING 1-12 M')")
print()
for alias, keys in generic_abbrev:
    print(f'  "{alias}" → {", ".join(keys)}')
    print(f'    FIX: Remove this standalone alias - it\'s part of longer strings')
    print()

print(f"\n❌ REAL CONFLICTS ({len(real_conflicts)} overlaps)")
print("-" * 80)
print("These need manual resolution - same alias in ambiguous contexts:")
print()
for alias, keys in real_conflicts:
    print(f'  "{alias}" → {", ".join(keys)}')
    # Provide specific fix suggestions
    if 'vd heizen summe' in alias:
        print(f'    FIX: "VD HEIZEN SUMME" should only be in VD_HEATING_SUM')
        print(f'         Remove from VD_HEATING_TOTAL (use "VD HEIZUNG GESAMT" instead)')
    elif 'isttemperatur' in alias and len(keys) == 2:
        print(f'    FIX: "ISTTEMPERATUR" without suffix should only be in ACTUAL_TEMPERATURE')
        print(f'         ACTUAL_TEMPERATURE_1 should use "ISTTEMPERATUR HK 1" or "ISTTEMPERATUR 1"')
    elif 'varmemængde' in alias:
        print(f'    FIX: "VARMEMÆNGDE" is section header for AMOUNT_OF_HEAT_SECTION')
        print(f'         Should not appear in HEATING_SECTION (use "VARME" if needed)')
    print()

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total overlaps: {len(overlaps)}")
print(f"  ✓ Contextual OK: {len(contextual_ok)}")
print(f"  ⚠️  Generic abbreviations: {len(generic_abbrev)}")
print(f"  ❌ Real conflicts: {len(real_conflicts)}")
print()
print("RECOMMENDATION:")
print("1. Remove generic abbreviations (they're parsing artifacts)")
print("2. Fix real conflicts by making aliases more specific")
print("3. Keep contextual overlaps - they work correctly")
