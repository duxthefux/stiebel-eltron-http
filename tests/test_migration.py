import pytest

from types import SimpleNamespace

from importlib import util
from types import SimpleNamespace

spec = util.spec_from_file_location(
    "stiebel_const", "custom_components/stiebel_eltron_http/const.py"
)
const = util.module_from_spec(spec)
spec.loader.exec_module(const)  # type: ignore

from custom_components.stiebel_eltron_http.__init__ import async_migrate_entry
CONF_FETCH_ENERGY = const.CONF_FETCH_ENERGY
DEFAULT_FETCH_ENERGY = const.DEFAULT_FETCH_ENERGY


class DummyConfigEntries:
    def __init__(self):
        self.last_update = None

    def async_update_entry(self, entry, data=None, options=None):
        # Simulate Home Assistant updating the entry in place (synchronous stub)
        if data is not None:
            entry.data = data
        if options is not None:
            entry.options = options
        self.last_update = (data, options)


class DummyEntry:
    def __init__(self, version, data, options=None):
        self.version = version
        self.data = data
        self.options = options or {}
        self.entry_id = "dummy"


def test_migration_moves_fetch_to_options():
    # Prepare a v2 entry that has fetch flag in data
    entry = DummyEntry(version=2, data={"host": "1.2.3.4", CONF_FETCH_ENERGY: False})

    dummy_config = DummyConfigEntries()
    hass = SimpleNamespace(config_entries=dummy_config)

    import asyncio

    result = asyncio.run(async_migrate_entry(hass, entry))

    assert result is True
    # After migration entry should be bumped to version 3
    assert entry.version == 3
    # fetch flag should have been moved into options
    assert CONF_FETCH_ENERGY not in entry.data
    assert entry.options.get(CONF_FETCH_ENERGY, None) is False
