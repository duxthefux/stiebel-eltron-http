#!/usr/bin/env python3
"""Map test data field names to sensor translation keys for all languages.

Uses STRUCTURE-BASED extraction (position in table) instead of keyword matching.
This ensures all languages get the same sensors since the HTML structure is identical.
"""

import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup

# Set UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

TESTDATA_DIR = Path(__file__).parent / "testdata"
TRANSLATIONS_DIR = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "translations"


# Structure-based field mapping: (page, section_position, field_position) -> sensor_key
# Positions are 0-indexed. This map is based on German test data structure,
# which is IDENTICAL across all languages (same device, same firmware).
#
# NOTE: All languages should extract the same sensors. If a language has the same word
# for multiple sensors in different sections, we'll prefix with section name later.
FIELD_STRUCTURE_MAP = {
    # ============================================================================
    # s_1_0: System overview - temperatures and settings
    # ============================================================================
    # Section 0: HEIZUNG (Heating circuit data)
    ('s_1_0', 0, 0): 'outside_temperature',       # AUSSENTEMPERATUR
    ('s_1_0', 0, 1): 'actual_temperature_hk_1',   # ISTTEMPERATUR HK 1
    ('s_1_0', 0, 2): 'set_temperature_hk_1',      # SOLLTEMPERATUR HK 1
    ('s_1_0', 0, 3): 'actual_temperature_hk_2',   # ISTTEMPERATUR HK 2
    ('s_1_0', 0, 4): 'set_temperature_hk_2',      # SOLLTEMPERATUR HK 2
    # [5] is FESTWERTBETRIEB (fixed value mode) - not in sensor list
    ('s_1_0', 0, 6): 'actual_buffer_temperature', # PUFFERISTTEMPERATUR
    ('s_1_0', 0, 7): 'set_buffer_temperature',    # PUFFERSOLLTEMPERATUR
    ('s_1_0', 0, 8): 'frost_protection_temperature',  # FROSTSCHUTZ
    
    # Section 1: WARMWASSER (DHW)
    ('s_1_0', 1, 0): 'dhw_temperature',           # ISTTEMPERATUR
    ('s_1_0', 1, 1): 'dhw_set_temperature',       # SOLLTEMPERATUR
    
    # Section 2: WÄRMEERZEUGER EXTERN (External heat generator)
    ('s_1_0', 2, 0): 'external_actual_temperature', # ISTTEMPERATUR
    ('s_1_0', 2, 1): 'external_set_temperature',    # SOLLTEMPERATUR
    ('s_1_0', 2, 2): 'dual_mode_temp_hzg',          # BIVALENZTEMPERATUR HZG
    ('s_1_0', 2, 3): 'lower_limit_hzg',             # UNTERE EINSATZGRENZE HZG
    ('s_1_0', 2, 4): 'dual_mode_temp_ww',           # BIVALENZTEMPERATUR WW
    ('s_1_0', 2, 5): 'lower_limit_ww',              # UNTERE EINSATZGRENZE WW
    
    # ============================================================================
    # s_1_1: Heat pump process data
    # ============================================================================
    # Section 0: PROZESSDATEN (Process data - 20 fields)
    ('s_1_1', 0, 0): 'return_temperature',         # RÜCKLAUFTEMPERATUR
    ('s_1_1', 0, 1): 'supply_temperature',         # VORLAUFTEMPERATUR
    # [2] is FROSTSCHUTZTEMPERATUR (duplicate of s_1_0[0][8])
    # [3] is AUSSENTEMPERATUR (duplicate of s_1_0[0][0])
    ('s_1_1', 0, 4): 'compressor_inlet_temperature',  # VERDICHTEREINTRITTSTEMPERATUR
    ('s_1_1', 0, 5): 'hot_gas_temperature',           # HEISSGASTEMPERATUR
    ('s_1_1', 0, 6): 'condenser_temperature',         # VERFLÜSSIGERTEMPERATUR
    ('s_1_1', 0, 7): 'oil_sump_temperature',          # ÖLSUMPFTEMPERATUR
    ('s_1_1', 0, 8): 'low_pressure',                  # DRUCK NIEDERDRUCK
    ('s_1_1', 0, 9): 'high_pressure',                 # DRUCK HOCHDRUCK
    # [10] is WP WASSERVOLUMENSTROM (water flow) - not in sensor list
    ('s_1_1', 0, 11): 'inverter_current',             # STROM INVERTER
    ('s_1_1', 0, 12): 'inverter_voltage',             # SPANNUNG INVERTER
    ('s_1_1', 0, 13): 'compressor_speed_actual',      # ISTDREHZAHL VERDICHTER
    ('s_1_1', 0, 14): 'compressor_speed_target',      # SOLLDREHZAHL VERDICHTER
    ('s_1_1', 0, 15): 'heat_source_return_temperature', # RÜCKLAUFTEMPERATUR WÄRMEQUELLE
    ('s_1_1', 0, 16): 'heat_source_flow_temperature', # VORLAUFTEMPERATUR WÄRMEQUELLE
    ('s_1_1', 0, 17): 'heat_source_pressure',# WÄRMEQUELLENDRUCK
    ('s_1_1', 0, 18): 'heat_source_pump_rate',         # LEISTUNG WÄRMEQUELLENPUMPE
    ('s_1_1', 0, 19): 'inverter_power',               # INVERTER AUFNAHMELEISTUNG
    
    # Section 1: WÄRMEMENGE (Heat quantity - PRODUCED not consumed)
    # NOTE: German sensor names say "ERZEUGT" (produced) but field names don't
    # Extracting these via alias-based approach instead (dhw_produced_today, heat_produced_today, etc)
    
    # Section 2: LEISTUNGSAUFNAHME (Power consumption - consumed)
    # NOTE: These map to heating_consumed_today, dhw_consumed_today but have ambiguous names
    # We'll handle via structure map with section context
    
    # Section 3: LAUFZEIT (Runtime statistics)
    ('s_1_1', 3, 0): 'runtime_vd_heating',     # VD HEIZEN
    ('s_1_1', 3, 1): 'runtime_vd_dhw',         # VD WARMWASSER
    ('s_1_1', 3, 2): 'runtime_vd_defrost',     # VD ABTAUEN
    ('s_1_1', 3, 3): 'defrost_time',           # ZEIT ABTAUEN
    ('s_1_1', 3, 4): 'defrost_starts',         # STARTS ABTAUEN
    
    # Section 4: STARTS (Start counters)
    ('s_1_1', 4, 0): 'compressor_starts',      # VERDICHTER
    
    # ============================================================================
    # s_1_8: Energy and efficiency data
    # ============================================================================
    # Section 0: WÄRMEMENGE (Heat produced - time periods)
    ('s_1_8', 0, 0): 'heat_produced_today',       # HEIZEN 1-24 h
    ('s_1_8', 0, 1): 'total_heat_produced',       # HEIZEN 1-12 M
    # [2] HEIZEN 13-24 M (months 13-24) - not in current sensor list
    ('s_1_8', 0, 3): 'dhw_produced_today',        # WARMWASSER 1-24 h
    ('s_1_8', 0, 4): 'total_dhw_produced',        # WARMWASSER 1-12 M
    # [5] WARMWASSER 13-24 M - not in current sensor list
    
    # Section 1: STROMVERBRAUCH (Power consumption - time periods)
    ('s_1_8', 1, 0): 'heating_consumed_today',    # HEIZEN 1-24 h
    ('s_1_8', 1, 1): 'total_heating_consumed',    # HEIZEN 1-12 M
    # [2] HEIZEN 13-24 M - not in current sensor list
    ('s_1_8', 1, 3): 'dhw_consumed_today',        # WARMWASSER 1-24 h
    ('s_1_8', 1, 4): 'total_dhw_consumed',        # WARMWASSER 1-12 M
    # [5] WARMWASSER 13-24 M - not in current sensor list
    
    # Section 2: EFFIZIENZ (Efficiency - time periods)
    ('s_1_8', 2, 0): 'efficiency_heating_today',   # HEIZEN 1-24 h
    ('s_1_8', 2, 1): 'efficiency_heating_1_12m',   # HEIZEN 1-12 M
    ('s_1_8', 2, 2): 'efficiency_heating_13_24m',  # HEIZEN 13-24 M
    ('s_1_8', 2, 3): 'efficiency_dhw_today',       # WARMWASSER 1-24 h
    ('s_1_8', 2, 4): 'efficiency_dhw_1_12m',       # WARMWASSER 1-12 M
    ('s_1_8', 2, 5): 'efficiency_dhw_13_24m',      # WARMWASSER 13-24 M

}


def extract_fields_by_position(html_file: Path) -> list[dict]:
    """Extract all fields with their section name, maintaining order.
    
    Returns: List of sections, each with: {
        'name': section_name,
        'fields': [(field_name, value), ...]
    }
    """
    html = html_file.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    sections = []
    
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
            sections.append({'name': section_name, 'fields': fields})
    
    return sections


def extract_field_by_structure(page: str, section_pos: int, field_pos: int, lang: str) -> str | None:
    """Extract field name by its structural position in the HTML.
    
    Args:
        page: Page name (e.g., 's_1_1')
        section_pos: 0-indexed section position
        field_pos: 0-indexed field position within section
        lang: Language code
        
    Returns:
        Field name at that position, or None if not found
    """
    html_file = TESTDATA_DIR / f"{page}_{lang}.html"
    if not html_file.exists():
        return None
    
    sections = extract_fields_by_position(html_file)
    
    if section_pos >= len(sections):
        return None
    
    section = sections[section_pos]
    if field_pos >= len(section['fields']):
        return None
    
    field_name, _ = section['fields'][field_pos]
    return field_name


def map_sensor_names(lang: str):
    """Map sensor keys to their translated names from test data using STRUCTURE-BASED extraction.
    
    This function extracts field names by their position in the HTML structure, which is
    identical across all languages (same device, same firmware).
    """
    mapping = {}
    
    # Use structure-based extraction for ALL fields
    # The FIELD_STRUCTURE_MAP covers s_1_0, s_1_1, and s_1_8
    for (page, section_pos, field_pos), sensor_key in FIELD_STRUCTURE_MAP.items():
        field_name = extract_field_by_structure(page, section_pos, field_pos, lang)
        if field_name:
            mapping[sensor_key] = field_name
    
    return mapping


def main():
    """Extract translations for all languages and update JSON files."""
    langs = ['cs', 'da', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']
    
    print("=" * 80)
    print("EXTRACTING SENSOR TRANSLATIONS FROM TEST DATA")
    print("=" * 80)
    
    for lang in langs:
        print(f"\n{lang.upper()}:")
        mapping = map_sensor_names(lang)
        
        if not mapping:
            print("  No translations found")
            continue
        
        # Load existing translation file
        trans_file = TRANSLATIONS_DIR / f"{lang}.json"
        if not trans_file.exists():
            print(f"  Translation file not found: {trans_file}")
            continue
        
        trans_data = json.load(trans_file.open(encoding='utf-8'))
        sensors = trans_data.get('entity', {}).get('sensor', {})
        
        # Add/update translations
        added = 0
        updated = 0
        for sensor_key, field_name in mapping.items():
            if sensor_key in sensors:
                if sensors[sensor_key]['name'] != field_name:
                    print(f"  UPDATE {sensor_key}: {sensors[sensor_key]['name']} -> {field_name}")
                    sensors[sensor_key]['name'] = field_name
                    updated += 1
            else:
                print(f"  ADD {sensor_key}: {field_name}")
                sensors[sensor_key] = {'name': field_name}
                added += 1
        
        if added > 0 or updated > 0:
            # Save updated translation file
            trans_file.write_text(
                json.dumps(trans_data, indent=4, ensure_ascii=False) + '\n',
                encoding='utf-8'
            )
            print(f"  ✓ Saved: {added} added, {updated} updated")
    
    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)

if __name__ == "__main__":
    main()
