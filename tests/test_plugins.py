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


def test_plugin_registry_capabilities_are_sorted():
    registry = PluginRegistry()
    registry.register_action("z_action", lambda: None)
    registry.register_action("a_action", lambda: None)
    registry.register_detector("ocr_text", lambda: None)
    registry.register_detector("accessibility_hint", lambda: None)

    capabilities = registry.capabilities()

    assert capabilities["actions"] == ["a_action", "z_action"]
    assert capabilities["detectors"] == ["accessibility_hint", "ocr_text"]


def test_plugin_registry_replaces_existing_capability():
    registry = PluginRegistry()

    def first():
        return "first"

    def second():
        return "second"

    registry.register_policy("boundary_check", first)
    registry.register_policy("boundary_check", second)

    assert registry.capabilities()["policies"] == ["boundary_check"]
    assert registry.policies["boundary_check"]() == "second"


def test_plugin_registry_instances_are_isolated():
    left = PluginRegistry()
    right = PluginRegistry()

    left.register_environment("left_env", lambda: None)

    assert left.capabilities()["environment"] == ["left_env"]
    assert right.capabilities()["environment"] == []
