# Roadmap

This roadmap tracks near-term maintenance work. It is not a commitment to add
large features to core; Android Harness should remain a small host-side Android
automation layer.

## Near Term

- Keep the CLI and helper API stable for common ADB-backed workflows.
- Add focused tests for diagnostics, UI parsing, plugin registration, and CLI
  execution behavior.
- Improve installation and troubleshooting documentation for agent runtimes.
- Document safe plugin patterns for optional device-side components.
- Add examples for authorized emulator and test-device workflows.

## Plugin Candidates

- OCR observation plugin.
- Environment reporting plugin.
- Input method adapter improvements.
- Policy guard plugin for local safety checks.

## CI And Release Work

- Add GitHub Actions for lint-free test execution.
- Publish a `v0.1.0` release with changelog notes.
- Add issue templates for bug reports, feature proposals, and safety boundary
  reports.
- Keep `NOTICE.md` current when third-party code, documentation, models,
  datasets, or device-side components are introduced.

## Non-Goals

- Do not move app-specific business flows into core.
- Do not add account automation, payment automation, CAPTCHA handling, or risk
  control bypass workflows.
- Do not hide ADB, root, emulator, automation, or debugging signals.
