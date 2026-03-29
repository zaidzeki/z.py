# CHANGELOG

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
