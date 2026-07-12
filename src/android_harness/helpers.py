"""Agent-facing helpers for Android Harness."""

from __future__ import annotations

import os
import re
import shlex
import tempfile
import time
from pathlib import Path
from typing import Mapping

from .adb import AdbClient, AdbError
from .admin import current_app as _current_app
from .ui import Bounds
from .ui import Element, parse_ui_xml, visible_texts as _visible_texts


__all__ = [
    "adb_connect",
    "adb_disconnect",
    "adb_tcpip",
    "bounds_center",
    "clear_text",
    "current_app",
    "device_info",
    "find_text",
    "force_stop",
    "get_client",
    "handle_permission_dialog",
    "launch_app",
    "logcat_tail",
    "long_press",
    "open_deeplink",
    "page_info",
    "press_key",
    "pull_file",
    "push_file",
    "screen_size",
    "screenshot",
    "set_device",
    "state_snapshot",
    "swipe",
    "tap",
    "tap_element",
    "tap_if_text",
    "tap_text",
    "type_text",
    "ui_tree",
    "ui_xml",
    "visible_texts",
    "wait_for_activity",
    "wait_for_app",
    "wait_for_screen_change",
    "wait_for_text",
    "wait_until_screen_stable",
]

_client = AdbClient()

_ALLOW_PERMISSION_TEXTS = (
    "仅在使用中允许",
    "始终允许",
    "允许",
    "Allow",
    "While using the app",
    "Only this time",
)
_DENY_PERMISSION_TEXTS = ("拒绝", "不允许", "Deny", "Don't allow", "Don’t allow")


def set_device(serial: str | None, *, transport_name: str | None = None) -> None:
    """Select the device used by subsequent helper calls."""

    global _client
    if transport_name is None:
        _client = AdbClient(serial=serial, adb_path=_client.adb_path, transport=_client.transport)
    else:
        _client = AdbClient(serial=serial, adb_path=_client.adb_path, transport_name=transport_name)


def get_client() -> AdbClient:
    """Return the currently selected ADB client for plugins and advanced helpers."""

    return _client


def adb_connect(host: str, port: int = 5555) -> str:
    """Connect to an adb-over-TCP/IP endpoint and select it for later calls."""

    target = _tcpip_target(host, port)
    output = _client.connect(target)
    set_device(target)
    return output


def adb_disconnect(host: str | None = None, port: int = 5555) -> str:
    """Disconnect one adb-over-TCP/IP endpoint, or all endpoints when host is None."""

    target = _tcpip_target(host, port) if host else None
    return _client.disconnect(target)


def adb_tcpip(port: int = 5555) -> str:
    """Restart the selected USB-connected device's adbd in TCP/IP mode."""

    return _client.tcpip(port)


def device_info() -> dict[str, str]:
    """Return basic device facts."""

    return {
        "serial": _client.serial or os.environ.get("ANDROID_SERIAL", ""),
        "model": _client.getprop("ro.product.model"),
        "manufacturer": _client.getprop("ro.product.manufacturer"),
        "android_version": _client.getprop("ro.build.version.release"),
        "sdk_version": _client.getprop("ro.build.version.sdk"),
        "screen_size": _client.shell(["wm", "size"]).strip(),
        "screen_density": _client.shell(["wm", "density"]).strip(),
    }


def screen_size() -> tuple[int, int]:
    """Return the physical screen size as ``(width, height)``."""

    return _parse_wm_size(_client.shell(["wm", "size"]))


def current_app() -> dict[str, str | None]:
    """Return the foreground package and activity when available."""

    return _current_app(_client)


def state_snapshot(include_screenshot: bool = False) -> dict[str, object]:
    """Return a compact state snapshot for agent decision making."""

    snapshot: dict[str, object] = {
        "device_info": device_info(),
        "current_app": current_app(),
        "visible_texts": visible_texts(),
    }
    if include_screenshot:
        snapshot["screenshot"] = screenshot()
    return snapshot


def screenshot(path: str | Path | None = None) -> str:
    """Capture a PNG screenshot and return its local path."""

    if path is None:
        stamp = int(time.time() * 1000)
        path = Path(tempfile.gettempdir()) / "android-harness" / f"screenshot-{stamp}.png"
    return str(_client.screenshot(path))


def tap(x: int, y: int) -> None:
    _client.shell(["input", "tap", str(x), str(y)])


def long_press(x: int, y: int, duration_ms: int = 700) -> None:
    _client.shell(["input", "swipe", str(x), str(y), str(x), str(y), str(duration_ms)])


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 400) -> None:
    _client.shell(["input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])


def press_key(key: str | int) -> None:
    mapping = {
        "BACK": "4",
        "HOME": "3",
        "ENTER": "66",
        "MENU": "82",
        "POWER": "26",
        "RECENTS": "187",
        "TAB": "61",
    }
    code = mapping.get(str(key).upper(), str(key))
    _client.shell(["input", "keyevent", code])


def clear_text(max_chars: int = 80) -> None:
    """Best-effort clearing for the currently focused text field."""

    try:
        _client.shell(["input", "keycombination", "113", "29"], timeout=5)
        _client.shell(["input", "keyevent", "67"], timeout=5)
        return
    except AdbError:
        pass

    _client.shell(["input", "keyevent", "123"], timeout=5)
    for _ in range(max(0, max_chars)):
        _client.shell(["input", "keyevent", "67"], timeout=5)


def type_text(text: str) -> None:
    """Type text through adb shell input.

    This is only for printable ASCII text that does not contain a literal
    percent sign. Complex Unicode, percent signs, and multi-line input should be
    implemented through an input-method plugin rather than folded into core.
    """

    escaped = _adb_input_text_arg(text)
    _client.shell(f"input text {escaped}")


def launch_app(package: str, activity: str | None = None) -> None:
    if activity:
        component = f"{package}/{activity}"
        _client.shell(["am", "start", "-n", component])
    else:
        _client.shell(["monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"])


def force_stop(package: str) -> None:
    _client.shell(["am", "force-stop", package])


def open_deeplink(uri: str) -> None:
    _client.shell(["am", "start", "-a", "android.intent.action.VIEW", "-d", uri])


def ui_xml() -> str:
    remote_path = "/sdcard/window_dump.xml"
    _client.shell(["uiautomator", "dump", remote_path], timeout=15)
    return _client.pull_text(remote_path, timeout=15)


def ui_tree() -> list[Element]:
    return parse_ui_xml(ui_xml())


def visible_texts() -> list[str]:
    return _visible_texts(ui_tree())


def find_text(text: str, *, exact: bool = False) -> list[Element]:
    elements = ui_tree()
    matches: list[Element] = []
    for element in elements:
        candidates = [value for value in (element.text, element.content_desc) if value]
        if exact:
            if any(value == text for value in candidates):
                matches.append(element)
        elif any(text in value for value in candidates):
            matches.append(element)
    return matches


def tap_element(element: Element) -> None:
    x, y = element.bounds.center
    tap(x, y)


def bounds_center(bounds: Bounds | Mapping[str, int] | object) -> tuple[int, int]:
    """Return the center point for a Bounds object or dict-like bounds."""

    if isinstance(bounds, Bounds):
        return bounds.center
    if isinstance(bounds, Mapping):
        left = int(bounds["left"])
        top = int(bounds["top"])
        right = int(bounds["right"])
        bottom = int(bounds["bottom"])
        return ((left + right) // 2, (top + bottom) // 2)

    left = int(getattr(bounds, "left"))
    top = int(getattr(bounds, "top"))
    right = int(getattr(bounds, "right"))
    bottom = int(getattr(bounds, "bottom"))
    return ((left + right) // 2, (top + bottom) // 2)


def wait_for_text(text: str, timeout: float = 10, interval: float = 0.5, exact: bool = False) -> Element | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        matches = find_text(text, exact=exact)
        if matches:
            return matches[0]
        time.sleep(interval)
    return None


def tap_text(text: str, exact: bool = False, timeout: float = 5) -> bool:
    element = wait_for_text(text, timeout=timeout, exact=exact)
    if element is None:
        return False
    tap_element(element)
    return True


def tap_if_text(text: str, exact: bool = False) -> bool:
    matches = find_text(text, exact=exact)
    if not matches:
        return False
    tap_element(matches[0])
    return True


def wait_for_app(package: str, timeout: float = 10, interval: float = 0.5) -> dict[str, str | None] | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        app = current_app()
        if app.get("package") == package:
            return app
        time.sleep(interval)
    return None


def wait_for_activity(activity: str, timeout: float = 10, interval: float = 0.5) -> dict[str, str | None] | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        app = current_app()
        current = app.get("activity")
        if current and (current == activity or current.endswith(activity)):
            return app
        time.sleep(interval)
    return None


def wait_for_screen_change(timeout: float = 5, interval: float = 0.5, threshold: int = 0) -> bool:
    baseline = _screen_bytes()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        time.sleep(interval)
        current = _screen_bytes()
        if _screens_differ(baseline, current, threshold):
            return True
    return False


def wait_until_screen_stable(timeout: float = 5, interval: float = 0.5, stable_count: int = 2) -> bool:
    needed = max(1, stable_count)
    same_count = 0
    previous = _screen_bytes()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        time.sleep(interval)
        current = _screen_bytes()
        if current == previous:
            same_count += 1
            if same_count >= needed:
                return True
        else:
            same_count = 0
            previous = current
    return False


def handle_permission_dialog(allow: bool = True, timeout: float = 3) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        element = _find_permission_button(allow)
        if element is not None:
            tap_element(element)
            return True
        time.sleep(0.3)
    return False


def page_info() -> dict[str, object]:
    elements = ui_tree()
    return {
        "current_app": current_app(),
        "visible_texts": _visible_texts(elements),
        "clickable": [
            {
                "text": element.text,
                "content_desc": element.content_desc,
                "resource_id": element.resource_id,
                "bounds": _bounds_to_dict(element.bounds),
            }
            for element in elements
            if element.clickable and element.enabled
        ],
    }


def push_file(local: str | Path, remote: str) -> None:
    _client.run(["push", str(local), remote])


def pull_file(remote: str, local: str | Path) -> None:
    _client.run(["pull", remote, str(local)])


def logcat_tail(lines: int = 200) -> str:
    return _client.run(["logcat", "-d", "-t", str(lines)], timeout=20).stdout


def _bounds_to_dict(bounds: Bounds) -> dict[str, int]:
    return {
        "left": bounds.left,
        "top": bounds.top,
        "right": bounds.right,
        "bottom": bounds.bottom,
    }


def _parse_wm_size(output: str) -> tuple[int, int]:
    match = re.search(r"Physical size:\s*(\d+)x(\d+)", output)
    if match is None:
        match = re.search(r"\b(\d+)x(\d+)\b", output)
    if match is None:
        raise ValueError(f"unable to parse screen size from wm size output: {output!r}")
    return int(match.group(1)), int(match.group(2))


def _tcpip_target(host: str, port: int = 5555) -> str:
    if ":" in host:
        return host
    return f"{host}:{port}"


def _adb_input_text_arg(text: str) -> str:
    if "%" in text:
        raise AdbError(
            "type_text() cannot reliably type literal '%' through adb shell input text; "
            "use the ADBKeyboard plugin for percent signs or complex text."
        )
    if any(ord(char) < 0x20 or ord(char) >= 0x7F for char in text):
        raise AdbError(
            "type_text() only supports printable ASCII through adb shell input text; "
            "use the ADBKeyboard plugin for Unicode, newlines, or complex text."
        )
    return shlex.quote(text.replace(" ", "%s"))


def _permission_button_texts(allow: bool) -> tuple[str, ...]:
    return _ALLOW_PERMISSION_TEXTS if allow else _DENY_PERMISSION_TEXTS


def _find_permission_button(allow: bool) -> Element | None:
    elements = [element for element in ui_tree() if element.enabled]
    target_texts = _permission_button_texts(allow)
    opposite_texts = _permission_button_texts(not allow)

    for candidate in target_texts:
        for element in elements:
            texts = [value for value in (element.text, element.content_desc) if value]
            if any(_permission_text_equals(value, candidate) for value in texts):
                return element

    for candidate in target_texts:
        for element in elements:
            texts = [value for value in (element.text, element.content_desc) if value]
            if any(_permission_text_matches(value, opposite_texts) for value in texts):
                continue
            if any(_permission_text_contains(value, candidate) for value in texts):
                return element
    return None


def _permission_text_equals(value: str, candidate: str) -> bool:
    return value == candidate or value.casefold() == candidate.casefold()


def _permission_text_contains(value: str, candidate: str) -> bool:
    return candidate.casefold() in value.casefold()


def _permission_text_matches(value: str, candidates: tuple[str, ...]) -> bool:
    for candidate in candidates:
        if _permission_text_equals(value, candidate) or _permission_text_contains(value, candidate):
            return True
    return False


def _screen_bytes() -> bytes:
    with tempfile.NamedTemporaryFile(prefix="android-harness-screen-", suffix=".png", delete=False) as handle:
        path = Path(handle.name)
    try:
        _client.screenshot(path)
        return path.read_bytes()
    finally:
        path.unlink(missing_ok=True)


def _screens_differ(left: bytes, right: bytes, threshold: int) -> bool:
    if threshold <= 0:
        return left != right
    if abs(len(left) - len(right)) > threshold:
        return True
    distance = abs(len(left) - len(right))
    for a, b in zip(left, right):
        if a != b:
            distance += 1
            if distance > threshold:
                return True
    return False
