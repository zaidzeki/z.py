"""File cleanup and hash matching utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path

CHUNK_SIZE = 64 * 1024  # 64KB


def remove_files_by_hash(
    algo: str, target_hashes: set[str] | list[str], search_path: str | Path = "."
) -> int:
    """Recursively scans a directory and deletes files matching a set of hashes.

    Args:
        algo: Hash algorithm to use (e.g., 'sha256', 'sha1', 'md5').
        target_hashes: A set or list of hex strings to match against.
        search_path: Root directory to begin the search.

    Returns:
        The total number of files deleted.
    """
    deleted_count = 0
    search_root = Path(search_path)
    normalized_hashes = {h.lower() for h in target_hashes}

    print(f"[*] Scanning {search_root.absolute()} for matches...")

    for file_path in search_root.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            hasher = hashlib.new(algo)
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
                    hasher.update(chunk)

            if hasher.hexdigest().lower() in normalized_hashes:
                print(f"[-] Deleting matching file: {file_path}")
                file_path.unlink()
                deleted_count += 1
        except Exception as e:
            print(f"[!] Error processing {file_path}: {e}")

    print(f"[+] Cleanup finished. Total files removed: {deleted_count}")
    return deleted_count
