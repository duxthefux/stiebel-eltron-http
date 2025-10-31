import pytest

from custom_components.stiebel_eltron_http import parsing


def test_normalize_text_basic():
    assert parsing._normalize_text("  AbC  De  ") == "abc de"
    # non-string inputs return empty string
    assert parsing._normalize_text(None) == ""
    assert parsing._normalize_text(123) == ""


def test_matches_alias_exact_and_substring():
    candidates = ["ISTTEMPERATUR", "OUTSIDE TEMPERATURE"]
    # candidate is a substring of header -> match
    assert parsing._matches_alias("Isttemperatur HK 1", candidates) is True
    # exact match (case-insensitive)
    assert parsing._matches_alias("outside temperature", candidates) is True
    # empty header yields False
    assert parsing._matches_alias("", candidates) is False


def test_find_best_alias_prefers_longest():
    aliases = {
        "INVERTER_POWER": ["INVERTER POWER"],
        "INVERTER_POWER_INPUT": ["INVERTER POWER CONSUMPTION", "INVERTER POWER INPUT"],
    }

    header = "Inverter Power Consumption"
    assert parsing._find_best_alias(header, aliases) == "INVERTER_POWER_INPUT"

    # shorter header should match the shorter canonical candidate
    assert parsing._find_best_alias("Inverter Power", aliases) == "INVERTER_POWER"


def test_find_best_alias_no_match():
    aliases = {"A": ["foo"], "B": ["bar"]}
    assert parsing._find_best_alias("something else", aliases) is None
