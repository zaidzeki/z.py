# BACKLOG

## P0: Bundle Versioning & Compression
- **Goal**: Implement bundle format v1 with built-in compression.
- **Details**:
  - Since the library has not been used yet, there is no need for backward compatibility with v0.
  - Integrate standard library compression (e.g., `zlib` or `bz2`).
  - Prepend a version/compression header at the start of the bundle file.

## P1: Secure Streaming Encryption (`aes_secure`)
- **Goal**: Create a secure streaming encryption alternative to the fast-mode obfuscation.
- **Details**:
  - Implement a key derivation function using PBKDF2 (with salt and work factor) instead of simple single-hash KDF.
  - Implement authenticated encryption using AES-GCM (with MAC / integrity checks) to prevent ciphertext tampering and malleability attacks.

## P2: Store & Crypto Improvements
- **Optimistic File-locking for `Store`**:
  - Implement file-level locks during `Store.save()` to prevent concurrent write corruption.
- **Namespace Views**:
  - Design a lightweight `NamespaceView` object to provide clean mutable mapping semantics per namespace.
- **File-based Streaming APIs for `z.crypto`**:
  - Add streaming versions of the core `z.crypto` algorithms (FAST, FULL, PIPELINE, PQC) to handle large files efficiently without loading them entirely in memory.

## P3: Batch Image Manipulation
- **Goal**: Expand `zi image` CLI to handle directories and batch actions.
- **Details**:
  - Support input directory (`--input-dir`) and output directory (`--output-dir`).
  - Add filters for file extensions (e.g., convert only `*.png` or `*.jpg`).
  - Implement recursive directory traversal flags.
