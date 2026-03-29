# z

A Python package that now includes the `z.crypto` encryption module.

It also includes `z.ftp` for simple FTP/FTPS connection lifecycle and file operations.
It includes a CLI entrypoint alias `zi` for recovery and cipher workflows.

## `z.crypto` modes

- **FAST-MODE** for videos/images and other header-dependent formats.  
  Format: `[len_IV][IV][len_cipher_text][cipher_text][rest cleartext]`
- **FULL-MODE** for full-file encryption.  
  Format: `[len_IV][IV][cipher_text]`
- **PQC-MODE** via provider integration (designed for `qclib` adapters).
- **PIPELINE-MODE** hybrid encryption using RSA public-key wrapping + AES content encryption.  
  Format: `[len_metadata][JSON file stat data][len_key][AES_KEY][len_IV][IV][ciphertext][len_padding][padding]`

## Quick start

```bash
pip install -e .
pytest
```

## Example

```python
from z.crypto import encrypt_full, decrypt_full

key = b"k" * 32
cipher = encrypt_full(b"hello", key)
plain = decrypt_full(cipher, key)
assert plain == b"hello"
```

## FTP example

```python
from z.ftp import FTP

ftp = FTP(user="user", password="pass", host="ftp.example.com", port=21, cwd="/", use_tls=True)
session = ftp.open()
session.upload("report.pdf")
session.close()
```

## CLI example

```bash
zi recover backup.tar
zi cipher generate --name alpha --aliases a1,a2 --strength high
zi cipher encrypt --name alpha --rsa-bits 2048
```
