#!/usr/bin/env python3
"""Map test data field names to sensor translation keys for all languages.

Uses STRUCTURE-BASED extraction (position in table) instead of keyword matching.
This ensures all languages get the same sensors since the HTML structure is identical.
"""

import sys
import json
from pathlib import Path
from bs4 import BeautifulSoup

# Add parent directory to path to import from custom_components
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.i18n.canonical_keys import CanonicalKey
from custom_components.stiebel_eltron_http.i18n import get_aliases

# Set UTF-8 encoding for output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

TESTDATA_DIR = Path(__file__).parent / "testdata"
TRANSLATIONS_DIR = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "translations"

# Structure-based field mapping: (page, section_position, field_position) -> sensor_key
# Positions are 0-indexed. This map is based on German test data structure,
# which is IDENTICAL across all languages (same device, same firmware).
FIELD_STRUCTURE_MAP = {
    # s_1_1, Section 1 (WÄRMEMENGE / VÄRMEMÄNGD / etc): Heat quantity/runtime statistics
    ('s_1_1', 3, 0): 'runtime_vd_heating',    # VD HEIZEN / VD UPPVÄRMNING / etc
    ('s_1_1', 3, 1): 'runtime_vd_dhw',        # VD WARMWASSER / VD VARMVATTEN / etc
    ('s_1_1', 3, 2): 'runtime_vd_defrost',    # VD ABTAUEN / VD AVFROSTNING / etc
    ('s_1_1', 3, 3): 'defrost_time',          # ZEIT ABTAUEN / TID AVFROSTNING / etc
    ('s_1_1', 3, 4): 'defrost_starts',        # STARTS ABTAUEN / STARTS AVFROSTNING / etc
    
    # s_1_1, Section 4 (STARTS / STARTAR / etc): Start counters
    ('s_1_1', 4, 0): 'compressor_starts',     # VERDICHTER / KOMPRESSOR / etc
    
    # s_1_1, Section 0 (PROZESSDATEN / PROCESSDATA / etc): Process data
    ('s_1_1', 0, 18): 'inverter_power_input', # AUFNAHMELEISTUNG INVERTER / STRÖMFÖRBR. OMRIKTARE
    ('s_1_1', 0, 19): 'inverter_power',       # INVERTER AUFNAHMELEISTUNG / INVERTER POWER
    
    # s_1_0: System info page - using alias-based extraction for these
    # (handled separately in map_sensor_names function)
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

def extract_field_via_aliases(soup, canonical_key: CanonicalKey, section_context: CanonicalKey | None = None) -> str | None:
    """Extract field name using canonical key aliases (same logic as scraper).
    
    Uses the i18n alias system to find fields, ensuring we extract exactly what
    the scraper would parse.
    """
    aliases = get_aliases(canonical_key)
    if not aliases:
        return None
    
    tables = soup.find_all('table', class_='info')
    
    for table in tables:
        # Check section context if specified
        if section_context:
            section_header = table.find('th', class_='round-top')
            if section_header:
                section_title = section_header.get_text(strip=True)
                section_aliases = get_aliases(section_context)
                if not any(alias.upper() in section_title.upper() for alias in section_aliases):
                    continue
        
        # Look for field in this table
        rows = table.find_all('tr')
        for row in rows:
            key_cell = row.find('td', class_='key')
            if key_cell:
                field_name = key_cell.get_text(strip=True)
                # Check if field matches any alias
                for alias in aliases:
                    if alias.upper() == field_name.upper():
                        return field_name
    
    return None

def map_sensor_names(lang: str):
    """Map sensor keys to their translated names from test data using STRUCTURE-BASED extraction."""
    mapping = {}
    
    # Use structure-based extraction for fields that appear in consistent positions
    for (page, section_pos, field_pos), sensor_key in FIELD_STRUCTURE_MAP.items():
        field_name = extract_field_by_structure(page, section_pos, field_pos, lang)
        if field_name:
            mapping[sensor_key] = field_name
    
    # For s_1_0 fields, use alias-based extraction (sections vary more)
    s_1_0 = TESTDATA_DIR / f"s_1_0_{lang}.html"
    if s_1_0.exists():
        soup = BeautifulSoup(s_1_0.read_text(encoding='utf-8'), 'html.parser')
        
        # Extract fields using alias matching
        alias_fields = {
            'external_actual_temperature': CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE,
            'external_set_temperature': CanonicalKey.EXTERNAL_SET_TEMPERATURE,
            'dual_mode_temp_hzg': CanonicalKey.DUAL_MODE_TEMP_HZG,
            'dual_mode_temp_ww': CanonicalKey.DUAL_MODE_TEMP_WW,
            'lower_limit_hzg': CanonicalKey.LOWER_LIMIT_HZG,
            'lower_limit_ww': CanonicalKey.LOWER_LIMIT_WW,
            'dhw_set_temperature': CanonicalKey.DHW_SET_TEMPERATURE,
        }
        
        for sensor_key, canonical_key in alias_fields.items():
            # For external fields, use section context
            if 'external_' in sensor_key:
                field_name = extract_field_via_aliases(soup, canonical_key, section_context=CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION)
            else:
                field_name = extract_field_via_aliases(soup, canonical_key)
            
            if field_name:
                mapping[sensor_key] = field_name
    
    return mapping
                    # VD HEIZEN / HP HEATING / VD OGRZEWANIE / etc
                    if any(w in field_upper for w in ['HEIZ', 'TOPENI', 'RISCALDAMENTO', 'CHAUFFAGE', 'VERWARMING', 'LÄMMITYS', 'CALEFACCIÓN', 'CALEFACCI', 'VARME', 'FŰTÉS', 'FUTES', 'UPPVÄRMNING', 'UPPVARMNING', 'OGRZEW']):
                        if 'TAG' not in field_upper and 'SUMME' not in field_upper and 'DAY' not in field_upper and 'DZIEN' not in field_upper and 'TOTAL' not in field_upper and 'SUMA' not in field_upper:
                            mapping['runtime_vd_heating'] = field
                    # VD WARMWASSER / HP DHW / VD CIEPLA WODA / etc
                    elif any(w in field_upper for w in ['WARMWASSER', 'VODA', 'ACQUA', 'EAU', 'AGUA', 'WATER', 'VESI', 'VAND', 'VÍZ', 'VIZ', 'VARMVATTEN', 'CIEPLA WODA', 'CIEPLEJ WODY']):
                        if 'TAG' not in field_upper and 'SUMME' not in field_upper and 'DAY' not in field_upper and 'DZIEN' not in field_upper and 'TOTAL' not in field_upper and 'SUMA' not in field_upper:
                            mapping['runtime_vd_dhw'] = field
                    # VD ABTAUEN / HP DEFROST / VD ROZMRAZANIE / etc
                    elif any(w in field_upper for w in ['ABTAU', 'DEFROST', 'ODMRZ', 'SBRINAMENTO', 'DÉGIVRAGE', 'DEGIVRAGE', 'AFRIJMING', 'SULATUS', 'ROZMRAZ', 'AVFROSTNING']):
                        if 'TAG' not in field_upper and 'SUMME' not in field_upper and 'DAY' not in field_upper and 'DZIEN' not in field_upper and 'TOTAL' not in field_upper and 'ZEIT' not in field_upper and 'TIME' not in field_upper and 'CZAS' not in field_upper and 'STARTS' not in field_upper and 'START' not in field_upper:
                            mapping['runtime_vd_defrost'] = field
                
                # Defrost statistics
                if any(w in field_upper for w in ['ABTAU', 'DEFROST', 'ODMRZ', 'SBRINAMENTO', 'DÉGIVRAGE', 'DEGIVRAGE', 'AFRIJMING', 'SULATUS', 'ROZMRAZ', 'AVFROSTNING']):
                    if any(w in field_upper for w in ['ZEIT', 'TIME', 'TEMPO', 'TEMPS', 'TIJD', 'AIKA', 'CZAS']):
                        mapping['defrost_time'] = field
                    elif any(w in field_upper for w in ['STARTS', 'START', 'POČET', 'NUMERO', 'NOMBRE', 'AANTAL', 'LUKUMÄÄRÄ']):
                        mapping['defrost_starts'] = field
                
                # Compressor starts
                if any(w in field_upper for w in ['VERDICHTER', 'COMPRESSOR', 'KOMPRESOR', 'COMPRESSORE', 'COMPRESSEUR', 'KOMPRESSORI', 'SPRĘŻARKA', 'SPREZARKA']):
                    if any(w in field_upper for w in ['STARTS', 'START', 'POČET', 'NUMERO']):
                        mapping['compressor_starts'] = field
                    elif field == field.strip() and not any(w in field_upper for w in ['TEMP', 'DREHZAHL', 'SPEED', 'TEPLOTA', 'WLOTU', 'INLET']):
                        # Just "VERDICHTER" or "SPRĘŻARKA" or similar - likely the starts counter
                        if lang in ['de', 'pl']:  # German and Polish use just the compressor name
                            mapping['compressor_starts'] = field
                
                # Inverter current
                if any(w in field_upper for w in ['INVERTER', 'STŘÍDAČ', 'INVERTITORE', 'ONDULEUR', 'OMVORMER', 'VAIHTOSUUNTAAJA']):
                    if any(w in field_upper for w in ['STROM', 'CURRENT', 'PROUD', 'CORRENTE', 'COURANT', 'STROOM', 'VIRTA']):
                        mapping['inverter_current'] = field
    
    # s_1_8: Efficiency/Energy page
    s_1_8 = TESTDATA_DIR / f"s_1_8_{lang}.html"
    if s_1_8.exists():
        sections = extract_fields_by_section(s_1_8)
        
        # Find the efficiency, heat quantity, and power consumption sections
        efficiency_section = None
        heat_section = None
        power_section = None
        
        for section_name in sections.keys():
            name_upper = section_name.upper()
            if any(w in name_upper for w in ['EFFI', 'ÚČINNOST', 'HATÉKONY', 'TEHOKKUUS', 'EFEKTYWN']):
                efficiency_section = section_name
            elif any(w in name_upper for w in ['WÄRMEMENGE', 'WARMEMENGE', 'TEPLA', 'CALORE', 'CHALEUR', 'VARM', 'LÄMPÖ', 'LAMPOMAA', 'CALOR', 'ILOSC CIEPLA', 'ILOSC', 'AMOUNT', 'CANTIDAD']):
                heat_section = section_name
            elif any(w in name_upper for w in ['STROM', 'PROUD', 'ELECTRIC', 'ENERGI', 'VIRRAN', 'CONSUMO', 'ZUŻYCIE', 'ZUZYCIE', 'POWER']):
                power_section = section_name
        
        # Map efficiency fields
        if efficiency_section and efficiency_section in sections:
            fields = sections[efficiency_section]
            for field in fields:
                field_upper = field.upper()
                # Heating efficiency sensors - include all variations found in test data
                if any(w in field_upper for w in ['HEIZ', 'TOPENI', 'VYTAP', 'VYTÁPĚNÍ', 'RISCALDAMENTO', 'CHAUFFAGE', 'VERWARMING', 'VERWARMEN', 'LÄMMITYS', 'LAMMITYS', 'CALEFACCIÓN', 'CALEFACCI', 'VARME', 'VÄRME', 'VARM', 'FŰTÉS', 'FUTES', 'UPPVÄRMNING', 'UPPVARMNING', 'GRZANIE']):
                    if '1-24' in field or '1–24' in field or '1–24' in field:
                        mapping['efficiency_heating_today'] = field
                    elif '1-12' in field or '1–12' in field or '1–12' in field:
                        mapping['efficiency_heating_1_12m'] = field
                    elif '13-24' in field or '13–24' in field or '13–24' in field:
                        mapping['efficiency_heating_13_24m'] = field
                # DHW efficiency sensors
                elif any(w in field_upper for w in ['WARMWASSER', 'VODA', 'ACQUA', 'EAU', 'AGUA', 'WATER', 'VESI', 'VAND', 'VÍZ', 'VIZ', 'VARMVATTEN', 'CWU']):
                    if '1-24' in field or '1–24' in field or '1–24' in field:
                        mapping['efficiency_dhw_today'] = field
                    elif '1-12' in field or '1–12' in field or '1–12' in field:
                        mapping['efficiency_dhw_1_12m'] = field
                    elif '13-24' in field or '13–24' in field or '13–24' in field:
                        mapping['efficiency_dhw_13_24m'] = field
        
        # Map heat produced fields (from WÄRMEMENGE section)
        if heat_section and heat_section in sections:
            fields = sections[heat_section]
            for field in fields:
                field_upper = field.upper()
                # Heating produced - include all variations found in test data
                if any(w in field_upper for w in ['HEIZ', 'TOPENI', 'VYTAP', 'VYTÁPĚNÍ', 'RISCALDAMENTO', 'CHAUFFAGE', 'VERWARMING', 'VERWARMEN', 'LÄMMITYS', 'LAMMITYS', 'CALEFACCIÓN', 'CALEFACCI', 'VARME', 'VÄRME', 'VARM', 'FŰTÉS', 'FUTES', 'UPPVÄRMNING', 'UPPVARMNING', 'GRZANIE']):
                    if '1-24' in field or '1–24' in field or '1–24' in field:
                        mapping['heat_produced_today'] = field
                    elif '1-12' in field or '1–12' in field or '1–12' in field:
                        mapping['total_heat_produced'] = field
                # DHW produced
                elif any(w in field_upper for w in ['WARMWASSER', 'VODA', 'ACQUA', 'EAU', 'AGUA', 'WATER', 'VESI', 'VAND', 'VÍZ', 'VIZ', 'VARMVATTEN', 'CWU']):
                    if '1-24' in field or '1–24' in field or '1–24' in field:
                        mapping['dhw_produced_today'] = field
                    elif '1-12' in field or '1–12' in field or '1–12' in field:
                        mapping['total_dhw_produced'] = field
        
        # Map power consumed fields (from STROMVERBRAUCH / power consumption section)
        if power_section and power_section in sections:
            fields = sections[power_section]
            for field in fields:
                field_upper = field.upper()
                # Heating consumed
                if any(w in field_upper for w in ['HEIZ', 'TOPENI', 'VYTAP', 'VYTÁPĚNÍ', 'RISCALDAMENTO', 'CHAUFFAGE', 'VERWARMING', 'VERWARMEN', 'LÄMMITYS', 'LAMMITYS', 'CALEFACCIÓN', 'CALEFACCI', 'VARME', 'VÄRME', 'VARM', 'FŰTÉS', 'FUTES', 'UPPVÄRMNING', 'UPPVARMNING', 'GRZANIE']):
                    if '1-24' in field or '1–24' in field or '1–24' in field:
                        mapping['heating_consumed_today'] = field
                # DHW consumed
                elif any(w in field_upper for w in ['WARMWASSER', 'VODA', 'ACQUA', 'EAU', 'AGUA', 'WATER', 'VESI', 'VAND', 'VÍZ', 'VIZ', 'VARMVATTEN', 'CWU']):
                    if '1-24' in field or '1–24' in field or '1–24' in field:
                        mapping['dhw_consumed_today'] = field
    
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
