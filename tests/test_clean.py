from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from z.clean import remove_files_by_hash
from z.cli import main


def test_remove_files_by_hash(tmp_path: Path) -> None:
    # Create test files
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"
    file3 = tmp_path / "file3.txt"

    file1.write_bytes(b"hello world")  # sha1: 2aae6c35c94fcfb415dbe95f408b9ce91ee846ed
    file2.write_bytes(b"antigravity")  # sha1: d288b43f9a7d3ef2a59a941ef2c0209f8742b781
    file3.write_bytes(b"different content")

    sha1_1 = hashlib.sha1(b"hello world").hexdigest()
    sha1_2 = hashlib.sha1(b"antigravity").hexdigest()

    # Call with sha1 hashes to remove file1 and file2
    deleted = remove_files_by_hash("sha1", {sha1_1, sha1_2}, tmp_path)
    assert deleted == 2

    assert not file1.exists()
    assert not file2.exists()
    assert file3.exists()


def test_remove_files_by_hash_sha256(tmp_path: Path) -> None:
    file1 = tmp_path / "file1.txt"
    file2 = tmp_path / "file2.txt"

    file1.write_bytes(b"test1")
    file2.write_bytes(b"test2")

    sha256_1 = hashlib.sha256(b"test1").hexdigest()

    deleted = remove_files_by_hash("sha256", {sha256_1}, tmp_path)
    assert deleted == 1
    assert not file1.exists()
    assert file2.exists()


def test_cli_clean_subcommand(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    file1 = tmp_path / "file1.txt"
    file1.write_bytes(b"hello")

    sha256_val = hashlib.sha256(b"hello").hexdigest()

    # Run CLI command 'clean'
    exit_code = main(
        [
            "clean",
            "--algo",
            "sha256",
            "--hashes",
            sha256_val,
            "--path",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    assert not file1.exists()

    out = capsys.readouterr().out
    assert "Cleanup finished" in out
    assert "Total files removed: 1" in out
