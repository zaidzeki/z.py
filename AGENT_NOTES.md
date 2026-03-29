# AGENT_NOTES

- Project now includes binary bundle/unbundle support in `z.bundle`.
- Versioning policy applied: feature work bumped `0.1.0` to `0.2.0`.
- Repository-level AGENTS instructions expanded and linked via lowercase alias.
- Added `z.store.Store` with namespaced SHA-256 keyed records and JSON persistence.
- Added dict-like indexing support to `Store` via `__getitem__`, `__setitem__`, and `__delitem__`.
- Added `z.crypto` with four encryption modes: FAST, FULL, PQC (backend-injected), and PIPELINE (hybrid RSA+AES with optional payload padding).
- Added `zi image` CLI command (`z.cli`) with Pillow conversion, quality validation, optimize flag, and JPEG RGB fallback.
- Added CLI tests for successful WEBP conversion and unsupported format validation.
- Introduced `NOTES.md` for persistent cross-agent project context as requested.
