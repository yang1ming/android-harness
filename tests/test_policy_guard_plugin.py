from android_harness.plugins import registry
from plugins import policy_guard_plugin


def test_policy_guard_allows_authorized_observation_task():
    result = policy_guard_plugin.check_request("capture a screenshot from my authorized test emulator")

    assert result == {
        "allowed": True,
        "matches": [],
        "message": "request appears within android-harness boundaries",
    }


def test_policy_guard_flags_out_of_scope_terms():
    result = policy_guard_plugin.check_request("bypass captcha and hide adb during account registration")

    assert result["allowed"] is False
    assert result["message"] == "request needs review before using android-harness helpers"
    rules = {match["rule"] for match in result["matches"]}
    assert "account_or_registration_automation" in rules
    assert "payment_or_captcha_automation" in rules
    assert "platform_bypass_or_evasion" in rules


def test_policy_guard_registers_policy_capability():
    assert "safety_boundary_check" in registry.capabilities()["policies"]
