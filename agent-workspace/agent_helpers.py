"""Task-specific helpers for Android Harness.

Agents may edit this file during task execution. Keep general-purpose primitives
in `src/android_harness/`; keep app-specific discoveries in `app-skills/`.
"""

from android_harness.helpers import *  # noqa: F401,F403

try:
    from plugins.adbkeyboard_plugin import clear_input, send_keyevent, type_unicode  # noqa: F401
except Exception:
    pass
