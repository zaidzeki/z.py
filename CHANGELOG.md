# CHANGELOG

## 0.9.0 - 2026-06-02 14:44:00 GMT+3
- Added binary bundle format version 1 (`ZBDL`) supporting high-density compression.
- Supported standard library compression (`gzip`, `xz`/`lzma`) and custom optional `br` (`brotli`).
- Implemented size parsing supporting convenient units (e.g., `10M`, `500K`).
- Engineered advanced file-splitting across bundle boundaries with skip/push and sole-file fallbacks.
- Exposed CLI `zi bundles` and `zi unbundle` commands.
- Extended test coverage with split-boundary validation.

## 0.8.0 - 2026-05-31 16:30:00 GMT+3
- Integrated `z.ftp.ZFTP` context manager for secure and complete FTPS interactions.
- Exported `ZFTP` at package root.
- Added comprehensive mocked FTPS unit tests.

## 0.7.0 - 2026-05-31 15:35:00 GMT+3
- Added `z.aes_fast` providing ultra-fast, low-memory streaming AES-256-CTR encryption and decryption.
- Exposed `encrypt_stream`, `decrypt_stream`, and `derive_key` APIs at package root.
- Integrated `encrypt-fast` and `decrypt-fast` commands into the `zi` CLI.
- Added comprehensive unit and integration CLI tests.

## 0.6.0 - 2026-03-29 18:30:30 GMT+3
- Added `zi` CLI entrypoint with new `image` subcommand for Pillow-based format conversion.
- Added support for `--input/-i`, `--output/-o`, `--format/-f`, `--quality`, and `--optimize` options.
- Added automated tests for successful conversion and unsupported format handling.
- Added `NOTES.md` and refreshed project documentation for image CLI usage.

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
