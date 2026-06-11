"""Diagnostics for Android Harness."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import tempfile
from pathlib import Path
from typing import Callable

from .adb import AdbClient


@dataclass(frozen=True)
class DoctorReport:
    adb_available: bool
    devices: list[tuple[str, str]]
    selected_serial: str | None
    device_ready: bool
    tcpip_target: str | None = None
    tcpip_connected: bool | None = None
    model: str | None = None
    android_version: str | None = None
    sdk_version: str | None = None
    screen_size: str | None = None
    screen_density: str | None = None
    uiautomator_available: bool | None = None
    screenshot_available: bool | None = None
    current_package: str | None = None
    current_activity: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def doctor(serial: str | None = None, *, transport_name: str | None = None) -> DoctorReport:
    client = AdbClient(serial=serial, transport_name=transport_name)
    try:
        client.require_available()
        devices = client.devices()
    except Exception as exc:
        return DoctorReport(
            adb_available=False,
            devices=[],
            selected_serial=serial,
            device_ready=False,
            error=str(exc),
        )

    ready_devices = [device for device in devices if device[1] == "device"]
    selected = serial or client.serial or (ready_devices[0][0] if len(ready_devices) == 1 else None)
    if not selected:
        return DoctorReport(
            adb_available=True,
            devices=devices,
            selected_serial=None,
            device_ready=False,
            error="select a single authorized device with ANDROID_SERIAL or -s",
        )

    tcpip_target = selected if _is_tcpip_serial(selected) else None
    tcpip_connected: bool | None = None
    selected_state = next((state for device_serial, state in devices if device_serial == selected), None)
    if tcpip_target and selected_state != "device":
        try:
            client.connect(tcpip_target, timeout=10)
            tcpip_connected = True
            devices = client.devices()
            selected_state = next((state for device_serial, state in devices if device_serial == selected), None)
        except Exception:
            tcpip_connected = False

    if selected_state != "device":
        detail = selected_state or "not listed"
        return DoctorReport(
            adb_available=True,
            devices=devices,
            selected_serial=selected,
            device_ready=False,
            tcpip_target=tcpip_target,
            tcpip_connected=tcpip_connected,
            error=f"selected device is not authorized/ready: {detail}",
        )

    selected_client = AdbClient(serial=selected, transport=client.transport)
    errors: list[str] = []

    def probe(label: str, action: Callable[[], object]) -> object | None:
        try:
            return action()
        except Exception as exc:
            errors.append(f"{label}: {exc}")
            return None

    model = probe("model", lambda: selected_client.getprop("ro.product.model"))
    android_version = probe("android_version", lambda: selected_client.getprop("ro.build.version.release"))
    sdk_version = probe("sdk_version", lambda: selected_client.getprop("ro.build.version.sdk"))
    screen_size = probe("screen_size", lambda: selected_client.shell(["wm", "size"]).strip())
    screen_density = probe("screen_density", lambda: selected_client.shell(["wm", "density"]).strip())

    uiautomator_available = _probe_uiautomator(selected_client, errors)
    screenshot_available = _probe_screenshot(selected_client, errors)

    app = probe("current_app", lambda: current_app(selected_client))
    current_package = app.get("package") if isinstance(app, dict) else None
    current_activity = app.get("activity") if isinstance(app, dict) else None

    return DoctorReport(
        adb_available=True,
        devices=devices,
        selected_serial=selected,
        device_ready=True,
        tcpip_target=tcpip_target,
        tcpip_connected=tcpip_connected,
        model=model if isinstance(model, str) else None,
        android_version=android_version if isinstance(android_version, str) else None,
        sdk_version=sdk_version if isinstance(sdk_version, str) else None,
        screen_size=screen_size if isinstance(screen_size, str) else None,
        screen_density=screen_density if isinstance(screen_density, str) else None,
        uiautomator_available=uiautomator_available,
        screenshot_available=screenshot_available,
        current_package=current_package,
        current_activity=current_activity,
        error="; ".join(errors) or None,
    )


def _is_tcpip_serial(serial: str) -> bool:
    host, separator, port = serial.rpartition(":")
    if not separator or not host or not port.isdigit():
        return False
    return "." in host or host == "localhost" or host.startswith("[")


def _probe_uiautomator(client: AdbClient, errors: list[str]) -> bool:
    try:
        client.shell(["uiautomator", "dump", "/sdcard/window_dump.xml"], timeout=15)
        return True
    except Exception as exc:
        errors.append(f"uiautomator: {exc}")
        return False


def _probe_screenshot(client: AdbClient, errors: list[str]) -> bool:
    with tempfile.NamedTemporaryFile(prefix="android-harness-doctor-", suffix=".png", delete=False) as handle:
        path = Path(handle.name)
    try:
        client.screenshot(path)
        return path.stat().st_size > 0
    except Exception as exc:
        errors.append(f"screenshot: {exc}")
        return False
    finally:
        path.unlink(missing_ok=True)


def current_app(client: AdbClient) -> dict[str, str | None]:
    output = client.shell(["dumpsys", "window", "windows"], timeout=10)
    for line in output.splitlines():
        if "mCurrentFocus=" in line or "mFocusedApp=" in line:
            package, activity = _parse_component_line(line)
            if package or activity:
                return {"package": package, "activity": activity}
    output = client.shell(["dumpsys", "activity", "activities"], timeout=10)
    for line in output.splitlines():
        if "mResumedActivity:" in line or "topResumedActivity=" in line:
            package, activity = _parse_component_line(line)
            if package or activity:
                return {"package": package, "activity": activity}
    return {"package": None, "activity": None}


def _parse_component_line(line: str) -> tuple[str | None, str | None]:
    marker = " u0 "
    fragment = line.split(marker, 1)[-1] if marker in line else line
    for token in fragment.replace("}", " ").replace("{", " ").split():
        if "/" not in token:
            continue
        component = token.strip()
        package, activity = component.split("/", 1)
        activity = activity.strip()
        if activity.startswith("."):
            activity = package + activity
        return package or None, activity or None
    return None, None
