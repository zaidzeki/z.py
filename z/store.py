"""Persistent namespaced store with cryptographic keys."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StoreRecord:
    """Stored record metadata."""

    namespace: str
    key: str
    payload: dict[str, Any]


class Store:
    """Track namespaced instances and persist them to disk.

    The store keeps entries grouped by namespace. Each entry gets a deterministic
    cryptographic key generated from a canonical JSON representation of the payload.

    Dict-like convenience helpers are available:
    - ``store[namespace]`` -> list of :class:`StoreRecord` in that namespace
    - ``store[namespace, key]`` -> payload dictionary
    - ``store[namespace] = payload`` -> register payload in namespace
    - ``del store[namespace, key]`` -> remove one entry
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._namespaces: dict[str, dict[str, dict[str, Any]]] = {}
        if self._path.exists():
            self.load()

    def __getitem__(self, item: str | tuple[str, str]) -> list[StoreRecord] | dict[str, Any]:
        """Dictionary-like access to namespaces and records."""
        if isinstance(item, tuple):
            namespace, key = item
            payload = self._namespaces.get(namespace, {}).get(key)
            if payload is None:
                raise KeyError((namespace, key))
            return payload

        return self.records(item)

    def __setitem__(self, namespace: str, payload: dict[str, Any]) -> None:
        """Dictionary-like registration: ``store[namespace] = payload``."""
        self.register(namespace, payload)

    def __delitem__(self, item: tuple[str, str]) -> None:
        """Dictionary-like delete: ``del store[namespace, key]``."""
        namespace, key = item
        removed = self.remove(namespace, key)
        if not removed:
            raise KeyError((namespace, key))

    @staticmethod
    def make_key(payload: dict[str, Any]) -> str:
        """Create a deterministic SHA-256 key for a payload dictionary."""
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def register(self, namespace: str, payload: dict[str, Any]) -> str:
        """Register payload in a namespace and return its key.

        Existing matching payloads are de-duplicated by key.
        """
        key = self.make_key(payload)
        bucket = self._namespaces.setdefault(namespace, {})
        bucket[key] = payload
        return key

    def exists(self, namespace: str, payload: dict[str, Any]) -> bool:
        """Return whether payload exists in namespace."""
        key = self.make_key(payload)
        return key in self._namespaces.get(namespace, {})

    def get(self, namespace: str, key: str) -> StoreRecord | None:
        """Fetch a record by namespace and key."""
        payload = self._namespaces.get(namespace, {}).get(key)
        if payload is None:
            return None
        return StoreRecord(namespace=namespace, key=key, payload=payload)

    def remove(self, namespace: str, key: str) -> bool:
        """Delete a key from a namespace and return whether it existed."""
        bucket = self._namespaces.get(namespace)
        if not bucket or key not in bucket:
            return False

        del bucket[key]
        if not bucket:
            del self._namespaces[namespace]
        return True

    def records(self, namespace: str) -> list[StoreRecord]:
        """List all records from one namespace."""
        return [
            StoreRecord(namespace=namespace, key=key, payload=payload)
            for key, payload in sorted(self._namespaces.get(namespace, {}).items())
        ]

    def load(self) -> None:
        """Load store state from the backing JSON file."""
        data = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Store file must contain a JSON object")

        parsed: dict[str, dict[str, dict[str, Any]]] = {}
        for namespace, records in data.items():
            if not isinstance(namespace, str) or not isinstance(records, dict):
                raise ValueError("Invalid store structure")
            parsed[namespace] = {}
            for key, payload in records.items():
                if not isinstance(key, str) or not isinstance(payload, dict):
                    raise ValueError("Invalid store record")
                parsed[namespace][key] = payload

        self._namespaces = parsed

    def save(self) -> Path:
        """Persist state to disk and return the file path."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        serialized = json.dumps(self._namespaces, indent=2, sort_keys=True, ensure_ascii=False)
        self._path.write_text(f"{serialized}\n", encoding="utf-8")
        return self._path
