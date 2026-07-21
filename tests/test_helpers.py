import json

import pytest

from android_harness.adb import AdbClient, AdbError
from android_harness import helpers
from android_harness.transport import AdbResult, SubprocessAdbTransport
from android_harness.ui import Bounds, Element


class _FakeTransport:
    def __init__(self, stdout: str = ""):
        self.stdout = stdout
        self.calls = []

    def run(self, adb_path, serial, args, *, timeout=30, text=True):
        self.calls.append((adb_path, serial, list(args), timeout, text))
        return AdbResult(tuple([adb_path, *args]), 0, self.stdout, "")

    def screenshot(self, adb_path, serial, path, *, timeout=30):
        self.calls.append((adb_path, serial, ["screenshot", str(path)], timeout, True))
        return path


def _element(text: str | None, bounds: Bounds | None = None, enabled: bool = True, focused: bool = False) -> Element:
    return Element(
        text=text,
        resource_id=None,
        class_name="android.widget.Button",
        content_desc=None,
        bounds=bounds or Bounds(10, 20, 110, 220),
        clickable=True,
        enabled=enabled,
        focused=focused,
    )


def test_parse_wm_size_physical_size():
    assert helpers._parse_wm_size("Physical size: 1080x2400\n") == (1080, 2400)


def test_parse_wm_size_override_output():
    output = "Override size: 720x1280\nPhysical size: 1080x2400\n"

    assert helpers._parse_wm_size(output) == (1080, 2400)


def test_tcpip_target_adds_default_port_only_when_needed():
    assert helpers._tcpip_target("192.168.1.20") == "192.168.1.20:5555"
    assert helpers._tcpip_target("192.168.1.20:5566") == "192.168.1.20:5566"


def test_bounds_center_supports_bounds_and_mapping():
    assert helpers.bounds_center(Bounds(10, 20, 110, 220)) == (60, 120)
    assert helpers.bounds_center({"left": 0, "top": 10, "right": 100, "bottom": 210}) == (50, 110)


def test_get_client_returns_selected_client(monkeypatch):
    client = object()
    monkeypatch.setattr(helpers, "_client", client)

    assert helpers.get_client() is client


def test_set_device_preserves_current_transport_when_unspecified(monkeypatch):
    transport = _FakeTransport()
    monkeypatch.setattr(helpers, "_client", AdbClient(serial="old-device", adb_path="custom-adb", transport=transport))

    helpers.set_device("new-device")

    client = helpers.get_client()
    assert client.serial == "new-device"
    assert client.adb_path == "custom-adb"
    assert client.transport is transport


def test_set_device_can_explicitly_replace_transport(monkeypatch):
    transport = _FakeTransport()
    monkeypatch.setattr(helpers, "_client", AdbClient(serial="old-device", transport=transport))

    helpers.set_device("new-device", transport_name="subprocess")

    client = helpers.get_client()
    assert client.serial == "new-device"
    assert isinstance(client.transport, SubprocessAdbTransport)


def test_adb_connect_preserves_current_transport(monkeypatch):
    transport = _FakeTransport(stdout="connected to 192.168.1.20:5555\n")
    monkeypatch.setattr(helpers, "_client", AdbClient(transport=transport))

    output = helpers.adb_connect("192.168.1.20")

    client = helpers.get_client()
    assert output == "connected to 192.168.1.20:5555"
    assert client.serial == "192.168.1.20:5555"
    assert client.transport is transport
    assert transport.calls == [("adb", None, ["connect", "192.168.1.20:5555"], 30, True)]


def test_helpers_star_import_exports_only_agent_surface():
    namespace = {}

    exec("from android_harness.helpers import *", namespace)

    assert "tap" in namespace
    assert "type_text" in namespace
    assert "os" not in namespace
    assert "re" not in namespace
    assert "shlex" not in namespace
    assert "Path" not in namespace
    assert "AdbClient" not in namespace
    assert "annotations" not in namespace


def test_type_text_keeps_spaces_and_shell_metacharacters_safe(monkeypatch):
    class FakeClient:
        def __init__(self):
            self.commands = []

        def shell(self, args, timeout=30):
            self.commands.append(args)
            return ""

    client = FakeClient()
    monkeypatch.setattr(helpers, "_client", client)

    helpers.type_text("foo & bar")

    assert client.commands == ["input text 'foo%s&%sbar'"]


def test_type_text_rejects_literal_percent(monkeypatch):
    class FakeClient:
        def shell(self, args, timeout=30):
            raise AssertionError("unsafe text should not be sent to adb")

    monkeypatch.setattr(helpers, "_client", FakeClient())

    with pytest.raises(AdbError, match="ADBKeyboard"):
        helpers.type_text("50% discount")


def test_type_text_rejects_non_ascii(monkeypatch):
    class FakeClient:
        def shell(self, args, timeout=30):
            raise AssertionError("unsafe text should not be sent to adb")

    monkeypatch.setattr(helpers, "_client", FakeClient())

    with pytest.raises(AdbError, match="printable ASCII"):
        helpers.type_text("你好")


def test_page_info_is_json_serializable(monkeypatch):
    clickable = _element("Allow")
    focused = _element("Name", Bounds(20, 40, 220, 100), focused=True)
    monkeypatch.setattr(helpers, "ui_tree", lambda: [clickable, focused])
    monkeypatch.setattr(helpers, "current_app", lambda: {"package": "com.example", "activity": ".Main"})

    info = helpers.page_info()

    assert info["element_count"] == 2
    assert info["clickable"][0]["class_name"] == "android.widget.Button"
    assert info["clickable"][0]["bounds"] == {
        "left": 10,
        "top": 20,
        "right": 110,
        "bottom": 220,
        "width": 100,
        "height": 200,
        "center_x": 60,
        "center_y": 120,
    }
    assert info["focused"][0]["text"] == "Name"
    assert info["focused"][0]["bounds"] == {
        "left": 20,
        "top": 40,
        "right": 220,
        "bottom": 100,
        "width": 200,
        "height": 60,
        "center_x": 120,
        "center_y": 70,
    }
    json.dumps(info)


def test_permission_button_candidates():
    assert "允许" in helpers._permission_button_texts(True)
    assert "Allow" in helpers._permission_button_texts(True)
    assert "拒绝" in helpers._permission_button_texts(False)
    assert "Deny" in helpers._permission_button_texts(False)


def test_find_permission_button_prefers_candidate_order(monkeypatch):
    elements = [_element("允许"), _element("仅在使用中允许")]
    monkeypatch.setattr(helpers, "ui_tree", lambda: elements)

    assert helpers._find_permission_button(True).text == "仅在使用中允许"


def test_find_permission_button_does_not_match_allow_inside_deny_text(monkeypatch):
    elements = [_element("不允许"), _element("允许")]
    monkeypatch.setattr(helpers, "ui_tree", lambda: elements)

    assert helpers._find_permission_button(True).text == "允许"


def test_find_permission_button_matches_common_deny_text(monkeypatch):
    elements = [_element("允许"), _element("不允许")]
    monkeypatch.setattr(helpers, "ui_tree", lambda: elements)

    assert helpers._find_permission_button(False).text == "不允许"


def test_find_permission_button_does_not_match_english_allow_inside_deny_text(monkeypatch):
    elements = [_element("Don't Allow"), _element("Allow")]
    monkeypatch.setattr(helpers, "ui_tree", lambda: elements)

    assert helpers._find_permission_button(True).text == "Allow"


def test_tap_if_text_taps_first_match(monkeypatch):
    tapped = []
    element = _element("Allow")
    monkeypatch.setattr(helpers, "find_text", lambda text, exact=False: [element])
    monkeypatch.setattr(helpers, "tap_element", lambda match: tapped.append(match))

    assert helpers.tap_if_text("Allow") is True
    assert tapped == [element]


def test_tap_if_text_returns_false_without_match(monkeypatch):
    monkeypatch.setattr(helpers, "find_text", lambda text, exact=False: [])
    monkeypatch.setattr(helpers, "tap_element", lambda match: (_ for _ in ()).throw(AssertionError("unexpected tap")))

    assert helpers.tap_if_text("Allow") is False
