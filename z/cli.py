"""Command-line interface for ``z`` utilities."""

from __future__ import annotations

import argparse
from pathlib import Path


_FORMAT_ALIASES = {
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "png": "PNG",
    "webp": "WEBP",
    "gif": "GIF",
    "bmp": "BMP",
    "tiff": "TIFF",
}


def convert_image(
    input_path: str | Path,
    output_path: str | Path,
    fmt: str,
    *,
    quality: int | None = None,
    optimize: bool = False,
) -> Path:
    """Convert an image to a target format using Pillow.

    Args:
        input_path: Source image path.
        output_path: Output image path.
        fmt: Requested output format (e.g., webp, jpg, png, gif).
        quality: Optional output quality in the range 1..100.
        optimize: Whether Pillow should attempt optimization.

    Returns:
        The resolved output path.
    """
    normalized_fmt = fmt.strip().lower()
    if normalized_fmt not in _FORMAT_ALIASES:
        supported = ", ".join(sorted(_FORMAT_ALIASES))
        raise ValueError(f"Unsupported format '{fmt}'. Supported formats: {supported}")

    if quality is not None and not 1 <= quality <= 100:
        raise ValueError("quality must be between 1 and 100")

    input_file = Path(input_path)
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    save_kwargs: dict[str, int | bool | str] = {
        "format": _FORMAT_ALIASES[normalized_fmt],
        "optimize": optimize,
    }
    if quality is not None:
        save_kwargs["quality"] = quality

    try:
        from PIL import Image
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Pillow is required for `zi image`. Install dependency: Pillow>=10.0.0"
        ) from exc

    with Image.open(input_file) as img:
        if _FORMAT_ALIASES[normalized_fmt] == "JPEG" and img.mode in {"RGBA", "LA", "P"}:
            img = img.convert("RGB")
        img.save(output_file, **save_kwargs)

    return output_file


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level CLI parser."""
    parser = argparse.ArgumentParser(prog="zi", description="z image and utility commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    image_parser = subparsers.add_parser("image", help="convert and optimize images")
    image_parser.add_argument("--input", "-i", required=True, help="input image filepath")
    image_parser.add_argument("--output", "-o", required=True, help="output image filepath")
    image_parser.add_argument(
        "--format",
        "-f",
        required=True,
        help="target format (webp, jpg, png, gif, ...)",
    )
    image_parser.add_argument(
        "--quality",
        type=int,
        help="quality level from 1 to 100 (format-dependent)",
    )
    image_parser.add_argument(
        "--optimize",
        action="store_true",
        help="enable format optimizer when supported",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the ``zi`` CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "image":
        output = convert_image(
            args.input,
            args.output,
            args.format,
            quality=args.quality,
            optimize=args.optimize,
        )
        print(f"Saved converted image: {output}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
