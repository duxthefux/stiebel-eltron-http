import pytest

from custom_components.stiebel_eltron_http import parsing


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("23,3°C", 23.3),
        ("-5,0°C", -5.0),
        ("not-a-number", None),
    ],
)
def test_convert_temperature(inp, expected):
    assert parsing._convert_temperature(inp) == expected


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("53,3%", 53.3),
        ("100%", 100.0),
        ("n/a", None),
    ],
)
def test_convert_percentage(inp, expected):
    assert parsing._convert_percentage(inp) == expected


def test_convert_energy_kwh_and_mwh():
    assert parsing._convert_energy("24,249kWh") == pytest.approx(24.249)
    # MWh should be converted to kWh
    assert parsing._convert_energy("1,5MWh") == pytest.approx(1500.0)
    assert parsing._convert_energy("no unit") is None


@pytest.mark.parametrize(
    "inp,expected",
    [
        ("5,22bar", pytest.approx(5.22)),
        ("31,9l/min", pytest.approx(31.9)),
        ("1,2kW", pytest.approx(1.2)),
        ("---", None),
    ],
)
def test_convert_numeric(inp, expected):
    val = parsing._convert_numeric(inp)
    if expected is None:
        assert val is None
    else:
        assert val == expected
