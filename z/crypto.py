"""Encryption utilities for the ``z.crypto`` module."""

from __future__ import annotations

import json
from typing import Any, Protocol

_LEN_SIZE = 4
_AES_BLOCK = 16


def _require_crypto() -> tuple[Any, Any, Any, Any, Any]:
    try:
        from Crypto.Cipher import AES, PKCS1_OAEP
        from Crypto.PublicKey import RSA
        from Crypto.Random import get_random_bytes
        from Crypto.Util.Padding import pad, unpad
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise ModuleNotFoundError(
            "PyCryptodome is required for z.crypto helpers. Install `pycryptodome`."
        ) from exc
    return AES, PKCS1_OAEP, RSA, get_random_bytes, (pad, unpad)


class PQCProvider(Protocol):
    """Protocol expected by PQC helper functions."""

    def encrypt(self, data: bytes) -> bytes: ...

    def decrypt(self, data: bytes) -> bytes: ...


def _pack_len(value: int) -> bytes:
    return value.to_bytes(_LEN_SIZE, "big")


def _unpack_len(blob: bytes, offset: int) -> tuple[int, int]:
    end = offset + _LEN_SIZE
    if end > len(blob):
        raise ValueError("payload too small for length prefix")
    return int.from_bytes(blob[offset:end], "big"), end


def _read_chunk(blob: bytes, offset: int) -> tuple[bytes, int]:
    size, cursor = _unpack_len(blob, offset)
    end = cursor + size
    if end > len(blob):
        raise ValueError("payload chunk is truncated")
    return blob[cursor:end], end


def encrypt_full(data: bytes, key: bytes) -> bytes:
    """Encrypt bytes in FULL-MODE: ``[len_IV][IV][cipher_text]``."""
    AES, _, _, get_random_bytes, (pad, _) = _require_crypto()
    iv = get_random_bytes(_AES_BLOCK)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(pad(data, _AES_BLOCK))
    return b"".join((_pack_len(len(iv)), iv, ciphertext))


def decrypt_full(payload: bytes, key: bytes) -> bytes:
    """Decrypt FULL-MODE payloads."""
    AES, _, _, _, (_, unpad) = _require_crypto()
    iv, cursor = _read_chunk(payload, 0)
    ciphertext = payload[cursor:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return unpad(cipher.decrypt(ciphertext), _AES_BLOCK)


def encrypt_fast(data: bytes, key: bytes, header_len: int = 4096) -> bytes:
    """Encrypt bytes in FAST-MODE: ``[len_IV][IV][len_cipher_text][cipher_text][rest]``."""
    AES, _, _, get_random_bytes, (pad, _) = _require_crypto()
    if header_len < 0:
        raise ValueError("header_len must be >= 0")
    iv = get_random_bytes(_AES_BLOCK)
    header = data[:header_len]
    clear_tail = data[header_len:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    ciphertext = cipher.encrypt(pad(header, _AES_BLOCK))
    return b"".join((_pack_len(len(iv)), iv, _pack_len(len(ciphertext)), ciphertext, clear_tail))


def decrypt_fast(payload: bytes, key: bytes) -> bytes:
    """Decrypt FAST-MODE payloads."""
    AES, _, _, _, (_, unpad) = _require_crypto()
    iv, cursor = _read_chunk(payload, 0)
    ciphertext, cursor = _read_chunk(payload, cursor)
    clear_tail = payload[cursor:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    header = unpad(cipher.decrypt(ciphertext), _AES_BLOCK)
    return header + clear_tail


def encrypt_pqc(data: bytes, provider: PQCProvider) -> bytes:
    """Encrypt bytes in PQC-MODE via a qclib-compatible provider."""
    return provider.encrypt(data)


def decrypt_pqc(payload: bytes, provider: PQCProvider) -> bytes:
    """Decrypt bytes in PQC-MODE via a qclib-compatible provider."""
    return provider.decrypt(payload)


def encrypt_pipeline(
    data: bytes,
    public_key_pem: bytes,
    *,
    pad_to_size: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> bytes:
    """Encrypt in PIPELINE-MODE.

    Format: ``[len_metadata][JSON][len_key][AES_KEY][len_IV][IV][ciphertext][len_padding][padding]``.
    """
    AES, PKCS1_OAEP, RSA, get_random_bytes, (pad, _) = _require_crypto()
    effective_metadata: dict[str, Any] = {"original_size": len(data), "algorithm": "AES-256-CBC"}
    if metadata:
        effective_metadata.update(metadata)
    metadata_blob = json.dumps(effective_metadata, separators=(",", ":")).encode("utf-8")

    aes_key = get_random_bytes(32)
    iv = get_random_bytes(_AES_BLOCK)
    aes_cipher = AES.new(aes_key, AES.MODE_CBC, iv=iv)
    ciphertext = aes_cipher.encrypt(pad(data, _AES_BLOCK))

    wrapped_key = PKCS1_OAEP.new(RSA.import_key(public_key_pem)).encrypt(aes_key)

    payload = b"".join(
        (
            _pack_len(len(metadata_blob)),
            metadata_blob,
            _pack_len(len(wrapped_key)),
            wrapped_key,
            _pack_len(len(iv)),
            iv,
            ciphertext,
        )
    )

    padding = b""
    if pad_to_size is not None:
        if pad_to_size < len(payload) + _LEN_SIZE:
            raise ValueError("pad_to_size is too small for payload")
        padding = get_random_bytes(pad_to_size - len(payload) - _LEN_SIZE)

    return b"".join((payload, _pack_len(len(padding)), padding))


def decrypt_pipeline(payload: bytes, private_key_pem: bytes) -> tuple[bytes, dict[str, Any]]:
    """Decrypt PIPELINE-MODE payloads and return ``(plaintext, metadata)``."""
    AES, PKCS1_OAEP, RSA, _, (_, unpad) = _require_crypto()
    metadata_blob, cursor = _read_chunk(payload, 0)
    wrapped_key, cursor = _read_chunk(payload, cursor)
    iv, cursor = _read_chunk(payload, cursor)

    metadata = json.loads(metadata_blob.decode("utf-8"))
    original_size = int(metadata.get("original_size", -1))
    if original_size < 0:
        raise ValueError("metadata must contain non-negative original_size")

    ciphertext_len = ((original_size // _AES_BLOCK) + 1) * _AES_BLOCK
    cipher_end = cursor + ciphertext_len
    if cipher_end > len(payload):
        raise ValueError("payload ciphertext is truncated")
    ciphertext = payload[cursor:cipher_end]

    padding_len, after_len = _unpack_len(payload, cipher_end)
    if after_len + padding_len != len(payload):
        raise ValueError("invalid padding length")

    aes_key = PKCS1_OAEP.new(RSA.import_key(private_key_pem)).decrypt(wrapped_key)
    plaintext = unpad(AES.new(aes_key, AES.MODE_CBC, iv=iv).decrypt(ciphertext), _AES_BLOCK)
    return plaintext, metadata
