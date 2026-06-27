from android_harness.observation import SNAPSHOT_SCHEMA_VERSION, redact_snapshot_text, versioned_snapshot


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
