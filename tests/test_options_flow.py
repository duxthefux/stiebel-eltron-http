import pytest

from types import SimpleNamespace, ModuleType
import sys

# Provide a minimal dummy 'voluptuous' module for test environments that
# don't have it installed. The real integration expects voluptuous at import
# time; for our unit test we only need to avoid import errors and do not use
# the real validation features.
vol = ModuleType("voluptuous")
setattr(vol, "Schema", lambda *a, **k: {})
setattr(vol, "Optional", lambda *a, **k: None)
setattr(vol, "Required", lambda *a, **k: None)
setattr(vol, "In", lambda *a, **k: None)
sys.modules.setdefault("voluptuous", vol)

## Provide minimal Home Assistant shims required by config_flow import
ha = ModuleType("homeassistant")
config_entries_mod = ModuleType("homeassistant.config_entries")

class DummyConfigFlow:
    pass

class DummyOptionsFlow:
    pass

setattr(config_entries_mod, "ConfigFlow", DummyConfigFlow)
setattr(config_entries_mod, "OptionsFlow", DummyOptionsFlow)
setattr(ha, "config_entries", config_entries_mod)

const_mod = ModuleType("homeassistant.const")
setattr(const_mod, "CONF_DEVICE_ID", "device_id")
setattr(const_mod, "CONF_HOST", "host")
setattr(const_mod, "CONF_NAME", "name")
class _Platform:
    SENSOR = "sensor"

setattr(const_mod, "Platform", _Platform)
sys.modules.setdefault("homeassistant", ha)
sys.modules.setdefault("homeassistant.config_entries", config_entries_mod)
sys.modules.setdefault("homeassistant.const", const_mod)

# Minimal helpers used by config_flow; they won't be executed in tests but must exist
helpers_mod = ModuleType("homeassistant.helpers")
aiohttp_client_mod = ModuleType("homeassistant.helpers.aiohttp_client")
setattr(aiohttp_client_mod, "async_create_clientsession", lambda hass: None)
setattr(aiohttp_client_mod, "async_get_clientsession", lambda hass: None)
device_registry_mod = ModuleType("homeassistant.helpers.device_registry")
setattr(device_registry_mod, "format_mac", lambda s: s)
service_info_mod = ModuleType("homeassistant.helpers.service_info")
ssdp_mod = ModuleType("homeassistant.helpers.service_info.ssdp")
setattr(ssdp_mod, "ATTR_UPNP_FRIENDLY_NAME", "friendly_name")
setattr(ssdp_mod, "ATTR_UPNP_PRESENTATION_URL", "presentation_url")
setattr(ssdp_mod, "ATTR_UPNP_SERIAL", "serial")
class SsdpServiceInfo:
    def __init__(self, upnp):
        self.upnp = upnp
setattr(ssdp_mod, "SsdpServiceInfo", SsdpServiceInfo)

sys.modules.setdefault("homeassistant.helpers", helpers_mod)
sys.modules.setdefault("homeassistant.helpers.aiohttp_client", aiohttp_client_mod)
sys.modules.setdefault("homeassistant.helpers.device_registry", device_registry_mod)
sys.modules.setdefault("homeassistant.helpers.service_info", service_info_mod)
sys.modules.setdefault("homeassistant.helpers.service_info.ssdp", ssdp_mod)

from importlib import util

spec = util.spec_from_file_location(
    "stiebel_const", "custom_components/stiebel_eltron_http/const.py"
)
const = util.module_from_spec(spec)
spec.loader.exec_module(const)  # type: ignore

CONF_FETCH_ENERGY = const.CONF_FETCH_ENERGY
CONF_LANGUAGE = const.CONF_LANGUAGE


class DummyConfigEntries:
    def __init__(self):
        self.last_update = None

    def async_update_entry(self, entry, data=None, options=None):
        # record call for assertions
        self.last_update = (data, options)


class DummyEntry:
    def __init__(self, data=None, options=None):
        self.data = data or {}
        self.options = options or {}


def test_options_flow_updates_options(monkeypatch):
    try:
        from custom_components.stiebel_eltron_http.config_flow import OptionsFlowHandler
    except Exception:
        pytest.skip("Home Assistant environment not available for config_flow import")

    entry = DummyEntry(data={"host": "1.2.3.4"}, options={})
    handler = OptionsFlowHandler(entry)

    # Provide a fake hass with config_entries that records updates
    dummy_config = DummyConfigEntries()
    hass = SimpleNamespace(config_entries=dummy_config)
    handler.hass = hass

    # Simulate user submitting options
    user_input = {CONF_FETCH_ENERGY: True, CONF_LANGUAGE: "de"}

    import asyncio

    result = asyncio.run(handler.async_step_init(user_input=user_input))

    # Options flow should create an entry result
    assert result is not None
    # The dummy config entries should have recorded that options were updated
    assert dummy_config.last_update is not None
    _, options = dummy_config.last_update
    assert options[CONF_FETCH_ENERGY] is True
    assert options[CONF_LANGUAGE] == "de"
