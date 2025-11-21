from custom_components.stiebel_eltron_http import mapping
import custom_components.stiebel_eltron_http.mapping as mapping
from custom_components.stiebel_eltron_http.i18n import HEADER_ALIASES
from custom_components.stiebel_eltron_http.mapping import ALLOWED_UNMAPPED_CANONICALS


def test_mapping_completeness_programmatic():
    """Programmatically ensure canonical keys in HEADER_ALIASES are covered.

    We derive the canonical keys from `i18n.HEADER_ALIASES` and assert that
    every non-section canonical key is present in either
    `mapping.CANONICAL_TO_CONST` or `mapping.ENERGY_CONSUMED_MAP`.

    Some canonical keys are intentionally only used as section headers and are
    skipped (they end with '_SECTION'). A small set of parsing-only aliases
    that do not map to integration constants are allowed and listed in
    `allowed_unmapped`.
    """
    aliases = set(HEADER_ALIASES.keys())

    # Keys that represent section headers and shouldn't be present in the maps
    section_keys = {k for k in aliases if k.endswith("_SECTION")}

    # Use the shared whitelist from mapping.py
    allowed_unmapped = set(ALLOWED_UNMAPPED_CANONICALS)

    candidates = aliases - section_keys - allowed_unmapped

    missing = []
    for k in sorted(candidates):
        if k in mapping.CANONICAL_TO_CONST:
            continue
        if k in mapping.ENERGY_CONSUMED_MAP:
            continue
        missing.append(k)

    assert not missing, f"Mapping missing canonical keys: {missing}"
