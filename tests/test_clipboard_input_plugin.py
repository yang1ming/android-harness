from android_harness import helpers
from android_harness.plugins import registry
from plugins import clipboard_input_plugin


class FakeClient:
    def __init__(self):
        self.calls = []

    def shell(self, args, timeout=30):
        self.calls.append(args)
        return ""


def test_set_clipboard_text_uses_android_clipboard_service(monkeypatch):
    client = FakeClient()
    monkeypatch.setattr(helpers, "_client", client)

    clipboard_input_plugin.set_clipboard_text("你好 50%", label="test")

    assert client.calls == [["cmd", "clipboard", "set", "text", "test", "你好 50%"]]


def test_paste_clipboard_sends_keycode_paste(monkeypatch):
    pressed = []
    monkeypatch.setattr(helpers, "press_key", lambda key: pressed.append(key))

    clipboard_input_plugin.paste_clipboard()

    assert pressed == [clipboard_input_plugin.KEYCODE_PASTE]


def test_type_via_clipboard_can_skip_paste(monkeypatch):
    client = FakeClient()
    pressed = []
    monkeypatch.setattr(helpers, "_client", client)
    monkeypatch.setattr(helpers, "press_key", lambda key: pressed.append(key))

    clipboard_input_plugin.type_via_clipboard("Draft", paste=False)

    assert client.calls == [["cmd", "clipboard", "set", "text", "android-harness", "Draft"]]
    assert pressed == []


def test_type_via_clipboard_sets_text_and_pastes(monkeypatch):
    client = FakeClient()
    pressed = []
    monkeypatch.setattr(helpers, "_client", client)
    monkeypatch.setattr(helpers, "press_key", lambda key: pressed.append(key))

    clipboard_input_plugin.type_via_clipboard("Ready")

    assert client.calls == [["cmd", "clipboard", "set", "text", "android-harness", "Ready"]]
    assert pressed == [clipboard_input_plugin.KEYCODE_PASTE]


def test_clipboard_input_status_does_not_read_clipboard():
    assert clipboard_input_plugin.clipboard_input_status() == {
        "available": "device-dependent",
        "set_command": "cmd clipboard set text",
        "paste_keycode": 279,
        "reads_clipboard": False,
    }


def test_clipboard_input_plugin_registers_capabilities():
    capabilities = registry.capabilities()

    assert "set_clipboard_text" in capabilities["actions"]
    assert "paste_clipboard" in capabilities["actions"]
    assert "type_via_clipboard" in capabilities["actions"]
    assert "clipboard_input_status" in capabilities["environment"]
