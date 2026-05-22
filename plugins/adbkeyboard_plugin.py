"""ADBKeyboard input-method plugin.

This plugin depends on the external ADBKeyboard IME being installed on the
device. It stays outside core because it requires an APK and changes the active
input method.
"""

from __future__ import annotations

import base64

from android_harness import helpers


ADB_KEYBOARD_IME = "com.android.adbkeyboard/.AdbIME"


def list_imes() -> list[str]:
    """Return enabled input methods reported by Android."""

    output = helpers._client.shell(["ime", "list", "-s"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def current_ime() -> str | None:
    """Return the current default input method, when Android reports one."""

    output = helpers._client.shell(["settings", "get", "secure", "default_input_method"])
    value = output.strip()
    if not value or value == "null":
        return None
    return value


def enable_adbkeyboard() -> str:
    """Enable ADBKeyboard if it is installed but not currently enabled."""

    if ADB_KEYBOARD_IME in list_imes():
        return "already enabled"
    return helpers._client.shell(["ime", "enable", ADB_KEYBOARD_IME]).strip()


def set_adbkeyboard() -> str | None:
    """Switch to ADBKeyboard and return the previous IME."""

    previous = current_ime()
    if previous == ADB_KEYBOARD_IME:
        return previous
    enable_adbkeyboard()
    helpers._client.shell(["ime", "set", ADB_KEYBOARD_IME])
    return previous


def restore_ime(ime: str | None) -> None:
    """Restore a previous input method if one was captured."""

    if ime and ime != ADB_KEYBOARD_IME:
        helpers._client.shell(["ime", "set", ime])


def type_unicode(text: str, *, restore: bool = True) -> None:
    """Type Unicode text through ADBKeyboard using base64 transport."""

    previous = set_adbkeyboard()
    try:
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        helpers._client.shell(["am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", encoded])
    finally:
        if restore:
            restore_ime(previous)


def clear_input(*, restore: bool = True) -> None:
    """Clear the focused text field through ADBKeyboard."""

    previous = set_adbkeyboard()
    try:
        helpers._client.shell(["am", "broadcast", "-a", "ADB_CLEAR_TEXT"])
    finally:
        if restore:
            restore_ime(previous)


def send_keyevent(code: int, *, restore: bool = True) -> None:
    """Send a keyevent through ADBKeyboard."""

    previous = set_adbkeyboard()
    try:
        helpers._client.shell(["am", "broadcast", "-a", "ADB_INPUT_KEYEVENT", "--ei", "code", str(code)])
    finally:
        if restore:
            restore_ime(previous)
