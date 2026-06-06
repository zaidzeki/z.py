# AGENT_NOTES

- Project now includes binary bundle/unbundle support in `z.bundle`.
- Versioning policy applied: feature work bumped `0.8.0` to `0.9.0`.
- Repository-level AGENTS instructions expanded and linked via lowercase alias.
- Added `z.store.Store` with namespaced SHA-256 keyed records and JSON persistence.
- Added dict-like indexing support to `Store` via `__getitem__`, `__setitem__`, and `__delitem__`.
- Added `z.crypto` with four encryption modes: FAST, FULL, PQC (backend-injected), and PIPELINE (hybrid RSA+AES with optional payload padding).
- Added `zi image` CLI command (`z.cli`) with Pillow conversion, quality validation, optimize flag, and JPEG RGB fallback.
- Added CLI tests for successful WEBP conversion and unsupported format validation.
- Introduced `NOTES.md` for persistent cross-agent project context as requested.
- Integrated ultra-fast streaming AES-256-CTR encryption under `z.aes_fast` and exposed it in `zi` CLI as `encrypt-fast` and `decrypt-fast` subcommands.
- Integrated `SlimShadyFTP` client with full FTPS support and context manager lifecycle hooks.
- Upgraded binary bundle implementation to format version 1 (`ZBDL`), introducing sequential multi-part files, Gzip/XZ/Brotli compression, and chunk-splitting boundary constraints.
- Integrated `z.ratelimit` sliding-window rate limiter; `limit` decorator is thread-safe using a single lock per wrapped function; `delay_duration` accepts both float and `"Xs"` string forms.