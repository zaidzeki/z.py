# DESIGN

## Image Processing

`z.image.process_image` uses `Pillow` to handle image operations. It supports:
- Format conversion (e.g., PNG to WebP).
- Quality setting for lossy formats.
- File-level optimization during save.

The `zi` CLI provides an entry point for these operations via the `image` subcommand.

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
