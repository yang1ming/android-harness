"""Observation payload helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


SNAPSHOT_SCHEMA_VERSION = "android-harness.snapshot.v1"


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
