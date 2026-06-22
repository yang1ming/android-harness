# Changelog

All notable changes to Android Harness are tracked here.

## Unreleased

### Added

- `android-harness snapshot --page-info` to include clickable element metadata.
- `android-harness snapshot --output PATH` to write JSON snapshots to files.
- Stable `schema_version` marker for `android-harness snapshot` output.
- `android-harness snapshot` for machine-readable device, foreground app, and
  visible text observation from the CLI.
- Environment report plugin and example for authorized test-device issue
  triage without collecting logcat, UI text, screenshots, or account data.
- Troubleshooting guides for Linux, ADB, emulators, ADB-over-TCP, and daemon
  transport.

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
