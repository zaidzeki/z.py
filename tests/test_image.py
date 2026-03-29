"""Tests for image processing."""

import pytest
from pathlib import Path
from PIL import Image
from z.image import process_image
from z.cli import main


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample image for testing."""
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_path)
    return img_path


def test_process_image_format_change(sample_image, tmp_path):
    """Test changing image format."""
    output_path = tmp_path / "test.webp"
    process_image(sample_image, output_path, img_format="webp")
    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.format == "WEBP"


def test_process_image_quality(sample_image, tmp_path):
    """Test setting image quality."""
    output_path = tmp_path / "test.jpg"
    # JPEG supports quality
    process_image(sample_image, output_path, img_format="jpeg", quality=50)
    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.format == "JPEG"


def test_process_image_optimize(sample_image, tmp_path):
    """Test image optimization."""
    output_path = tmp_path / "test_opt.png"
    process_image(sample_image, output_path, optimize=True)
    assert output_path.exists()


def test_cli_image_command(sample_image, tmp_path, capsys):
    """Test the 'zi image' CLI command."""
    output_path = tmp_path / "cli_test.webp"
    args = ["image", "--input", str(sample_image), "--output", str(output_path), "--format", "webp"]
    exit_code = main(args)
    assert exit_code == 0
    assert output_path.exists()
    captured = capsys.readouterr()
    assert "Image processed and saved to" in captured.out
    with Image.open(output_path) as img:
        assert img.format == "WEBP"


def test_cli_error_handling(tmp_path, capsys):
    """Test CLI error handling for non-existent input."""
    output_path = tmp_path / "error_test.webp"
    args = ["image", "--input", "non_existent.png", "--output", str(output_path)]
    exit_code = main(args)
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error" in captured.err
