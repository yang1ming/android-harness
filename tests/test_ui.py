from android_harness.ui import parse_bounds, parse_ui_xml, visible_texts


def test_parse_bounds_center():
    bounds = parse_bounds("[10,20][110,220]")

    assert bounds.left == 10
    assert bounds.top == 20
    assert bounds.right == 110
    assert bounds.bottom == 220
    assert bounds.center == (60, 120)


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
