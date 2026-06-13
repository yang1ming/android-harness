"""Basic observation example for android-harness exec."""

print("device_info:")
print(device_info())

print("current_app:")
print(current_app())

path = screenshot()
print(f"screenshot: {path}")

info = page_info()
print(f"visible_texts: {info['visible_texts'][:10]}")
print(f"clickable_count: {len(info['clickable'])}")
