"""Optional OCR plugin backed by the host's Tesseract CLI.

This stays outside core because OCR requires an external host dependency and
can expose on-screen text content. Use it only with authorized devices and test
environments where collecting screen text is appropriate.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from android_harness import helpers
from android_harness.plugins import registry


DEFAULT_TESSERACT = "tesseract"
DEFAULT_LANG = "eng"


def ocr_status(*, tesseract_path: str = DEFAULT_TESSERACT) -> dict[str, object]:
    """Return whether the configured Tesseract executable is available."""

    resolved = shutil.which(tesseract_path)
    return {
        "available": resolved is not None,
        "tesseract": resolved or tesseract_path,
        "default_lang": DEFAULT_LANG,
    }


def ocr_text(
    image_path: str | Path | None = None,
    *,
    lang: str = DEFAULT_LANG,
    timeout: float | None = 30,
    tesseract_path: str = DEFAULT_TESSERACT,
) -> str:
    """Run OCR on a local image path or on a fresh device screenshot."""

    executable = _require_tesseract(tesseract_path)
    image = Path(image_path) if image_path is not None else Path(helpers.screenshot())
    result = subprocess.run(
        [executable, str(image), "stdout", "-l", lang],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() or "no stderr"
        raise RuntimeError(f"tesseract failed ({result.returncode}): {stderr}")
    return result.stdout.strip()


def ocr_lines(
    image_path: str | Path | None = None,
    *,
    lang: str = DEFAULT_LANG,
    timeout: float | None = 30,
    tesseract_path: str = DEFAULT_TESSERACT,
) -> list[str]:
    """Return non-empty OCR lines from a local image or fresh screenshot."""

    text = ocr_text(image_path, lang=lang, timeout=timeout, tesseract_path=tesseract_path)
    return [line.strip() for line in text.splitlines() if line.strip()]


def _require_tesseract(tesseract_path: str) -> str:
    executable = shutil.which(tesseract_path)
    if executable is None:
        raise RuntimeError(
            f"tesseract not found on PATH: {tesseract_path}. "
            "Install Tesseract or pass tesseract_path to the OCR plugin."
        )
    return executable


registry.register_detector("ocr_text", ocr_text)
registry.register_detector("ocr_lines", ocr_lines)
registry.register_environment("ocr_status", ocr_status)
