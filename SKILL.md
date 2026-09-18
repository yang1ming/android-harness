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
android-harness snapshot --page-info --summary
```

This count-only snapshot is the preferred broad first pass. Use
`android-harness snapshot --page-info --redact-text` when resource IDs, classes,
and bounds are needed without visible text, or `--redact-all` when the artifact
will be shared. Print the full `page_info()` only after confirming the foreground
app and screen are in scope and the complete visible text and content descriptions
are needed locally; they can include unrelated account or search-history text and
consume substantial context.

Helpers are pre-imported for scripts. Prefer this loop:

1. Take a screenshot.
2. Inspect current app and UI tree if needed.
3. Act with tap, swipe, type, or key events.
4. Wait for screen/app/text change.
5. Capture the result.

Screenshots are the primary observation source. `uiautomator` XML is an auxiliary
source and may be incomplete for WebView, games, canvas, or custom-rendered UI.

Target controls in this order: text or content description, resource ID and
bounds, screenshot inspection, stable coordinates, then optional host-side OCR.
See `interaction-skills/targeting.md` for the compact fallback pattern.

## Safety

Use this harness only on devices and apps where automation is authorized. The
core does not hide ADB, root, accessibility, emulator, or automation signals.
