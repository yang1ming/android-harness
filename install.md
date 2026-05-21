# Install

## Prerequisites

- Python 3.10+
- Android platform-tools with `adb` on `PATH`
- A connected device or emulator with USB debugging authorized

## Local Install

```bash
python -m pip install -e .
android-harness doctor
```

If multiple devices are connected, set:

```bash
export ANDROID_SERIAL=<device-id>
```

or pass `-s <device-id>`:

```bash
android-harness -s emulator-5554 doctor
```
