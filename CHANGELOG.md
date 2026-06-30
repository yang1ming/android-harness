# Changelog

All notable changes to Android Harness are tracked here.

## Unreleased

### Added

- `android-harness doctor --compact` and `--output PATH` for machine-readable
  diagnostic artifacts.
- GitHub Actions `Release Build` workflow and release checklist documentation
  for repeatable package artifacts.
- `android-harness smoke` for structured release and issue-triage smoke
  reports.
- Public JSON schema fixtures for snapshot summary and smoke report outputs.
- Optional `plugins/clipboard_input_plugin.py` for device-dependent clipboard
  text input through Android's clipboard service and KEYCODE_PASTE.
- `android-harness snapshot --summary` for count-based CI and agent log output.
- Optional `plugins/ocr_plugin.py` for host-side Tesseract OCR observation.
- `android-harness snapshot --redact-text` to keep snapshot structure and counts
  while removing visible UI text and content descriptions from logs.
- Explicit `helpers.__all__` public surface for agent wildcard imports and CLI
  execution environments.
- `android-harness snapshot --compact` for single-line JSON output in agent
  pipelines and CI logs.
- `adbkeyboard_active()` context manager in the ADBKeyboard plugin for reusable
  IME switching with automatic restoration.
- Focused plugin registry behavior tests for sorting, replacement, and
  instance isolation.
- Authorized device smoke example for real devices and emulators.
- Local policy guard plugin for advisory project-boundary checks.
- UI XML parsing edge-case coverage and clearer bounds validation.
- `android-harness snapshot --page-info` to include clickable element metadata.
- `android-harness snapshot --output PATH` to write JSON snapshots to files.
- Stable `schema_version` marker for `android-harness snapshot` output.
- `android-harness snapshot` for machine-readable device, foreground app, and
  visible text observation from the CLI.
- Environment report plugin and example for authorized test-device issue
  triage without collecting logcat, UI text, screenshots, or account data.
- Troubleshooting guides for Linux, ADB, emulators, ADB-over-TCP, and daemon
  transport.

### Fixed

- `android-harness smoke` now explains skipped screenshot and uiautomator
  probes when no selected device is ready.
- `type_text()` now rejects literal `%`, Unicode, and control characters instead
  of sending text that `adb shell input text` may silently mangle.

## 0.1.0 - 2026-06-13

Initial alpha release for host-side, ADB-first Android device interaction.

### Added

- Core `android-harness` CLI with `doctor`, `repl`, `exec`, and stdin execution.
- Agent-facing helpers for device facts, screenshots, UI XML parsing, input
  events, app launching, file transfer, logcat, waiting, and permission dialogs.
- Optional ADB daemon transport over a local Unix socket.
- Plugin registry and ADBKeyboard Unicode input plugin example.
- Interaction skill notes for text input, scrolling, and permissions.
- Installation guides in English and Simplified Chinese.
- Contribution guide, roadmap, issue templates, PR template, and GitHub Actions CI.
- README demo GIF preview.

### Boundaries

- Core remains host-side and ADB-first.
- Core does not install APKs, inject into apps, enable AccessibilityService, or
  hide ADB/root/emulator/automation/debugging signals.
- App-specific business flows, account data, detection evasion, and platform
  bypass logic are out of scope for core.
