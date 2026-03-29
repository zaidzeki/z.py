# CHANGELOG

## 0.4.0 - 2026-03-29 11:29:26 GMT+3
- Added `z.cli` module and `zi` command alias.
- Added `zi recover` support for `gzip`, `xz`, `bz2`, `br`, `tar`, and `zip` recovery workflows.
- Added `zi cipher generate` and `zi cipher encrypt` flows with prompt/getpass support and cipher DB/key storage under `~/.zekiprod/cipher`.
- Added CLI test coverage and updated README.

## 0.3.0 - 2026-03-29 11:20:48 GMT+3
- Added `z.ftp` module with `FTP` config factory and `FTPInstance` session methods: `cd`, `ls`, `upload`, `rm`, `download`, `mv`, `close`.
- Added tests for FTP behavior via fake clients to avoid network dependency.
- Exported FTP APIs from package root and updated README examples.

## 0.2.0 - 2026-03-29 11:13:00 GMT+3
- Added `z.crypto` module with FAST, FULL, PQC-provider, and PIPELINE encryption modes.
- Added tests for crypto round-trips.
- Updated package metadata and README.
- Added project governance documents (`AGENT_NOTES.md`, `BACKLOG.md`, `DESIGN.md`).
