# Release Guide

This guide keeps Android Harness releases small, repeatable, and auditable.

## Release Checklist

1. Confirm the working tree is clean:

   ```bash
   git status --short
   ```

2. Run local checks:

   ```bash
   make check PYTHON=.venv/bin/python
   ```

3. Build the package locally:

   ```bash
   .venv/bin/python -m build --outdir /tmp/android-harness-dist
   ```

4. Confirm `CHANGELOG.md` has the user-facing changes for the release.

5. Confirm `ROADMAP.md` reflects completed and remaining public work.

6. Create and push a version tag:

   ```bash
   git tag v0.1.0
   git push github v0.1.0
   ```

7. Wait for the `CI` and `Release Build` GitHub Actions workflows to pass.

8. Create a GitHub Release from the tag and attach the `android-harness-dist`
   artifact from the `Release Build` workflow.

9. Run the manual smoke checklist on an authorized device or emulator:

   ```bash
   android-harness doctor
   android-harness exec examples/basic_observe.py
   ```

## Release Boundaries

- Release artifacts should contain only the host-side Python package and docs.
- Do not bundle Android APKs, keystores, account data, screenshots, or device
  logs.
- Optional device-side dependencies, such as ADBKeyboard, must stay external and
  documented as separate user-managed components.
- Release notes must not claim stealth, evasion, account automation, payment
  automation, CAPTCHA handling, or risk-control bypass support.
