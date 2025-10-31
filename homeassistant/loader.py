"""Minimal loader shim for tests."""

async def async_get_loaded_integration(hass, domain):
    """Return a placeholder object representing a loaded integration.

    Tests that import the integration only need this function to exist; returning
    None keeps behavior simple and avoids importing Home Assistant.
    """
    return None
