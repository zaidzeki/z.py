"""Tests for ``z.image``."""

import pytest
from pathlib import Path
from PIL import Image
from z import process_image


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample image for testing."""
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return img_path


def test_process_image_format_conversion(sample_image, tmp_path):
    output_path = tmp_path / "output.webp"
    process_image(sample_image, output_path, format="webp")

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.format == "WEBP"


def test_process_image_quality(sample_image, tmp_path):
    output_path = tmp_path / "output.jpg"
    process_image(sample_image, output_path, format="jpg", quality=50)

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.format == "JPEG"


def test_process_image_optimize(sample_image, tmp_path):
    output_path = tmp_path / "output_opt.png"
    process_image(sample_image, output_path, optimize=True)

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.format == "PNG"


def test_process_image_inferred_format(sample_image, tmp_path):
    output_path = tmp_path / "output.gif"
    process_image(sample_image, output_path)

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.format == "GIF"


def test_process_image_not_found():
    with pytest.raises(FileNotFoundError):
        process_image("non_existent.png", "out.png")
