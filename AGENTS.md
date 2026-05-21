android-harness is a thin layer that connects agents to Android devices through
ADB and optional observation plugins.

# Communication

The primary developer for this project reads Chinese. Agent responses,
documentation notes, plans, reviews, and implementation summaries should be
written in clear Simplified Chinese by default. Keep code identifiers, command
names, API names, file paths, and protocol names in their original English form.

# Code priorities

- Clarity
- Small core
- Stable interfaces
- Explicit boundaries

# Overview

Core code lives in `src/android_harness/`:

- `adb.py` - low-level ADB command wrapper.
- `admin.py` - diagnostics and device readiness checks.
- `helpers.py` - agent-facing Android primitives auto-imported by the CLI.
- `plugins.py` - capability registry for optional extensions.
- `run.py` - the `android-harness` CLI.
- `ui.py` - uiautomator XML parsing and element model.

Agents should edit only inside `agent-workspace/` for task-specific helpers and
skills. Keep reusable Android mechanics in `interaction-skills/`.

# Boundaries

Do not add app-specific business flows, account data, detection evasion, or
platform bypass logic to core. Add authorized test adaptations and environment
reporting as plugins.
