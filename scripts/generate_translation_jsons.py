"""Generate translation JSON files for all languages.

Creates Home Assistant translation JSON files for each language based on
CANONICAL_TO_CONST mapping and language-specific entity names.
"""

import json
from pathlib import Path

# Language metadata - full names as they appear in i18n files
LANGUAGES = {
    'de': 'German',
    'en': 'English',
    'fr': 'French',
    'nl': 'Dutch',
    'it': 'Italian',
    'sv': 'Swedish',
    'es': 'Spanish',
    'pl': 'Polish',
    'cs': 'Czech',
    'hu': 'Hungarian',
    'fi': 'Finnish',
    'da': 'Danish',
}

# Entity name translations per language
# Based on field names that appear in testdata
ENTITY_TRANSLATIONS = {
    'de': {
        'room_temperature': 'Raumtemperatur',
        'dhw_temperature': 'Warmwassertemperatur',
        'room_relative_humidity': 'Raumfeuchte (relativ)',
        'outside_temperature': 'Außentemperatur',
        'total_heat_produced': 'Erzeugte Heizenergie (gesamt)',
        'heat_produced_today': 'Erzeugte Heizenergie (heute)',
        'total_dhw_produced': 'Erzeugte Warmwasserenergie (gesamt)',
        'dhw_produced_today': 'Erzeugte Warmwasserenergie (heute)',
        'total_heating_consumed': 'Verbrauchte Heizenergie (gesamt)',
        'heating_consumed_today': 'Verbrauchte Heizenergie (heute)',
        'total_dhw_consumed': 'Verbrauchte Warmwasserenergie (gesamt)',
        'dhw_consumed_today': 'Verbrauchte Warmwasserenergie (heute)',
        'return_temperature': 'Rücklauftemperatur',
        'supply_temperature': 'Vorlauftemperatur',
        'frost_protection_temperature': 'Frostschutztemperatur',
        'compressor_inlet_temperature': 'Verdichtereintrittstemperatur',
        'hot_gas_temperature': 'Heißgastemperatur',
        'condenser_temperature': 'Verflüssigertemperatur',
        'oil_sump_temperature': 'Ölsumpftemperatur',
        'low_pressure': 'Niederdruck',
        'high_pressure': 'Hochdruck',
        'water_flow': 'Wasservolumenstrom',
        'inverter_current': 'Inverter Strom',
        'inverter_voltage': 'Inverter Spannung',
        'compressor_speed_actual': 'Istdrehzahl Verdichter',
        'compressor_speed_target': 'Solldrehzahl Verdichter',
        'fan_power_relative': 'Lüfterleistung (relativ)',
        'evaporator_inlet_temperature': 'Verdampfer Eintrittstemperatur',
        'evaporator_outlet_temperature': 'Verdampfer Austrittstemperatur',
        'inverter_power_input': 'Aufnahmeleistung Inverter',
        'inverter_power': 'Inverter Leistung',
        'efficiency_heating_today': 'Heiz-Effizienz (heute)',
        'efficiency_heating_1_12m': 'Heiz-Effizienz (1-12 Monate)',
        'efficiency_heating_13_24m': 'Heiz-Effizienz (13-24 Monate)',
        'efficiency_dhw_today': 'Warmwasser-Effizienz (heute)',
        'efficiency_dhw_1_12m': 'Warmwasser-Effizienz (1-12 Monate)',
        'efficiency_dhw_13_24m': 'Warmwasser-Effizienz (13-24 Monate)',
        'start_betriebsart': 'Betriebsart',
        'start_portal_ok': 'Portal verbunden',
        'start_system_ok': 'System OK',
    },
    'en': {
        'room_temperature': 'Room Temperature',
        'dhw_temperature': 'DHW Temperature',
        'room_relative_humidity': 'Room Relative Humidity',
        'outside_temperature': 'Outside Temperature',
        'total_heat_produced': 'Total Heat Produced',
        'heat_produced_today': 'Heat Produced Today',
        'total_dhw_produced': 'Total DHW Produced',
        'dhw_produced_today': 'DHW Produced Today',
        'total_heating_consumed': 'Total Heating Consumed',
        'heating_consumed_today': 'Heating Consumed Today',
        'total_dhw_consumed': 'Total DHW Consumed',
        'dhw_consumed_today': 'DHW Consumed Today',
        'return_temperature': 'Return Temperature',
        'supply_temperature': 'Supply Temperature',
        'frost_protection_temperature': 'Frost Protection Temperature',
        'compressor_inlet_temperature': 'Compressor Inlet Temperature',
        'hot_gas_temperature': 'Hot Gas Temperature',
        'condenser_temperature': 'Condenser Temperature',
        'oil_sump_temperature': 'Oil Sump Temperature',
        'low_pressure': 'Low Pressure',
        'high_pressure': 'High Pressure',
        'water_flow': 'Water Flow',
        'inverter_current': 'Inverter Current',
        'inverter_voltage': 'Inverter Voltage',
        'compressor_speed_actual': 'Compressor Speed Actual',
        'compressor_speed_target': 'Compressor Speed Target',
        'fan_power_relative': 'Fan Power Relative',
        'evaporator_inlet_temperature': 'Evaporator Inlet Temperature',
        'evaporator_outlet_temperature': 'Evaporator Outlet Temperature',
        'inverter_power_input': 'Inverter Power Input',
        'inverter_power': 'Inverter Power',
        'efficiency_heating_today': 'Heating Efficiency Today',
        'efficiency_heating_1_12m': 'Heating Efficiency 1-12M',
        'efficiency_heating_13_24m': 'Heating Efficiency 13-24M',
        'efficiency_dhw_today': 'DHW Efficiency Today',
        'efficiency_dhw_1_12m': 'DHW Efficiency 1-12M',
        'efficiency_dhw_13_24m': 'DHW Efficiency 13-24M',
        'start_betriebsart': 'Operating Mode',
        'start_portal_ok': 'Portal Connected',
        'start_system_ok': 'System OK',
    },
}

# Base structure for all language files
def create_translation_structure(lang_code, entity_names):
    """Create the translation JSON structure."""
    return {
        "config": {
            "step": {
                "user": {
                    "data": {
                        "host": "Host"
                    },
                    "data_description": {
                        "host": {
                            'de': "Der Hostname oder die IP-Adresse Ihres Stiebel Eltron ISG-Geräts.",
                            'en': "The hostname or IP address of your Stiebel Eltron ISG device.",
                        }.get(lang_code, "The hostname or IP address of your Stiebel Eltron ISG device.")
                    }
                }
            },
            "error": {
                "cannot_connect": "[%key:common::config_flow::error::cannot_connect%]",
                "unknown": "[%key:common::config_flow::error::unknown%]"
            },
            "abort": {
                "already_configured": "[%key:common::config_flow::abort::already_configured_device%]",
                "cannot_connect": "[%key:common::config_flow::error::cannot_connect%]",
                "unknown": "[%key:common::config_flow::error::unknown%]"
            }
        },
        "title": "Stiebel Eltron ISG",
        "entity": {
            "sensor": {
                key: {"name": name}
                for key, name in entity_names.items()
                if key not in ['start_portal_ok', 'start_system_ok']
            },
            "binary_sensor": {
                key: {"name": name}
                for key, name in entity_names.items()
                if key in ['start_portal_ok', 'start_system_ok']
            }
        }
    }


def main():
    """Generate all translation JSON files."""
    # Get paths
    root_dir = Path(__file__).parent.parent
    translations_dir = root_dir / 'custom_components' / 'stiebel_eltron_http' / 'translations'
    translations_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("GENERATING TRANSLATION JSON FILES")
    print("=" * 80)
    print()
    
    for lang_code, lang_name in LANGUAGES.items():
        print(f"Processing {lang_name} ({lang_code})...")
        
        # Get entity translations for this language
        # Fall back to English if not available
        entity_names = ENTITY_TRANSLATIONS.get(lang_code, ENTITY_TRANSLATIONS['en'])
        
        # Create the translation structure
        translation = create_translation_structure(lang_code, entity_names)
        
        # Write to file
        output_file = translations_dir / f"{lang_code}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(translation, f, indent=4, ensure_ascii=False)
        
        sensor_count = len(translation['entity']['sensor'])
        binary_sensor_count = len(translation['entity']['binary_sensor'])
        print(f"  ✓ Created {lang_code}.json")
        print(f"    Sensors: {sensor_count}, Binary Sensors: {binary_sensor_count}")
    
    print()
    print("=" * 80)
    print(f"SUMMARY: Generated {len(LANGUAGES)} translation files")
    print("=" * 80)


if __name__ == '__main__':
    main()
