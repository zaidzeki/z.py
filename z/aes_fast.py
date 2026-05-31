"""Ultra-fast, low-memory AES-256-CTR file encryption.

Key derivation: Single SHA3-512 hash (no iterations, no salt).

WARNING: "Super minimum security" means:
  - No authentication (MAC). Ciphertext is malleable (bit-flipping attacks).
  - No KDF work factor. Vulnerable to rapid GPU brute-force if password is weak.
  - Use only for obfuscation or when performance/memory strictly outweighs security.
"""

from __future__ import annotations

import io
import os

# Standard dynamic fallback resolving for PyCryptodome / PyCryptodomex
try:
    from Crypto.Cipher import AES
    from Crypto.Hash import SHA3_512
except ImportError:
    try:
        from Cryptodome.Cipher import AES
        from Cryptodome.Hash import SHA3_512
    except ImportError as exc:
        raise ImportError(
            "The 'pycryptodome' or 'pycryptodomex' package is required to run this script. "
            "Please install it using 'pip install pycryptodome'."
        ) from exc

MAGIC = b"FAST"
NONCE_LEN = 8  # 8 bytes nonce + 8 bytes counter for CTR mode
CHUNK_SIZE = 256 * 1024  # 256 KB chunks for optimal I/O vs memory balance


def derive_key(password: str) -> bytes:
    """Derive a 256-bit key from a password.

    Uses a single SHA3-512 hash. This is extremely fast but provides
    no brute-force work factor or salt. Use only when performance
    outweighs cryptographic strength requirements.

    Parameters
    ----------
    password : str
        The plain-text password to derive the key from.

    Returns
    -------
    bytes
        A 32-byte key derived from the password.
    """
    return SHA3_512.new(password.encode("utf-8")).digest()[:32]


def encrypt_stream(in_file: io.IOBase, out_file: io.IOBase, password: str) -> None:
    """Stream-encrypts data in chunks to maintain O(1) memory usage.

    Parameters
    ----------
    in_file : io.IOBase
        The input binary stream to read plaintext from.
    out_file : io.IOBase
        The output binary stream to write ciphertext to.
    password : str
        The encryption password.
    """
    key = derive_key(password)
    nonce = os.urandom(NONCE_LEN)

    out_file.write(MAGIC)
    out_file.write(nonce)

    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)

    while True:
        chunk = in_file.read(CHUNK_SIZE)
        if not chunk:
            break
        out_file.write(cipher.encrypt(chunk))


def decrypt_stream(in_file: io.IOBase, out_file: io.IOBase, password: str) -> None:
    """Stream-decrypts data in chunks.

    Parameters
    ----------
    in_file : io.IOBase
        The input binary stream to read ciphertext from.
    out_file : io.IOBase
        The output binary stream to write decrypted plaintext to.
    password : str
        The decryption password.

    Raises
    ------
    ValueError
        If the stream header magic is invalid or truncated.
    """
    magic = in_file.read(4)
    if magic != MAGIC:
        raise ValueError("Not a valid encrypted file (bad magic)")

    nonce = in_file.read(NONCE_LEN)
    if len(nonce) != NONCE_LEN:
        raise ValueError("Truncated header")

    key = derive_key(password)
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)

    while True:
        chunk = in_file.read(CHUNK_SIZE)
        if not chunk:
            break
        out_file.write(cipher.decrypt(chunk))
