from android_harness import helpers
from plugins import environment_report_plugin


class FakeTransport:
    pass


class FakeClient:
    def __init__(self):
        self.adb_path = "adb"
        self.serial = "emulator-5554"
        self.transport = FakeTransport()

    def devices(self):
        return [("emulator-5554", "device")]

    def getprop(self, key):
        values = {
            "ro.product.model": "Pixel Test",
            "ro.product.manufacturer": "Google",
            "ro.build.version.release": "15",
            "ro.build.version.sdk": "35",
        }
        return values[key]

    def shell(self, args, timeout=30):
        if args == ["wm", "size"]:
            return "Physical size: 1080x2400\n"
        if args == ["wm", "density"]:
            return "Physical density: 420\n"
        if args == ["uiautomator", "dump", "/sdcard/window_dump.xml"]:
            return "UI hierarchy dumped to: /sdcard/window_dump.xml\n"
        raise AssertionError(f"unexpected shell args: {args}")


def test_environment_report_collects_non_content_metadata(monkeypatch):
    monkeypatch.setattr(helpers, "_client", FakeClient())
    monkeypatch.setattr(helpers, "current_app", lambda: {"package": "com.example", "activity": ".Main"})
    monkeypatch.setattr(helpers, "screenshot", lambda: "/tmp/android-harness/screenshot.png")

    report = environment_report_plugin.environment_report()

    assert report["adb"] == {
        "path": "adb",
        "serial": "emulator-5554",
        "transport": "FakeTransport",
    }
    assert report["devices"] == [("emulator-5554", "device")]
    assert report["device"]["model"] == "Pixel Test"
    assert report["display"]["size"] == "Physical size: 1080x2400"
    assert report["current_app"] == {"package": "com.example", "activity": ".Main"}
    assert report["capabilities"] == {"uiautomator": True, "screenshot": True}


def test_environment_report_keeps_probe_errors_structured(monkeypatch):
    class BrokenClient(FakeClient):
        def getprop(self, key):
            raise RuntimeError("device unavailable")

    monkeypatch.setattr(helpers, "_client", BrokenClient())
    monkeypatch.setattr(helpers, "current_app", lambda: {"package": None, "activity": None})
    monkeypatch.setattr(helpers, "screenshot", lambda: "/tmp/android-harness/screenshot.png")

    report = environment_report_plugin.environment_report()

    assert report["device"]["model"] == {"error": "ro.product.model: device unavailable"}
