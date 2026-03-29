"""CLI entry point for the ``z`` package."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .image import process_image


def main(argv: Sequence[str] | None = None) -> int:
    """Run the ``zi`` CLI.

    Args:
        argv: Command-line arguments. Defaults to ``sys.argv[1:]``.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = argparse.ArgumentParser(prog="zi", description="z CLI tool.")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run.")

    # Image subcommand
    image_parser = subparsers.add_parser("image", help="Process an image.")
    image_parser.add_argument("--input", "-i", required=True, help="Input image path.")
    image_parser.add_argument("--output", "-o", required=True, help="Output image path.")
    image_parser.add_argument("--format", "-f", help="Target image format (e.g., webp, jpg, png).")
    image_parser.add_argument("--quality", type=int, help="Image quality (1-100).")
    image_parser.add_argument(
        "--optimize", action="store_true", help="Optimize the output image."
    )

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.command == "image":
        try:
            process_image(
                input_path=args.input,
                output_path=args.output,
                img_format=args.format,
                quality=args.quality,
                optimize=args.optimize,
            )
            print(f"Image processed and saved to {args.output}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    elif not args.command:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
