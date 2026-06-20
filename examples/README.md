# Examples

Run these scripts through `android-harness exec` so the helper functions are
preloaded into the execution environment.

## Basic Observation

```bash
android-harness exec examples/basic_observe.py
```

This prints device facts, foreground app information, a screenshot path, and a
small UI summary.

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
