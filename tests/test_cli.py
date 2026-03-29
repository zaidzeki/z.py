"""Tests for the ``zi`` CLI."""

import subprocess
from pathlib import Path
from PIL import Image


def test_zi_image_command(tmp_path):
    """Test the 'zi image' command via subprocess."""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.webp"

    img = Image.new("RGB", (50, 50), color="blue")
    img.save(input_path)

    result = subprocess.run(
        ["zi", "image", "-i", str(input_path), "-o", str(output_path), "-f", "webp"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "Image processed successfully" in result.stdout
    assert output_path.exists()

    with Image.open(output_path) as out_img:
        assert out_img.format == "WEBP"


def test_zi_image_quality_and_optimize(tmp_path):
    """Test 'zi image' with quality and optimize flags."""
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.jpg"

    img = Image.new("RGB", (50, 50), color="green")
    img.save(input_path)

    result = subprocess.run(
        ["zi", "image", "--input", str(input_path), "--output", str(output_path), "--quality", "75", "--optimize"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_path.exists()

    with Image.open(output_path) as out_img:
        assert out_img.format == "JPEG"


def test_zi_help():
    """Test 'zi --help'."""
    result = subprocess.run(["zi", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "z command-line interface" in result.stdout
    assert "image" in result.stdout
