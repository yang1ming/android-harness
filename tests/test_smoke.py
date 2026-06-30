import json
from pathlib import Path

from android_harness import smoke


FIXTURES = Path(__file__).parent / "fixtures"


class FakeReport:
    def __init__(self, payload):
        self.payload = payload

    def to_dict(self):
        return self.payload


def test_run_smoke_returns_passed_structured_report(monkeypatch):
    def fake_doctor(serial=None, *, transport_name=None):
        assert serial == "emulator-5554"
        assert transport_name == "daemon"
        return FakeReport(
            {
                "adb_available": True,
                "devices": [["emulator-5554", "device"]],
                "selected_serial": "emulator-5554",
                "device_ready": True,
                "screenshot_available": True,
                "uiautomator_available": True,
                "error": None,
            }
        )

    monkeypatch.setattr(smoke, "doctor", fake_doctor)
    monkeypatch.setattr(smoke, "daemon_status", lambda: "running: /tmp/android-harness/daemon.sock")

    report = smoke.run_smoke("emulator-5554", transport_name="daemon")

    assert report["schema_version"] == smoke.SMOKE_SCHEMA_VERSION
    assert report["ok"] is True
    assert report["transport"] == "daemon"
    assert report["selected_serial"] == "emulator-5554"
    assert report["daemon"]["running"] is True
    assert [check["name"] for check in report["checks"]] == [
        "adb_available",
        "device_ready",
        "screenshot_available",
        "uiautomator_available",
    ]
    assert all(check["ok"] for check in report["checks"])


def test_smoke_report_matches_public_schema_fixture(monkeypatch):
    def fake_doctor(serial=None, *, transport_name=None):
        return FakeReport(
            {
                "adb_available": True,
                "devices": [["emulator-5554", "device"]],
                "selected_serial": "emulator-5554",
                "device_ready": True,
                "screenshot_available": True,
                "uiautomator_available": True,
                "error": None,
            }
        )

    monkeypatch.setattr(smoke, "doctor", fake_doctor)
    monkeypatch.setattr(smoke, "daemon_status", lambda: "running: /tmp/android-harness/daemon.sock")

    payload = json.loads(json.dumps(smoke.run_smoke("emulator-5554", transport_name="daemon")))
    fixture = json.loads((FIXTURES / "smoke_report_v1.json").read_text())

    assert payload == fixture


def test_redact_smoke_report_removes_device_identifiers():
    report = {
        "schema_version": smoke.SMOKE_SCHEMA_VERSION,
        "ok": False,
        "selected_serial": "emulator-5554",
        "checks": [
            {
                "name": "device_ready",
                "ok": False,
                "detail": "selected device emulator-5554 is offline",
            }
        ],
        "doctor": {
            "selected_serial": "emulator-5554",
            "devices": [["emulator-5554", "offline"], ["192.168.1.20:5555", "device"]],
            "error": "selected device emulator-5554 is not ready",
        },
    }

    redacted = smoke.redact_smoke_report(report)

    encoded = json.dumps(redacted)
    assert "emulator-5554" not in encoded
    assert "192.168.1.20:5555" not in encoded
    assert redacted["device_redacted"] is True
    assert redacted["selected_serial"] == smoke.REDACTED_DEVICE
    assert redacted["doctor"]["devices"] == [
        [smoke.REDACTED_DEVICE, "offline"],
        [smoke.REDACTED_DEVICE, "device"],
    ]
    assert report["selected_serial"] == "emulator-5554"


def test_run_smoke_marks_failed_device_probe(monkeypatch):
    def fake_doctor(serial=None, *, transport_name=None):
        return FakeReport(
            {
                "adb_available": True,
                "devices": [("emulator-5554", "device")],
                "selected_serial": "emulator-5554",
                "device_ready": True,
                "screenshot_available": False,
                "uiautomator_available": True,
                "error": "screenshot: failed",
            }
        )

    monkeypatch.setattr(smoke, "doctor", fake_doctor)
    monkeypatch.setattr(smoke, "daemon_status", lambda: "not running: /tmp/android-harness/daemon.sock")

    report = smoke.run_smoke()

    assert report["ok"] is False
    assert report["daemon"]["running"] is False
    screenshot_check = next(check for check in report["checks"] if check["name"] == "screenshot_available")
    assert screenshot_check == {
        "name": "screenshot_available",
        "ok": False,
        "detail": "screenshot probe failed",
    }


def test_run_smoke_explains_skipped_device_probes(monkeypatch):
    def fake_doctor(serial=None, *, transport_name=None):
        return FakeReport(
            {
                "adb_available": True,
                "devices": [],
                "selected_serial": None,
                "device_ready": False,
                "screenshot_available": None,
                "uiautomator_available": None,
                "error": "select a single authorized device with ANDROID_SERIAL or -s",
            }
        )

    monkeypatch.setattr(smoke, "doctor", fake_doctor)
    monkeypatch.setattr(smoke, "daemon_status", lambda: "not running: /tmp/android-harness/daemon.sock")

    report = smoke.run_smoke()

    assert report["ok"] is False
    screenshot_check = next(check for check in report["checks"] if check["name"] == "screenshot_available")
    uiautomator_check = next(check for check in report["checks"] if check["name"] == "uiautomator_available")
    assert screenshot_check == {
        "name": "screenshot_available",
        "ok": False,
        "detail": "not checked because device is not ready",
    }
    assert uiautomator_check == {
        "name": "uiautomator_available",
        "ok": False,
        "detail": "not checked because device is not ready",
    }
