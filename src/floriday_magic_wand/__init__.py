"""Floriday magic wand package."""

from .client import FloridayClient
from .web import run_server

__all__ = ["FloridayClient", "run_server"]
