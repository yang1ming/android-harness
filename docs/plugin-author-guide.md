# Plugin Author Guide

Plugins add optional Android Harness capabilities without expanding the small
core. Use a plugin when a feature needs an extra APK, service, model, network
access, heavier dependency, policy check, or device-specific integration.

## Good Plugin Candidates

- OCR and visual observation.
- Input method adapters.
- Environment reporting for authorized test devices.
- Local policy guards.
- Optional device-side components with explicit setup instructions.

## Keep Out Of Plugins

Do not add plugins for:

- Unauthorized device, app, account, payment, CAPTCHA, or bulk-registration
  workflows.
- Detection evasion, platform bypass, or automation-hiding behavior.
- Real account data, tokens, payment data, private messages, or personal data.
- App-specific business flows that should live in `agent-workspace/`.

## Accessing ADB

Plugins should use the active helper client instead of constructing unrelated
ADB state:

```python
from android_harness import helpers


def current_ime() -> str | None:
    output = helpers.get_client().shell(["settings", "get", "secure", "default_input_method"])
    value = output.strip()
    return value if value and value != "null" else None
```

This keeps `-s`, `ANDROID_SERIAL`, and `--transport daemon` behavior consistent
with the active CLI/helper session.

## Registry Shape

The current registry is intentionally small:

```python
from android_harness.plugins import registry


def describe_environment() -> dict[str, str]:
    return {"example": "value"}


registry.register_environment("example_environment", describe_environment)
```

Available buckets:

- `register_action(name, fn)`
- `register_detector(name, fn)`
- `register_policy(name, fn)`
- `register_environment(name, fn)`

Plugin loading is still explicit in this alpha release. Do not rely on automatic
plugin discovery unless a future release documents it.

## Documentation Expectations

Each plugin should document:

- What capability it adds.
- Required host dependencies.
- Required device-side components, if any.
- Required Android permissions or settings.
- Safety and misuse boundaries.
- Minimal verification commands.

The `plugins/adbkeyboard_plugin.py` module is the reference example for an
optional device-side component. It documents its external IME dependency and
keeps Unicode text input outside core. Its `adbkeyboard_active()` context
manager is the preferred shape when a plugin needs to temporarily switch Android
state and reliably restore it when the operation exits.

The `plugins/ocr_plugin.py` module is the reference example for a host-side
optional dependency. It shells out to Tesseract only when the plugin is imported
and leaves core free of OCR dependencies.
