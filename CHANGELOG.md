# CHANGELOG

## 0.12.0 - 2026-06-06 14:38:00 GMT+3
- Added `z.clean` module containing the `remove_files_by_hash` function to recursively clean files matching a set of hashes.
- Exposed `clean` subcommand in `zi` CLI parser.
- Added comprehensive unit tests in `tests/test_clean.py`.
- Bumped version `0.11.0` → `0.12.0`.

## 0.11.0 - 2026-06-06 12:29:00 GMT+3
- Added `z.filetree` module with `FileStructureGenerator` class and `generate_tree` convenience function.
- Renders Unicode directory trees with `├──` / `└──` connectors and `│` continuation lines.
- Supports `max_depth`, `include_hidden`, and a configurable `ignore_list` (default ignores `.git`, `__pycache__`, `.DS_Store`, `node_modules`).
- Directories sorted before files; entries sorted case-insensitively within each group.
- Handles `PermissionError` gracefully with an inline `[Permission Denied]` marker.
- Exported `FileStructureGenerator` and `generate_tree` at package root.
- Added `zi tree [path] [--depth N] [--hidden] [--ignore NAME…]` CLI subcommand.
- Added `tests/test_filetree.py` with 23 tests covering root line, entry listing, connectors, depth limiting, hidden-file control, custom ignore lists, permission errors, and class-API idempotence.
- Bumped version `0.10.0` → `0.11.0`.

## 0.10.0 - 2026-06-06 11:41:00 GMT+3
- Added `z.ratelimit` module with sliding-window `limit` decorator and `RateLimitExceeded` exception.
- Supports `cphs` (0.5 s), `cpm` (60 s), `cph` (3 600 s), `cpd` (86 400 s), `cpw` (604 800 s) windows.
- Implemented thread-safe call-history eviction with a single `threading.Lock`.
- `delay=True` mode sleeps and retries; `delay=False` mode silently returns `None` or raises on breach.
- `delay_duration` accepts both `float` and string forms like `"0.5s"`.
- Exported `limit` and `RateLimitExceeded` at package root.
- Added comprehensive test suite: basic limits, sliding-window behaviour, delay mode, thread safety, and metadata preservation.

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
