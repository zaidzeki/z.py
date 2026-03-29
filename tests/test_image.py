"""Tests for ``z.image``."""

from pathlib import Path
from PIL import Image
import pytest
from z import process_image


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a sample image for testing."""
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return img_path


def test_process_image_format(sample_image: Path, tmp_path: Path) -> None:
    output_path = tmp_path / "output.webp"
    process_image(sample_image, output_path, img_format="WEBP")

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.format == "WEBP"


def test_process_image_quality(sample_image: Path, tmp_path: Path) -> None:
    output_path_low = tmp_path / "output_low.jpg"
    output_path_high = tmp_path / "output_high.jpg"

    process_image(sample_image, output_path_low, img_format="JPEG", quality=10)
    process_image(sample_image, output_path_high, img_format="JPEG", quality=90)

    assert output_path_low.stat().st_size < output_path_high.stat().st_size


def test_process_image_optimize(sample_image: Path, tmp_path: Path) -> None:
    output_path = tmp_path / "output_opt.png"
    process_image(sample_image, output_path, optimize=True)

    assert output_path.exists()


def test_process_image_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        process_image("non_existent.png", "output.png")
