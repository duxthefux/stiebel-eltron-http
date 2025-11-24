#!/usr/bin/env python3
"""Extract all sensor field names using position-based matching (structure-based, not keyword-based)."""

import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).parent.parent))

TESTDATA_DIR = Path(__file__).parent / "testdata"
TRANSLATIONS_DIR = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "translations"

def extract_all_fields_by_position(html_file: Path) -> dict[str, list[tuple[str, str]]]:
    """Extract all fields with their section and position.
    
    Returns: {section_name: [(field_name, value), ...]}
    """
    html = html_file.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    sections = {}
    
    for table in soup.find_all("table", class_="info"):
        th = table.find("th")
        if not th:
            continue
        
        section_name = th.get_text(strip=True)
        fields = []
        
        for row in table.find_all("tr"):
            key_cells = row.find_all("td", class_="key")
            value_cells = row.find_all("td", class_="value")
            
            if key_cells and value_cells:
                field_name = key_cells[0].get_text(strip=True)
                field_value = value_cells[0].get_text(strip=True)
                if field_name:
                    fields.append((field_name, field_value))
        
        if fields:
            sections[section_name] = fields
    
    return sections

# Define the structure mapping: (page, section_index, field_index) -> sensor_key
# This is based on German test data structure, which should be identical across all languages
STRUCTURE_MAP = {
    # s_1_1: Heat pump runtime statistics
    ('s_1_1', 'WÄRMEMENGE', 0): 'runtime_vd_heating',  # VD HEIZEN TAG / HP HEATING DAY
    ('s_1_1', 'WÄRMEMENGE', 1): 'vd_heating_total',    # VD HEIZEN SUMME / HP HEATING TOTAL
    ('s_1_1', 'WÄRMEMENGE', 2): 'runtime_vd_dhw',      # VD WARMWASSER TAG / HP DHW DAY
    ('s_1_1', 'WÄRMEMENGE', 3): 'vd_dhw_total',        # VD WARMWASSER SUMME / HP DHW TOTAL
    ('s_1_1', 'WÄRMEMENGE', 4): 'runtime_vd_defrost',  # VD ABTAUEN / HP DEFROST
    ('s_1_1', 'WÄRMEMENGE', 5): 'defrost_time',        # ABTAUZEIT / DEFROST TIME
    
    ('s_1_1', 'INVERTER', 0): 'inverter_current',      # STROM INVERTER / INVERTER CURRENT
    ('s_1_1', 'INVERTER', 1): 'inverter_voltage',      # SPANNUNG INVERTER / INVERTER VOLTAGE
    ('s_1_1', 'INVERTER', 2): 'inverter_power_input',  # AUFNAHMELEISTUNG INVERTER / INVERTER POWER CONSUMPTION
    ('s_1_1', 'INVERTER', 3): 'inverter_power',        # INVERTER AUFNAHMELEISTUNG / INVERTER POWER
    
    ('s_1_1', 'VERDICHTER', 0): 'compressor_inlet_temp',  # WÄRMEQUELLE EINTRITT / SOURCE INLET
    ('s_1_1', 'VERDICHTER', 1): 'compressor_outlet_temp', # WÄRMEQUELLE AUSTRITT / SOURCE OUTLET
    
    ('s_1_1', 'TEMPERATUR', 0): 'compressor_temp',        # VERDICHTER / COMPRESSOR (temperature)
    ('s_1_1', 'TEMPERATUR', 1): 'evaporator_temp',        # VERDAMPFER / EVAPORATOR
    ('s_1_1', 'TEMPERATUR', 2): 'condenser_temp',         # VERFLÜSSIGER / CONDENSER
    ('s_1_1', 'TEMPERATUR', 3): 'hs_inlet_temp',          # HEIZKREIS EINTRITT / HS INLET
    ('s_1_1', 'TEMPERATUR', 4): 'hs_outlet_temp',         # HEIZKREIS AUSTRITT / HS OUTLET
    
    ('s_1_1', 'AANT. KEREN STARTEN', 0): 'compressor_starts',  # VERDICHTER / COMPRESSOR (starts)
    ('s_1_1', 'ANTAL STARTER', 0): 'defrost_starts',     # ABTAUEN STARTS / DEFROST STARTS
}

def get_section_by_position(sections_dict: dict, position: int) -> str | None:
    """Get section name by position index."""
    section_names = list(sections_dict.keys())
    if 0 <= position < len(section_names):
        return section_names[position]
    return None

print("Comparing structure across test data files:")
print("=" * 100)

# First, analyze German structure to build the map
de_s_1_1 = TESTDATA_DIR / "s_1_1_de.html"
de_sections = extract_all_fields_by_position(de_s_1_1)

print("\nGerman (DE) s_1_1 structure:")
for i, (section_name, fields) in enumerate(de_sections.items()):
    print(f"\n  Section {i}: {section_name} ({len(fields)} fields)")
    for j, (field_name, value) in enumerate(fields):
        print(f"    [{j}] {field_name} = {value}")

# Now compare with Swedish
sv_s_1_1 = TESTDATA_DIR / "s_1_1_sv.html"
sv_sections = extract_all_fields_by_position(sv_s_1_1)

print("\n\nSwedish (SV) s_1_1 structure:")
for i, (section_name, fields) in enumerate(sv_sections.items()):
    print(f"\n  Section {i}: {section_name} ({len(fields)} fields)")
    for j, (field_name, value) in enumerate(fields):
        print(f"    [{j}] {field_name} = {value}")
