# CHANGELOG

## 0.6.0 (2025-02-17 11:34 GMT+3)
- Added image processing support via `z.image.process_image`.
- Added `zi image` CLI for format conversion, optimization, and quality adjustment.
- Added `Pillow` dependency.

## 0.5.0 - 2026-03-29 12:05:00 GMT+3
- Added new `z.crypto` module with FAST, FULL, PQC, and PIPELINE encryption/decryption helpers.
- Added tests for all crypto modes including hybrid encryption padding behavior.
- Exported crypto APIs from package root and documented mode formats.
- Added runtime dependency on `pycryptodome`.

## 0.4.0 - 2026-03-29 11:30:00 GMT+3
- Added dict-like indexing support in `Store` for convenient namespace/record get, set, and delete operations.
- Extended store tests and documentation for the indexing behavior.

## 0.3.0 - 2026-03-29 11:10:00 GMT+3
- Added `z.store.Store` for namespaced, SHA-256 keyed instance tracking with JSON disk persistence.
- Added tests for registration, deduplication, persistence reload, and removal behavior.

## 0.2.0 - 2026-03-29 10:32:00 GMT+3
- Added `z.bundle` with binary `bundle` and `unbundle` APIs that preserve file paths.
- Added tests for regular, recursive, and directory-validation bundle flows.
- Exported bundle APIs from package root.
