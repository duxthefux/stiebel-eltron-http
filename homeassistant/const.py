"""Minimal subset of Home Assistant constants used by the integration during tests."""

CONF_HOST = "host"


class Platform:
    SENSOR = "sensor"


# Some integrations reference ATTR_SW_VERSION; provide a sensible default.
ATTR_SW_VERSION = "sw_version"
