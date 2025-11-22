"""Internationalization (i18n) package for Stiebel Eltron field name translations.

This package provides translations for canonical field names across 12 languages.
All translations are extracted from actual test data to ensure accuracy.

Languages supported:
- German (de)
- English (en)
- French (fr)
- Dutch (nl)
- Italian (it)
- Swedish (sv)
- Spanish (es)
- Polish (pl)
- Czech (cs)
- Hungarian (hu)
- Finnish (fi)
- Danish (da)
"""

import sys

# Import canonical keys
try:
    from .canonical_keys import CanonicalKey
except ImportError:
    # Fallback for manual module loading in tests
    CanonicalKey = sys.modules["custom_components.stiebel_eltron_http.i18n.canonical_keys"].CanonicalKey

# Import language modules - check if they're already loaded (for manual test loading)
if "custom_components.stiebel_eltron_http.i18n.de" in sys.modules:
    # Modules already loaded manually in tests
    de = sys.modules["custom_components.stiebel_eltron_http.i18n.de"]
    en = sys.modules["custom_components.stiebel_eltron_http.i18n.en"]
    fr = sys.modules["custom_components.stiebel_eltron_http.i18n.fr"]
    nl = sys.modules["custom_components.stiebel_eltron_http.i18n.nl"]
    it = sys.modules["custom_components.stiebel_eltron_http.i18n.it"]
    sv = sys.modules["custom_components.stiebel_eltron_http.i18n.sv"]
    es = sys.modules["custom_components.stiebel_eltron_http.i18n.es"]
    pl = sys.modules["custom_components.stiebel_eltron_http.i18n.pl"]
    cs = sys.modules["custom_components.stiebel_eltron_http.i18n.cs"]
    hu = sys.modules["custom_components.stiebel_eltron_http.i18n.hu"]
    fi = sys.modules["custom_components.stiebel_eltron_http.i18n.fi"]
    da = sys.modules["custom_components.stiebel_eltron_http.i18n.da"]
else:
    # Normal import
    from . import de, en, fr, nl, it, sv, es, pl, cs, hu, fi, da

# Combine all language translations into a single HEADER_ALIASES dict
# This mirrors the structure of mapping.py HEADER_ALIASES
HEADER_ALIASES: dict[CanonicalKey, list[str]] = {}

# Collect all translations from all languages
all_language_modules = [de, en, fr, nl, it, sv, es, pl, cs, hu, fi, da]

for lang_module in all_language_modules:
    for key, translations in lang_module.TRANSLATIONS.items():
        if key not in HEADER_ALIASES:
            HEADER_ALIASES[key] = []
        
        # Add translations, avoiding duplicates
        for translation in translations:
            if translation not in HEADER_ALIASES[key]:
                HEADER_ALIASES[key].append(translation)

# Add keys that aren't in testdata but are needed for functionality
# These are manually maintained fallbacks from mapping.py
if CanonicalKey.DHW_SECTION not in HEADER_ALIASES:
    HEADER_ALIASES[CanonicalKey.DHW_SECTION] = [
        "DHW",
        "Warmwasser",
        "WW",
        "TRINKWASSER",
        "DHW (Warmwasser)",
    ]

if CanonicalKey.START_OPERATION_MODE not in HEADER_ALIASES:
    HEADER_ALIASES[CanonicalKey.START_OPERATION_MODE] = [
        "BETRIEBSART",
        "OPERATION",
        "OPERATION MODE",
        "OPERATING MODE",
        "MODE",
    ]

if CanonicalKey.ROOM_TEMPERATURE_SECTION not in HEADER_ALIASES:
    HEADER_ALIASES[CanonicalKey.ROOM_TEMPERATURE_SECTION] = [
        "ROOM TEMPERATURE",
        "RAUMTEMPERATUR",
        "RAUM TEMPERATUR",
    ]

if CanonicalKey.VD_HEATING_SUM not in HEADER_ALIASES:
    HEADER_ALIASES[CanonicalKey.VD_HEATING_SUM] = [
        "VD HEIZUNG SUMME",
        "VD HEATING",
    ]

def to_canonical_key(value: str | CanonicalKey) -> CanonicalKey | None:
    """Convert a string or CanonicalKey to a CanonicalKey enum member.
    
    Args:
        value: Either a string matching a CanonicalKey name, or a CanonicalKey member
        
    Returns:
        The corresponding CanonicalKey member, or None if not found
    """
    if isinstance(value, CanonicalKey):
        return value
    if isinstance(value, str):
        try:
            return CanonicalKey(value)
        except ValueError:
            return None
    return None


def get_aliases(value: str | CanonicalKey) -> list[str]:
    """Get the list of translation aliases for a canonical key.
    
    Args:
        value: Either a string matching a CanonicalKey name, or a CanonicalKey member
        
    Returns:
        List of translation strings for this canonical key.
        - If given a CanonicalKey, return HEADER_ALIASES[CanonicalKey] or [].
        - If given a str that matches a CanonicalKey name, return that key's
          aliases list. Otherwise return a single-item list with the original
          string so callers can still perform literal matching.
    """
    if isinstance(value, CanonicalKey):
        return HEADER_ALIASES.get(value, [])
    if not isinstance(value, str):
        return []
    ck = to_canonical_key(value)
    if ck is None:
        return [value]
    return HEADER_ALIASES.get(ck, [value])


__all__ = [
    "CanonicalKey",
    "HEADER_ALIASES",
    "to_canonical_key",
    "get_aliases",
    "de",
    "en",
    "fr",
    "nl",
    "it",
    "sv",
    "es",
    "pl",
    "cs",
    "hu",
    "fi",
    "da",
]
