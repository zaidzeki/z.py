"""Binary bundle utilities with filepath preservation.

Bundle format for each entry:
    [16-bit big-endian path length][path bytes][32-bit big-endian data length][data bytes]
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


def _normalize_inputs(filepaths: str | Path | Iterable[str | Path]) -> list[Path]:
    if isinstance(filepaths, (str, Path)):
        items = [filepaths]
    else:
        items = list(filepaths)

    if not items:
        raise ValueError("filepaths must contain at least one path")

    return [Path(item) for item in items]


def _collect_files(
    filepaths: str | Path | Iterable[str | Path], recursively: bool
) -> list[tuple[Path, Path]]:
    roots = _normalize_inputs(filepaths)
    collected: list[tuple[Path, Path]] = []

    for root in roots:
        if not root.exists():
            raise FileNotFoundError(f"Path does not exist: {root}")

        if root.is_file():
            collected.append((root, Path(root.name)))
            continue

        if not recursively:
            raise IsADirectoryError(f"Directory provided but recursively=False: {root}")

        for child in sorted(path for path in root.rglob("*") if path.is_file()):
            relative = root.name / child.relative_to(root)
            collected.append((child, relative))

    return collected


def bundle(
    filepaths: str | Path | Iterable[str | Path],
    output_path: str | Path,
    recursively: bool = False,
) -> Path:
    """Bundle files into a single binary file.

    Args:
        filepaths: Single path or iterable of paths to include.
        output_path: Bundle destination path.
        recursively: Recursively include files for directory inputs.

    Returns:
        The output bundle path.
    """
    entries = _collect_files(filepaths, recursively=recursively)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("wb") as stream:
        for source, relative_path in entries:
            path_bytes = str(relative_path.as_posix()).encode("utf-8")
            if len(path_bytes) > 0xFFFF:
                raise ValueError(f"Path too long for 16-bit length: {relative_path}")

            data = source.read_bytes()
            if len(data) > 0xFFFFFFFF:
                raise ValueError(f"File too large for 32-bit length: {source}")

            stream.write(len(path_bytes).to_bytes(2, byteorder="big", signed=False))
            stream.write(path_bytes)
            stream.write(len(data).to_bytes(4, byteorder="big", signed=False))
            stream.write(data)

    return output


def unbundle(input_path: str | Path, output_dir: str | Path) -> list[Path]:
    """Extract a bundle into an output directory.

    Args:
        input_path: Source bundle file path.
        output_dir: Directory where extracted files are written.

    Returns:
        List of extracted file paths.
    """
    source = Path(input_path)
    target_root = Path(output_dir)
    target_root.mkdir(parents=True, exist_ok=True)

    data = source.read_bytes()
    cursor = 0
    extracted: list[Path] = []

    while cursor < len(data):
        if cursor + 2 > len(data):
            raise ValueError("Corrupt bundle: missing path length")
        path_len = int.from_bytes(data[cursor : cursor + 2], byteorder="big", signed=False)
        cursor += 2

        if cursor + path_len > len(data):
            raise ValueError("Corrupt bundle: incomplete path payload")
        rel_path = data[cursor : cursor + path_len].decode("utf-8")
        cursor += path_len

        if cursor + 4 > len(data):
            raise ValueError("Corrupt bundle: missing data length")
        data_len = int.from_bytes(data[cursor : cursor + 4], byteorder="big", signed=False)
        cursor += 4

        if cursor + data_len > len(data):
            raise ValueError("Corrupt bundle: incomplete file payload")
        payload = data[cursor : cursor + data_len]
        cursor += data_len

        destination = target_root / Path(rel_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(payload)
        extracted.append(destination)

    return extracted
