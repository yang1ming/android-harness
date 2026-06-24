"""Authorized device smoke example for real devices and emulators."""

from pprint import pprint


snapshot = state_snapshot(include_screenshot=False)
page = page_info()

pprint(
    {
        "serial": snapshot["device_info"].get("serial"),
        "model": snapshot["device_info"].get("model"),
        "android_version": snapshot["device_info"].get("android_version"),
        "current_app": snapshot["current_app"],
        "visible_text_count": len(snapshot["visible_texts"]),
        "sample_visible_texts": snapshot["visible_texts"][:10],
        "clickable_count": len(page["clickable"]),
    }
)
