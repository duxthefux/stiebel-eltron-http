from pathlib import Path

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.const import (
    START_BETRIEBSART,
    START_SYSTEM_STATUS,
    START_PORTAL_STATUS,
)


def test_start_page_de_extracts_expected_values() -> None:
    """Ensure the German START page fixture yields Betriebsart, Systemstatus and Portalstatus."""
    repo_root = Path(__file__).resolve().parent.parent
    fixture = repo_root / "scripts" / "testdata" / "s_0_0_de.html"
    html = fixture.read_text(encoding="utf-8")

    client = StiebelEltronScrapingClient("testhost", None)
    res = client._extract_start_page(html)

    # Betriebsart expected as value attribute in the fixture
    assert START_BETRIEBSART in res
    assert res[START_BETRIEBSART] == "PROGRAMMBETRIEB"

    # Systemstatus should contain the longer descriptive phrase and may include a short 'info' appended
    assert START_SYSTEM_STATUS in res
    assert "Ihr System arbeitet korrekt" in res[START_SYSTEM_STATUS]

    # Portalstatus should include the short info line indicating portal key presence
    assert START_PORTAL_STATUS in res
    assert "Portalschlüssel vorhanden" in res[START_PORTAL_STATUS]


def test_start_page_en_extracts_expected_values() -> None:
    """Ensure the English START page fixture yields Betriebsart, Systemstatus and Portalstatus."""
    repo_root = Path(__file__).resolve().parent.parent
    fixture = repo_root / "scripts" / "testdata" / "s_0_0_en.html"
    html = fixture.read_text(encoding="utf-8")

    client = StiebelEltronScrapingClient("testhost", None)
    res = client._extract_start_page(html)

    # Betriebsart expected as value attribute in the English fixture as well
    assert START_BETRIEBSART in res
    # allow common English labels like PROGRAMMBETRIEB or translated
    assert isinstance(res[START_BETRIEBSART], str) and len(res[START_BETRIEBSART]) > 0

    # Systemstatus should contain a descriptive phrase
    assert START_SYSTEM_STATUS in res
    assert "system" in res[START_SYSTEM_STATUS].lower() or "Ihr System" in res[START_SYSTEM_STATUS]

    # Portalstatus should include a short info line indicating portal key presence
    assert START_PORTAL_STATUS in res
    assert "portal" in res[START_PORTAL_STATUS].lower() or "Portalschlüssel" in res[START_PORTAL_STATUS]
