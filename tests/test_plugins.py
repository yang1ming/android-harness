from android_harness.plugins import PluginRegistry


def test_plugin_registry_capabilities():
    registry = PluginRegistry()
    registry.register_action("human_tap", lambda: None)
    registry.register_detector("ocr_text", lambda: None)
    registry.register_environment("posture", lambda: None)
    registry.register_policy("confirm_sensitive_action", lambda: None)

    assert registry.capabilities() == {
        "actions": ["human_tap"],
        "detectors": ["ocr_text"],
        "environment": ["posture"],
        "policies": ["confirm_sensitive_action"],
    }
