"""Basic observation example for android-harness exec."""

print("device_info:")
print(device_info())

print("current_app:")
print(current_app())

path = screenshot()
print(f"screenshot: {path}")

info = page_info()
print(f"visible_text_count: {len(info['visible_texts'])}")
print(f"clickable_count: {len(info['clickable'])}")
