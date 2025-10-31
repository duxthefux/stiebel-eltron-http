"""Minimal async_timeout shim for unit tests.

Provides a simple async context manager `timeout()` that does nothing but
allow import and usage in `async with async_timeout.timeout(...):` blocks.
"""
from __future__ import annotations

from typing import Any


class _TimeoutCM:
    def __init__(self, seconds: Any) -> None:
        self.seconds = seconds

    async def __aenter__(self):  # pragma: no cover - shim
        return None

    async def __aexit__(self, exc_type, exc, tb):  # pragma: no cover - shim
        return False


def timeout(seconds: Any) -> _TimeoutCM:
    return _TimeoutCM(seconds)
