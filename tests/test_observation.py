import json
from pathlib import Path

from android_harness.observation import (
    REDACTED_DEVICE,
    REDACTED_PATH,
    SNAPSHOT_SCHEMA_VERSION,
    redact_snapshot_device,
    redact_snapshot_paths,
    redact_snapshot_text,
    summarize_snapshot,
    versioned_snapshot,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_versioned_snapshot_adds_schema_marker_without_nesting_payload():
    snapshot = {
        "device_info": {"serial": "emulator-5554"},
        "current_app": {"package": "com.example", "activity": ".Main"},
        "visible_texts": ["Ready"],
    }

    payload = versioned_snapshot(snapshot)

    assert payload["schema_version"] == SNAPSHOT_SCHEMA_VERSION
    assert payload["device_info"] == {"serial": "emulator-5554"}
    assert payload["current_app"] == {"package": "com.example", "activity": ".Main"}
    assert payload["visible_texts"] == ["Ready"]


def test_redact_snapshot_text_removes_text_content_but_preserves_counts():
    snapshot = {
        "device_info": {"serial": "emulator-5554"},
        "current_app": {"package": "com.example", "activity": ".Main"},
        "visible_texts": ["Ready", "Secret"],
        "page_info": {
            "visible_texts": ["Ready"],
            "clickable": [
                {
                    "text": "Start",
                    "content_desc": "Start button",
                    "resource_id": "pkg:id/start",
                    "bounds": {"left": 1, "top": 2, "right": 3, "bottom": 4},
                }
            ],
        },
    }

    redacted = redact_snapshot_text(snapshot)

    assert redacted["text_redacted"] is True
    assert redacted["visible_texts"] == []
    assert redacted["visible_text_count"] == 2
    assert redacted["page_info"]["visible_texts"] == []
    assert redacted["page_info"]["visible_text_count"] == 1
    assert redacted["page_info"]["clickable"][0] == {
        "text": None,
        "content_desc": None,
        "resource_id": "pkg:id/start",
        "bounds": {"left": 1, "top": 2, "right": 3, "bottom": 4},
    }
    assert snapshot["visible_texts"] == ["Ready", "Secret"]


def test_redact_snapshot_device_removes_serial_without_mutating_source():
    snapshot = {
        "device_info": {
            "serial": "emulator-5554",
            "model": "Pixel Test",
        },
        "current_app": {"package": "com.example", "activity": ".Main"},
        "visible_texts": ["Ready"],
    }

    redacted = redact_snapshot_device(snapshot)

    assert redacted["device_redacted"] is True
    assert redacted["device_info"] == {
        "serial": REDACTED_DEVICE,
        "model": "Pixel Test",
    }
    assert snapshot["device_info"]["serial"] == "emulator-5554"


def test_redact_snapshot_paths_removes_screenshot_path_without_mutating_source():
    snapshot = {
        "device_info": {"serial": "emulator-5554"},
        "current_app": {"package": "com.example", "activity": ".Main"},
        "visible_texts": ["Ready"],
        "screenshot": "/tmp/android-harness/screen.png",
    }

    redacted = redact_snapshot_paths(snapshot)

    assert redacted["paths_redacted"] is True
    assert redacted["screenshot"] == REDACTED_PATH
    assert snapshot["screenshot"] == "/tmp/android-harness/screen.png"


def test_summarize_snapshot_returns_counts_without_text_content():
    snapshot = {
        "device_info": {"serial": "emulator-5554"},
        "current_app": {"package": "com.example", "activity": ".Main"},
        "visible_texts": ["Ready", "Secret"],
        "screenshot": "/tmp/android-harness/screen.png",
        "page_info": {
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Ready"],
            "clickable": [
                {"text": "Start", "content_desc": "Start button", "class_name": "android.widget.Button"},
                {"text": "Name", "content_desc": None, "class_name": "android.widget.EditText"},
                {"text": "Stop", "content_desc": "Stop button", "class_name": "android.widget.Button"},
            ],
        },
    }

    summary = summarize_snapshot(snapshot)

    assert summary == {
        "summary": True,
        "device_info": {"serial": "emulator-5554"},
        "current_app": {"package": "com.example", "activity": ".Main"},
        "screenshot": "/tmp/android-harness/screen.png",
        "visible_text_count": 2,
        "page_info": {
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_text_count": 1,
            "clickable_count": 3,
            "clickable_class_counts": {
                "android.widget.Button": 2,
                "android.widget.EditText": 1,
            },
        },
    }


def test_snapshot_summary_matches_public_schema_fixture():
    snapshot = {
        "device_info": {"serial": "emulator-5554", "model": "Pixel Test"},
        "current_app": {"package": "com.example", "activity": ".Main"},
        "visible_texts": ["Ready", "Secret"],
        "screenshot": "/tmp/android-harness/screen.png",
        "page_info": {
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Ready"],
            "clickable": [
                {"text": "Start", "content_desc": "Start button", "class_name": "android.widget.Button"},
                {"text": "Stop", "content_desc": "Stop button", "class_name": "android.widget.Button"},
            ],
        },
    }

    payload = versioned_snapshot(summarize_snapshot(snapshot))
    fixture = json.loads((FIXTURES / "snapshot_summary_v1.json").read_text())

    assert payload == fixture
