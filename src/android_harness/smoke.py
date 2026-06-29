"""Structured smoke checks for release and issue triage."""

from __future__ import annotations

import os
from typing import Any

from .admin import doctor
from .daemon import daemon_status


SMOKE_SCHEMA_VERSION = "android-harness.smoke.v1"


def run_smoke(serial: str | None = None, *, transport_name: str | None = None) -> dict[str, Any]:
    """Run host-side and selected-device smoke checks."""

    doctor_report = doctor(serial, transport_name=transport_name).to_dict()
    daemon = _daemon_probe()
    checks = _checks_from_doctor(doctor_report)

    return {
        "schema_version": SMOKE_SCHEMA_VERSION,
        "ok": all(check["ok"] for check in checks),
        "transport": _selected_transport(transport_name),
        "selected_serial": doctor_report.get("selected_serial"),
        "checks": checks,
        "doctor": doctor_report,
        "daemon": daemon,
    }


def _checks_from_doctor(doctor_report: dict[str, Any]) -> list[dict[str, object]]:
    return [
        _check(
            "adb_available",
            doctor_report.get("adb_available") is True,
            doctor_report.get("error") if doctor_report.get("adb_available") is not True else None,
        ),
        _check(
            "device_ready",
            doctor_report.get("device_ready") is True,
            doctor_report.get("error") if doctor_report.get("device_ready") is not True else None,
        ),
        _check(
            "screenshot_available",
            doctor_report.get("screenshot_available") is True,
            _probe_detail(doctor_report, "screenshot_available", "screenshot probe failed"),
        ),
        _check(
            "uiautomator_available",
            doctor_report.get("uiautomator_available") is True,
            _probe_detail(doctor_report, "uiautomator_available", "uiautomator probe failed"),
        ),
    ]


def _check(name: str, ok: bool, detail: object | None = None) -> dict[str, object]:
    payload: dict[str, object] = {"name": name, "ok": ok}
    if detail:
        payload["detail"] = detail
    return payload


def _probe_detail(doctor_report: dict[str, Any], key: str, fallback: str) -> str | None:
    value = doctor_report.get(key)
    if value is False:
        return fallback
    if value is None and doctor_report.get("device_ready") is not True:
        return "not checked because device is not ready"
    return None


def _daemon_probe() -> dict[str, object]:
    try:
        status = daemon_status()
    except Exception as exc:
        return {"running": False, "status": f"error: {exc}"}
    return {"running": status.startswith("running:"), "status": status}


def _selected_transport(transport_name: str | None) -> str:
    return transport_name or os.environ.get("ANDROID_HARNESS_TRANSPORT") or "subprocess"
