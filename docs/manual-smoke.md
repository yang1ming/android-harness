# Manual Smoke Test

Use this checklist before releases and after changes that affect ADB, helpers,
the CLI, daemon transport, or device-facing behavior.

Run only on devices, emulators, apps, and accounts where automation is
authorized.

## Preconditions

- Python 3.10+
- Android platform-tools with `adb` on `PATH`
- One authorized Android device or emulator
- Repository installed in editable mode:

```bash
python3 -m pip install -e ".[dev]"
```

If more than one device is connected, set `ANDROID_SERIAL` or pass `-s`.

## Local Checks

```bash
make check
```

Expected result:

- pytest passes.
- compileall passes.

## Executable Smoke Summary

```bash
android-harness smoke
android-harness smoke --compact --output /tmp/android-harness-smoke.json
android-harness smoke --summary --output /tmp/android-harness-smoke-summary.json
android-harness smoke --redact-device --output /tmp/android-harness-smoke-redacted.json
android-harness smoke --redact-paths --output /tmp/android-harness-smoke-paths-redacted.json
android-harness smoke --redact-all --output /tmp/android-harness-smoke-safe.json
```

Expected result:

- The command prints a JSON report with `schema_version`,
  `ok`, `checks`, `doctor`, and `daemon`.
- The exit code is `0` only when adb, the selected device, screenshot capture,
  and uiautomator probing are available.
- The report can be attached to issues after removing any environment-specific
  paths or device identifiers that should stay private.
- Use `--summary` when the report should only include check counts, failed check
  names, and high-level daemon/doctor status.
- Use `--redact-device` when the report should preserve check results but hide
  selected device serials.
- Use `--redact-paths` when the report should hide local daemon socket paths.
- Use `--redact-all` for issue attachments that should hide both device
  identifiers and local paths.

## Device Readiness

```bash
adb devices
android-harness doctor
```

Expected result:

- Exactly one selected device is ready, or `-s`/`ANDROID_SERIAL` selects one.
- `device_ready` is `true`.
- screenshot and uiautomator probes are available when supported by the device.

## Basic Observation

```bash
android-harness exec examples/basic_observe.py
```

Expected result:

- Device facts print successfully.
- Current foreground app is reported.
- A screenshot path is printed.
- Visible text and clickable counts are printed.

## Basic Interaction

```bash
android-harness <<'PY'
press_key("HOME")
wait_until_screen_stable(timeout=5)
print(current_app())
print(screenshot())
PY
```

Expected result:

- The device returns to the launcher or home surface.
- The screen reaches a stable state.
- A screenshot is captured.

## Package Launch

Use an authorized test app with no unsaved work. Replace `com.example.app` with
its verified package:

```bash
android-harness <<'PY'
package = "com.example.app"
launch_app(package)
print(wait_for_app(package, timeout=10))
print(screenshot())
PY
```

Check both an app with no running task and an app resumed from the background
after visiting a nested screen. If available, include an app with a launcher
activity alias. Confirm the foreground package and inspect the resulting screen;
do not assume a launcher request always returns to the app's home screen.

Also verify a known explicit activity still opens as before. Resolver fallback,
invalid output, and command-error cases are covered by unit tests; do not alter
device permissions or app data just to trigger them. If navigation is unexpected,
follow `interaction-skills/recovery.md` rather than adding retries to core.

## Optional Daemon Transport

```bash
android-harness daemon start
android-harness daemon status
android-harness --transport daemon doctor
android-harness --transport daemon exec examples/daemon_transport.py
android-harness daemon stop
```

Expected result:

- Daemon reports `running` after start.
- `--transport daemon doctor` reaches the same selected device behavior as the
  default subprocess transport.
- The daemon example captures a screenshot.
- Daemon reports `not running` after stop.

## Safety Boundary

Do not include these in smoke tests:

- Third-party private accounts.
- CAPTCHA, payment, bulk registration, or risk-control bypass flows.
- Detection evasion or automation-hiding behavior.
- Real tokens, SMS, personal data, private messages, or payment information.
