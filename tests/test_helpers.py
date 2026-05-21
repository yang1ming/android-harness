from android_harness import helpers
from android_harness.ui import Bounds, Element


def _element(text: str | None, bounds: Bounds | None = None, enabled: bool = True) -> Element:
    return Element(
        text=text,
        resource_id=None,
        class_name="android.widget.Button",
        content_desc=None,
        bounds=bounds or Bounds(10, 20, 110, 220),
        clickable=True,
        enabled=enabled,
        focused=False,
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


def test_permission_button_candidates():
    assert "允许" in helpers._permission_button_texts(True)
    assert "Allow" in helpers._permission_button_texts(True)
    assert "拒绝" in helpers._permission_button_texts(False)
    assert "Deny" in helpers._permission_button_texts(False)


def test_find_permission_button_prefers_candidate_order(monkeypatch):
    elements = [_element("允许"), _element("仅在使用中允许")]
    monkeypatch.setattr(helpers, "ui_tree", lambda: elements)

    assert helpers._find_permission_button(True).text == "仅在使用中允许"


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
