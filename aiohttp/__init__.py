"""Minimal aiohttp shim for unit tests.

This shim provides only the symbols needed at import time by the scraper during
unit tests. It does not perform real HTTP operations.
"""
from typing import Any


class ClientError(Exception):
    """Base client error."""


class ClientResponseError(ClientError):
    """Raised on HTTP response errors in the real aiohttp package."""


class ClientResponse:
    """Minimal ClientResponse placeholder."""

    def __init__(self, status: int = 200, text: str = "") -> None:
        self.status = status
        self._text = text

    def raise_for_status(self) -> None:
        if 400 <= self.status:
            raise ClientResponseError(f"HTTP {self.status}")

    async def text(self) -> str:  # pragma: no cover - shim
        return self._text


class ClientSession:
    """Placeholder ClientSession with a no-op request method."""

    async def request(self, *args: Any, **kwargs: Any) -> ClientResponse:  # pragma: no cover - shim
        return ClientResponse()


__all__ = ["ClientError", "ClientResponseError", "ClientResponse", "ClientSession"]
