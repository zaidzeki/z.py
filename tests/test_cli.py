"""Tests for ``zi`` CLI image conversion."""

from __future__ import annotations

from pathlib import Path

import pytest
from z.cli import main

pytest.importorskip("PIL")


def _write_png(path: Path) -> None:
    from PIL import Image

    with Image.new("RGB", (16, 16), color=(255, 0, 0)) as img:
        img.save(path, format="PNG")


def test_zi_image_converts_to_webp(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src = tmp_path / "input.png"
    dst = tmp_path / "output.webp"
    _write_png(src)

    exit_code = main(
        [
            "image",
            "--input",
            str(src),
            "--output",
            str(dst),
            "--format",
            "webp",
            "--quality",
            "80",
            "--optimize",
        ]
    )

    out = capsys.readouterr().out
    assert exit_code == 0
    assert "Saved converted image" in out
    assert dst.exists()


def test_zi_image_rejects_unsupported_format(tmp_path: Path) -> None:
    src = tmp_path / "input.png"
    dst = tmp_path / "output.invalid"
    _write_png(src)

    with pytest.raises(ValueError, match="Unsupported format"):
        main(
            [
                "image",
                "--input",
                str(src),
                "--output",
                str(dst),
                "--format",
                "invalid",
            ]
        )
