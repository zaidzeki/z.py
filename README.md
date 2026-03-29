# z

A minimal Python package scaffold.

## Quick start

```bash
pip install -e .
pytest
```

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
