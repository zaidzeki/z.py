"""Tests for the ``zi`` CLI."""

from pathlib import Path
from PIL import Image
import pytest
from z.cli import main


@pytest.fixture
def sample_image(tmp_path: Path) -> Path:
    """Create a sample image for testing."""
    img_path = tmp_path / "test.png"
    img = Image.new("RGB", (10, 10), color="blue")
    img.save(img_path)
    return img_path


def test_cli_image_command(sample_image: Path, tmp_path: Path) -> None:
    output_path = tmp_path / "cli_output.jpg"
    exit_code = main(
        ["image", "--input", str(sample_image), "--output", str(output_path), "--format", "JPEG"]
    )

    assert exit_code == 0
    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.format == "JPEG"


def test_cli_image_options(sample_image: Path, tmp_path: Path) -> None:
    output_path = tmp_path / "cli_opt_output.webp"
    exit_code = main(
        [
            "image",
            "-i",
            str(sample_image),
            "-o",
            str(output_path),
            "-f",
            "WEBP",
            "--quality",
            "50",
            "--optimize",
        ]
    )

    assert exit_code == 0
    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.format == "WEBP"


def test_cli_error_handling(tmp_path: Path) -> None:
    exit_code = main(["image", "-i", "non_existent.png", "-o", "out.png"])
    assert exit_code == 1


def test_cli_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "z CLI tool" in captured.out
