"""Environment report plugin for authorized test devices.

The report is intended for issue triage and smoke-test notes. It avoids
collecting logcat, UI text, screenshots, account data, or app-private content.
"""

from __future__ import annotations

from typing import Any, Callable

from android_harness import helpers
from android_harness.plugins import registry


def environment_report() -> dict[str, Any]:
    """Return a compact, non-content environment report for the active device."""

    client = helpers.get_client()
    report: dict[str, Any] = {
        "adb": {
            "path": client.adb_path,
            "serial": client.serial,
            "transport": client.transport.__class__.__name__,
        },
        "host": {
            "android_harness": "python",
        },
        "devices": _probe("devices", client.devices),
        "device": {
            "model": _probe("ro.product.model", lambda: client.getprop("ro.product.model")),
            "manufacturer": _probe("ro.product.manufacturer", lambda: client.getprop("ro.product.manufacturer")),
            "android_version": _probe("ro.build.version.release", lambda: client.getprop("ro.build.version.release")),
            "sdk_version": _probe("ro.build.version.sdk", lambda: client.getprop("ro.build.version.sdk")),
        },
        "display": {
            "size": _probe("wm size", lambda: client.shell(["wm", "size"]).strip()),
            "density": _probe("wm density", lambda: client.shell(["wm", "density"]).strip()),
        },
        "current_app": _probe("current_app", helpers.current_app),
        "capabilities": {
            "uiautomator": _probe_bool(
                "uiautomator",
                lambda: client.shell(["uiautomator", "dump", "/sdcard/window_dump.xml"], timeout=15),
            ),
            "screenshot": _probe_bool("screenshot", lambda: helpers.screenshot()),
        },
    }
    return report


def _probe(label: str, action: Callable[[], Any]) -> Any:
    try:
        return action()
    except Exception as exc:
        return {"error": f"{label}: {exc}"}


def _probe_bool(label: str, action: Callable[[], Any]) -> bool | dict[str, str]:
    value = _probe(label, action)
    if isinstance(value, dict) and "error" in value:
        return value
    return True


registry.register_environment("device_environment", environment_report)
