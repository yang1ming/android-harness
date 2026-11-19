# Launch And Navigation Recovery

Use this guide when an authorized app does not come forward or reaches an
unexpected screen. These are agent decisions, not an automatic recovery loop
inside `launch_app()`.

## Observe Before Retrying

1. Check `current_app()` and a fresh screenshot. For a broad UI check, prefer
   `android-harness snapshot --page-info --summary`; inspect full UI text only
   when the current app and screen are in scope.
2. Distinguish a device/ADB failure from an app navigation problem. For an
   offline or unauthorized device, follow `docs/troubleshooting.md`; repeatedly
   launching an app will not repair the connection.
3. If a launch is still in progress, use a bounded wait such as
   `wait_for_app(package, timeout=10)`, then inspect again. A timeout or a
   successful launch command alone does not prove which screen is visible.

## Recover With The Least Disruption

- `launch_app(package)` requests the resolved MAIN/LAUNCHER component, with
  Monkey as a fallback only when resolution is unavailable or unusable. It can
  resume an existing task; it does not promise the app's home screen.
- If the target app is already foreground, inspect its actual state. Use a
  visible navigation control or a verified app-specific route rather than
  repeatedly launching it. Follow `targeting.md` for UI selection.
- Before repeating any action, check whether it already succeeded. Do not
  blindly repeat submissions, sends, or other actions with side effects.
- Use `BACK` or `HOME` only when leaving the screen will not discard work.
  Re-observe after each step and set a small retry budget, for example one
  retry after a state-changing recovery step. Stop if the state does not
  improve.
- Use an explicit activity or deep link only when it is known, authorized,
  and recorded for that app. Do not guess internal activities or bypass access
  controls.
- Force-stop/relaunch is a last resort: first establish that interrupting the
  app is acceptable and no unsaved work will be lost. Ask the user if unsure.
  Do not clear app data, log out, reinstall, or change permissions as generic
  recovery steps.
- Stop and ask for help on login, permission, CAPTCHA, payment, or other
  sensitive/unexpected screens instead of inventing a bypass.

## Record Only Reusable Knowledge

Put verified package-specific routes, screen cues, safe retry limits, and
stop conditions in `agent-workspace/app-skills/<package>/`. In the source
checkout, `agent-workspace/app-skills/README.md` describes the note format.
Keep temporary task code in `agent-workspace/agent_helpers.py`.

Record the app/version and what was actually tested. Do not store credentials,
account data, private UI content, screenshots, or device logs in the repository.
Keep failures explicit; do not turn these notes into a new core recovery API.
