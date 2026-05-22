import base64

from android_harness import helpers
from plugins import adbkeyboard_plugin


class FakeClient:
    def __init__(self):
        self.calls = []
        self.enabled_imes = "com.example/.Ime\n"
        self.current = "com.example/.Ime"

    def shell(self, args, timeout=30):
        self.calls.append(args)
        if args == ["ime", "list", "-s"]:
            return self.enabled_imes
        if args == ["settings", "get", "secure", "default_input_method"]:
            return f"{self.current}\n"
        if args == ["ime", "enable", adbkeyboard_plugin.ADB_KEYBOARD_IME]:
            self.enabled_imes += f"{adbkeyboard_plugin.ADB_KEYBOARD_IME}\n"
            return "Input method enabled\n"
        if args == ["ime", "set", adbkeyboard_plugin.ADB_KEYBOARD_IME]:
            self.current = adbkeyboard_plugin.ADB_KEYBOARD_IME
            return ""
        if args == ["ime", "set", "com.example/.Ime"]:
            self.current = "com.example/.Ime"
            return ""
        if args[:3] == ["am", "broadcast", "-a"]:
            return "Broadcast completed\n"
        raise AssertionError(f"unexpected shell args: {args}")


def test_type_unicode_uses_b64_and_restores_ime(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(helpers, "_client", client)

    adbkeyboard_plugin.type_unicode("你好 ☂️ 17°C")

    encoded = base64.b64encode("你好 ☂️ 17°C".encode("utf-8")).decode("ascii")
    assert ["am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", encoded] in client.calls
    assert client.calls[-1] == ["ime", "set", "com.example/.Ime"]


def test_clear_input_can_keep_adbkeyboard_active(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(helpers, "_client", client)

    adbkeyboard_plugin.clear_input(restore=False)

    assert ["am", "broadcast", "-a", "ADB_CLEAR_TEXT"] in client.calls
    assert client.calls[-1] == ["am", "broadcast", "-a", "ADB_CLEAR_TEXT"]


def test_send_keyevent_broadcasts_code(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(helpers, "_client", client)

    adbkeyboard_plugin.send_keyevent(66)

    assert ["am", "broadcast", "-a", "ADB_INPUT_KEYEVENT", "--ei", "code", "66"] in client.calls
