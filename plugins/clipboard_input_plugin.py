"""Optional clipboard-based text input plugin.

This adapter uses Android's host-visible clipboard service plus KEYCODE_PASTE.
It is best-effort and device-dependent, so it stays outside core. Use it only
with authorized devices and focused fields where paste input is appropriate.
"""

from __future__ import annotations

from android_harness import helpers
from android_harness.plugins import registry


KEYCODE_PASTE = 279
DEFAULT_LABEL = "android-harness"


def set_clipboard_text(text: str, *, label: str = DEFAULT_LABEL) -> None:
    """Set Android clipboard text through ``cmd clipboard``."""

    helpers.get_client().shell(["cmd", "clipboard", "set", "text", label, text])


def paste_clipboard() -> None:
    """Send Android KEYCODE_PASTE to the focused input field."""

    helpers.press_key(KEYCODE_PASTE)


def type_via_clipboard(text: str, *, label: str = DEFAULT_LABEL, paste: bool = True) -> None:
    """Set clipboard text and optionally paste it into the focused field."""

    set_clipboard_text(text, label=label)
    if paste:
        paste_clipboard()


def clipboard_input_status() -> dict[str, object]:
    """Return static capability notes without reading clipboard contents."""

    return {
        "available": "device-dependent",
        "set_command": "cmd clipboard set text",
        "paste_keycode": KEYCODE_PASTE,
        "reads_clipboard": False,
    }


registry.register_action("set_clipboard_text", set_clipboard_text)
registry.register_action("paste_clipboard", paste_clipboard)
registry.register_action("type_via_clipboard", type_via_clipboard)
registry.register_environment("clipboard_input_status", clipboard_input_status)
