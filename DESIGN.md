# DESIGN

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
