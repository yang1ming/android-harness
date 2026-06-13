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
