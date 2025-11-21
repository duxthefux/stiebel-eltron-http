import pytest

from custom_components.stiebel_eltron_http import i18n


def test_to_canonical_key_accepts_member():
    assert i18n.to_canonical_key(i18n.CanonicalKey.ACTUAL_TEMPERATURE) is i18n.CanonicalKey.ACTUAL_TEMPERATURE


def test_to_canonical_key_from_str():
    assert i18n.to_canonical_key("ACTUAL_TEMPERATURE") is i18n.CanonicalKey.ACTUAL_TEMPERATURE


def test_to_canonical_key_unknown():
    assert i18n.to_canonical_key("NON_EXISTENT_KEY") is None


def test_to_canonical_key_bad_type():
    assert i18n.to_canonical_key(123) is None


def test_get_aliases_with_enum():
    aliases = i18n.get_aliases(i18n.CanonicalKey.ACTUAL_TEMPERATURE)
    assert isinstance(aliases, list)
    assert len(aliases) > 0


def test_get_aliases_with_matching_string():
    aliases_str = i18n.get_aliases("ACTUAL_TEMPERATURE")
    aliases_enum = i18n.get_aliases(i18n.CanonicalKey.ACTUAL_TEMPERATURE)
    assert aliases_str == aliases_enum


def test_get_aliases_with_unknown_string():
    assert i18n.get_aliases("SOME_RANDOM_HEADER") == ["SOME_RANDOM_HEADER"]


def test_get_aliases_bad_type():
    assert i18n.get_aliases(3.14) == []
