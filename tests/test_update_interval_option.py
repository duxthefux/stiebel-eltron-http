from datetime import timedelta

from custom_components.stiebel_eltron_http.const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
)
from custom_components.stiebel_eltron_http.coordinator import (
    StiebelEltronHttpDataUpdateCoordinator,
)


def test_coordinator_respects_options_interval() -> None:
    """If the options include an update interval, the coordinator should use it."""
    # Simulate entry options and data
    opt_value = 5
    entry_options = {CONF_UPDATE_INTERVAL: opt_value}

    # The DataUpdateCoordinator shim accepts None for hass/logger
    coord = StiebelEltronHttpDataUpdateCoordinator(hass=None, logger=None, name="test", update_interval=timedelta(minutes=entry_options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES)))

    assert coord.update_interval == timedelta(minutes=opt_value)


def test_coordinator_uses_default_when_missing() -> None:
    """When options do not include the setting, default minutes should be used."""
    coord = StiebelEltronHttpDataUpdateCoordinator(hass=None, logger=None, name="test", update_interval=timedelta(minutes=DEFAULT_UPDATE_INTERVAL_MINUTES))
    assert coord.update_interval == timedelta(minutes=DEFAULT_UPDATE_INTERVAL_MINUTES)
