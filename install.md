# Agent Skill Install Guide

[中文](install.zh.md) | English

This guide is written for agents and agent runtimes that need to install and use
Android Harness as a skill.

Android Harness has two parts:

- `SKILL.md`: the agent-facing skill entrypoint.
- `android-harness`: the host-side CLI used by the skill to control authorized
  Android devices through ADB.

Installing only the skill file is not enough. The agent execution environment
must also be able to run the `android-harness` CLI.

## Requirements

- Python 3.10+
- Android platform-tools with `adb` on `PATH`
- An authorized Android device or emulator
- USB debugging enabled and authorized, or an authorized ADB over TCP/IP target

Android Harness is host-side / ADB-first. Do not deploy this repository itself
onto Android devices.

If `adb`, the emulator, USB authorization, ADB-over-TCP, or daemon transport
fails, see [docs/troubleshooting.md](docs/troubleshooting.md).

## Install From A Git Repository

Clone the repository to a stable path:

```bash
git clone <repo-url> /path/to/android-harness
cd /path/to/android-harness
python -m pip install -e .
android-harness doctor
```

If multiple devices are connected, set:

```bash
export ANDROID_SERIAL=<device-id>
```

or pass `-s <device-id>` when running commands:

```bash
android-harness -s emulator-5554 doctor
```

## Install The Agent Skill

The repository root `SKILL.md` is the skill entrypoint.

If the agent reads skills directly from GitHub repositories, point the agent's
skill installer at this repository URL. The installer should use the root
`SKILL.md`.

If the agent reads skills from a local skill directory, install the skill files
there. For Codex-style skill discovery:

```bash
mkdir -p ~/.codex/skills/android-harness
cp /path/to/android-harness/SKILL.md ~/.codex/skills/android-harness/SKILL.md
cp /path/to/android-harness/README.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/README.zh.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/install.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/install.zh.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/NOTICE.md ~/.codex/skills/android-harness/
cp /path/to/android-harness/LICENSE ~/.codex/skills/android-harness/
cp -R /path/to/android-harness/docs ~/.codex/skills/android-harness/
cp -R /path/to/android-harness/interaction-skills ~/.codex/skills/android-harness/
```

The copied skill should still call the CLI installed from the repository path:

```bash
android-harness doctor
```

## Verify Agent Readiness

Run:

```bash
android-harness doctor
```

Then verify the helper environment:

```bash
android-harness <<'PY'
print(device_info())
print(current_app())
print(page_info())
PY
```

A ready agent should use this operating loop:

1. Take a screenshot.
2. Inspect the current app and UI tree when useful.
3. Act with tap, swipe, text input, or key events.
4. Wait for screen, app, or text changes.
5. Capture the result.

## Optional Device-Side Components

Core Android Harness does not require an APK or AccessibilityService.

Some optional plugins may require device-side components. For example,
`plugins/adbkeyboard_plugin.py` interoperates with the external ADBKeyboard IME
for Unicode text input. That IME is not distributed by this repository, and
users are responsible for installing and using it under its own license and
policies.

## Safety Boundary

Use this skill only with devices, apps, and environments where automation is
authorized.

Do not use Android Harness for:

- Unauthorized devices, apps, or accounts.
- Account takeover, CAPTCHA handling, payment flows, bulk registration, or risk
  control bypass.
- Hiding ADB, root, emulator, automation, or debugging signals.
- App-specific business flows in core.
- Account data or private operational data in core.
