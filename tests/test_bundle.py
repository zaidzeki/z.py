"""Tests for ``z.bundle``."""

from pathlib import Path

import pytest

from z.bundle import bundle, unbundle


def test_bundle_unbundle_multiple_files(tmp_path: Path) -> None:
    alpha = tmp_path / "alpha.txt"
    beta = tmp_path / "beta.bin"
    alpha.write_text("hello", encoding="utf-8")
    beta.write_bytes(b"\x00\x01\x02")

    archive = tmp_path / "out" / "archive.zb"
    bundle([alpha, beta], archive)

    output = tmp_path / "extracted"
    paths = unbundle(archive, output)

    assert (output / "alpha.txt").read_text(encoding="utf-8") == "hello"
    assert (output / "beta.bin").read_bytes() == b"\x00\x01\x02"
    assert sorted(path.relative_to(output).as_posix() for path in paths) == [
        "alpha.txt",
        "beta.bin",
    ]


def test_bundle_directory_requires_recursive(tmp_path: Path) -> None:
    folder = tmp_path / "src"
    folder.mkdir()
    (folder / "note.txt").write_text("data", encoding="utf-8")

    with pytest.raises(IsADirectoryError):
        bundle(folder, tmp_path / "archive.zb", recursively=False)


def test_bundle_recursive_preserves_tree(tmp_path: Path) -> None:
    root = tmp_path / "assets"
    nested = root / "css"
    nested.mkdir(parents=True)
    (nested / "site.css").write_text("body{}", encoding="utf-8")

    archive = tmp_path / "archive.zb"
    bundle(root, archive, recursively=True)

    extracted = tmp_path / "extract"
    unbundle(archive, extracted)

    restored = extracted / "assets" / "css" / "site.css"
    assert restored.read_text(encoding="utf-8") == "body{}"
