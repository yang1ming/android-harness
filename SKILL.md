---
name: android
description: Direct Android device control through ADB. Use for authorized device automation, testing, screenshots, UI inspection, and app interaction.
---

# android-harness

Direct Android device control through ADB. For task-specific edits, use
`agent-workspace/agent_helpers.py`. For app-specific knowledge, use
`agent-workspace/app-skills/<package>/`.

## Usage

```bash
android-harness <<'PY'
print(device_info())
print(current_app())
print(page_info())
PY
```

Helpers are pre-imported. Prefer this loop:

1. Take a screenshot.
2. Inspect current app and UI tree if needed.
3. Act with tap, swipe, type, or key events.
4. Wait for screen/app/text change.
5. Capture the result.

Screenshots are the primary observation source. `uiautomator` XML is an auxiliary
source and may be incomplete for WebView, games, canvas, or custom-rendered UI.

## Safety

Use this harness only on devices and apps where automation is authorized. The
core does not hide ADB, root, accessibility, emulator, or automation signals.
