"""Image processing utilities for the ``z`` package."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image


def process_image(
    input_path: str | Path,
    output_path: str | Path,
    format: str | None = None,
    quality: int | None = None,
    optimize: bool = False,
) -> Path:
    """Process an image with optional format, quality, and optimization settings.

    Args:
        input_path: Path to the source image.
        output_path: Path to the output image.
        format: Target format (e.g., 'webp', 'jpeg', 'png'). If None, inferred from output_path.
        quality: Image quality (1-100).
        optimize: Whether to optimize the output image.

    Returns:
        The output image path.
    """
    input_p = Path(input_path)
    output_p = Path(output_path)

    if not input_p.exists():
        raise FileNotFoundError(f"Input image not found: {input_p}")

    with Image.open(input_p) as img:
        save_kwargs: dict[str, Any] = {}
        if quality is not None:
            save_kwargs["quality"] = quality
        if optimize:
            save_kwargs["optimize"] = True

        # Normalize format
        if format:
            fmt = format.upper()
            if fmt == "JPG":
                fmt = "JPEG"
            save_kwargs["format"] = fmt

        output_p.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_p, **save_kwargs)

    return output_p
