# Text Input

Prefer `type_text()` for simple printable ASCII text without literal `%`. For
complex Unicode text, percent signs, newlines, or apps that reject shell input
escaping, add an input-method plugin rather than changing core.

## ADB shell input limits

`type_text()` uses Android's built-in `adb shell input text` path. It is useful
for short ASCII strings, but it is not a reliable Unicode transport. Some vendor
ROMs, including MIUI builds observed on Android 11, can corrupt even simple
English input or ignore `%s` space escaping.

Use `type_text()` only when all of these are true:

- The text is printable ASCII and does not contain a literal `%`.
- The target device has already been checked with a real input field.
- Corruption would not cause account, payment, or destructive actions.

## ADBKeyboard plugin

For Chinese, emoji, symbols, newlines, percent signs, and vendor ROMs with broken
`input text`, use `plugins/adbkeyboard_plugin.py`.

The plugin assumes the external ADBKeyboard IME is installed on the device:

```bash
adb shell ime enable com.android.adbkeyboard/.AdbIME
```

From `android-harness`, the default `agent-workspace/agent_helpers.py` attempts
to expose these helpers when the plugin is importable:

```python
type_unicode("你好 ☂️ 17°C 湿度 100%")
clear_input()
send_keyevent(66)
```

The plugin always transports text with `ADB_INPUT_B64`, not `ADB_INPUT_TEXT`.
This avoids shell quoting and Unicode truncation problems:

```bash
adb shell am broadcast -a ADB_INPUT_B64 --es msg "<base64>"
```

The plugin switches to ADBKeyboard, sends the input, and restores the previous
IME by default. If a task intentionally wants to keep ADBKeyboard active for a
batch of operations, pass `restore=False` and restore the previous IME explicitly.
