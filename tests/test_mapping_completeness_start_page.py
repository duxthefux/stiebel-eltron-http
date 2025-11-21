from custom_components.stiebel_eltron_http.mapping import (
    CanonicalKey,
    CANONICAL_TO_CONST,
)
from custom_components.stiebel_eltron_http.i18n import HEADER_ALIASES
from custom_components.stiebel_eltron_http.const import (
    START_BETRIEBSART,
)


def test_start_page_canonical_keys_present():
    """Ensure start-page canonical keys have aliases and are mapped to consts."""
    for ck, const in (
        (CanonicalKey.START_BETRIEBSART, START_BETRIEBSART),
    ):
        assert ck in HEADER_ALIASES, f"Missing aliases for {ck}"
        aliases = HEADER_ALIASES.get(ck)
        assert aliases and len(aliases) > 0, f"No aliases listed for {ck}"
        assert CANONICAL_TO_CONST.get(ck) == const, f"Canonical {ck} not mapped to {const}"
