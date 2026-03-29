"""Tests for ``z.cli``."""

from __future__ import annotations

import builtins
import gzip
from pathlib import Path
import sqlite3
import tarfile
import zipfile

import z.cli as cli


def _set_store(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path / "cipher"
    monkeypatch.setattr(cli, "CIPHER_ROOT", root)
    monkeypatch.setattr(cli, "KEYS_DIR", root / "keys")
    monkeypatch.setattr(cli, "DB_PATH", root / "main.db")


def test_recover_gzip(tmp_path: Path) -> None:
    src = tmp_path / "hello.txt.gz"
    src.write_bytes(gzip.compress(b"hello"))

    out = cli.recover(src)

    assert out.read_bytes() == b"hello"
    assert out.name == "hello.txt"


def test_recover_zip(tmp_path: Path) -> None:
    archive = tmp_path / "files.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("a.txt", b"A")

    out_dir = cli.recover(archive)

    assert (out_dir / "a.txt").read_bytes() == b"A"


def test_recover_tar(tmp_path: Path) -> None:
    source = tmp_path / "b.txt"
    source.write_bytes(b"B")
    archive = tmp_path / "files.tar"
    with tarfile.open(archive, "w") as tf:
        tf.add(source, arcname="b.txt")

    out_dir = cli.recover(archive)

    assert (out_dir / "b.txt").read_bytes() == b"B"


def test_cipher_generate_and_alias_resolution(monkeypatch, tmp_path: Path) -> None:
    _set_store(monkeypatch, tmp_path)

    cli.cipher_generate(name="alpha", aliases="a1,a2", strength="high", password="secret")

    assert cli._resolve_cipher_name("alpha") == "alpha"
    assert cli._resolve_cipher_name("a2") == "alpha"

    with sqlite3.connect(cli.DB_PATH) as conn:
        row = conn.execute(
            "SELECT name, aliases, strength FROM ciphers WHERE name='alpha'"
        ).fetchone()
    assert row == ("alpha", "a1,a2", "high")


def test_main_generate_prompt_flow(monkeypatch, tmp_path: Path) -> None:
    _set_store(monkeypatch, tmp_path)

    answers = iter(["omega", "o1,o2", "medium"])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))
    monkeypatch.setattr(cli.getpass, "getpass", lambda _: "pw")

    code = cli.main(["cipher", "generate"])

    assert code == 0
    assert cli._resolve_cipher_name("o1") == "omega"
