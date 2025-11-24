"""Minimal test shim for Home Assistant core modules used during tests.

This lightweight package provides just enough symbols so tests can import
the integration modules without having Home Assistant installed.

Do not use this in production; it's only for local unit testing.
"""

__all__ = ["const", "helpers", "loader"]
