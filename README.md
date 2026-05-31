# z

A minimal Python package scaffold with bundling, storage, crypto, and image CLI helpers.

## Quick start

```bash
pip install -e .
pytest
```

## CLI: `zi image`

Use Pillow-backed conversion with format, quality, and optimization flags:

```bash
zi image \
  --input ./input.png \
  --output ./output.webp \
  --format webp \
  --quality 82 \
  --optimize
```

Arguments:

- `--input/-i` input filepath
- `--output/-o` output filepath
- `--format/-f` target format (`webp`, `jpg`, `png`, `gif`, ...)
- `--quality` output quality (`1..100`)
- `--optimize` enable Pillow optimization when supported

## CLI: `zi encrypt-fast` & `zi decrypt-fast`

Ultra-fast, low-memory AES-256-CTR streaming file encryption:

```bash
zi encrypt-fast -i large_file.bin -o large_file.enc -p password
zi decrypt-fast -i large_file.enc -o large_file.out -p password
```

Omit the `-p` parameter to be securely prompted for the password.

## Bundle mode

```python
from z import bundle, unbundle

bundle(["a.txt", "b.txt"], "archive.zb")
unbundle("archive.zb", "./out")
```

For directory paths, pass `recursively=True`.

## Namespaced store

```python
from z import Store

store = Store("./data/store.json")
store["widgets"] = {"id": 1, "name": "alpha"}  # dict-like register
records = store["widgets"]
payload = store["widgets", records[0].key]  # dict-like lookup
store.save()

assert payload["name"] == "alpha"
```

Records are keyed by deterministic SHA-256 hashes of canonical JSON payloads.

## `z.crypto` modes

```python
from z.crypto import encrypt_fast, decrypt_fast, encrypt_full, decrypt_full

key = b"k" * 32
payload = encrypt_fast(b"video-bytes", key, chunk_size=1024)
assert decrypt_fast(payload, key) == b"video-bytes"

blob = encrypt_full(b"plain-text", key)
assert decrypt_full(blob, key) == b"plain-text"
```

Available modes:

- `FAST-MODE`: `[len_IV][IV][len_cipher_text][cipher_text][rest_cleartext]`
- `FULL-MODE`: `[len_IV][IV][cipher_text]`
- `PQC-MODE`: KEM + AES-GCM (uses `qclib` backend when available, or custom backend injection)
- `PIPELINE-MODE`: public-key wrapped AES key + metadata + optional payload padding

## Streaming encryption (low-memory)

For large files, use `encrypt_stream` and `decrypt_stream` with a file-like interface:

```python
from z import encrypt_stream, decrypt_stream

with open("large.bin", "rb") as fin, open("large.enc", "wb") as fout:
    encrypt_stream(fin, fout, "securepassword")

with open("large.enc", "rb") as fin, open("large.dec", "wb") as fout:
    decrypt_stream(fin, fout, "securepassword")
```

