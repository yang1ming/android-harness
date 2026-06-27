# Android Harness

[中文](README.zh.md) | English

![CI](https://github.com/yang1ming/android-harness/actions/workflows/ci.yml/badge.svg?branch=main)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Status](https://img.shields.io/badge/status-alpha-orange)
![License](https://img.shields.io/badge/license-MIT-green)
![Android](https://img.shields.io/badge/android-ADB--first-3DDC84)

**A small host-side Android automation layer for agents, built on ADB and
optional plugins.**

Android Harness is a lightweight, extensible Android device control layer that
agents can use and improve incrementally. It exposes stable primitives for
authorized real devices and emulators: ADB, screenshots, input events,
uiautomator XML, logs, and files.

It is an independent Android-focused project inspired by the architecture of
Browser Harness. It is not affiliated with Browser Use, and it is not an
official Android version of Browser Harness.

Status: Alpha. The core API aims to stay small and stable, while plugins, skill
conventions, and CLI ergonomics may still evolve.

## Capabilities

| Area | What Android Harness provides |
| --- | --- |
| ADB control | Direct subprocess-backed `adb` by default, with optional local daemon transport. |
| Observation | Screenshots, uiautomator XML, device facts, screen facts, app facts, logs, and files. |
| Interaction | Tap, swipe, keyevent, text input, waits, and Python helper execution through the CLI. |
| Agent workflow | Local workspace helpers, reusable interaction skills, examples, and smoke-test docs. |
| Extension points | Optional plugins for input methods, OCR, environment reporting, and policy checks. |
| Boundaries | Authorized devices only; no account takeover, CAPTCHA, payment, bypass, or signal-hiding flows. |

## Demo

Watch the Android Harness skill demo preview below.

This demo shows execution without a self-summary or reusable task memory. For
repeated tasks, capturing a short summary as an interaction skill or workspace
note should make later runs faster and more consistent.

![Android Harness skill demo preview](docs/assets/demo-preview.gif)

## Documentation

| Resource | Purpose |
| --- | --- |
| [install.md](install.md) | CLI and Agent Skill installation. |
| [docs/troubleshooting.md](docs/troubleshooting.md) | Linux, ADB, emulator, ADB-over-TCP, and daemon failure checks. |
| [examples/](examples/) | Runnable examples for observation, daemon transport, and authorized device smoke checks. |
| [docs/helpers-reference.md](docs/helpers-reference.md) | Agent-facing helper API reference. |
| [docs/plugin-author-guide.md](docs/plugin-author-guide.md) | Plugin boundaries and extension patterns. |
| [docs/manual-smoke.md](docs/manual-smoke.md) | Manual checks for authorized devices and emulators. |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution process and expectations. |
| [ROADMAP.md](ROADMAP.md) | Current maintenance direction. |
| [CHANGELOG.md](CHANGELOG.md) | User-facing change history. |

Local checks:

```bash
make check
```

## Positioning

- The core stays small and stable, exposing Android automation primitives.
- It runs on the developer or agent host and controls devices through `adb`.
- It is not an Android APK, AccessibilityService, or persistent on-device agent.
- Task-specific helpers live in `agent-workspace/agent_helpers.py`.
- Reusable app knowledge lives in `agent-workspace/app-skills/`.
- Reusable interaction knowledge lives in `interaction-skills/`.
- OCR, human-like interaction, environment reporting, input method adapters, and
  policy checks belong in plugins.

## ADB Or On-Device Deployment?

Android Harness is **ADB-first / host-side** by default:

```text
agent or developer machine
  -> android-harness
  -> adb
  -> authorized Android device or emulator
```

This means:

- Install and run it on your local machine, CI runner, remote development host,
  or agent execution environment.
- The Android device only needs authorized USB debugging, or an authorized ADB
  over TCP/IP connection.
- The core does not install APKs, inject into apps, or enable AccessibilityService.
- The core does not hide ADB, root, emulator, automation, or debugging signals.
- Device-side components must be explicit plugin dependencies. For example,
  `plugins/adbkeyboard_plugin.py` depends on the external ADBKeyboard IME.

Do not deploy Android Harness itself directly onto Android devices. If an
on-device agent is needed in the future, it should be a separate project or a
clearly isolated plugin with its own permission, update, audit, and safety model.

## Optional ADB Daemon Transport

Android Harness uses direct subprocess-backed `adb` calls by default. For long
agent sessions, an optional local daemon can proxy adb commands over a Unix
socket:

```bash
android-harness daemon start
android-harness --transport daemon doctor
android-harness daemon status
android-harness daemon stop
```

The daemon is opt-in. If `--transport daemon` or
`ANDROID_HARNESS_TRANSPORT=daemon` is not set, behavior remains subprocess-first.
The daemon listens only on a local Unix socket and does not hide ADB, root,
emulator, automation, or debugging signals.

## Quick Start

For full CLI and Agent Skill installation instructions, see
[install.md](install.md). A Chinese version is available at
[install.zh.md](install.zh.md).

Runnable examples are available in [examples/](examples/).

Connect an Android device or emulator with authorized USB debugging, then run:

```bash
android-harness doctor
```

Print a machine-readable state snapshot:

```bash
android-harness snapshot
android-harness snapshot --screenshot
android-harness snapshot --compact
android-harness snapshot --redact-text
android-harness snapshot --page-info --output /tmp/android-snapshot.json
```

Snapshot output includes a `schema_version` field so agents and CI jobs can
parse it safely as the observation format evolves. Use `--compact` when a
single-line JSON record is easier to consume in logs or pipelines. Use
`--redact-text` when logs should keep structure and counts without visible UI
text or content descriptions.

Optional OCR lives in the plugin layer and uses the host's Tesseract CLI when
available:

```bash
android-harness exec examples/ocr_observe.py
```

Run helper code through a heredoc:

```bash
android-harness <<'PY'
print(device_info())
print(current_app())
path = screenshot()
print(path)
PY
```

Disable local workspace helpers:

```bash
android-harness --no-workspace <<'PY'
print(page_info())
PY
```

## Unicode Text Input

The core `type_text()` helper uses `adb shell input text` and is only intended
for simple printable ASCII without literal `%`. For Chinese, emoji, percent
signs, newlines, symbols, or vendor ROMs with broken shell input behavior, use
an input-method plugin.

After installing and enabling ADBKeyboard, use the optional plugin:

```bash
android-harness <<'PY'
type_unicode("你好 ☂️ 17°C 湿度 100%")
clear_input()
PY
```

The plugin lives at `plugins/adbkeyboard_plugin.py`. It sends text through
`ADB_INPUT_B64`, switches to ADBKeyboard for the operation, and restores the
previous input method by default. For several input operations in one block,
use `adbkeyboard_active()` to switch once and restore when the block exits.

## Architecture

```text
src/android_harness/
  run.py       # CLI and Python execution environment
  helpers.py   # public agent-facing primitives
  adb.py       # ADB backend
  ui.py        # uiautomator XML parsing
  plugins.py   # plugin registry and boundaries
  admin.py     # diagnostics

agent-workspace/
  agent_helpers.py
  app-skills/

plugins/
  adbkeyboard_plugin.py

interaction-skills/
  permissions.md
  scrolling.md
  text-input.md
```

## Usage Boundaries

Appropriate use cases:

- Owned devices, test devices, emulators, and authorized remote devices.
- App QA, automation testing, UI issue reproduction, screenshots, and diagnostics.
- Agent-driven Android operation in authorized environments.
- Capturing reusable Android interaction knowledge as skills.

Out of scope or not accepted:

- Unauthorized devices, unauthorized apps, or third-party account environments.
- Account takeover, CAPTCHA handling, payment flows, bulk registration, or risk
  control bypass.
- Hiding ADB, root, emulator, automation, or debugging signals.
- Adding app-specific business flows, account data, or private operational logic
  to the core.
- Presenting Android Harness as an official Android version of Browser Harness.

## Core, Plugin, And Skill Boundaries

Put in core:

- ADB wrapper, device facts, screen facts, input events, files, logs, waits, and
  diagnostics.
- Stable primitives that do not depend on a specific app, account, model, or
  external service.

Put in plugins:

- OCR, input-method adapters, human-like tapping, environment reporting, and
  policy guards.
- Capabilities that require an extra APK, service, model, network access, or
  heavier dependency.

Put in `interaction-skills/`:

- Reusable Android interaction techniques, such as permissions, scrolling, and
  text input.
- Markdown instructions for agent operating strategy and caveats.

Put in `agent-workspace/`:

- Temporary helpers for the current task.
- App-specific observations and authorized testing knowledge.

Do not put in core:

- App-specific business flows.
- Account data.
- Detection evasion.
- Platform bypass logic.

## Responsible Disclosure

If you discover a security issue or a boundary issue that could enable misuse,
please report it through a private channel first. If the GitHub repository has
Security Advisories enabled, use a Security Advisory. Otherwise, open a public
issue with a non-sensitive summary and request private coordination.

Useful reports include:

- Affected version or commit.
- Host OS, Android version, device type, and ADB connection mode.
- Minimal reproduction steps.
- Impact and expected boundary.
- Logs that do not contain real accounts, tokens, payment information, personal
  data, or third-party private data.

Please do not publicly post:

- Steps that directly enable unauthorized device or account operation.
- Detection bypass, platform bypass, or automation-hiding details.
- Real device, account, token, SMS, CAPTCHA, payment, or personal data.

## License And Attribution

This project is licensed under the MIT License. MIT is a short permissive open
source license that allows commercial use, distribution, modification, and
private use, while requiring preservation of copyright and license notices.

This project is independently implemented and inspired by the architecture of
Browser Harness. It is not affiliated with Browser Use and is not an official
Android version of Browser Harness. Unless explicitly stated in `NOTICE.md`,
this repository does not include source code, documentation, or assets copied
from Browser Harness or other third-party projects.

If third-party code, documentation, models, datasets, or device-side components
are introduced in the future, their license compatibility must be reviewed
before merge, and upstream copyright, license, and attribution notices must be
preserved in `NOTICE.md` or the relevant files.

See `NOTICE.md` for attribution and third-party notices.

## License

MIT License. See `LICENSE`.
