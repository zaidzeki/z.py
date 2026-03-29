"""Command-line interface for the ``z`` package."""

from __future__ import annotations

import argparse
import sys

from .image import process_image


def main() -> int:
    """CLI entry point for the ``zi`` tool."""
    parser = argparse.ArgumentParser(prog="zi", description="z command-line interface")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Image subcommand
    image_parser = subparsers.add_parser("image", help="Process an image")
    image_parser.add_argument("--input", "-i", required=True, help="Input image filepath")
    image_parser.add_argument("--output", "-o", required=True, help="Output image filepath")
    image_parser.add_argument("--format", "-f", help="Target format (webp, jpg, png, gif, ...)")
    image_parser.add_argument("--quality", type=int, help="Image quality (1-100)")
    image_parser.add_argument("--optimize", action="store_true", help="Optimize the output image")

    args = parser.parse_args()

    if args.command == "image":
        try:
            process_image(
                input_path=args.input,
                output_path=args.output,
                format=args.format,
                quality=args.quality,
                optimize=args.optimize,
            )
            print(f"Image processed successfully: {args.output}")
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
