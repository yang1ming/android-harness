# Helper Reference

These helpers are preloaded when code runs through `android-harness`, including
stdin execution, `android-harness repl`, and `android-harness exec`.

```bash
android-harness <<'PY'
print(device_info())
print(current_app())
print(page_info())
PY
```

Use these helpers only with devices, apps, and environments where automation is
authorized.

## Device And Transport

- `set_device(serial, transport_name=None)` selects the device and optional
  transport for later helper calls.
- `get_client()` returns the active `AdbClient` for advanced helpers and
  plugins.
- `adb_connect(host, port=5555)` connects to an adb-over-TCP/IP target and
  selects it.
- `adb_disconnect(host=None, port=5555)` disconnects one adb-over-TCP/IP target,
  or all targets when `host` is omitted.
- `adb_tcpip(port=5555)` restarts the selected USB-connected device's adbd in
  TCP/IP mode.

## Observation

- `device_info()` returns serial, model, manufacturer, Android version, SDK,
  screen size, and density.
- `screen_size()` returns `(width, height)` parsed from `wm size`.
- `current_app()` returns foreground package and activity when Android reports
  them.
- `screenshot(path=None)` captures a PNG screenshot and returns the local path.
- `state_snapshot(include_screenshot=False)` returns device info, current app,
  visible texts, and optionally a screenshot path. The CLI `snapshot` command
  can also include `page_info()`, write the JSON payload to a file, and print
  compact single-line JSON with `--compact`.
- `ui_xml()` dumps uiautomator XML and returns it as text.
- `ui_tree()` parses uiautomator XML into `Element` objects.
- `visible_texts()` returns visible text and content descriptions from the UI
  tree.
- `page_info()` returns current app, visible texts, and clickable enabled
  elements with bounds.

## Finding And Tapping UI

- `find_text(text, exact=False)` returns UI elements whose text or content
  description matches.
- `wait_for_text(text, timeout=10, interval=0.5, exact=False)` waits for a
  matching element.
- `tap_element(element)` taps an element's center.
- `tap_text(text, exact=False, timeout=5)` waits for and taps matching text.
- `tap_if_text(text, exact=False)` taps the first current match when present.
- `bounds_center(bounds)` returns the center of a `Bounds` object or compatible
  mapping/object.

## Input And App Control

- `tap(x, y)` taps screen coordinates.
- `long_press(x, y, duration_ms=700)` long-presses screen coordinates.
- `swipe(x1, y1, x2, y2, duration_ms=400)` swipes between coordinates.
- `press_key(key)` sends a key event. Common names include `BACK`, `HOME`,
  `ENTER`, `MENU`, `POWER`, `RECENTS`, and `TAB`.
- `clear_text(max_chars=80)` best-effort clears the focused text field.
- `type_text(text)` types printable ASCII without literal `%` through
  `adb shell input text`; use an input-method plugin for percent signs,
  newlines, complex Unicode, and device-specific shell input failures.
- `launch_app(package, activity=None)` starts an app by package or explicit
  component.
- `force_stop(package)` force-stops an app.
- `open_deeplink(uri)` opens a URI through Android's `VIEW` intent.

## Waiting

- `wait_for_app(package, timeout=10, interval=0.5)` waits for a foreground
  package.
- `wait_for_activity(activity, timeout=10, interval=0.5)` waits for a matching
  foreground activity.
- `wait_for_screen_change(timeout=5, interval=0.5, threshold=0)` waits for
  screenshot bytes to change.
- `wait_until_screen_stable(timeout=5, interval=0.5, stable_count=2)` waits for
  repeated identical screenshots.
- `handle_permission_dialog(allow=True, timeout=3)` taps common allow/deny
  permission buttons when found.

## Files And Logs

- `push_file(local, remote)` pushes a file to the selected device.
- `pull_file(remote, local)` pulls a file from the selected device.
- `logcat_tail(lines=200)` returns recent logcat output.

## Notes

- uiautomator XML can be incomplete for WebView, games, canvas, and custom UI.
  Prefer screenshots as the primary observation source.
- Core helpers do not hide ADB, root, emulator, automation, or debugging
  signals.
- Keep app-specific business flows and account data outside core.
