import re
from pathlib import Path

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.const import MAC_ADDRESS_KEY


def test_profile_network_mac_labeled_positive() -> None:
    """A labeled MAC field should be parsed and normalized."""
    html = '''
    <div class="calibration round span-24 last" style="height:40px">
        <div class="span-12">
            <h3 style="line-height:40px;margin-top:0px">MAC-address</h3>
        </div>
        <div class="span-5 values" style="line-height:40px;margin-top:0px">AA:BB:CC:11:22:33</div>
    </div>
    '''

    client = StiebelEltronScrapingClient("testhost", None)
    res = client._extract_profile_network(html)

    assert MAC_ADDRESS_KEY in res
    assert re.match(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$", res[MAC_ADDRESS_KEY])


def test_profile_network_mac_fixture_redacted() -> None:
    """Ensure extraction from the provided fixture does not crash and returns
    either no MAC (redacted) or a valid normalized MAC string.
    """
    repo_root = Path(__file__).resolve().parent.parent
    fixture = repo_root / "scripts" / "testdata" / "s_5_0_en.html"
    html = fixture.read_text(encoding="utf-8")

    client = StiebelEltronScrapingClient("testhost", None)
    res = client._extract_profile_network(html)

    if MAC_ADDRESS_KEY in res:
        assert re.match(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$", res[MAC_ADDRESS_KEY])
    else:
        # expected for redacted fixtures
        assert MAC_ADDRESS_KEY not in res


def test_profile_network_mac_fixture_de() -> None:
    """Ensure extraction from the German fixture does not crash and returns
    either no MAC (redacted) or a valid normalized MAC string.
    """
    repo_root = Path(__file__).resolve().parent.parent
    fixture = repo_root / "scripts" / "testdata" / "s_5_0_de.html"
    html = fixture.read_text(encoding="utf-8")

    client = StiebelEltronScrapingClient("testhost", None)
    res = client._extract_profile_network(html)

    if MAC_ADDRESS_KEY in res:
        assert re.match(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$", res[MAC_ADDRESS_KEY])
    else:
        # expected for redacted fixtures
        assert MAC_ADDRESS_KEY not in res


def test_profile_network_mac_synthetic() -> None:
    """Extraction from a synthetic fixture should return the exact expected MAC."""
    repo_root = Path(__file__).resolve().parent.parent
    fixture = repo_root / "scripts" / "testdata" / "s_5_0_synthetic.html"
    html = fixture.read_text(encoding="utf-8")

    client = StiebelEltronScrapingClient("testhost", None)
    res = client._extract_profile_network(html)

    assert MAC_ADDRESS_KEY in res
    assert res[MAC_ADDRESS_KEY] == "aa:bb:cc:11:22:33"


def test_profile_network_mac_whitespace() -> None:
    """Ensure extractor tolerates leading/trailing whitespace and tabs in the value element."""
    html = '''
    <div class="calibration round span-24 last" style="height:40px">
        <div class="span-12">
            <h3 style="line-height:40px;margin-top:0px">MAC-address</h3>
        </div>
        <div class="span-5 values" style="line-height:40px;margin-top:0px">   78:E9:96:20:3A:CD 	</div>
    </div>
    '''

    client = StiebelEltronScrapingClient("testhost", None)
    res = client._extract_profile_network(html)

    assert MAC_ADDRESS_KEY in res
    assert res[MAC_ADDRESS_KEY] == "78:e9:96:20:3a:cd"
