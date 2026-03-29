"""CLI entry point for ``zi``."""

import argparse
import sys
from typing import Sequence

from z.image import process_image


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(prog="zi", description="z image processing tool")
    subparsers = parser.add_subparsers(dest="command")

    # image subcommand
    image_parser = subparsers.add_parser("image", help="Process an image")
    image_parser.add_argument("--input", "-i", required=True, help="Input image filepath")
    image_parser.add_argument("--output", "-o", required=True, help="Output image filepath")
    image_parser.add_argument("--format", "-f", help="Target format (webp, jpeg, png, etc.)")
    image_parser.add_argument("--quality", type=int, help="Output quality (1-100)")
    image_parser.add_argument("--optimize", action="store_true", help="Optimize output image")

    args = parser.parse_args(argv)

    if args.command == "image":
        try:
            process_image(
                input_path=args.input,
                output_path=args.output,
                img_format=args.format,
                quality=args.quality,
                optimize=args.optimize,
            )
            print(f"Image processed and saved to: {args.output}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
