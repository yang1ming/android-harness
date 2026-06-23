"""Local policy guard plugin for Android Harness boundary checks.

This plugin is advisory. It does not enforce runtime policy, intercept ADB, or
hide automation signals. It helps callers flag requests that appear outside the
project's documented boundaries before running helper code.
"""

from __future__ import annotations

from dataclasses import dataclass

from android_harness.plugins import registry


@dataclass(frozen=True)
class PolicyRule:
    name: str
    reason: str
    terms: tuple[str, ...]


_RULES = (
    PolicyRule(
        "account_or_registration_automation",
        "Account creation, login, bulk registration, and account workflows are outside core boundaries.",
        ("account", "login", "register", "registration", "bulk-registration", "账号", "登录", "注册"),
    ),
    PolicyRule(
        "payment_or_captcha_automation",
        "Payment and CAPTCHA workflows are explicitly out of scope.",
        ("payment", "checkout", "captcha", "支付", "付款", "验证码"),
    ),
    PolicyRule(
        "platform_bypass_or_evasion",
        "Detection evasion, risk-control bypass, and hiding automation signals are not supported.",
        ("bypass", "evasion", "hide adb", "hide automation", "risk control", "风控", "绕过", "隐藏"),
    ),
    PolicyRule(
        "private_or_personal_data",
        "Real account data, tokens, payment data, private messages, and personal data must stay out of core.",
        ("token", "password", "private message", "personal data", "密码", "私信", "个人数据"),
    ),
)


def check_request(text: str) -> dict[str, object]:
    """Return advisory policy matches for a requested automation task."""

    normalized = text.casefold()
    matches: list[dict[str, object]] = []
    for rule in _RULES:
        terms = [term for term in rule.terms if term.casefold() in normalized]
        if terms:
            matches.append({"rule": rule.name, "terms": terms, "reason": rule.reason})

    return {
        "allowed": not matches,
        "matches": matches,
        "message": "request appears within android-harness boundaries"
        if not matches
        else "request needs review before using android-harness helpers",
    }


registry.register_policy("safety_boundary_check", check_request)
