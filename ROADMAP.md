# Roadmap

This roadmap tracks public maintenance direction for Android Harness. It is not
a promise to add large features to core; the project should remain a small,
host-side, ADB-first Android automation layer.

## Completed

- Public README demo GIF preview.
- GitHub Actions CI for Python 3.10, 3.11, and 3.12.
- Issue templates for bug reports, feature proposals, and safety boundary
  reports.
- Pull request template with check and boundary reminders.
- `CHANGELOG.md` with initial `0.1.0` notes.
- Runnable examples for basic observation and daemon transport.
- Manual smoke test checklist for authorized devices and emulators.
- Helper reference documentation.
- Plugin author guide.
- Linux, ADB, emulator, ADB-over-TCP, and daemon troubleshooting guides.
- Optional local ADB daemon transport.
- Daemon lifecycle tests, stale socket handling, and startup diagnostics.
- ADBKeyboard Unicode input plugin example.
- Environment reporting plugin for authorized test devices.
- Machine-readable `android-harness snapshot` CLI command.
- Structured observation schema versioning.
- Snapshot page-info and JSON file output options.
- Snapshot compact JSON output option.
- UI XML bounds validation and edge-case tests.
- Local policy guard plugin for misuse boundary checks.
- Focused plugin registry usage tests.
- Authorized emulator and test-device smoke examples.
- ADBKeyboard context manager for reusable IME switching.
- Redacted snapshot output for safer CI and agent logs.
- Optional host-side Tesseract OCR observation plugin.
- Snapshot summary output for count-based CI and agent logs.
- Optional clipboard input plugin as an additional input adapter.
- Release build workflow and release checklist documentation.
- Executable JSON smoke runner for release and issue triage.
- Public JSON schema compatibility fixtures for snapshot and smoke outputs.
- Doctor compact and file JSON output options.
- Smoke report device identifier redaction for safer issue triage.
- Doctor JSON schema marker and compatibility fixture.
- Doctor report device identifier redaction for safer issue triage.
- Snapshot device identifier redaction for safer issue triage.
- Version command with JSON output for release and issue triage.
- Version JSON schema compatibility fixture.
- Version file output option for release and issue triage artifacts.
- Daemon status JSON output for release and issue triage artifacts.
- Snapshot local path redaction for safer issue triage artifacts.
- Daemon status path redaction for safer issue triage artifacts.
- Helper device switching preserves the selected ADB transport.
- Smoke report path redaction for safer issue triage artifacts.
- Snapshot share-safe redaction preset for issue triage artifacts.

## Next

- Keep the CLI and helper API stable for common ADB-backed workflows.
- Improve machine-readable observation output for agent and CI use cases.

## Later

- Additional device-specific input adapters beyond the current examples.
- More reusable interaction skills for common Android patterns.

## Release Work

- Publish a `v0.1.0` GitHub Release and tag after `CI` and `Release Build`
  pass.
- Keep `CHANGELOG.md` current for every user-facing change.
- Keep `NOTICE.md` current when third-party code, documentation, models,
  datasets, or device-side components are introduced.
- Consider packaging and publishing only after install, smoke-test, and release
  workflows are stable.

## Non-Goals

- Do not move app-specific business flows into core.
- Do not add account automation, payment automation, CAPTCHA handling, or risk
  control bypass workflows.
- Do not hide ADB, root, emulator, automation, or debugging signals.
- Do not turn core into an APK, AccessibilityService, or persistent on-device
  agent.
