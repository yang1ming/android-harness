# Examples

Run these scripts through `android-harness exec` so the helper functions are
preloaded into the execution environment.

## Basic Observation

```bash
android-harness exec examples/basic_observe.py
```

This prints device facts, foreground app information, a screenshot path, and a
small UI summary.

## Authorized Device Smoke

```bash
android-harness -s emulator-5554 exec examples/authorized_device_smoke.py
android-harness snapshot --compact
android-harness snapshot --page-info --output /tmp/android-snapshot.json
```

Use this against an authorized emulator or test device when you want a compact
readiness check without app-specific business actions.

## Daemon Transport

```bash
android-harness daemon start
android-harness --transport daemon exec examples/daemon_transport.py
android-harness daemon stop
```

The helper code is the same; only the transport selection changes.

## Environment Report

```bash
android-harness exec examples/environment_report.py
```

This prints non-content metadata for issue triage, including adb selection,
device facts, display facts, foreground app identity, and basic capability
probes. It does not collect logcat, UI text, screenshots, account data, or
app-private content.

## OCR Observation

```bash
android-harness exec examples/ocr_observe.py
```

This optional example uses `plugins/ocr_plugin.py` and the host's Tesseract CLI.
Use it only when collecting visible screen text is appropriate for the
authorized device or emulator under test.

## Clipboard Input

```bash
android-harness exec examples/clipboard_input.py
```

This optional example uses `plugins/clipboard_input_plugin.py` to set clipboard
text and send KEYCODE_PASTE. It is device-dependent and should only be used with
authorized devices and focused fields where paste input is expected.
