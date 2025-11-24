# Adding New Sensors from Test Data

This guide describes the complete process for adding new sensors to the Stiebel Eltron ISG integration when you have HTML test data from new pages.

> **📝 How to use this guide**: Code examples marked with **📝 Customize** show placeholders you need to replace with your actual values. See [scripts/samples/](scripts/samples/) for complete code templates with `### USER:` markers indicating customization points.

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step-by-Step Process](#step-by-step-process)
4. [Translation System Architecture](#translation-system-architecture)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [Utility Scripts Reference](#utility-scripts-reference)
8. [Sample Scripts](#sample-scripts)

## Overview

The integration uses a **two-tier translation system**:

1. **i18n/*.py files** - Parsing translations for finding fields in HTML
   - Contains field names AS THEY APPEAR in the HTML
   - Used by the scraper to locate fields during parsing
   - Language-specific parsing aliases

2. **translations/*.json files** - UI display names for Home Assistant
   - Contains user-facing sensor names with section prefixes for clarity
   - Shown in Home Assistant UI
   - Can differ from HTML field names

The extraction uses **structure-based mapping**: `(page, section_index, field_index) → sensor_key`
- Language-agnostic: Position is the same across all languages (same firmware)
- Deterministic: No keyword matching failures
- Complete: Covers all sensors systematically

## Prerequisites

Before starting, you need:
- HTML test data files from the new ISG page(s) for all 10 languages:
  - German (de), English (en), French (fr), Dutch (nl), Italian (it)
  - Swedish (sv), Spanish (es), Polish (pl), Czech (cs), Hungarian (hu)
  - Finnish (fi), Danish (da)
- The page URL pattern (e.g., `?s=1,9` for page 1, section 9)
- Basic understanding of the device's sensor structure

## Step-by-Step Process

### Phase 1: Add Page to Fetch Configuration

**1.1 Update the scraper to fetch the new page**

**1.1 Update the scraper to fetch the new page**

See the complete template in [scripts/samples/template_add_new_page.py](scripts/samples/template_add_new_page.py).

Edit `custom_components/stiebel_eltron_http/scraper.py` and add your page to the fetch list:

```python
async def async_fetch_data(self) -> dict[str, Any]:
    """Fetch data from all pages."""
    pages = [
        ("?s=1,0", self._extract_info_system),
        ("?s=1,1", self._extract_info_heatpump),
        ("?s=1,8", self._extract_info_efficiency),
        ("?s=2,7", self._extract_info_diagnosis),
        ("?s=1,9", self._extract_info_new_page),    # <- ADD YOUR PAGE HERE
    ]
```

> **📝 Customize**: Change `?s=1,9` to your page URL and `_extract_info_new_page` to a descriptive method name.

**1.2 Create the extractor method**

Add a new extraction method in `scraper.py` (see template for complete implementation):

```python
def _extract_info_new_page(self, html: str) -> dict[str, Any]:
    """Extract data from the new page (s=1,9)."""
    # See scripts/samples/template_add_new_page.py for complete structure
    soup = BeautifulSoup(html, "html.parser")
    data = {}
    # Structure-based extraction logic goes here (see Phase 3)
    return data
```

> **📝 Customize**: Update docstring and method name to match your page.

### Phase 2: Collect and Analyze Test Data

**2.1 Collect HTML files**

Use the existing **`scripts/tools/fetch_testdata.py`** utility to automatically fetch test data from your ISG device:

```bash
# Fetch all default pages for all languages
python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --all-languages

# Fetch specific page for all languages
python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --all-languages --endpoints "/?s=1,9"

# Fetch multiple new pages
python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --all-languages --endpoints "/?s=1,9" "/?s=1,10"

# Keep original values (no harmonization)
python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --all-languages --no-harmonize
```

The script will:
- Auto-detect all available languages from the device
- Fetch specified pages for each language
- Save files as `scripts/testdata/s_1_9_de.html`, `s_1_9_en.html`, etc.
- By default, harmonize values across languages for consistent testing
- Sanitize sensitive data (MAC addresses, IP addresses)

**Manual collection** (if needed):
- Access your ISG web interface
- Navigate to the new page (e.g., `http://192.168.1.50/?s=1,9`)
- Change language in settings (usually at `/?s=5,3`)
- Save HTML for each language: `scripts/testdata/s_1_9_{lang}.html`
- Repeat for all 12 languages: de, en, fr, nl, it, sv, es, pl, cs, hu, fi, da

**2.2 Analyze page structure**

Use the general-purpose structure analyzer from **`scripts/samples/analyze_page_structure.py`**:

```bash
# Analyze structure of a specific page
python scripts/samples/analyze_page_structure.py scripts/testdata/s_1_9_de.html
```

This script will show:
- Number of sections
- Section names (with indices)
- Field positions and names
- Field values

See [scripts/samples/analyze_page_structure.py](scripts/samples/analyze_page_structure.py) for the implementation.

**2.3 Run analysis across all languages**

Verify that all languages have the same structure using **`scripts/samples/verify_structure_consistency.py`**:

```bash
# Check structure consistency across all 12 languages
python scripts/samples/verify_structure_consistency.py s_1_9
```

This will show:
- Number of sections in each language
- Number of fields per section
- Whether all languages have identical structure

See [scripts/samples/verify_structure_consistency.py](scripts/samples/verify_structure_consistency.py) for the implementation.

All languages MUST have the same structure for structure-based extraction to work correctly.

### Phase 3: Extract Field Names and Values

**3.1 Identify which fields to extract**

Determine which sensors are useful for Home Assistant:
- Temperature sensors (°C)
- Energy sensors (kWh, MWh)
- Power sensors (kW)
- Pressure sensors (bar)
- Flow sensors (l/min)
- Status/mode strings
- Percentages (%)

**3.2 Create structure mapping**

Add sensor key constants to `custom_components/stiebel_eltron_http/const.py`:

```python
# Sensor keys for new page
NEW_SENSOR_1_KEY = "new_sensor_1"
NEW_SENSOR_2_KEY = "new_sensor_2"
# ... add all new sensor keys
```

> **📝 Customize**: Use descriptive names that match your sensor purpose (e.g., `INVERTER_POWER_KEY`, `DHW_TEMPERATURE_KEY`).

Then update the **structure mapping** in **`scripts/map_translations_structure_based.py`**:

```python
FIELD_STRUCTURE_MAP = {
    # ... existing mappings ...
    
    # ============================================================================
    # s_1_9: New page description  <- DESCRIBE YOUR PAGE
    # ============================================================================
    # Section 0: Section name      <- ADD SECTION DESCRIPTION
    ('s_1_9', 0, 0): 'new_sensor_1',
    ('s_1_9', 0, 1): 'new_sensor_2',
    
    # Section 1: Another section
    ('s_1_9', 1, 0): 'new_sensor_3',
    # ... map all fields by position
}
```

> **📝 Customize**: Replace `s_1_9` with your page ID, add comments for each section, and map all fields using the structure from Phase 2.2 analysis.

See [scripts/samples/template_add_new_page.py](scripts/samples/template_add_new_page.py) for a complete template.

**3.3 Implement structure-based extraction**

Update the extractor method (see [scripts/samples/template_add_new_page.py](scripts/samples/template_add_new_page.py) for complete template):

```python
def _extract_info_new_page(self, html: str) -> dict[str, Any]:
    """Extract data from new page using structure-based mapping."""
    soup = BeautifulSoup(html, "html.parser")
    data = {}
    sections = soup.find_all('table', class_='info')
    
    for section_idx, section in enumerate(sections):
        rows = section.find_all('tr')[1:]  # Skip header
        
        for field_idx, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            
            # Look up sensor key using structure map
            map_key = ("s_1_9", section_idx, field_idx)  # <- CHANGE PAGE ID
            sensor_key = FIELD_STRUCTURE_MAP.get(map_key)
            
            if sensor_key:
                value_text = cells[1].get_text(strip=True)
                value = self._parse_value(value_text, sensor_key)
                if value is not None:
                    data[sensor_key] = value
    
    return data
```

> **📝 Customize**: Change `"s_1_9"` to match your page ID from the structure map.

### Phase 4: Extract Translations

**4.1 Extract field names from all languages**

**RECOMMENDED**: Use the custom extraction script with section prefixes from **`scripts/samples/extract_with_section_prefixes.py`**:

```bash
# Extract translations with section prefixes for all languages
python scripts/samples/extract_with_section_prefixes.py s_1_9
```

This script will:
- Extract field names WITH section prefixes from all 12 languages
- Output JSON ready to paste into `translations/*.json` files
- Save results to `scripts/extracted_s_1_9_translations.json`

See [scripts/samples/extract_with_section_prefixes.py](scripts/samples/extract_with_section_prefixes.py) for the implementation.

**Why section prefixes?**
- Provides context in the UI (e.g., "DHW Actual Temperature" vs just "Actual Temperature")
- Prevents naming conflicts between sections
- Matches the expected format in JSON translation files

**Alternative**: You can use the existing **`map_translations_structure_based.py`** script which generates translations based on the structure map:

```bash
# Run the structure-based translation extraction (preview mode)
python scripts/map_translations_structure_based.py 2>&1 | less
```

**Important Notes about map_translations_structure_based.py**:
- This script extracts **raw field names** from HTML (unprefixed)
- For disambiguation, you need to **manually add section prefixes** to the output
- The script shows what fields exist at each position across all languages
- Use the output as a guide, but add section prefixes for clarity in translations/*.json

> **📝 Note**: The `extract_with_section_prefixes.py` sample script (recommended above) already implements the proper extraction logic with section prefixes. Use that script instead of manually coding the extraction.

**4.2 Add section name translations**

Extract section names for i18n parsing using **`scripts/samples/extract_section_names.py`**:

```bash
# Extract section names from all languages
python scripts/samples/extract_section_names.py s_1_9
```

This script will:
- Extract section names from all 12 languages
- Output JSON with indexed section names (section_0, section_1, etc.)
- Save results to `scripts/extracted_s_1_9_sections.json`

See [scripts/samples/extract_section_names.py](scripts/samples/extract_section_names.py) for the implementation.

You'll need to add these section names to the i18n/*.py files for parsing.
```

### Phase 5: Update Translation Files

**5.1 Update translations/*.json files**

Add sensor entries to each language's JSON file with **section-prefixed names** for UI clarity:

```json
{
  "entity": {
    "sensor": {
      "new_sensor_1": {
        "name": "SECTION NAME FIELD NAME"
      },
      "new_sensor_2": {
        "name": "SECTION NAME FIELD NAME"
      }
    }
  }
}
```

> **📝 Customize**: Replace `new_sensor_1`, `new_sensor_2` with your actual sensor keys, and use the output from `extract_with_section_prefixes.py` for the translated names.

Example for German (`translations/de.json`):
```json
{
  "new_sensor_1": {
    "name": "PROZESSDATEN RÜCKLAUFTEMPERATUR"
  }
}
```

**5.2 Update i18n/*.py files with parsing aliases**

Add **unprefixed field names** (as they appear in HTML) to `i18n/*.py` files for parsing:

Example for German (`i18n/de.py`):
```python
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    # Existing entries...
    
    # New section name for structure identification
    CanonicalKey.NEW_SECTION: [
        "SECTION NAME IN GERMAN",  # <- FROM extract_section_names.py
    ],
    
    # New field names (unprefixed, as they appear in HTML)
    CanonicalKey.NEW_SENSOR_1: [
        "RÜCKLAUFTEMPERATUR",  # <- WITHOUT section prefix
    ],
    CanonicalKey.NEW_SENSOR_2: [
        "VORLAUFTEMPERATUR",  # <- WITHOUT section prefix
    ],
}
```

> **📝 Customize**: 
> - Section names: Use output from `extract_section_names.py`
> - Field names: Use the "value" part from `extract_with_section_prefixes.py` (without the section prefix)
> - Repeat for all 12 language files (de, en, fr, nl, it, sv, es, pl, cs, hu, fi, da)

**Important**: 
- **translations/*.json**: Use section-prefixed names for UI display (`"SECTION NAME FIELD NAME"`)
- **i18n/*.py**: Use unprefixed field names for HTML parsing (`"FIELD NAME"`)

### Phase 6: Define Sensor Entities

**6.1 Add sensor definitions**

See the complete template with examples in [scripts/samples/template_sensor_definitions.py](scripts/samples/template_sensor_definitions.py).

Edit `custom_components/stiebel_eltron_http/sensor.py`:

```python
# Import new keys
from .const import (
    NEW_SENSOR_1_KEY,
    NEW_SENSOR_2_KEY,
    # ...
)

# Add sensor descriptions
SENSORS: tuple[SensorEntityDescription, ...] = (
    # ... existing sensors ...
    
    # Temperature sensor example
    SensorEntityDescription(
        key=NEW_SENSOR_1_KEY,
        name="New Sensor 1",  # <- CUSTOMIZE NAME
        translation_key=NEW_SENSOR_1_KEY,
        device_class=SensorDeviceClass.TEMPERATURE,  # <- CHOOSE DEVICE CLASS
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,  # <- CHOOSE STATE CLASS
    ),
    # ... add all new sensors
)
```

> **📝 Customize**: Choose appropriate `device_class`, `native_unit_of_measurement`, and `state_class` for each sensor. See template file for common combinations (temperature, energy, power, pressure, flow, percentage, etc.).

**6.2 Add canonical keys**

Edit `custom_components/stiebel_eltron_http/i18n/canonical_keys.py`:

```python
class CanonicalKey(str, Enum):
    """Canonical keys for all translatable fields."""
    
    # Existing keys...
    
    # New section
    NEW_SECTION = "NEW_SECTION"  # <- CUSTOMIZE SECTION NAME
    
    # New sensors
    NEW_SENSOR_1 = "NEW_SENSOR_1"  # <- USE UPPERCASE VERSION OF KEY
    NEW_SENSOR_2 = "NEW_SENSOR_2"
    # ...
```

> **📝 Customize**: Use descriptive, uppercase names that match your sensor keys.

### Phase 7: Add Tests

**7.1 Add test data files**

Ensure all language HTML files are in `scripts/testdata/`:
```
s_1_9_de.html, s_1_9_en.html, s_1_9_fr.html, etc.
```

**7.2 Create extraction tests**

Add test in `tests/test_values_not_none.py` (automatic via parametrization).

**7.3 Create localization tests**

Add tests for all languages in `tests/test_scraper_localization.py`:

```python
@pytest.mark.parametrize("file_path", [
    TESTDATA_DIR / "s_1_9_de.html",  # <- CHANGE PAGE ID
    TESTDATA_DIR / "s_1_9_en.html",
    # ... all 12 languages
])
def test_new_page_parsing(scraper_client, file_path: Path):  # <- CUSTOMIZE TEST NAME
    """Ensure the scraper extracts values from new page."""
    html = file_path.read_text(encoding="utf-8")
    data = scraper_client._extract_info_new_page(html)  # <- YOUR EXTRACTOR METHOD
    
    # Verify expected keys are present
    assert NEW_SENSOR_1_KEY in data  # <- YOUR SENSOR KEYS
    assert NEW_SENSOR_2_KEY in data
    
    # Verify values are correct type
    assert isinstance(data[NEW_SENSOR_1_KEY], (int, float))
```

> **📝 Customize**: 
> - Change `s_1_9` to your page ID
> - Update test name to be descriptive
> - Call your actual extractor method
> - Assert all your sensor keys are present
> - Add type checks appropriate for your sensors

### Phase 8: Verify Translations

**8.1 Run translation summary**

Use the existing **`translation_summary.py`** utility:

```bash
python scripts/translation_summary.py
```

Expected output:
```
====================================================================================================
TRANSLATION COMPLETENESS SUMMARY
====================================================================================================

Sensor counts per language:
---------------------------------------------------------------------------------------------------
  CS: 60 sensors  # 55 existing + 5 new
  DA: 60 sensors
  ES: 60 sensors
  FI: 60 sensors
  FR: 60 sensors
  HU: 60 sensors
  IT: 60 sensors
  NL: 60 sensors
  PL: 60 sensors
  SV: 60 sensors

Total unique sensors across all languages: 60

Sensor consistency check:
---------------------------------------------------------------------------------------------------
  DA: ✓ IDENTICAL to CS
  ES: ✓ IDENTICAL to CS
  FI: ✓ IDENTICAL to CS
  FR: ✓ IDENTICAL to CS
  HU: ✓ IDENTICAL to CS
  IT: ✓ IDENTICAL to CS
  NL: ✓ IDENTICAL to CS
  PL: ✓ IDENTICAL to CS
  SV: ✓ IDENTICAL to CS

✅ SUCCESS: All languages have IDENTICAL sensor sets!
```

**8.2 Check for duplicate names**

Use the existing **`check_duplicate_names.py`** utility:

```bash
python scripts/check_duplicate_names.py
```

Should report no duplicates if section prefixes are used correctly. If duplicates are found, add section prefixes to the affected sensors in translations/*.json files.

### Phase 9: Run Tests

**9.1 Run full test suite**

```bash
python -m pytest tests/ -v
```

All tests should pass (except intentional xfails).

**9.2 Run specific tests**

```bash
# Test new page extraction
python -m pytest tests/test_scraper_localization.py::test_new_page_parsing -v

# Test values are not None
python -m pytest tests/test_values_not_none.py -k "s_1_9" -v
```

## Translation System Architecture

### Two-Tier System

```
┌─────────────────────────────────────────────────────────────┐
│ HTML (ISG Web Interface)                                    │
│ ┌────────────────┐                                          │
│ │ ISTTEMPERATUR  │ ◄─── Field name as shown in HTML        │
│ │ 23,3°C         │                                          │
│ └────────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
           │
           │ Scraper uses i18n/*.py to FIND field
           ▼
┌─────────────────────────────────────────────────────────────┐
│ i18n/de.py (PARSING)                                        │
│ CanonicalKey.ACTUAL_TEMPERATURE: ["ISTTEMPERATUR"]          │
│                                                              │
│ → Unprefixed field name for matching HTML                   │
│ → Used by scraper to locate fields                          │
└─────────────────────────────────────────────────────────────┘
           │
           │ Maps to canonical key
           ▼
┌─────────────────────────────────────────────────────────────┐
│ translations/de.json (DISPLAY)                              │
│ "dhw_temperature": {                                        │
│   "name": "WARMWASSER ISTTEMPERATUR"                        │
│ }                                                            │
│                                                              │
│ → Section-prefixed name for UI clarity                      │
│ → Shown to user in Home Assistant                           │
└─────────────────────────────────────────────────────────────┘
```

### Why Two Tiers?

1. **HTML Parsing**: HTML uses short, generic field names without section prefixes
   - "ISTTEMPERATUR" appears in DHW, Heating, External sections
   - Parser needs exact match to HTML text
   - i18n/*.py provides these unprefixed names

2. **UI Display**: Users need descriptive names to distinguish sensors
   - "WARMWASSER ISTTEMPERATUR" vs "WÄRMEERZEUGER EXTERN ISTTEMPERATUR"
   - Section prefixes prevent confusion
   - translations/*.json provides these prefixed names

### Adding Parsing Aliases vs Display Names

**When to add to i18n/*.py (parsing aliases)**:
- Field name as it appears in HTML (unprefixed)
- Parser can't find field in HTML
- Generic field names used in multiple sections
- Section header names for structure identification

**When to add to translations/*.json (display names)**:
- User-facing sensor name in Home Assistant UI
- Should include section prefix for disambiguation
- Can be more descriptive than HTML field name
- Follows Home Assistant naming conventions

## Testing

### Test Coverage Checklist

- [ ] All language HTML files collected (12 languages minimum)
- [ ] Structure analysis confirms consistent layout
- [ ] Field extraction works for all languages
- [ ] Translation files updated for all languages
- [ ] i18n parsing aliases added for all languages
- [ ] Sensor definitions added
- [ ] Canonical keys defined
- [ ] Tests added for new page
- [ ] Full test suite passes
- [ ] Translation summary shows all languages identical
- [ ] No duplicate sensor names

### Common Test Failures

**"extractor returned None for key X"**
- Missing parsing alias in i18n/*.py
- Check HTML field name matches alias exactly
- Add unprefixed field name to PARSING_TRANSLATIONS

**"0 metrics parsed from s_1_9_hu.html"**
- Section name mismatch in i18n/hu.py
- Check section header name exactly matches HTML
- Verify all field parsing aliases present

**"Languages have different sensor counts"**
- Missing translation in one or more languages
- Run extraction script to generate all translations
- Ensure all 12+ languages updated

## Troubleshooting

### Issue: Parser Can't Find Field

**Symptom**: Sensor value is None or missing

**Debug steps**:
1. Check HTML field name:
   ```python
   from bs4 import BeautifulSoup
   html = open('scripts/testdata/s_1_9_de.html', 'r', encoding='utf-8').read()
   soup = BeautifulSoup(html, 'html.parser')
   sections = soup.find_all('table', class_='info')
   # Examine field names
   ```

2. Verify i18n parsing alias matches exactly:
   ```python
   from custom_components.stiebel_eltron_http.i18n import de
   print(de.PARSING_TRANSLATIONS[CanonicalKey.NEW_SENSOR])
   ```

3. Add missing alias to i18n/*.py (unprefixed!)

### Issue: Duplicate Sensor Names

**Symptom**: Warning about duplicate names in translation summary

**Solution**: Add section prefixes to translations/*.json
```json
// Before (ambiguous)
"temperature": {"name": "TEMPERATUR"}

// After (clear)
"dhw_temperature": {"name": "WARMWASSER TEMPERATUR"}
"external_temperature": {"name": "WÄRMEERZEUGER EXTERN TEMPERATUR"}
```

### Issue: Section Name Mismatch

**Symptom**: No fields extracted from section in specific language

**Debug**:
```python
# Check actual section name in HTML
from bs4 import BeautifulSoup
html = open('scripts/testdata/s_1_9_hu.html', 'r', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')
sections = soup.find_all('table', class_='info')
for i, s in enumerate(sections):
    print(f"Section {i}: {s.find('th').get_text(strip=True)}")
```

Compare with i18n file and fix exact spelling/spacing.

### Issue: Import Errors After Adding Canonical Keys

**Symptom**: `ImportError: cannot import name 'NEW_SENSOR_KEY'`

**Solution**: Ensure key is added in all required places:
1. `i18n/canonical_keys.py` - CanonicalKey enum
2. `const.py` - Key constant definition
3. `sensor.py` - Import statement

## Summary

Adding new sensors requires coordinated updates across multiple files:

1. **Data Collection**: HTML files from all languages
2. **Analysis**: Structure and field identification
3. **Constants**: Sensor keys and structure mapping
4. **Extraction**: Scraper methods and parsing logic
5. **Translations**: Both i18n (parsing) and JSON (display)
6. **Entities**: Sensor definitions and canonical keys
7. **Tests**: Verification across all languages

The key insight: **i18n files contain HTML field names for parsing, JSON files contain user-friendly display names with section prefixes**.

## Utility Scripts Reference

The `scripts/` directory contains many utility scripts to help with the sensor addition process. Here are the key ones:

### Data Collection Scripts

**`tools/fetch_testdata.py`** ⭐ **ESSENTIAL FOR DATA COLLECTION**
- Automatically fetches HTML pages from ISG device for all languages
- Auto-detects available languages from device
- Harmonizes values across languages for consistent testing
- Sanitizes sensitive data (MAC/IP addresses)
- Usage:
  ```bash
  # Fetch all default pages for all languages
  python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --all-languages
  
  # Fetch specific new page(s)
  python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --all-languages --endpoints "/?s=1,9"
  
  # Keep original values (no harmonization)
  python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --all-languages --no-harmonize
  ```
- Saves to: `scripts/testdata/s_X_Y_{lang}.html`
- **Pro tip**: Use `--harmonize` (default) for test data to ensure all languages have identical values

### Core Translation Scripts

**`map_translations_structure_based.py`** ⭐ **IMPORTANT - USE WITH CAUTION**
- Generates translations for ALL languages based on structure mapping
- Uses `FIELD_STRUCTURE_MAP` to extract field names by position
- **Extracts RAW field names without section prefixes**
- **Note**: For UI clarity, you should manually add section prefixes to the output
- Best used as a reference/verification tool rather than direct copy-paste
- Usage: `python scripts/map_translations_structure_based.py` (preview mode - shows updates but doesn't save)
- **Recommendation**: Create custom extraction scripts that add section prefixes (see Phase 4.1 in guide)

**`translation_summary.py`** ⭐
- Shows sensor count for each language
- Verifies all languages have identical sensor sets
- Reports which languages are missing sensors
- Usage: `python scripts/translation_summary.py`

**`check_duplicate_names.py`** ⭐
- Checks if any language has duplicate sensor names
- Identifies where section prefixes are needed
- Usage: `python scripts/check_duplicate_names.py`

### Analysis Scripts

**`analyze_structure.py`**
- Analyzes HTML structure of test data files
- Shows sections, field positions, and values
- **Note**: Currently hardcoded to analyze s_1_1 files for German/Swedish comparison
- **For new pages**: Create a custom analysis script (see Phase 2.2 template)
- Usage: `python scripts/analyze_structure.py`

**`analyze_all_pages.py`**
- Comprehensive analysis of all test data pages
- Shows structure across multiple pages and languages
- Usage: `python scripts/analyze_all_pages.py`

**`verify_translations_vs_testdata.py`**
- Verifies translation files match actual test data
- Identifies missing or extra translations
- Usage: `python scripts/verify_translations_vs_testdata.py`

**`extract_all_languages.py`**
- Extracts field names from all language test data files
- Useful for getting raw field names before structure mapping
- Usage: `python scripts/extract_all_languages.py`

### Helper Scripts for Specific Tasks

**`add_dhw_parsing_aliases.py`**
- Bulk adds DHW temperature aliases to i18n files
- Example of automated i18n file updates
- Usage: See script for configuration

**`extract_parsing_aliases.py`**
- Extracts unprefixed field names from HTML for parsing aliases
- Useful when adding new parsing translations to i18n files
- Usage: `python scripts/extract_parsing_aliases.py`

**`check_hu_fields.py`**, **`check_hu_section.py`**
- Debug scripts for checking specific language issues

## Sample Scripts

The `scripts/samples/` directory contains reusable sample scripts that demonstrate common workflows. These scripts are designed to be general-purpose and can be used directly or adapted for specific needs.

### Extraction and Analysis Scripts

**`analyze_page_structure.py`** ⭐
- General-purpose HTML structure analyzer
- Takes HTML file path as command-line argument
- Shows sections, field positions, names, and values
- Usage: `python scripts/samples/analyze_page_structure.py scripts/testdata/s_1_9_de.html`
- See Phase 2.2 in this guide

**`verify_structure_consistency.py`** ⭐
- Verifies all language versions of a page have identical structure
- Essential before implementing structure-based extraction
- Usage: `python scripts/samples/verify_structure_consistency.py s_1_9`
- See Phase 2.3 in this guide

**`extract_with_section_prefixes.py`** ⭐ **RECOMMENDED FOR NEW PAGES**
- Extracts field names WITH section prefixes from all languages
- Output is ready to paste into translations/*.json files
- Saves results to `scripts/extracted_<page>_translations.json`
- Usage: `python scripts/samples/extract_with_section_prefixes.py s_1_9`
- See Phase 4.1 in this guide

**`extract_section_names.py`** ⭐
- Extracts section names from all languages
- Output is ready for i18n/*.py files
- Saves results to `scripts/extracted_<page>_sections.json`
- Usage: `python scripts/samples/extract_section_names.py s_1_9`
- See Phase 4.2 in this guide

### Code Templates

**`template_add_new_page.py`** 📝 **CODE TEMPLATE**
- Complete template for adding a new ISG page to the scraper
- Shows all code changes needed in scraper.py and related files
- Includes placeholders marked with `### USER:` comments for customization
- Copy relevant sections and adapt to your specific page
- See Phases 1 and 3 in this guide

**`template_sensor_definitions.py`** 📝 **CODE TEMPLATE**
- Template for adding sensor entity definitions in sensor.py
- Examples for all common sensor types (temperature, energy, power, etc.)
- Guidelines for choosing device_class and state_class
- Reference for units and sensor configurations
- See Phase 6 in this guide

**Note**: 
- Sample scripts (`.py` files without "template" prefix) can be run directly
- Template files contain code examples with `### USER:` markers showing what to customize
- All scripts demonstrate best practices for structure-based extraction with section prefixes
- Example of how to create language-specific diagnostic tools

### Development Scripts

**`analyze_all_pages.py`**
- Comprehensive analysis of all test data pages
- Shows structure across all pages and languages
- Usage: `python scripts/analyze_all_pages.py`

### Typical Workflow Using Scripts

When adding a new page (e.g., s_1_9):

1. **Collect test data** - Use the fetch script to get HTML for all languages:
   ```bash
   # Replace with your ISG device IP address
   python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --all-languages --endpoints "/?s=1,9"
   ```
   
   This will save files as `scripts/testdata/s_1_9_de.html`, `s_1_9_en.html`, etc.

2. **Analyze structure** - Create a custom analysis script:
   ```python
   #!/usr/bin/env python3
   """Analyze s_1_9 structure."""
   from bs4 import BeautifulSoup
   
   for lang in ['de', 'en', 'fr']:  # Test a few languages
       html = open(f'scripts/testdata/s_1_9_{lang}.html', encoding='utf-8').read()
2. **Verify structure consistency**:
   ```bash
   python scripts/samples/verify_structure_consistency.py s_1_9
   ```
   See [scripts/samples/verify_structure_consistency.py](scripts/samples/verify_structure_consistency.py)

3. **Update structure map** - Edit `scripts/map_translations_structure_based.py`:
   ```python
   FIELD_STRUCTURE_MAP = {
       # ... existing ...
       ('s_1_9', 0, 0): 'new_sensor_1',
       # ... add all new mappings based on structure analysis
   }
   ```

4. **Extract translations with section prefixes**:
   ```bash
   python scripts/samples/extract_with_section_prefixes.py s_1_9
   ```
   See [scripts/samples/extract_with_section_prefixes.py](scripts/samples/extract_with_section_prefixes.py)

5. **Extract section names for i18n**:
   ```bash
   python scripts/samples/extract_section_names.py s_1_9
   ```
   See [scripts/samples/extract_section_names.py](scripts/samples/extract_section_names.py)

6. **Copy translations** - Paste script output into each `translations/*.json` file

7. **Add i18n aliases** - Add unprefixed field names and section names to `i18n/*.py`:
   ```python
   # For each language, add to PARSING_TRANSLATIONS:
   CanonicalKey.NEW_SENSOR_1: ["UNPREFIXED_FIELD_NAME"],
   CanonicalKey.NEW_SECTION: ["SECTION_NAME"],
   ```

7. **Verify completeness**:
   ```bash
   python scripts/translation_summary.py
   python scripts/check_duplicate_names.py
   ```

8. **Run tests**:
   ```bash
   python -m pytest tests/ -v
   ```

### Script Maintenance Notes

- Most scripts are self-contained and work with test data files
- Scripts assume standard directory structure: `scripts/testdata/*.html`
- Many scripts output to stdout - redirect to files if needed
- Some older scripts may not match current architecture - use the ⭐ marked scripts first
