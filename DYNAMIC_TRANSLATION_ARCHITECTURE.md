# Dynamic Translation Loading Architecture

## Overview

The i18n package now uses **dynamic loading from JSON files** to maintain a single source of truth for translations. This ensures that `de.py` (and other language files) stay synchronized with their corresponding `de.json` translation files.

## Architecture

### Single Source of Truth: `translations/*.json`

The `translations/de.json` file contains the user-facing entity names for Home Assistant:

```json
{
    "entity": {
        "sensor": {
            "total_heating_consumed": {
                "name": "VD HEIZEN SUMME"
            },
            "inverter_power_input": {
                "name": "AUFNAHMELEISTUNG INVERTER"
            }
            ...
        }
    }
}
```

### Dynamic Loading: `i18n/json_loader.py`

A new helper module `json_loader.py` provides the `load_translations_from_json()` function that:

1. Reads the JSON file for the specified language
2. Uses reverse mapping (const_key → canonical_key) to convert sensor names to canonical keys
3. Optionally merges with HTML field variations (see below)
4. Returns a `dict[CanonicalKey, list[str]]` ready for use

### Language Files: `i18n/de.py`

Each language file now consists of:

1. **HTML Field Variations** - Manual dictionary of strings extracted from ISG web interface HTML that DON'T have direct sensor mappings (sections, field variations, etc.)

2. **Dynamic Loading** - Call to `load_translations_from_json()` that merges JSON translations with HTML variations

```python
# Field variations extracted from HTML testdata
HTML_FIELD_VARIATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: ["WÄRMEMENGE"],
    CanonicalKey.EFFICIENCY_SECTION: ["EFFIZIENZ"],
    CanonicalKey.VD_HEATING_SUM: ["VD HEIZUNG SUMME"],
    ...
}

# Load from JSON and merge with HTML field variations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('de', HTML_FIELD_VARIATIONS)
```

## Benefits

### 1. No Duplication
- Entity names are defined once in `*.json` files
- No need to manually sync between JSON and Python files

### 2. Maintainability
- Update `de.json` → changes automatically reflected in `de.py`
- Clear separation: JSON for user-facing names, Python for HTML parsing variations

### 3. Correctness
- JSON is generated from actual testdata HTML files
- HTML field variations supplement JSON with parsing-specific strings

## What Goes Where?

### In `translations/*.json`:
- ✅ User-facing sensor names (from `sensor.name`)
- ✅ Entity names shown in Home Assistant UI
- ✅ Anything that maps to a sensor const key

### In `i18n/de.py` HTML_FIELD_VARIATIONS:
- ✅ Section headings (`WÄRMEMENGE`, `EFFIZIENZ`, etc.)
- ✅ Field variations that don't map to sensors (`VD_HEATING_SUM`)
- ✅ HTML-specific strings needed for parsing
- ✅ Unmapped canonical keys (in `ALLOWED_UNMAPPED_CANONICALS`)

## Example Flow

1. User runs `extract_entity_translations.py` → generates `translations/de.json` from HTML testdata
2. Python module loads → `de.py` calls `load_translations_from_json('de', HTML_FIELD_VARIATIONS)`
3. json_loader:
   - Reads `translations/de.json`
   - Reverses `CANONICAL_TO_CONST` mapping to find canonical keys
   - Merges JSON translations with `HTML_FIELD_VARIATIONS`
   - Returns combined dictionary
4. Runtime: Code uses `HEADER_ALIASES` which combines all 12 languages

## Files Changed

- ✅ `i18n/json_loader.py` - New helper module for dynamic loading
- ✅ `i18n/de.py` - Now uses dynamic loading instead of static dict (12 languages total)
- ✅ All tests passing (240 passed, 1 skipped)

## Reduced File Size

`de.py` before (static):
- 131 lines with hardcoded translations

`de.py` after (dynamic):
- ~50 lines with HTML variations + dynamic loading
- Automatically stays in sync with JSON

## How to Update Translations

To add or update translations:

1. **For sensor entity names**: Update `translations/de.json` directly
2. **For HTML field variations**: Update `HTML_FIELD_VARIATIONS` in `i18n/de.py`
3. Run tests to verify: `python -m pytest tests/ -v`

The system automatically merges both sources at runtime.
