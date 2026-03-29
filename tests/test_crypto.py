"""Tests for ``z.crypto``."""

import importlib.util

import pytest

from z.crypto import (
    decrypt_fast,
    decrypt_full,
    decrypt_pipeline,
    encrypt_fast,
    encrypt_full,
    encrypt_pipeline,
)

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("Crypto") is None, reason="PyCryptodome is not installed"
)


KEY = b"k" * 32


def test_full_mode_round_trip() -> None:
    payload = encrypt_full(b"hello full mode", KEY)
    assert decrypt_full(payload, KEY) == b"hello full mode"


def test_fast_mode_round_trip_preserves_tail() -> None:
    data = b"HEADER" * 10 + b"-TAIL-DATA-" * 5
    payload = encrypt_fast(data, KEY, header_len=32)
    out = decrypt_fast(payload, KEY)
    assert out == data


def test_pipeline_mode_round_trip_with_padding() -> None:
    from Crypto.PublicKey import RSA

    key = RSA.generate(2048)
    pub = key.publickey().export_key()
    priv = key.export_key()

    data = b"classified report" * 40
    payload = encrypt_pipeline(data, pub, pad_to_size=4096, metadata={"kind": "report"})
    out, metadata = decrypt_pipeline(payload, priv)

    assert out == data
    assert metadata["original_size"] == len(data)
    assert metadata["kind"] == "report"
    assert len(payload) == 4096
