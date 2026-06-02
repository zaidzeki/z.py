"""Tests for ``z.bundle`` format v1, compression, and splitting."""

from pathlib import Path
import pytest
from z.bundle import bundle, unbundle, parse_size
from z.cli import main


def test_compression_roundtrip(tmp_path: Path) -> None:
    """Test that all supported compression types roundtrip successfully."""
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("Hello compression test", encoding="utf-8")
    file_b.write_text("My neat content here", encoding="utf-8")

    for comp in ["none", "gzip", "xz"]:
        archive = tmp_path / f"archive_{comp}.zb"
        bundle([file_a, file_b], archive, compression=comp)

        extracted = tmp_path / f"extract_{comp}"
        unbundle(archive, extracted)

        assert (extracted / "a.txt").read_text(encoding="utf-8") == "Hello compression test"
        assert (extracted / "b.txt").read_text(encoding="utf-8") == "My neat content here"


def test_split_enabled_split_boundaries(tmp_path: Path) -> None:
    """Test splitting file data across multiple sequential bundle parts."""
    file_a = tmp_path / "large_file.txt"
    file_a.write_bytes(b"A" * 1000)

    # Limit of 200 bytes per bundle part causes multiple files to be written
    archive = tmp_path / "split_archive.zb"
    parts = bundle(file_a, archive, max_size=200, split=True)

    assert len(parts) > 1
    for part in parts:
        assert part.exists()

    extracted = tmp_path / "extract_split"
    unbundle(archive, extracted)

    assert (extracted / "large_file.txt").read_bytes() == b"A" * 1000


def test_split_disabled_logic(tmp_path: Path) -> None:
    """Test split=False behavior: skip/push large files or include as is if single."""
    file_large = tmp_path / "large.txt"
    file_small = tmp_path / "small.txt"

    file_large.write_bytes(b"L" * 300)
    file_small.write_bytes(b"S" * 20)

    archive = tmp_path / "archive_disabled.zb"

    # Bundle 1 gets small.txt (which fits). large.txt is skipped.
    # Bundle 2 gets large.txt as the sole file (included as-is).
    parts = bundle([file_large, file_small], archive, max_size=200, split=False)

    assert len(parts) == 2
    extracted = tmp_path / "extract_disabled"
    unbundle(archive, extracted)

    assert (extracted / "large.txt").read_bytes() == b"L" * 300
    assert (extracted / "small.txt").read_bytes() == b"S" * 20


def test_size_parsing() -> None:
    """Test size parsing utility functions."""
    assert parse_size(None) is None
    assert parse_size(123) == 123
    assert parse_size("500") == 500
    assert parse_size("500K") == 500 * 1024
    assert parse_size("10M") == 10 * 1024 * 1024
    assert parse_size("2G") == 2 * 1024 * 1024 * 1024
    with pytest.raises(ValueError):
        parse_size("invalid")


def test_cli_bundles_and_unbundle(tmp_path: Path) -> None:
    """Test bundles and unbundle CLI commands through the main entrypoint."""
    file_a = tmp_path / "hello.txt"
    file_a.write_text("CLI test", encoding="utf-8")

    archive = tmp_path / "cli_archive.zb"

    ret_pack = main([
        "bundles",
        str(archive),
        str(file_a),
        "--max-size", "100K",
        "--compression", "gzip",
        "--split", "true"
    ])
    assert ret_pack == 0
    assert archive.exists()

    extract_dir = tmp_path / "cli_extract"
    ret_unpack = main([
        "unbundle",
        str(archive),
        "--output", str(extract_dir)
    ])
    assert ret_unpack == 0
    assert (extract_dir / "hello.txt").read_text(encoding="utf-8") == "CLI test"