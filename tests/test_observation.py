from android_harness.observation import SNAPSHOT_SCHEMA_VERSION, versioned_snapshot


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
