"""Symmetric and hybrid cryptography helpers for the ``z`` package."""

from __future__ import annotations

import json
import os
import struct
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Protocol

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


class PQCBackend(Protocol):
    """Minimal KEM interface expected from a PQC backend."""

    def encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]:
        """Return `(encapsulated_key, shared_secret)` for the provided public key."""

    def decapsulate(self, secret_key: bytes, encapsulated_key: bytes) -> bytes:
        """Return shared secret for a secret key and encapsulated key blob."""


@dataclass(frozen=True)
class PipelineMetadata:
    """Metadata written in pipeline payloads."""

    original_size: int
    mode: str = "PIPELINE-MODE"


def _pack_chunk(payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + payload


def _unpack_chunk(blob: bytes, cursor: int) -> tuple[bytes, int]:
    if cursor + 4 > len(blob):
        raise ValueError("Invalid payload: missing length prefix")
    size = struct.unpack(">I", blob[cursor : cursor + 4])[0]
    cursor += 4
    if cursor + size > len(blob):
        raise ValueError("Invalid payload: truncated chunk")
    return blob[cursor : cursor + size], cursor + size


def _new_iv() -> bytes:
    return os.urandom(12)


def _aes_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return ciphertext + tag


def _aes_decrypt(key: bytes, iv: bytes, ciphertext_and_tag: bytes) -> bytes:
    if len(ciphertext_and_tag) < 16:
        raise ValueError("Invalid ciphertext: missing authentication tag")
    ciphertext, tag = ciphertext_and_tag[:-16], ciphertext_and_tag[-16:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
    return cipher.decrypt_and_verify(ciphertext, tag)


def encrypt_fast(data: bytes, key: bytes, *, chunk_size: int = 1024 * 1024) -> bytes:
    """Encrypt only the first chunk and append remaining cleartext.

    Format: ``[len_IV][IV][len_cipher_text][cipher_text][rest_cleartext]``.
    """
    head = data[:chunk_size]
    rest = data[chunk_size:]
    iv = _new_iv()
    cipher_text = _aes_encrypt(key, iv, head)
    return _pack_chunk(iv) + _pack_chunk(cipher_text) + rest


def decrypt_fast(blob: bytes, key: bytes) -> bytes:
    """Decrypt payload produced by :func:`encrypt_fast`."""
    iv, cursor = _unpack_chunk(blob, 0)
    cipher_text, cursor = _unpack_chunk(blob, cursor)
    rest = blob[cursor:]
    return _aes_decrypt(key, iv, cipher_text) + rest


def encrypt_full(data: bytes, key: bytes) -> bytes:
    """Encrypt full payload.

    Format: ``[len_IV][IV][cipher_text]`` where cipher text includes auth tag.
    """
    iv = _new_iv()
    cipher_text = _aes_encrypt(key, iv, data)
    return _pack_chunk(iv) + cipher_text


def decrypt_full(blob: bytes, key: bytes) -> bytes:
    """Decrypt payload produced by :func:`encrypt_full`."""
    iv, cursor = _unpack_chunk(blob, 0)
    return _aes_decrypt(key, iv, blob[cursor:])


def encrypt_pipeline(
    data: bytes,
    public_key_pem: bytes,
    *,
    pad_to_size: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> bytes:
    """Encrypt payload with random AES key wrapped by an RSA public key.

    Format:
    ``[len_metadata][JSON metadata][len_key][encrypted_aes_key]``
    ``[len_IV][IV][ciphertext][len_padding][padding]``
    """
    aes_key = os.urandom(32)
    iv = _new_iv()
    ciphertext = _aes_encrypt(aes_key, iv, data)

    rsa_key = RSA.import_key(public_key_pem)
    wrapped_key = PKCS1_OAEP.new(rsa_key).encrypt(aes_key)

    payload_meta = metadata or {}
    payload_meta.setdefault("original_size", len(data))
    payload_meta.setdefault("mode", "PIPELINE-MODE")
    metadata_bytes = json.dumps(payload_meta, sort_keys=True, separators=(",", ":")).encode("utf-8")

    body = (
        _pack_chunk(metadata_bytes)
        + _pack_chunk(wrapped_key)
        + _pack_chunk(iv)
        + _pack_chunk(ciphertext)
    )
    if pad_to_size is not None:
        if pad_to_size < len(body) + 4:
            raise ValueError("pad_to_size is smaller than payload")
        padding = os.urandom(pad_to_size - len(body) - 4)
    else:
        padding = b""
    return body + _pack_chunk(padding)


def decrypt_pipeline(blob: bytes, private_key_pem: bytes) -> tuple[bytes, dict[str, Any]]:
    """Decrypt payload produced by :func:`encrypt_pipeline`."""
    metadata_bytes, cursor = _unpack_chunk(blob, 0)
    wrapped_key, cursor = _unpack_chunk(blob, cursor)
    iv, cursor = _unpack_chunk(blob, cursor)
    ciphertext, cursor = _unpack_chunk(blob, cursor)
    _padding, cursor = _unpack_chunk(blob, cursor)
    if cursor != len(blob):
        raise ValueError("Invalid payload: trailing bytes")

    rsa_key = RSA.import_key(private_key_pem)
    aes_key = PKCS1_OAEP.new(rsa_key).decrypt(wrapped_key)
    plaintext = _aes_decrypt(aes_key, iv, ciphertext)
    return plaintext, json.loads(metadata_bytes.decode("utf-8"))


def _load_default_pqc_backend() -> PQCBackend:
    """Load a default qclib backend if available."""
    qclib = import_module("qclib")
    if hasattr(qclib, "Kyber512"):
        return qclib.Kyber512()  # type: ignore[no-any-return]
    if hasattr(qclib, "Kyber"):
        return qclib.Kyber()  # type: ignore[no-any-return]
    raise RuntimeError("Unsupported qclib version: expected Kyber backend")


def encrypt_pqc(data: bytes, public_key: bytes, *, backend: PQCBackend | None = None) -> bytes:
    """Encrypt with PQC key encapsulation and AES-GCM payload encryption."""
    kem = backend or _load_default_pqc_backend()
    encapsulated_key, shared_secret = kem.encapsulate(public_key)
    aes_key = shared_secret[:32]
    iv = _new_iv()
    ciphertext = _aes_encrypt(aes_key, iv, data)
    return _pack_chunk(encapsulated_key) + _pack_chunk(iv) + ciphertext


def decrypt_pqc(blob: bytes, secret_key: bytes, *, backend: PQCBackend | None = None) -> bytes:
    """Decrypt payload produced by :func:`encrypt_pqc`."""
    kem = backend or _load_default_pqc_backend()
    encapsulated_key, cursor = _unpack_chunk(blob, 0)
    iv, cursor = _unpack_chunk(blob, cursor)
    shared_secret = kem.decapsulate(secret_key, encapsulated_key)
    aes_key = shared_secret[:32]
    return _aes_decrypt(aes_key, iv, blob[cursor:])
