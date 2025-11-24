# Sample Scripts and Templates

This directory contains reusable scripts and code templates for adding new sensors to the Stiebel Eltron ISG integration.

## 📊 Extraction and Analysis Scripts

These scripts can be run directly to analyze ISG HTML pages and extract translations.

### `analyze_page_structure.py`
**Purpose**: Analyze the structure of an ISG HTML page

**Usage**:
```bash
python scripts/samples/analyze_page_structure.py scripts/testdata/s_1_9_de.html
```

**Output**: Shows sections, field positions, names, and values

### `verify_structure_consistency.py`
**Purpose**: Verify all 12 language versions have identical structure

**Usage**:
```bash
python scripts/samples/verify_structure_consistency.py s_1_9
```

**Output**: Confirms all languages have matching section/field counts

### `extract_with_section_prefixes.py` ⭐
**Purpose**: Extract field names WITH section prefixes for all languages

**Usage**:
```bash
python scripts/samples/extract_with_section_prefixes.py s_1_9
```

**Output**: 
- Console: Progress summary
- File: `scripts/extracted_s_1_9_translations.json` (ready for `translations/*.json`)

**Why use this**: Section prefixes provide context in the UI and prevent naming conflicts

### `extract_section_names.py`
**Purpose**: Extract section names for all languages

**Usage**:
```bash
python scripts/samples/extract_section_names.py s_1_9
```

**Output**:
- Console: Section names by language
- File: `scripts/extracted_s_1_9_sections.json` (for `i18n/*.py` files)

## 📝 Code Templates

These files contain code examples with `### USER:` markers showing what to customize.

### `template_add_new_page.py`
**Purpose**: Complete template for adding a new ISG page

**Contains**:
- Step 1: Add page to fetch list in `scraper.py`
- Step 2: Create extraction method
- Step 3: Add structure mapping in `map_translations_structure_based.py`
- Step 4: Add sensor keys to `const.py`

**Usage**: Copy relevant sections to your actual files and customize

### `template_sensor_definitions.py`
**Purpose**: Template for sensor entity definitions

**Contains**:
- Examples for all common sensor types:
  - Temperature (°C)
  - Energy (kWh, MWh)
  - Power (kW)
  - Pressure (bar)
  - Flow rate (l/min)
  - Percentage (%)
  - Status/mode (text)
- Guidelines for choosing `device_class` and `state_class`
- Reference for units and configurations

**Usage**: Copy sensor definitions to `sensor.py` and customize

## 🔧 Customization Guidelines

### In Scripts
Scripts can be run as-is. They work with any page by passing the page ID as an argument.

### In Templates
Look for `### USER:` comments in template files:

```python
# ### USER: Change this to your page ID
map_key = ("s_1_9", section_idx, field_idx)
```

### In Documentation
Look for **📝 Customize** markers in `ADDING_NEW_SENSORS.md`:

```python
> **📝 Customize**: Change `?s=1,9` to your page URL
```

## 📚 Related Documentation

See [ADDING_NEW_SENSORS.md](../../ADDING_NEW_SENSORS.md) for the complete workflow guide.

## 🧪 Testing

All scripts have been tested with existing ISG test data and work correctly on Windows.

**Note**: Console output may show Unicode encoding warnings on Windows, but files are saved correctly with UTF-8 encoding.
