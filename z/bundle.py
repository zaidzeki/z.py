"""Binary bundle utilities with format v1 supporting compression, splitting, and path preservation."""

from __future__ import annotations

import gzip
import lzma
from pathlib import Path
from typing import Iterable


def compress_data(data: bytes, method: str) -> bytes:
    """Compress data using the specified method.

    Parameters
    ----------
    data : bytes
        The uncompressed data bytes.
    method : str
        The compression method: "gzip", "xz", "br", or "none".

    Returns
    -------
    bytes
        The compressed data bytes.
    """
    if method == "gzip":
        return gzip.compress(data)
    elif method == "xz":
        return lzma.compress(data)
    elif method == "br":
        try:
            import brotli
            return brotli.compress(data)
        except ImportError as exc:
            raise ImportError(
                "The 'brotli' package is required for 'br' compression. "
                "Please install it or choose another compression method."
            ) from exc
    elif method == "none":
        return data
    else:
        raise ValueError(f"Unknown compression method: {method}")


def decompress_data(data: bytes, method: str) -> bytes:
    """Decompress data using the specified method.

    Parameters
    ----------
    data : bytes
        The compressed data bytes.
    method : str
        The compression method: "gzip", "xz", "br", or "none".

    Returns
    -------
    bytes
        The decompressed data bytes.
    """
    if method == "gzip":
        return gzip.decompress(data)
    elif method == "xz":
        return lzma.decompress(data)
    elif method == "br":
        try:
            import brotli
            return brotli.decompress(data)
        except ImportError as exc:
            raise ImportError(
                "The 'brotli' package is required for 'br' compression. "
                "Please install it or choose another compression method."
            ) from exc
    elif method == "none":
        return data
    else:
        raise ValueError(f"Unknown compression method: {method}")


def parse_size(size_val: int | str | None) -> int | None:
    """Parse a size value (integer or string with units like K, M, G).

    Parameters
    ----------
    size_val : int | str | None
        The size value to parse.

    Returns
    -------
    int | None
        The size in bytes, or None if input was None.
    """
    if size_val is None:
        return None
    if isinstance(size_val, int):
        return size_val

    size_str = str(size_val).strip().upper()
    if not size_str:
        return None

    multipliers = {
        "K": 1024,
        "M": 1024 * 1024,
        "G": 1024 * 1024 * 1024,
        "KB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
    }

    for unit, mult in multipliers.items():
        if size_str.endswith(unit):
            num_part = size_str[:-len(unit)].strip()
            try:
                return int(float(num_part) * mult)
            except ValueError:
                pass

    try:
        return int(float(size_str))
    except ValueError as exc:
        raise ValueError(f"Invalid size string: {size_str}") from exc


def _normalize_inputs(filepaths: str | Path | Iterable[str | Path]) -> list[Path]:
    """Normalize filepaths argument into list of Path objects."""
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
    """Gather all matching files and their target relative paths."""
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


def _write_bundle_file(path: Path, entries: list[dict], compression_method: str) -> None:
    """Write bundle entries to a single file with magic/version header."""
    compression_codes = {"none": 0, "gzip": 1, "xz": 2, "br": 3}
    comp_code = compression_codes.get(compression_method, 0)

    header = b"ZBDL" + bytes([1, comp_code, 0, 0])

    with path.open("wb") as stream:
        stream.write(header)
        for entry in entries:
            path_bytes = entry["path_bytes"]
            flags = entry["flags"]
            part_index = entry["part_index"]
            data = entry["data"]

            # 1. path_len (2 bytes)
            stream.write(len(path_bytes).to_bytes(2, byteorder="big", signed=False))
            # 2. path bytes
            stream.write(path_bytes)
            # 3. flags (1 byte)
            stream.write(bytes([flags]))
            # 4. part_index (4 bytes) if split flag (bit 0) is set
            if flags & 0x01:
                if part_index is None:
                    part_index = 0
                stream.write(part_index.to_bytes(4, byteorder="big", signed=False))
            # 5. data_len (4 bytes)
            stream.write(len(data).to_bytes(4, byteorder="big", signed=False))
            # 6. data bytes
            stream.write(data)


def _read_bundle_file(path: Path) -> tuple[str, list[dict]]:
    """Read a bundle file, validating its magic/version, and parse its entries."""
    data = path.read_bytes()
    if len(data) < 8:
        raise ValueError("Corrupt bundle: too short to contain a header")

    magic = data[0:4]
    if magic != b"ZBDL":
        raise ValueError(f"Invalid bundle magic: {magic!r}")

    version = data[4]
    if version != 1:
        raise ValueError(f"Unsupported bundle version: {version}")

    comp_code = data[5]
    compression_methods = {0: "none", 1: "gzip", 2: "xz", 3: "br"}
    if comp_code not in compression_methods:
        raise ValueError(f"Unknown compression code: {comp_code}")
    compression_method = compression_methods[comp_code]

    cursor = 8
    entries = []

    while cursor < len(data):
        if cursor + 2 > len(data):
            raise ValueError("Corrupt bundle: missing path length")
        path_len = int.from_bytes(data[cursor : cursor + 2], byteorder="big", signed=False)
        cursor += 2

        if cursor + path_len > len(data):
            raise ValueError("Corrupt bundle: incomplete path payload")
        rel_path = data[cursor : cursor + path_len].decode("utf-8")
        cursor += path_len

        if cursor + 1 > len(data):
            raise ValueError("Corrupt bundle: missing flags")
        flags = data[cursor]
        cursor += 1

        part_index = None
        if flags & 0x01:
            if cursor + 4 > len(data):
                raise ValueError("Corrupt bundle: missing part index")
            part_index = int.from_bytes(data[cursor : cursor + 4], byteorder="big", signed=False)
            cursor += 4

        if cursor + 4 > len(data):
            raise ValueError("Corrupt bundle: missing data length")
        data_len = int.from_bytes(data[cursor : cursor + 4], byteorder="big", signed=False)
        cursor += 4

        if cursor + data_len > len(data):
            raise ValueError("Corrupt bundle: incomplete file payload")
        payload = data[cursor : cursor + data_len]
        cursor += data_len

        entries.append({
            "path": rel_path,
            "flags": flags,
            "part_index": part_index,
            "data": payload
        })

    return compression_method, entries


def _discover_parts(input_path: Path) -> list[Path]:
    """Find all sequential part files belonging to a split bundle."""
    parts = [input_path]
    base_str = str(input_path)

    # Sequence type 1: archive.zb, archive.zb.1, archive.zb.2...
    idx = 1
    while True:
        next_part = Path(f"{base_str}.{idx}")
        if next_part.exists():
            parts.append(next_part)
            idx += 1
        else:
            break

    # Sequence type 2: archive.part1.zb, archive.part2.zb...
    if ".part1." in input_path.name:
        idx = 2
        while True:
            part_name = input_path.name.replace(".part1.", f".part{idx}.")
            next_part = input_path.with_name(part_name)
            if next_part.exists():
                parts.append(next_part)
                idx += 1
            else:
                break

    return parts


def bundle(
    filepaths: str | Path | Iterable[str | Path],
    output_path: str | Path,
    recursively: bool = False,
    max_size: int | str | None = None,
    compression: str = "none",
    split: bool = True,
) -> list[Path]:
    """Bundle files into one or more v1 binary bundle files.

    Parameters
    ----------
    filepaths : str | Path | Iterable[str | Path]
        The file or directory paths to include.
    output_path : str | Path
        The destination bundle path.
    recursively : bool, optional
        Whether to recursively traverse directories, by default False.
    max_size : int | str | None, optional
        The maximum file size limit in bytes or string (e.g., '10M'), by default None.
    compression : str, optional
        The compression method to use ("gzip", "xz", "br", "none"), by default "none".
    split : bool, optional
        Whether to split file payloads across bundles if size limits are reached, by default True.

    Returns
    -------
    list[Path]
        The list of generated bundle file paths.
    """
    normalized_compression = compression.strip().lower()
    if normalized_compression not in {"none", "gzip", "xz", "br"}:
        raise ValueError(f"Unsupported compression method: {compression}")

    limit_bytes = parse_size(max_size) if isinstance(max_size, str) else max_size
    if limit_bytes is not None and limit_bytes <= 8:
        raise ValueError("max_size must be greater than bundle header size (8 bytes)")

    collected = _collect_files(filepaths, recursively=recursively)

    queue = []
    for source_path, relative_path in collected:
        raw_data = source_path.read_bytes()
        compressed_data = compress_data(raw_data, normalized_compression)
        queue.append({
            "path": relative_path,
            "data": compressed_data,
            "part_index": 0,
            "is_split_mode": False
        })

    bundles: list[list[dict]] = []
    current_bundle: list[dict] = []
    current_bundle_size = 8

    while queue:
        item = queue[0]
        path_bytes = str(item["path"].as_posix()).encode("utf-8")
        data = item["data"]
        part_index = item["part_index"]
        is_split_mode = item["is_split_mode"] or (part_index > 0)

        needed_full = (7 if not is_split_mode else 11) + len(path_bytes) + len(data)
        remaining_space = limit_bytes - current_bundle_size if limit_bytes is not None else float("inf")

        if needed_full <= remaining_space:
            entry = {
                "path": item["path"],
                "path_bytes": path_bytes,
                "data": data,
                "flags": 0x03 if is_split_mode else 0x00,
                "part_index": part_index if is_split_mode else None
            }
            current_bundle.append(entry)
            current_bundle_size += needed_full
            queue.pop(0)
            continue

        if split:
            split_entry_header_size = 11 + len(path_bytes)
            if remaining_space < split_entry_header_size + 1:
                if len(current_bundle) > 0:
                    bundles.append(current_bundle)
                    current_bundle = []
                    current_bundle_size = 8
                    continue
                fit_data_len = max(1, remaining_space - split_entry_header_size)
            else:
                fit_data_len = remaining_space - split_entry_header_size

            chunk_data = data[:fit_data_len]
            remaining_data = data[fit_data_len:]

            entry = {
                "path": item["path"],
                "path_bytes": path_bytes,
                "data": chunk_data,
                "flags": 0x01,
                "part_index": part_index
            }
            current_bundle.append(entry)
            current_bundle_size += split_entry_header_size + len(chunk_data)

            item["data"] = remaining_data
            item["part_index"] = part_index + 1
            item["is_split_mode"] = True

            bundles.append(current_bundle)
            current_bundle = []
            current_bundle_size = 8
            continue

        else:
            found_idx = -1
            for i, search_item in enumerate(queue):
                s_path_bytes = str(search_item["path"].as_posix()).encode("utf-8")
                s_needed = 7 + len(s_path_bytes) + len(search_item["data"])
                if s_needed <= remaining_space:
                    found_idx = i
                    break

            if found_idx != -1:
                fit_item = queue.pop(found_idx)
                f_path_bytes = str(fit_item["path"].as_posix()).encode("utf-8")
                entry = {
                    "path": fit_item["path"],
                    "path_bytes": f_path_bytes,
                    "data": fit_item["data"],
                    "flags": 0x00,
                    "part_index": None
                }
                current_bundle.append(entry)
                current_bundle_size += 7 + len(f_path_bytes) + len(fit_item["data"])
                continue
            else:
                if len(current_bundle) == 0:
                    first_item = queue.pop(0)
                    f_path_bytes = str(first_item["path"].as_posix()).encode("utf-8")
                    entry = {
                        "path": first_item["path"],
                        "path_bytes": f_path_bytes,
                        "data": first_item["data"],
                        "flags": 0x00,
                        "part_index": None
                    }
                    current_bundle.append(entry)
                    current_bundle_size += 7 + len(f_path_bytes) + len(first_item["data"])
                    bundles.append(current_bundle)
                    current_bundle = []
                    current_bundle_size = 8
                else:
                    bundles.append(current_bundle)
                    current_bundle = []
                    current_bundle_size = 8
                continue

    if len(current_bundle) > 0:
        bundles.append(current_bundle)

    output_files = []
    base_path = Path(output_path)
    base_path.parent.mkdir(parents=True, exist_ok=True)

    for idx, entries in enumerate(bundles):
        if len(bundles) == 1:
            part_path = base_path
        else:
            if idx == 0:
                part_path = base_path
            else:
                part_path = base_path.with_name(f"{base_path.name}.{idx}")

        _write_bundle_file(part_path, entries, normalized_compression)
        output_files.append(part_path)

    return output_files


def unbundle(input_path: str | Path, output_dir: str | Path) -> list[Path]:
    """Extract a bundle into an output directory, automatically locating and joining split parts.

    Parameters
    ----------
    input_path : str | Path
        The path to the main bundle file (or the first part).
    output_dir : str | Path
        The directory where files will be extracted.

    Returns
    -------
    list[Path]
        The sorted list of extracted file paths.
    """
    source = Path(input_path)
    target_root = Path(output_dir)
    target_root.mkdir(parents=True, exist_ok=True)

    part_files = _discover_parts(source)

    file_parts: dict[str, list[tuple[int | None, bytes, str]]] = {}
    non_split_files: dict[str, tuple[bytes, str]] = {}

    for part_file in part_files:
        comp_method, entries = _read_bundle_file(part_file)
        for entry in entries:
            path = entry["path"]
            flags = entry["flags"]
            part_index = entry["part_index"]
            data = entry["data"]

            if flags & 0x01:
                if path not in file_parts:
                    file_parts[path] = []
                file_parts[path].append((part_index, data, comp_method))
            else:
                non_split_files[path] = (data, comp_method)

    extracted: list[Path] = []

    for path_str, (data, comp_method) in non_split_files.items():
        destination = target_root / Path(path_str)
        destination.parent.mkdir(parents=True, exist_ok=True)
        decompressed_data = decompress_data(data, comp_method)
        destination.write_bytes(decompressed_data)
        extracted.append(destination)

    for path_str, parts in file_parts.items():
        parts.sort(key=lambda x: x[0] if x[0] is not None else 0)
        concatenated_data = b"".join(p[1] for p in parts)
        comp_method = parts[0][2]
        decompressed_data = decompress_data(concatenated_data, comp_method)

        destination = target_root / Path(path_str)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(decompressed_data)
        extracted.append(destination)

    return sorted(extracted)