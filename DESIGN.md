# DESIGN

## CLI image conversion

`zi image` is a thin Pillow wrapper intended for local/offline conversion:

- Input and output paths are explicit (`--input`, `--output`).
- Format normalization is handled via aliases (`jpg` -> `JPEG`, etc.).
- Quality is validated in the range `1..100`.
- `--optimize` is passed through to Pillow's save options.
- JPEG conversion auto-converts alpha-bearing modes to RGB for compatibility.

## Bundle mode format

Each file entry is written sequentially as:

1. `path_len`: 16-bit unsigned integer (big-endian)
2. `path`: UTF-8 bytes
3. `data_len`: 32-bit unsigned integer (big-endian)
4. `data`: raw file bytes

Directory inputs are supported only with `recursively=True`; extracted files are restored relative to the output directory.

## Namespaced store persistence

`z.store.Store` keeps records under namespaces and uses SHA-256 of canonical JSON payloads as stable keys.
The state is persisted as JSON (`namespace -> key -> payload`) so it can be synced to disk and loaded on startup.
Dict-like indexing is also available for convenience (`store[namespace]`, `store[namespace, key]`, and assignment/deletion variants).

## Crypto mode layouts

`z.crypto` uses AES-GCM for symmetric encryption and provides four payload modes.

- `FAST-MODE`: `[len_IV][IV][len_cipher_text][cipher_text][rest_cleartext]`
- `FULL-MODE`: `[len_IV][IV][cipher_text]`
- `PQC-MODE`: `[len_encapsulated_key][encapsulated_key][len_IV][IV][cipher_text]`
- `PIPELINE-MODE`: `[len_metadata][metadata_json][len_wrapped_key][wrapped_aes_key][len_IV][IV][len_ciphertext][ciphertext][len_padding][padding]`

`PIPELINE-MODE` supports optional deterministic outer payload size (`pad_to_size`) to reduce length leakage.

## Streaming AES-CTR (Fast) Mode

`z.aes_fast` provides a stream-based encryption mode using AES-256-CTR with a single SHA3-512 key derivation function (KDF).
Layout:
- `MAGIC`: 4 bytes (`FAST`)
- `NONCE`: 8 bytes (used as CTR mode nonce)
- `CIPHERTEXT`: remaining bytes processed in 256 KB chunks

Security Notes:
- No ciphertext authenticity (no MAC/malleable ciphertext).
- No KDF work factor (weak passwords can be brute-forced easily).
- Ideal for performance-critical or memory-constrained scenarios where obfuscation or basic confidentiality suffices.

## FTPS Client Integration

`z.ftp.ZFTP` is a context manager wrapper around `ftplib.FTP_TLS`:
- Supports parameter overrides for host, user, passwd, remote_dir, timeout, and ssl_version, defaulting to connection configurations.
- Calls `.auth()` and `.prot_p()` upon entering the context to establish secure TLS data channel connection, then logs in and directories to `remote_dir`.
- Exposes standard file operations: `upload`, `download`, `list_files`, `delete`, `mkdir`, `rmdir`, and `rename`.
- Safely terminates connections during block exit by calling `quit()` or falling back to `close()`.
