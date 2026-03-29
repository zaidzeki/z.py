"""Tests for ``z.store``."""

from pathlib import Path

from z.store import Store


def test_store_register_exists_and_get(tmp_path: Path) -> None:
    store = Store(tmp_path / "state.json")

    payload = {"id": 1, "name": "alpha"}
    key = store.register("widgets", payload)

    assert store.exists("widgets", payload)
    record = store.get("widgets", key)
    assert record is not None
    assert record.namespace == "widgets"
    assert record.key == key
    assert record.payload == payload


def test_store_deduplicates_by_hash(tmp_path: Path) -> None:
    store = Store(tmp_path / "state.json")

    payload_a = {"name": "alpha", "id": 1}
    payload_b = {"id": 1, "name": "alpha"}

    key_a = store.register("widgets", payload_a)
    key_b = store.register("widgets", payload_b)

    assert key_a == key_b
    assert len(store.records("widgets")) == 1


def test_store_save_and_reload(tmp_path: Path) -> None:
    path = tmp_path / "state" / "store.json"
    store = Store(path)

    payload = {"id": "abc", "enabled": True}
    key = store.register("flags", payload)
    store.save()

    loaded = Store(path)
    record = loaded.get("flags", key)

    assert record is not None
    assert record.payload == payload


def test_store_remove_cleans_empty_namespace(tmp_path: Path) -> None:
    store = Store(tmp_path / "state.json")
    key = store.register("jobs", {"run": "nightly"})

    assert store.remove("jobs", key)
    assert store.records("jobs") == []


def test_store_dict_like_indexing(tmp_path: Path) -> None:
    store = Store(tmp_path / "state.json")

    store["widgets"] = {"id": 2, "name": "beta"}
    records = store["widgets"]
    assert len(records) == 1

    key = records[0].key
    assert store["widgets", key] == {"id": 2, "name": "beta"}

    del store["widgets", key]
    assert store["widgets"] == []
