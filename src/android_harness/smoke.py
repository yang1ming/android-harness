"""Structured smoke checks for release and issue triage."""

from __future__ import annotations

import copy
import os
from typing import Any

from .admin import doctor
from .daemon import daemon_status


SMOKE_SCHEMA_VERSION = "android-harness.smoke.v1"
REDACTED_DEVICE = "<redacted-device>"


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


def redact_smoke_report(report: dict[str, Any]) -> dict[str, Any]:
    """Remove selected device identifiers from a smoke report."""

    redacted = copy.deepcopy(report)
    identifiers = _device_identifiers(redacted)

    if redacted.get("selected_serial"):
        redacted["selected_serial"] = REDACTED_DEVICE

    doctor_report = redacted.get("doctor")
    if isinstance(doctor_report, dict):
        if doctor_report.get("selected_serial"):
            doctor_report["selected_serial"] = REDACTED_DEVICE
        devices = doctor_report.get("devices")
        if isinstance(devices, list):
            doctor_report["devices"] = [_redact_device_entry(entry) for entry in devices]
        error = doctor_report.get("error")
        if isinstance(error, str):
            doctor_report["error"] = _replace_identifiers(error, identifiers)

    checks = redacted.get("checks")
    if isinstance(checks, list):
        for check in checks:
            if not isinstance(check, dict):
                continue
            detail = check.get("detail")
            if isinstance(detail, str):
                check["detail"] = _replace_identifiers(detail, identifiers)

    redacted["device_redacted"] = True
    return redacted


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


def _device_identifiers(report: dict[str, Any]) -> list[str]:
    identifiers: list[str] = []
    selected = report.get("selected_serial")
    if isinstance(selected, str) and selected:
        identifiers.append(selected)

    doctor_report = report.get("doctor")
    if isinstance(doctor_report, dict):
        doctor_selected = doctor_report.get("selected_serial")
        if isinstance(doctor_selected, str) and doctor_selected:
            identifiers.append(doctor_selected)
        devices = doctor_report.get("devices")
        if isinstance(devices, list):
            for entry in devices:
                if isinstance(entry, (list, tuple)) and entry and isinstance(entry[0], str) and entry[0]:
                    identifiers.append(entry[0])

    return sorted(set(identifiers), key=len, reverse=True)


def _redact_device_entry(entry: Any) -> Any:
    if not isinstance(entry, (list, tuple)) or not entry:
        return entry
    redacted = list(entry)
    if isinstance(redacted[0], str) and redacted[0]:
        redacted[0] = REDACTED_DEVICE
    return redacted


def _replace_identifiers(value: str, identifiers: list[str]) -> str:
    redacted = value
    for identifier in identifiers:
        redacted = redacted.replace(identifier, REDACTED_DEVICE)
    return redacted
