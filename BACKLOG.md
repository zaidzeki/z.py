# BACKLOG

## P0: Namespace Views
- **Goal**: Design a lightweight `NamespaceView` object.
- **Details**:
  - Provide clean mutable mapping semantics per namespace.

## P1: Secure Streaming Encryption (`aes_secure`)
- **Goal**: Create a secure streaming encryption alternative to the fast-mode obfuscation.
- **Details**:
  - Implement a key derivation function using PBKDF2 (with salt and work factor) instead of simple single-hash KDF.
  - Implement authenticated encryption using AES-GCM (with MAC / integrity checks) to prevent ciphertext tampering and malleability attacks.

## P2: Store & Crypto Improvements
- **Optimistic File-locking for `Store`**:
  - Implement file-level locks during `Store.save()` to prevent concurrent write corruption.
- **File-based Streaming APIs for `z.crypto`**:
  - Add streaming versions of the core `z.crypto` algorithms (FAST, FULL, PIPELINE, PQC) to handle large files efficiently without loading them entirely in memory.

## P3: Batch Image Manipulation
- **Goal**: Expand `zi image` CLI to handle directories and batch actions.
- **Details**:
  - Support input directory (`--input-dir`) and output directory (`--output-dir`).
  - Add filters for file extensions (e.g., convert only `*.png` or `*.jpg`).
  - Implement recursive directory traversal flags.