"""Observation payload helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


SNAPSHOT_SCHEMA_VERSION = "android-harness.snapshot.v1"


def versioned_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Add a stable schema marker to a state snapshot payload."""

    return {"schema_version": SNAPSHOT_SCHEMA_VERSION, **dict(snapshot)}
