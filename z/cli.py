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

    enc_parser = subparsers.add_parser(
        "encrypt-fast", help="encrypt a file using ultra-fast AES-256-CTR"
    )
    enc_parser.add_argument("--input", "-i", required=True, help="plaintext input file")
    enc_parser.add_argument("--output", "-o", required=True, help="ciphertext output file")
    enc_parser.add_argument("--password", "-p", help="password (omit to prompt)")

    dec_parser = subparsers.add_parser(
        "decrypt-fast", help="decrypt a file using ultra-fast AES-256-CTR"
    )
    dec_parser.add_argument("--input", "-i", required=True, help="ciphertext input file")
    dec_parser.add_argument("--output", "-o", required=True, help="plaintext output file")
    dec_parser.add_argument("--password", "-p", help="password (omit to prompt)")

    bundles_parser = subparsers.add_parser(
        "bundles", help="bundle files into compression-enabled v1 bundles"
    )
    bundles_parser.add_argument("bundle_name", help="name of the bundle output file")
    bundles_parser.add_argument("paths", nargs="+", help="files and/or folders to bundle")
    bundles_parser.add_argument(
        "--max-size", help="maximum size limit for each bundle part (e.g. 10M, 500K)"
    )
    bundles_parser.add_argument(
        "--compression",
        choices=["gzip", "xz", "br", "none"],
        default="none",
        help="compression method to use (default: none)",
    )
    bundles_parser.add_argument(
        "--split",
        choices=["true", "false"],
        default="true",
        help="whether to split files across bundles (default: true)",
    )

    unbundle_parser = subparsers.add_parser(
        "unbundle", help="extract a bundle into an output directory"
    )
    unbundle_parser.add_argument("bundle_name", help="name of the bundle file to extract")
    unbundle_parser.add_argument(
        "--output", "-o", required=True, help="output directory for extraction"
    )

    tree_parser = subparsers.add_parser("tree", help="display a Unicode directory tree")
    tree_parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="root directory to visualise (default: current directory)",
    )
    tree_parser.add_argument(
        "--depth",
        "-d",
        type=int,
        default=None,
        metavar="N",
        help="maximum depth (omit for unlimited)",
    )
    tree_parser.add_argument(
        "--hidden",
        action="store_true",
        help="include hidden files and directories",
    )
    tree_parser.add_argument(
        "--ignore",
        nargs="*",
        metavar="NAME",
        help="additional entry names to ignore (space-separated)",
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

    if args.command in ("encrypt-fast", "decrypt-fast"):
        import getpass
        import logging
        import os
        from .aes_fast import encrypt_stream, decrypt_stream

        logger = logging.getLogger("aes_fast")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        try:
            input_path = os.path.abspath(args.input)
            output_path = os.path.abspath(args.output)
            if input_path == output_path:
                logger.error("Input and output files must be different to prevent data truncation.")
                return 1
        except Exception as exc:
            logger.error(f"Failed to resolve file paths: {exc}")
            return 1

        password = args.password
        if not password:
            password = getpass.getpass("Password: ")
            if not password:
                logger.error("Empty password is not allowed.")
                return 1
            if args.command == "encrypt-fast":
                confirm = getpass.getpass("Confirm password: ")
                if password != confirm:
                    logger.error("Passwords do not match.")
                    return 1

        try:
            if args.command == "encrypt-fast":
                with open(args.input, "rb") as fin, open(args.output, "wb") as fout:
                    encrypt_stream(fin, fout, password)
            else:
                with open(args.input, "rb") as fin, open(args.output, "wb") as fout:
                    decrypt_stream(fin, fout, password)
        except OSError as exc:
            logger.error(f"I/O error: {exc}")
            return 2
        except ValueError as exc:
            logger.error(f"Decryption / Header integrity error: {exc}")
            return 3
        return 0

    if args.command == "bundles":
        import logging

        logger = logging.getLogger("bundle")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        try:
            from .bundle import bundle

            split_bool = args.split.lower() == "true"

            output_paths = bundle(
                filepaths=args.paths,
                output_path=args.bundle_name,
                recursively=True,
                max_size=args.max_size,
                compression=args.compression,
                split=split_bool,
            )
            print("Bundling successful. Created files:")
            for p in output_paths:
                print(f" - {p}")
            return 0
        except Exception as exc:
            logger.error(f"Bundling failed: {exc}")
            return 1

    if args.command == "unbundle":
        import logging

        logger = logging.getLogger("unbundle")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        try:
            from .bundle import unbundle

            extracted_paths = unbundle(args.bundle_name, args.output)
            print(
                f"Extraction successful. Extracted {len(extracted_paths)} files to '{args.output}'."
            )
            return 0
        except Exception as exc:
            logger.error(f"Extraction failed: {exc}")
            return 1

    if args.command == "tree":
        from .filetree import FileStructureGenerator

        ignore_list = list(FileStructureGenerator._DEFAULT_IGNORE)
        if args.ignore:
            ignore_list.extend(args.ignore)

        from .filetree import generate_tree

        print(
            generate_tree(
                args.path, max_depth=args.depth, include_hidden=args.hidden, ignore_list=ignore_list
            )
        )
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
