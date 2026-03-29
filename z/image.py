"""Image processing utilities for the ``z`` package."""

from __future__ import annotations

from pathlib import Path
from PIL import Image


def process_image(
    input_path: str | Path,
    output_path: str | Path,
    img_format: str | None = None,
    quality: int | None = None,
    optimize: bool = False,
) -> Path:
    """Process an image: change format, optimize and set quality.

    Args:
        input_path: Path to the input image.
        output_path: Path where the processed image will be saved.
        img_format: Target image format (e.g., 'webp', 'jpeg', 'png').
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
        save_kwargs = {}
        if img_format:
            save_kwargs["format"] = img_format
        if quality is not None:
            save_kwargs["quality"] = quality
        if optimize:
            save_kwargs["optimize"] = True

        output_p.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_p, **save_kwargs)

    return output_p
