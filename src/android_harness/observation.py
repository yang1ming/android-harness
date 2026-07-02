"""Observation payload helpers."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any


SNAPSHOT_SCHEMA_VERSION = "android-harness.snapshot.v1"
REDACTED_DEVICE = "<redacted-device>"


def versioned_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Add a stable schema marker to a state snapshot payload."""

    return {"schema_version": SNAPSHOT_SCHEMA_VERSION, **dict(snapshot)}


def redact_snapshot_text(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Remove UI text content from a snapshot while preserving useful counts."""

    redacted = dict(snapshot)
    _redact_visible_texts(redacted)

    page_info = redacted.get("page_info")
    if isinstance(page_info, Mapping):
        page = dict(page_info)
        _redact_visible_texts(page)
        clickable = page.get("clickable")
        if isinstance(clickable, list):
            page["clickable"] = [_redact_clickable_entry(entry) for entry in clickable]
        redacted["page_info"] = page

    redacted["text_redacted"] = True
    return redacted


def redact_snapshot_device(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Remove selected device identifiers from a snapshot payload."""

    redacted = copy.deepcopy(dict(snapshot))
    device_info = redacted.get("device_info")
    if isinstance(device_info, dict) and device_info.get("serial"):
        device_info["serial"] = REDACTED_DEVICE
    redacted["device_redacted"] = True
    return redacted


def summarize_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact count-based snapshot summary for logs and CI."""

    summary: dict[str, Any] = {
        "summary": True,
        "device_info": snapshot.get("device_info"),
        "current_app": snapshot.get("current_app"),
    }
    if "screenshot" in snapshot:
        summary["screenshot"] = snapshot["screenshot"]

    visible_texts = snapshot.get("visible_texts")
    if isinstance(visible_texts, list):
        summary["visible_text_count"] = len(visible_texts)

    page_info = snapshot.get("page_info")
    if isinstance(page_info, Mapping):
        page_summary: dict[str, Any] = {}
        if "current_app" in page_info:
            page_summary["current_app"] = page_info["current_app"]
        page_visible_texts = page_info.get("visible_texts")
        if isinstance(page_visible_texts, list):
            page_summary["visible_text_count"] = len(page_visible_texts)
        clickable = page_info.get("clickable")
        if isinstance(clickable, list):
            page_summary["clickable_count"] = len(clickable)
        summary["page_info"] = page_summary

    return summary


def _redact_visible_texts(payload: dict[str, Any]) -> None:
    visible_texts = payload.get("visible_texts")
    if isinstance(visible_texts, list):
        payload["visible_text_count"] = len(visible_texts)
        payload["visible_texts"] = []


def _redact_clickable_entry(entry: Any) -> Any:
    if not isinstance(entry, Mapping):
        return entry
    redacted = dict(entry)
    if "text" in redacted:
        redacted["text"] = None
    if "content_desc" in redacted:
        redacted["content_desc"] = None
    return redacted
