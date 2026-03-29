# BACKLOG

- Add optional compression support to bundle format while remaining backward compatible.
- Add optimistic file-locking for `Store.save()` to avoid concurrent write corruption.
- Consider adding a lightweight `NamespaceView` object for mutable mapping semantics per namespace.
- Add file-based streaming APIs for `z.crypto` to avoid loading large assets fully in memory.
- Add batch image conversion (`zi image --input-dir`) with recursive mode and extension filters.
