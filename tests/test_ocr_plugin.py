import subprocess

import pytest

from android_harness import helpers
from android_harness.plugins import registry
from plugins import ocr_plugin


def test_ocr_status_reports_available_tesseract(monkeypatch):
    monkeypatch.setattr(ocr_plugin.shutil, "which", lambda path: "/usr/bin/tesseract")

    assert ocr_plugin.ocr_status() == {
        "available": True,
        "tesseract": "/usr/bin/tesseract",
        "default_lang": "eng",
    }


def test_ocr_text_runs_tesseract_for_explicit_image(monkeypatch, tmp_path):
    image = tmp_path / "screen.png"
    image.write_bytes(b"png")
    captured = {}

    monkeypatch.setattr(ocr_plugin.shutil, "which", lambda path: "/usr/bin/tesseract")

    def fake_run(cmd, capture_output=True, text=True, timeout=30, check=False):
        captured["cmd"] = cmd
        captured["timeout"] = timeout
        captured["check"] = check
        return subprocess.CompletedProcess(cmd, 0, stdout=" Hello\nWorld \n", stderr="")

    monkeypatch.setattr(ocr_plugin.subprocess, "run", fake_run)

    assert ocr_plugin.ocr_text(image, lang="eng+chi_sim", timeout=7) == "Hello\nWorld"
    assert captured == {
        "cmd": ["/usr/bin/tesseract", str(image), "stdout", "-l", "eng+chi_sim"],
        "timeout": 7,
        "check": False,
    }


def test_ocr_lines_captures_screenshot_when_path_is_omitted(monkeypatch, tmp_path):
    image = tmp_path / "screen.png"
    image.write_bytes(b"png")

    monkeypatch.setattr(helpers, "screenshot", lambda: str(image))
    monkeypatch.setattr(ocr_plugin.shutil, "which", lambda path: "/usr/bin/tesseract")
    monkeypatch.setattr(
        ocr_plugin.subprocess,
        "run",
        lambda cmd, capture_output=True, text=True, timeout=30, check=False: subprocess.CompletedProcess(
            cmd,
            0,
            stdout="One\n\nTwo\n",
            stderr="",
        ),
    )

    assert ocr_plugin.ocr_lines() == ["One", "Two"]


def test_ocr_text_reports_missing_tesseract(monkeypatch, tmp_path):
    image = tmp_path / "screen.png"
    image.write_bytes(b"png")
    monkeypatch.setattr(ocr_plugin.shutil, "which", lambda path: None)

    with pytest.raises(RuntimeError, match="tesseract not found"):
        ocr_plugin.ocr_text(image)


def test_ocr_text_reports_tesseract_failure(monkeypatch, tmp_path):
    image = tmp_path / "screen.png"
    image.write_bytes(b"png")
    monkeypatch.setattr(ocr_plugin.shutil, "which", lambda path: "/usr/bin/tesseract")
    monkeypatch.setattr(
        ocr_plugin.subprocess,
        "run",
        lambda cmd, capture_output=True, text=True, timeout=30, check=False: subprocess.CompletedProcess(
            cmd,
            1,
            stdout="",
            stderr="bad image",
        ),
    )

    with pytest.raises(RuntimeError, match="bad image"):
        ocr_plugin.ocr_text(image)


def test_ocr_plugin_registers_capabilities():
    capabilities = registry.capabilities()

    assert "ocr_text" in capabilities["detectors"]
    assert "ocr_lines" in capabilities["detectors"]
    assert "ocr_status" in capabilities["environment"]
