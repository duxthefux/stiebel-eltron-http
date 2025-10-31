"""Minimal aiohttp client helper shim used in tests."""

async def async_get_clientsession(hass=None):
    """Return a minimal session placeholder for tests.

    The real Home Assistant helper returns an aiohttp.ClientSession tied to
    hass. For our unit tests we only need the symbol to exist so imports
    succeed; returning None is acceptable because tests import modules but
    don't call async_setup_entry.
    """
    return None
