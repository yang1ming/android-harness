import subprocess

from android_harness.adb import AdbClient


def test_connect_ignores_android_serial(monkeypatch):
    calls = []

    def fake_run(cmd, capture_output=True, check=False, timeout=30, text=True):
        calls.append(cmd)
        return subprocess.CompletedProcess(cmd, 0, stdout="connected to 192.168.1.20:5555\n", stderr="")

    monkeypatch.setenv("ANDROID_SERIAL", "usb-device")
    monkeypatch.setattr(subprocess, "run", fake_run)

    output = AdbClient().connect("192.168.1.20:5555")

    assert output == "connected to 192.168.1.20:5555"
    assert calls == [["adb", "connect", "192.168.1.20:5555"]]
