import pytest

from android_harness.ui import parse_bounds, parse_ui_xml, visible_texts


def test_parse_bounds_center():
    bounds = parse_bounds("[10,20][110,220]")

    assert bounds.left == 10
    assert bounds.top == 20
    assert bounds.right == 110
    assert bounds.bottom == 220
    assert bounds.center == (60, 120)


def test_parse_bounds_rejects_malformed_value():
    with pytest.raises(ValueError, match="invalid uiautomator bounds"):
        parse_bounds("10,20,110,220")


def test_parse_bounds_accepts_signed_coordinates():
    bounds = parse_bounds("[-5,-10][95,190]")

    assert bounds.left == -5
    assert bounds.top == -10
    assert bounds.right == 95
    assert bounds.bottom == 190
    assert bounds.center == (45, 90)


def test_parse_ui_xml_elements():
    xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
    <hierarchy rotation="0">
      <node text="允许" resource-id="pkg:id/allow" class="android.widget.Button"
            package="pkg" content-desc="" checkable="false" checked="false"
            clickable="true" enabled="true" focusable="true" focused="false"
            scrollable="false" long-clickable="false" password="false"
            selected="false" bounds="[520,1600][980,1720]" />
    </hierarchy>
    """

    elements = parse_ui_xml(xml)

    assert len(elements) == 1
    assert elements[0].text == "允许"
    assert elements[0].resource_id == "pkg:id/allow"
    assert elements[0].clickable is True
    assert elements[0].enabled is True
    assert visible_texts(elements) == ["允许"]


def test_parse_ui_xml_skips_nodes_without_valid_bounds():
    xml = """
    <hierarchy>
      <node text="missing" clickable="true" enabled="true" />
      <node text="bad" clickable="true" enabled="true" bounds="oops" />
      <node text="valid" clickable="true" enabled="true" bounds="[1,2][3,4]" />
    </hierarchy>
    """

    elements = parse_ui_xml(xml)

    assert len(elements) == 1
    assert elements[0].text == "valid"
    assert elements[0].bounds.center == (2, 3)
