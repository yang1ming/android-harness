from android_harness import admin


class FakeAdbClient:
    connected = False

    def __init__(self, serial=None, adb_path="adb"):
        self.serial = serial
        self.adb_path = adb_path

    def require_available(self):
        return None

    def devices(self):
        if FakeAdbClient.connected:
            return [("192.168.1.20:5555", "device")]
        return []

    def connect(self, target, timeout=30):
        assert target == "192.168.1.20:5555"
        FakeAdbClient.connected = True
        return f"connected to {target}"

    def getprop(self, key):
        values = {
            "ro.product.model": "Pixel Test",
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
        if args == ["dumpsys", "window", "windows"]:
            return "mCurrentFocus=Window{abc u0 com.example/.MainActivity}"
        raise AssertionError(f"unexpected shell args: {args}")

    def screenshot(self, path):
        path.write_bytes(b"png")
        return path


def test_is_tcpip_serial():
    assert admin._is_tcpip_serial("192.168.1.20:5555") is True
    assert admin._is_tcpip_serial("localhost:5555") is True
    assert admin._is_tcpip_serial("emulator-5554") is False


def test_doctor_connects_tcpip_serial(monkeypatch):
    FakeAdbClient.connected = False
    monkeypatch.setattr(admin, "AdbClient", FakeAdbClient)

    report = admin.doctor("192.168.1.20:5555").to_dict()

    assert report["adb_available"] is True
    assert report["device_ready"] is True
    assert report["tcpip_target"] == "192.168.1.20:5555"
    assert report["tcpip_connected"] is True
    assert report["current_package"] == "com.example"
