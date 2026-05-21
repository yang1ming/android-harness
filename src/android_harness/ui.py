"""uiautomator XML parsing."""

from __future__ import annotations

from dataclasses import dataclass
from xml.etree import ElementTree


@dataclass(frozen=True)
class Bounds:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def center(self) -> tuple[int, int]:
        return ((self.left + self.right) // 2, (self.top + self.bottom) // 2)


@dataclass(frozen=True)
class Element:
    text: str | None
    resource_id: str | None
    class_name: str | None
    content_desc: str | None
    bounds: Bounds
    clickable: bool
    enabled: bool
    focused: bool


def parse_bounds(value: str) -> Bounds:
    left_top, right_bottom = value.split("][")
    left, top = left_top.strip("[]").split(",")
    right, bottom = right_bottom.strip("[]").split(",")
    return Bounds(int(left), int(top), int(right), int(bottom))


def parse_bool(value: str | None) -> bool:
    return value == "true"


def parse_ui_xml(xml: str) -> list[Element]:
    root = ElementTree.fromstring(xml)
    elements: list[Element] = []
    for node in root.iter("node"):
        bounds_raw = node.attrib.get("bounds")
        if not bounds_raw:
            continue
        text = node.attrib.get("text") or None
        desc = node.attrib.get("content-desc") or None
        elements.append(
            Element(
                text=text,
                resource_id=node.attrib.get("resource-id") or None,
                class_name=node.attrib.get("class") or None,
                content_desc=desc,
                bounds=parse_bounds(bounds_raw),
                clickable=parse_bool(node.attrib.get("clickable")),
                enabled=parse_bool(node.attrib.get("enabled")),
                focused=parse_bool(node.attrib.get("focused")),
            )
        )
    return elements


def visible_texts(elements: list[Element]) -> list[str]:
    texts: list[str] = []
    for element in elements:
        if element.text:
            texts.append(element.text)
        if element.content_desc:
            texts.append(element.content_desc)
    return texts
