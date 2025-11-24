"""Minimal update coordinator shim for tests."""
from __future__ import annotations

from typing import Any


class UpdateFailed(Exception):
    """Raised when an update failed in the coordinator (test shim)."""


class DataUpdateCoordinator:
    """Very small shim of Home Assistant's DataUpdateCoordinator.

    This implementation provides only the pieces the integration uses during
    import and basic testing: a compatible constructor and a no-op
    asynchronous _async_setup method.
    """

    def __init__(self, hass: Any = None, logger: Any = None, name: str | None = None, update_interval: Any = None):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval

    async def _async_setup(self) -> None:  # pragma: no cover - simple shim
        """No-op setup used by tests."""
        return None
