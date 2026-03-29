# DESIGN

## Goals
- Provide practical multi-mode encryption APIs for different file characteristics.
- Keep binary wire formats explicit and length-prefixed for robust parsing.

## Modes
- FAST-MODE encrypts only an initial header segment.
- FULL-MODE encrypts full payload bytes.
- PQC-MODE delegates to a provider interface for post-quantum schemes.
- PIPELINE-MODE uses hybrid encryption: random AES session key wrapped by RSA public key.

## Security notes
- AES uses CBC + PKCS#7 padding via PyCryptodome.
- PIPELINE metadata includes `original_size` to safely recover ciphertext segment boundaries.

## CLI design
- `zi recover` auto-detects compression/archive format from suffix and writes recovered output.
- `zi cipher generate` stores user profile metadata in `~/.zekiprod/cipher/main.db`.
- `zi cipher encrypt` resolves profile by name/alias, creates RSA keys, and encrypts private key bytes via password-derived AES key.
