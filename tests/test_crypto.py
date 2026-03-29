"""Tests for ``z.crypto``."""

from __future__ import annotations

import pytest
from Crypto.PublicKey import RSA

from z.crypto import (
    decrypt_fast,
    decrypt_full,
    decrypt_pipeline,
    decrypt_pqc,
    encrypt_fast,
    encrypt_full,
    encrypt_pipeline,
    encrypt_pqc,
)


def test_full_mode_roundtrip() -> None:
    key = b"k" * 32
    plaintext = b"hello full mode"

    payload = encrypt_full(plaintext, key)

    assert decrypt_full(payload, key) == plaintext


def test_fast_mode_only_encrypts_prefix() -> None:
    key = b"f" * 32
    plaintext = b"A" * 32 + b"B" * 32

    payload = encrypt_fast(plaintext, key, chunk_size=32)

    assert payload.endswith(b"B" * 32)
    assert decrypt_fast(payload, key) == plaintext


def test_pipeline_mode_roundtrip_with_padding() -> None:
    key = RSA.generate(2048)
    public_pem = key.publickey().export_key()
    private_pem = key.export_key()

    plaintext = b"highly sensitive report"
    payload = encrypt_pipeline(plaintext, public_pem, pad_to_size=512)

    restored, metadata = decrypt_pipeline(payload, private_pem)
    assert restored == plaintext
    assert metadata["mode"] == "PIPELINE-MODE"
    assert metadata["original_size"] == len(plaintext)
    assert len(payload) == 512


class _FakePQC:
    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]:
        return b"capsule:" + public_key, b"s" * 32

    def decapsulate(self, secret_key: bytes, encapsulated_key: bytes) -> bytes:
        if secret_key != b"sk" or not encapsulated_key.startswith(b"capsule:"):
            raise ValueError("bad key")
        return b"s" * 32


def test_pqc_mode_roundtrip_with_custom_backend() -> None:
    backend = _FakePQC()
    plaintext = b"pqc content"

    payload = encrypt_pqc(plaintext, b"pk", backend=backend)

    assert decrypt_pqc(payload, b"sk", backend=backend) == plaintext


def test_pipeline_pad_validation() -> None:
    key = RSA.generate(2048)
    with pytest.raises(ValueError):
        encrypt_pipeline(b"tiny", key.publickey().export_key(), pad_to_size=8)
