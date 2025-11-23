# Deutsche Feldnamen-Zuordnung / German Field Mapping

Dieses Dokument zeigt die Zuordnung zwischen den deutschen Feldnamen auf der ISG-Weboberfläche und den Home Assistant Sensornamen.

This document shows the mapping between German field names on the ISG web interface and Home Assistant sensor names.

---

## Abschnitte / Sections

### START (s=0,0)

| ISG Feldname (Deutsch) | Home Assistant Sensor | Beschreibung |
|------------------------|----------------------|--------------|
| BETRIEBSART | `start_operation_mode` | Aktueller Betriebsmodus (z.B. PROGRAMMBETRIEB, KOMFORTBETRIEB) |

---

### HEIZUNG / Heating Section (s=1,0)

| ISG Feldname (Deutsch) | Home Assistant Sensor | Einheit | Beschreibung |
|------------------------|----------------------|---------|--------------|
| AUSSENTEMPERATUR | `outside_temperature` | °C | Außentemperatur |
| ISTTEMPERATUR HK 1 | `actual_temperature_hk_1` | °C | Ist-Temperatur Heizkreis 1 |
| SOLLTEMPERATUR HK 1 | `set_temperature_hk_1` | °C | Soll-Temperatur Heizkreis 1 |
| ISTTEMPERATUR HK 2 | `actual_temperature_hk_2` | °C | Ist-Temperatur Heizkreis 2 |
| SOLLTEMPERATUR HK 2 | `set_temperature_hk_2` | °C | Soll-Temperatur Heizkreis 2 |
| PUFFERISTTEMPERATUR | `actual_buffer_temperature` | °C | Ist-Temperatur Pufferspeicher |
| PUFFERSOLLTEMPERATUR | `set_buffer_temperature` | °C | Soll-Temperatur Pufferspeicher |
| FROSTSCHUTZTEMPERATUR | `frost_protection_temperature` | °C | Frostschutztemperatur |

---

### WARMWASSER / DHW Section (s=1,0)

| ISG Feldname (Deutsch) | Home Assistant Sensor | Einheit | Beschreibung |
|------------------------|----------------------|---------|--------------|
| ISTTEMPERATUR | `dhw_temperature` | °C | Ist-Temperatur Warmwasser |

**Hinweis:** In der WARMWASSER-Sektion ist "ISTTEMPERATUR" ein generischer Feldname, der durch die Sektion eindeutig als Warmwasser-Temperatur identifiziert wird.

---

### WÄRMEERZEUGER EXTERN / External Heat Source Section (s=1,0)

Für Hybrid-Systeme mit externem/zusätzlichem Wärmeerzeuger.

| ISG Feldname (Deutsch) | Home Assistant Sensor | Einheit | Beschreibung |
|------------------------|----------------------|---------|--------------|
| ISTTEMPERATUR | `external_actual_temperature` | °C | Ist-Temperatur externe Wärmequelle |
| SOLLTEMPERATUR | `external_set_temperature` | °C | Soll-Temperatur externe Wärmequelle |
| BIVALENZTEMPERATUR HZG | `dual_mode_temp_hzg` | °C | Bivalenztemperatur Heizung |
| BIVALENZTEMPERATUR WW | `dual_mode_temp_ww` | °C | Bivalenztemperatur Warmwasser |
| UNTERE EINSATZGRENZE HZG | `lower_limit_hzg` | Text | Untere Einsatzgrenze Heizung (z.B. "Aus") |
| UNTERE EINSATZGRENZE WW | `lower_limit_ww` | Text | Untere Einsatzgrenze Warmwasser (z.B. "Aus") |

**Hinweis:** Die Parser verwendet sektionsspezifische Filterung, um sicherzustellen, dass generische Feldnamen wie "ISTTEMPERATUR" und "SOLLTEMPERATUR" nur in der richtigen Sektion als externe Sensoren erkannt werden.

---

### PROZESSDATEN / Process Data Section (s=1,1)

| ISG Feldname (Deutsch) | Home Assistant Sensor | Einheit | Beschreibung |
|------------------------|----------------------|---------|--------------|
| RÜCKLAUFTEMPERATUR | `return_temperature` | °C | Rücklauftemperatur |
| VORLAUFTEMPERATUR | `supply_temperature` | °C | Vorlauftemperatur |
| VERDICHTEREINTRITTSTEMPERATUR | `compressor_inlet_temperature` | °C | Temperatur am Verdichtereintritt |
| HEISSGASTEMPERATUR | `hot_gas_temperature` | °C | Heißgastemperatur |
| VERFLÜSSIGERTEMPERATUR | `condenser_temperature` | °C | Kondensatortemperatur |
| ÖLSUMPFTEMPERATUR | `oil_sump_temperature` | °C | Ölsumpftemperatur |
| VERDAMPFEREINTRITTSTEMPERATUR | `evaporator_inlet_temperature` | °C | Temperatur am Verdampfereintritt |
| VERDAMPFERAUSTRITTSTEMPERATUR | `evaporator_outlet_temperature` | °C | Temperatur am Verdampferaustritt |
| DRUCK NIEDERDRUCK | `low_pressure` | bar | Niederdruckwert |
| DRUCK HOCHDRUCK | `high_pressure` | bar | Hochdruckwert |
| WP WASSERVOLUMENSTROM | `water_flow` | l/h | Wasservolumenstrom der Wärmepumpe |
| STROM INVERTER | `inverter_current` | A | Stromaufnahme Inverter |
| SPANNUNG INVERTER | `inverter_voltage` | V | Spannung Inverter |
| ISTDREHZAHL VERDICHTER | `compressor_speed_actual` | rpm | Ist-Drehzahl Verdichter |
| SOLLDREHZAHL VERDICHTER | `compressor_speed_target` | rpm | Soll-Drehzahl Verdichter |
| LÜFTERLEISTUNG RELATIV | `fan_power_relative` | % | Relative Lüfterleistung |
| INVERTER AUFNAHMELEISTUNG | `inverter_power` | W | Inverter Aufnahmeleistung |
| AUFNAHMELEISTUNG INVERTER | `inverter_power_input` | W | Inverter Eingangsleistung |

---

### WÄRMEMENGE / Amount of Heat Section (s=1,1)

| ISG Feldname (Deutsch) | Home Assistant Sensor | Einheit | Beschreibung |
|------------------------|----------------------|---------|--------------|
| HEIZEN 1-24 h | `heat_produced_today` | kWh | Heute erzeugte Wärmemenge Heizung |
| HEIZEN 1-12 M | `total_heat_produced` | kWh | Gesamt erzeugte Wärmemenge Heizung (1-12 Monate) |
| WARMWASSER 1-24 h | `dhw_produced_today` | kWh | Heute erzeugte Wärmemenge Warmwasser |
| WARMWASSER 1-12 M | `total_dhw_produced` | kWh | Gesamt erzeugte Wärmemenge Warmwasser (1-12 Monate) |

---

### STROMVERBRAUCH / Power Consumption Section (s=1,1)

| ISG Feldname (Deutsch) | Home Assistant Sensor | Einheit | Beschreibung |
|------------------------|----------------------|---------|--------------|
| HEIZEN 1-24 h | `heating_consumed_today` | kWh | Heute verbrauchter Strom Heizung |
| HEIZEN 1-12 M | `total_heating_consumed` | kWh | Gesamt verbrauchter Strom Heizung (1-12 Monate) |
| WARMWASSER 1-24 h | `dhw_consumed_today` | kWh | Heute verbrauchter Strom Warmwasser |
| WARMWASSER 1-12 M | `total_dhw_consumed` | kWh | Gesamt verbrauchter Strom Warmwasser (1-12 Monate) |

---

### EFFIZIENZ / Efficiency Section (s=1,1)

| ISG Feldname (Deutsch) | Home Assistant Sensor | Einheit | Beschreibung |
|------------------------|----------------------|---------|--------------|
| HEIZEN 1-24 h | `efficiency_heating_today` | COP | COP Heizung heute |
| HEIZEN 1-12 M | `efficiency_heating_1_12m` | COP | COP Heizung 1-12 Monate |
| HEIZEN 13-24 M | `efficiency_heating_13_24m` | COP | COP Heizung 13-24 Monate |
| WARMWASSER 1-24 h | `efficiency_dhw_today` | COP | COP Warmwasser heute |
| WARMWASSER 1-12 M | `efficiency_dhw_1_12m` | COP | COP Warmwasser 1-12 Monate |
| WARMWASSER 13-24 M | `efficiency_dhw_13_24m` | COP | COP Warmwasser 13-24 Monate |

---

### DIAGNOSE / Diagnostics Section (s=2,7)

| ISG Feldname (Deutsch) | Home Assistant Sensor | Einheit | Beschreibung |
|------------------------|----------------------|---------|--------------|
| VD HEIZUNG | `runtime_vd_heating` | h | Laufzeit Verdichter Heizung |
| VD WARMWASSER | `runtime_vd_dhw` | h | Laufzeit Verdichter Warmwasser |
| VD ABTAUEN | `runtime_vd_defrost` | h | Laufzeit Verdichter Abtauen |
| ABTAUZEIT | `defrost_time` | min | Abtauzeit |
| ANZAHL ABTAUVORGÄNGE | `defrost_starts` | Anzahl | Anzahl der Abtauvorgänge |
| KOMPRESSOR | `compressor_starts` | Anzahl | Anzahl Verdichter-Starts |

---

### ISG-NETZWERK / Network Section (s=5,0)

| ISG Feldname (Deutsch) | Home Assistant Sensor | Beschreibung |
|------------------------|----------------------|--------------|
| MAC-ADRESSE | `mac_address` | MAC-Adresse des ISG |

---

## Sektionsspezifisches Parsing

Die Integration verwendet **kontextbezogenes Parsing**, um Konflikte bei generischen Feldnamen zu vermeiden:

### Generische Feldnamen

Einige Feldnamen erscheinen in mehreren Sektionen. Die Parser erkennt diese anhand der Sektion:

| Feldname | In WARMWASSER-Sektion | In WÄRMEERZEUGER EXTERN-Sektion | In PROZESSDATEN-Sektion |
|----------|----------------------|--------------------------------|------------------------|
| ISTTEMPERATUR | `dhw_temperature` | `external_actual_temperature` | - |
| SOLLTEMPERATUR | - | `external_set_temperature` | - |
| FROSTSCHUTZTEMPERATUR | - | - | `frost_protection_temperature` |
| AUSSENTEMPERATUR | `outside_temperature` | - | `outside_temperature` |

### Wie funktioniert die Sektion-Erkennung?

1. **Sektion-Überschrift erkennen:** Der Parser liest die Tabellenüberschrift (z.B. "WARMWASSER", "WÄRMEERZEUGER EXTERN")
2. **Kontext setzen:** Basierend auf der Überschrift wird ein Sektionskontext festgelegt
3. **Feldnamen filtern:** Nur Sensoren, die zur aktuellen Sektion gehören, werden für das Matching berücksichtigt
4. **Eindeutige Zuordnung:** Dadurch wird sichergestellt, dass "ISTTEMPERATUR" in der WARMWASSER-Sektion zu `dhw_temperature` wird und in der WÄRMEERZEUGER EXTERN-Sektion zu `external_actual_temperature`

---

## Nicht gemappte Feldnamen

Einige Feldnamen werden aus den Testdaten extrahiert, aber nicht als Sensoren bereitgestellt (z.B. nur als Anzeigelabel verwendet):

- **ACTUAL_TEMPERATURE_1**: Wird für Raumtemperatur verwendet, aber über `room_temperature` abgebildet
- **RELATIVE_HUMIDITY_1**: Wird für Luftfeuchtigkeit verwendet, aber über `room_relative_humidity` abgebildet
- **VD_HEATING_SUM, NHZ_HEATING_SUM, NHZ_DHW_SUM**: Interne Parsing-Keys ohne direkte Sensor-Zuordnung

---

## Weitere Informationen

- **Quellcode:** Siehe `custom_components/stiebel_eltron_http/i18n/de.py` für alle deutschen Übersetzungen
- **Sensor-Definitionen:** Siehe `custom_components/stiebel_eltron_http/sensor.py` für Sensor-Konfigurationen
- **Tests:** Testdaten befinden sich in `scripts/testdata/s_*_de.html`

---

## Version

Dokumentation erstellt für Branch: `feature/improve-parsing-and-sensors`  
Datum: 23. November 2025
