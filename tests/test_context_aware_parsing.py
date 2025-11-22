"""Test context-aware parsing to ensure generic field names don't conflict."""

import bs4

from custom_components.stiebel_eltron_http.parsing import parse_process_data_table
from custom_components.stiebel_eltron_http.i18n import CanonicalKey


def test_isttemperatur_without_context_matches_any():
    """Without section context, ISTTEMPERATUR can match various canonical keys."""
    html = """
    <table>
        <tr><td>ISTTEMPERATUR</td><td>23,3°C</td></tr>
    </table>
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    
    # Without context, it might match external temperature (first in HEADER_ALIASES)
    result = parse_process_data_table(table)
    
    # Should match something (the exact match depends on alias ordering)
    assert len(result) > 0


def test_isttemperatur_with_external_context_matches_external():
    """With EXTERNAL_HEAT_SOURCE_SECTION context, ISTTEMPERATUR maps to external sensor."""
    html = """
    <table>
        <tr><td>ISTTEMPERATUR</td><td>23,3°C</td></tr>
        <tr><td>SOLLTEMPERATUR</td><td>24,5°C</td></tr>
    </table>
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    
    # With external heat source context, should only match external sensors
    result = parse_process_data_table(
        table,
        section_context=CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION,
    )
    
    assert CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE in result
    assert result[CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE] == 23.3
    assert CanonicalKey.EXTERNAL_SET_TEMPERATURE in result
    assert result[CanonicalKey.EXTERNAL_SET_TEMPERATURE] == 24.5


def test_context_filters_out_wrong_section_keys():
    """Section context should filter out canonical keys not belonging to that section."""
    html = """
    <table>
        <tr><td>ISTTEMPERATUR</td><td>23,3°C</td></tr>
        <tr><td>RÜCKLAUFTEMPERATUR</td><td>30,0°C</td></tr>
    </table>
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    
    # With external context, RÜCKLAUFTEMPERATUR (return temp) should be ignored
    # as it's not part of EXTERNAL_HEAT_SOURCE_SECTION
    result = parse_process_data_table(
        table,
        section_context=CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION,
    )
    
    # Should only have ISTTEMPERATUR (external), not RÜCKLAUFTEMPERATUR
    assert CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE in result
    assert CanonicalKey.RETURN_TEMPERATURE not in result


def test_no_context_allows_all_keys():
    """Without section context, all canonical keys are allowed."""
    html = """
    <table>
        <tr><td>RÜCKLAUFTEMPERATUR</td><td>30,0°C</td></tr>
        <tr><td>VORLAUFTEMPERATUR</td><td>35,0°C</td></tr>
    </table>
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    
    # Without context, should match process data keys
    result = parse_process_data_table(table)
    
    assert CanonicalKey.RETURN_TEMPERATURE in result
    assert result[CanonicalKey.RETURN_TEMPERATURE] == 30.0
    assert CanonicalKey.SUPPLY_TEMPERATURE in result
    assert result[CanonicalKey.SUPPLY_TEMPERATURE] == 35.0


def test_external_section_specific_keys_parsed():
    """External heat source specific keys should parse correctly with context."""
    html = """
    <table>
        <tr><td>BIVALENZTEMPERATUR HZG</td><td>5,0°C</td></tr>
        <tr><td>UNTERE EINSATZGRENZE WW</td><td>Aus</td></tr>
    </table>
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    
    result = parse_process_data_table(
        table,
        section_context=CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION,
    )
    
    assert CanonicalKey.DUAL_MODE_TEMP_HZG in result
    assert result[CanonicalKey.DUAL_MODE_TEMP_HZG] == 5.0
    assert CanonicalKey.LOWER_LIMIT_WW in result
    assert result[CanonicalKey.LOWER_LIMIT_WW] == "Aus"


def test_heating_section_context_filters_correctly():
    """HEATING_SECTION context should only match heating-related keys."""
    html = """
    <table>
        <tr><td>AUSSENTEMPERATUR</td><td>10,5°C</td></tr>
        <tr><td>FROSTSCHUTZTEMPERATUR</td><td>5,0°C</td></tr>
        <tr><td>RÜCKLAUFTEMPERATUR</td><td>30,0°C</td></tr>
    </table>
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    
    result = parse_process_data_table(
        table,
        section_context=CanonicalKey.HEATING_SECTION,
    )
    
    # Should match heating section keys
    assert CanonicalKey.OUTSIDE_TEMPERATURE in result
    assert result[CanonicalKey.OUTSIDE_TEMPERATURE] == 10.5
    assert CanonicalKey.FROST_PROTECTION_TEMPERATURE in result
    assert result[CanonicalKey.FROST_PROTECTION_TEMPERATURE] == 5.0
    
    # Should NOT match process data keys (RÜCKLAUFTEMPERATUR)
    assert CanonicalKey.RETURN_TEMPERATURE not in result


def test_process_data_section_context_filters_correctly():
    """PROCESS_DATA_SECTION context should only match process data keys."""
    html = """
    <table>
        <tr><td>RÜCKLAUFTEMPERATUR</td><td>30,0°C</td></tr>
        <tr><td>VORLAUFTEMPERATUR</td><td>35,0°C</td></tr>
        <tr><td>DRUCK HOCHDRUCK</td><td>5,22bar</td></tr>
        <tr><td>ISTTEMPERATUR HK 1</td><td>22,0°C</td></tr>
    </table>
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    
    result = parse_process_data_table(
        table,
        section_context=CanonicalKey.PROCESS_DATA_SECTION,
    )
    
    # Should match process data keys
    assert CanonicalKey.RETURN_TEMPERATURE in result
    assert result[CanonicalKey.RETURN_TEMPERATURE] == 30.0
    assert CanonicalKey.SUPPLY_TEMPERATURE in result
    assert result[CanonicalKey.SUPPLY_TEMPERATURE] == 35.0
    assert CanonicalKey.HIGH_PRESSURE in result
    assert result[CanonicalKey.HIGH_PRESSURE] == 5.22
    
    # Should NOT match heating section keys (ISTTEMPERATUR HK 1)
    assert CanonicalKey.ACTUAL_TEMPERATURE_HK_1 not in result


def test_multiple_sections_with_same_field_name():
    """Generic field names should map to different keys based on section context."""
    html = """
    <table>
        <tr><td>ISTTEMPERATUR</td><td>25,0°C</td></tr>
        <tr><td>SOLLTEMPERATUR</td><td>26,0°C</td></tr>
    </table>
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    
    # In external heat source section
    external_result = parse_process_data_table(
        table,
        section_context=CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION,
    )
    assert CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE in external_result
    assert external_result[CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE] == 25.0
    assert CanonicalKey.EXTERNAL_SET_TEMPERATURE in external_result
    assert external_result[CanonicalKey.EXTERNAL_SET_TEMPERATURE] == 26.0
    
    # Without context (backward compatibility - matches first alias)
    no_context_result = parse_process_data_table(table)
    # Should match something (exact key depends on alias ordering)
    assert len(no_context_result) > 0

