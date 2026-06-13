"""Daemon transport example for android-harness exec."""

print("transport: daemon")
print("device_info:")
print(device_info())

print("current_app:")
print(current_app())

path = screenshot()
print(f"screenshot: {path}")
