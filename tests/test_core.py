"""Tests for ``z.core``."""

from z import greet


def test_greet_uses_name() -> None:
    assert greet("Codex") == "Hello, Codex!"


def test_greet_defaults_when_blank() -> None:
    assert greet("   ") == "Hello, world!"
