from pathlib import Path

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.const import (
    START_OPERATION_MODE_KEY,
)


def test_start_page_de_extracts_expected_values() -> None:
    """Ensure the German START page fixture yields Betriebsart."""
    repo_root = Path(__file__).resolve().parent.parent
    fixture = repo_root / "scripts" / "testdata" / "s_0_0_de.html"
    html = fixture.read_text(encoding="utf-8")

    client = StiebelEltronScrapingClient("testhost", None)
    res = client._extract_start_page(html)

    # Betriebsart expected as value attribute in the fixture
    assert START_OPERATION_MODE_KEY in res
    assert res[START_OPERATION_MODE_KEY] == "PROGRAMMBETRIEB"


def test_start_page_en_extracts_expected_values() -> None:
    """Ensure the English START page fixture yields Betriebsart."""
    repo_root = Path(__file__).resolve().parent.parent
    fixture = repo_root / "scripts" / "testdata" / "s_0_0_en.html"
    html = fixture.read_text(encoding="utf-8")

    client = StiebelEltronScrapingClient("testhost", None)
    res = client._extract_start_page(html)

    # Betriebsart expected as value attribute in the English fixture as well
    assert START_OPERATION_MODE_KEY in res
    # allow common English labels like PROGRAMMBETRIEB or translated
    assert isinstance(res[START_OPERATION_MODE_KEY], str) and len(res[START_OPERATION_MODE_KEY]) > 0
