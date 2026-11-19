# App-Specific Notes

Store verified knowledge for an authorized app under its package name, for
example `com.example.app/recovery.md`. These notes supplement
`interaction-skills/recovery.md`; they are not imported or executed by core.
Create an app directory only after observing that app, not from guessed routes.
Package directories remain ignored by Git by default; only this generic guide
is tracked. Review and sanitize any app notes before intentionally sharing them.

Keep each note short:

- Scope: package, tested app version, Android version, and test date.
- Expected entry: observed launcher behavior and recognizable screen cues.
- Recovery: safe navigation steps, preconditions, and a small retry limit.
- Verification: how to tell that the intended screen was reached.
- Stop conditions: unsaved work, account boundaries, unexpected dialogs, or
  unchanged state after the retry budget.

Document an explicit activity or deep link only after verifying that it is an
authorized, stable entry point. Mark observations that may depend on app
version, login state, or navigation history instead of treating them as rules.
Do not assume a launch always resets navigation or opens the home screen.

Keep task-specific Python helpers in `agent-workspace/agent_helpers.py`.
Do not commit account identifiers, credentials, private UI text, screenshots,
logs, or operational notes containing user data. App-specific flows and retry
policy do not belong in `src/android_harness/`.
