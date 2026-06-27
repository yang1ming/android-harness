"""Optional clipboard input example.

Run only when the authorized device supports ``cmd clipboard`` and the focused
field accepts paste input.
"""

from plugins.clipboard_input_plugin import clipboard_input_status, type_via_clipboard


print({"clipboard_input_status": clipboard_input_status()})
type_via_clipboard("Hello from Android Harness")
