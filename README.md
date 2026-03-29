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
