# Scripts Directory

This directory contains diagnostic tools, utilities, and debugging scripts for the Stiebel Eltron HTTP integration.

## Structure

```
scripts/
├── diagnostic/         # Production diagnostic tools (committed)
├── debug/             # Ad-hoc debugging scripts (gitignored)
├── tools/             # Utility scripts
├── script_helpers.py  # Shared utilities for all scripts
└── testdata/          # Test HTML files from ISG devices
```

## Production Diagnostic Tools (`diagnostic/`)

These are committed and maintained tools for ongoing diagnostics:

### `check_mapping_overlaps.py`
Detects overlapping aliases in `mapping.py` that could cause ambiguous matching.

**Usage:**
```bash
python scripts/diagnostic/check_mapping_overlaps.py
```

**Output:** Lists all aliases that appear in multiple canonical keys.

### `check_all_sensors_all_languages.py`
Verifies that all expected sensors are extracted correctly across all 12 supported languages.

**Usage:**
```bash
python scripts/diagnostic/check_all_sensors_all_languages.py
```

**Output:** Reports missing sensors per language with detailed analysis.

### `analyze_overlaps.py`
Categorizes overlapping aliases into types (contextual, generic, real conflicts).

**Usage:**
```bash
python scripts/diagnostic/analyze_overlaps.py
```

**Output:** Categorized overlap report with recommendations.

### `show_real_conflicts.py`
Provides detailed analysis of real alias conflicts with testdata evidence and fix guidance.

**Usage:**
```bash
python scripts/diagnostic/show_real_conflicts.py
```

**Output:** Box-formatted detailed explanations with fix recommendations.

### `check_de_labels.py`
Inspects HTML structure and labels from any language testdata file.

**Usage:**
```bash
python scripts/diagnostic/check_de_labels.py scripts/testdata/s_1_1_fr.html
```

**Output:** Table headers and all row labels from the specified file.

## Utility Tools (`tools/`)

### `fetch_testdata.py`
Fetches ISG pages from a device and saves them as test HTML files.

**Usage:**
```bash
# Fetch all pages for current language
python scripts/tools/fetch_testdata.py --base http://192.168.1.50

# Fetch all languages
python scripts/tools/fetch_testdata.py --base http://servicewelt.localiot --all-languages

# Fetch specific endpoints
python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --endpoints "/?s=1,1" "/?s=2,7"

# Keep original values (no harmonization)
python scripts/tools/fetch_testdata.py --base http://192.168.1.50 --no-harmonize
```

**Features:**
- Auto-detects available languages
- Harmonizes numeric values for consistent cross-language testing
- Supports custom endpoints

### `extract_labels.py`
Extracts all unique labels from testdata HTML files.

**Usage:**
```bash
python scripts/tools/extract_labels.py
```

### `extract_lang_labels.py`
Extracts language-specific labels from testdata files.

**Usage:**
```bash
python scripts/tools/extract_lang_labels.py
```

## Debug Scripts (`debug/`)

Ad-hoc debugging scripts for specific investigations. These are not committed to version control.

Common debug scripts:
- `debug_dhw_de.py` - Debug DHW temperature extraction
- `debug_s_1_8.py` - Debug s=1,8 page parsing
- `debug_amount_of_heat.py` - Debug amount of heat extraction
- `compare_*.py` - Compare extraction across languages/pages
- `find_*.py` - Find specific labels in testdata

## Shared Utilities (`script_helpers.py`)

Common functions used by multiple scripts:

```python
from script_helpers import (
    setup_import_path,           # Add project root to Python path
    load_integration_modules,    # Load scraper, mapping, parsing, const
    load_test_helper,           # Load test module loader
    extract_aliases_from_dict_str, # Parse HEADER_ALIASES dict
    read_mapping_file,          # Read and parse mapping.py
    get_testdata_dir,          # Get testdata directory path
    ALIAS_REGEX,               # Regex for extracting aliases
)
```

## Testing

All diagnostic and utility scripts should work independently without requiring a Home Assistant installation. They use the custom module loading pattern from `tests/test_scraper_localization.py`.

## Development Workflow

1. **Finding issues**: Use `check_mapping_overlaps.py` and `check_all_sensors_all_languages.py`
2. **Investigating**: Create ad-hoc scripts in `debug/` folder
3. **Verifying fixes**: Run all tests with `python -m pytest tests/ -v`
4. **Fetching new testdata**: Use `fetch_testdata.py` when device firmware updates

## Contributing

When adding new diagnostic scripts:
1. Place production tools in `diagnostic/`
2. Place one-off debugging scripts in `debug/`
3. Use `script_helpers.py` for common functionality
4. Add documentation to this README
5. Ensure scripts work without Home Assistant runtime
