# Contributing

Thank you for considering a contribution to Android Harness.

Android Harness is intentionally small. Contributions should preserve clear
boundaries between reusable Android mechanics, optional plugins, and
task-specific agent workspaces.

## Good Contributions

- Fix bugs in ADB command handling, diagnostics, UI parsing, or CLI behavior.
- Improve tests for existing helpers and plugin boundaries.
- Improve documentation, installation notes, and safe usage examples.
- Add reusable interaction knowledge under `interaction-skills/`.
- Add optional plugins when they are explicitly scoped and documented.

## Out Of Scope

Please do not contribute:

- App-specific business flows in core.
- Account data, credentials, private operational notes, or real user data.
- Detection evasion, platform bypass, or automation-hiding logic.
- Unauthorized device, account, payment, CAPTCHA, or bulk-registration workflows.

## Development Setup

Install the project in editable mode with development dependencies:

```bash
python3 -m pip install -e ".[dev]"
```

Run the local checks:

```bash
make check
```

If `make` is unavailable, run the commands directly:

```bash
python3 -m pytest
python3 -m compileall src tests plugins agent-workspace
```

## Pull Request Checklist

- Keep the change focused on one behavior or documentation topic.
- Add or update tests for behavior changes.
- Keep reusable Android mechanics in `src/android_harness/`.
- Keep optional integrations in `plugins/`.
- Keep task-specific helpers in `agent-workspace/`.
- Update `README.md`, `README.zh.md`, or `install.md` when user-facing behavior changes.
