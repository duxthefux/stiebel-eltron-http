"""Minimal Home Assistant exceptions shim for tests."""


class HomeAssistantError(Exception):
    """Base class for Home Assistant test shim exceptions."""


class ConfigEntryAuthFailed(HomeAssistantError):
    """Raised when a config entry authentication fails (test shim)."""
