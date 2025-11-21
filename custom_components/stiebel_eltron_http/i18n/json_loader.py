"""Load translations from JSON files.

This module provides utilities to dynamically load translations from
the Home Assistant translation JSON files, ensuring a single source of truth.
"""

import json
from pathlib import Path
from typing import Any

from ..mapping import CANONICAL_TO_CONST, ENERGY_CONSUMED_MAP, CanonicalKey
from ..const import (
    ROOM_TEMPERATURE_KEY,
    ROOM_HUMIDITY_KEY,
    DHW_TEMPERATURE_KEY,
)


def _build_const_to_canonical() -> dict[str, list[CanonicalKey]]:
    """Build reverse mapping from const keys to canonical keys."""
    # Build complete mapping
    canonical_to_const_expanded = dict(CANONICAL_TO_CONST)
    canonical_to_const_expanded[CanonicalKey.ACTUAL_TEMPERATURE_1] = ROOM_TEMPERATURE_KEY
    canonical_to_const_expanded[CanonicalKey.RELATIVE_HUMIDITY_1] = ROOM_HUMIDITY_KEY
    canonical_to_const_expanded[CanonicalKey.ACTUAL_TEMPERATURE] = DHW_TEMPERATURE_KEY
    canonical_to_const_expanded.update(ENERGY_CONSUMED_MAP)
    
    # Reverse it: const_key -> list of canonical keys
    const_to_canonical: dict[str, list[CanonicalKey]] = {}
    for canonical_key, const_key in canonical_to_const_expanded.items():
        if const_key not in const_to_canonical:
            const_to_canonical[const_key] = []
        const_to_canonical[const_key].append(canonical_key)
    
    return const_to_canonical


def load_translations_from_json(
    lang_code: str,
    additional_translations: dict[CanonicalKey, list[str]] | None = None
) -> dict[CanonicalKey, list[str]]:
    """Load translations from a JSON file and optionally merge with additional ones.
    
    Args:
        lang_code: Language code (e.g., 'de', 'en', 'fr')
        additional_translations: Optional dictionary of manually-defined translations
                                to merge with JSON translations. These can include
                                field variations extracted from HTML testdata.
        
    Returns:
        Dictionary mapping canonical keys to lists of translation strings.
    """
    # Get path to JSON file
    json_path = Path(__file__).parent.parent / 'translations' / f'{lang_code}.json'
    
    # Start with additional translations if provided
    translations: dict[CanonicalKey, list[str]] = {}
    if additional_translations:
        for key, values in additional_translations.items():
            translations[key] = list(values)  # Copy the list
    
    if not json_path.exists():
        return translations
    
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data: dict[str, Any] = json.load(f)
    
    # Build reverse mapping
    const_to_canonical = _build_const_to_canonical()
    
    # Extract sensor translations
    sensors = json_data.get('entity', {}).get('sensor', {})
    
    # Merge JSON translations with existing ones
    for const_key, sensor_data in sensors.items():
        translation_text = sensor_data.get('name')
        if not translation_text:
            continue
        
        # Find canonical key(s) for this const key
        canonical_keys = const_to_canonical.get(const_key, [])
        
        for canonical_key in canonical_keys:
            if canonical_key not in translations:
                translations[canonical_key] = []
            if translation_text not in translations[canonical_key]:
                translations[canonical_key].append(translation_text)
    
    return translations
