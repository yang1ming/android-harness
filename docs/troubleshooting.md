# Troubleshooting

This guide covers common Linux, ADB, emulator, ADB-over-TCP, and daemon
transport failures for Android Harness.

Android Harness is host-side and ADB-first. It does not bypass Android security
prompts, account checks, app protections, emulator detection, root detection, or
automation/debugging signals.

## Fast Triage

Start with these commands on the same host where the agent or CLI runs:

```bash
which adb
adb version
adb devices -l
android-harness doctor
```

If daemon transport is enabled:

```bash
android-harness daemon status
android-harness --transport daemon doctor
```

When reporting an issue, include the redacted output of these commands, plus
host OS, Python version, Android version, connection mode, and device or
emulator model.

## ADB Is Missing Or The Wrong Version

Symptoms:

- `adb not found on PATH`
- `android-harness doctor` fails before selecting a device
- `adb version` is not the version you expected

Checks:

```bash
which adb
adb version
python -m pip show android-harness
```

Fixes:

- Install Android SDK Platform Tools or your distro package, such as
  `android-tools-adb`.
- Ensure the intended `adb` directory is earlier in `PATH` than older copies.
- Restart shells, terminals, services, or agent runtimes after changing `PATH`.
- Run `adb kill-server` and `adb start-server` after replacing `adb`.

## No Device Appears

Symptoms:

- `adb devices -l` shows only the header
- `android-harness doctor` reports no ready device

Checks:

```bash
adb kill-server
adb start-server
adb devices -l
```

Fixes:

- For physical devices, enable Developer options and USB debugging.
- Reconnect the cable and choose a data-capable USB mode if the device asks.
- Prefer a direct USB port over hubs while debugging connection issues.
- For emulators, confirm the emulator is fully booted before running doctor.
- If multiple agent runtimes exist, run these commands in the same runtime that
  will run `android-harness`.

## Device Is Unauthorized

Symptoms:

- `adb devices -l` shows `unauthorized`
- `android-harness doctor` cannot read device facts

Fixes:

- Unlock the Android device.
- Accept the USB debugging RSA prompt on the device.
- If the prompt does not appear, revoke USB debugging authorizations in Android
  Developer options, then reconnect and run `adb devices -l` again.
- Restart the ADB server:

```bash
adb kill-server
adb start-server
adb devices -l
```

Android Harness cannot skip this authorization step.

## Device Is Offline Or Flaky

Symptoms:

- `adb devices -l` shows `offline`
- commands intermittently time out
- screenshots or UI dumps sometimes fail

Fixes:

- Reconnect USB and wait a few seconds.
- Restart the ADB server.
- Reboot the emulator or physical device if it stays offline.
- Avoid switching USB modes during a run.
- If using ADB-over-TCP, reconnect from the host:

```bash
adb disconnect
adb connect <device-ip>:5555
```

## Linux USB Permission Errors

Symptoms:

- `adb devices -l` shows `no permissions`
- A physical device works as root but not as the agent user

Checks:

```bash
id
lsusb
adb devices -l
```

Fixes:

- Install distro or vendor udev rules for Android devices.
- Add the agent user to the relevant device-access group used by your distro,
  commonly `plugdev` or `adbusers`.
- Log out and back in after group changes.
- Reconnect the device and restart the ADB server.

Avoid running long-lived agent sessions as root just to work around USB
permissions. Fixing udev and group access is easier to audit.

## Multiple Devices Are Connected

Symptoms:

- `adb` reports `more than one device/emulator`
- `android-harness doctor` selects a different target than expected

Fixes:

Use one of these:

```bash
export ANDROID_SERIAL=<device-id>
android-harness doctor
```

```bash
android-harness -s <device-id> doctor
```

Use the same serial for scripts, examples, smoke tests, and agent runs.

## Emulator Does Not Appear

Symptoms:

- The Android Emulator is open but absent from `adb devices -l`
- `emulator-5554` is offline
- emulator boot is slow or fails on Linux

Checks:

```bash
adb devices -l
adb shell getprop sys.boot_completed
ls -l /dev/kvm
```

Fixes:

- Wait until the emulator finishes booting and `sys.boot_completed` returns `1`.
- Install Android Emulator, Android SDK Platform Tools, and at least one system
  image through Android Studio or SDK tools.
- On Linux, confirm the user can access `/dev/kvm` for hardware acceleration.
- In nested virtualization, VM, container, or WSL environments, verify that KVM
  or an equivalent emulator acceleration path is available.
- If the emulator remains offline, restart ADB and restart the emulator.

## ADB-Over-TCP Cannot Connect

Symptoms:

- `adb connect <ip>:5555` fails
- `android-harness -s <ip>:5555 doctor` cannot reach the device

Checks:

```bash
adb devices -l
adb tcpip 5555
adb connect <device-ip>:5555
adb devices -l
```

Fixes:

- Authorize the device over USB before switching to TCP/IP.
- Ensure host and device are on a reachable network.
- Use the full serial, including port, such as `<device-ip>:5555`.
- Disable TCP/IP mode when finished if the test environment does not require it:

```bash
adb disconnect <device-ip>:5555
```

Do not expose ADB-over-TCP on untrusted networks.

## Daemon Transport Fails

Symptoms:

- `android-harness --transport daemon doctor` reports the daemon is unavailable
- `android-harness daemon status` reports `stale socket`
- daemon startup fails with a log path

Checks:

```bash
android-harness daemon status
android-harness daemon stop
android-harness daemon start
android-harness --transport daemon doctor
```

Notes:

- The daemon is optional. Default subprocess transport should still work without
  daemon:

```bash
android-harness --transport subprocess doctor
```

- The default socket path is `${XDG_RUNTIME_DIR}/android-harness/daemon.sock`.
  If `XDG_RUNTIME_DIR` is missing or unusable, the fallback is
  `/tmp/android-harness-${uid}/daemon.sock`.
- Startup diagnostics write to a log next to the socket, for example
  `daemon.sock.log`.
- A stale socket means a socket path exists but no healthy daemon responded.
  `daemon stop` removes stale sockets, and `daemon start` removes stale sockets
  before launching a new daemon.

## Screenshots Or UI Dumps Fail

Symptoms:

- screenshot files are empty or missing
- `uiautomator` output is empty or malformed
- `page_info()` cannot parse the current screen

Fixes:

- Confirm the device is unlocked and awake.
- Run `android-harness doctor` first.
- Try a plain screenshot:

```bash
adb exec-out screencap -p > /tmp/android-screen.png
```

- Some secure screens intentionally block screenshots or UI inspection. Android
  Harness does not bypass those platform or app restrictions.

## Unicode Text Input Fails

Symptoms:

- Chinese, emoji, or symbols are garbled
- `adb shell input text` cannot enter the intended text

Fix:

- Use an input-method plugin such as `plugins/adbkeyboard_plugin.py`.
- Keep the core `type_text()` helper for simple ASCII text only.

## Before Opening An Issue

Include:

- `android-harness doctor` output
- `adb devices -l`
- `adb version`
- Host OS and Python version
- Android version, device model, emulator name, and connection mode
- Whether daemon transport was enabled
- Redacted logs without real accounts, tokens, payment data, SMS, CAPTCHA, or
  personal data
