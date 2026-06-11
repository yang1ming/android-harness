import base64
import json
import os
from pathlib import Path
import socket
import threading

import pytest

from android_harness.adb import AdbClient, AdbError
from android_harness.daemon import handle_daemon_request
from android_harness.transport import DaemonAdbTransport, SubprocessAdbTransport, default_socket_path


def _serve_once(socket_path, response):
    ready = threading.Event()

    def run():
        if socket_path.exists():
            socket_path.unlink()
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(str(socket_path))
            server.listen(1)
            ready.set()
            conn, _addr = server.accept()
            with conn:
                conn.recv(4096)
                conn.sendall(json.dumps(response).encode("utf-8") + b"\n")

    thread = threading.Thread(target=run)
    thread.start()
    ready.wait(timeout=2)
    return thread


def test_adb_client_defaults_to_subprocess_transport(monkeypatch):
    monkeypatch.delenv("ANDROID_HARNESS_TRANSPORT", raising=False)

    client = AdbClient()

    assert isinstance(client.transport, SubprocessAdbTransport)


def test_adb_client_uses_daemon_transport_from_env(monkeypatch):
    monkeypatch.setenv("ANDROID_HARNESS_TRANSPORT", "daemon")

    client = AdbClient()

    assert isinstance(client.transport, DaemonAdbTransport)


def test_daemon_transport_sends_run_request(tmp_path):
    socket_path = tmp_path / "daemon.sock"
    thread = _serve_once(
        socket_path,
        {
            "id": "response",
            "ok": True,
            "returncode": 0,
            "stdout": "List of devices attached\n",
            "stderr": "",
        },
    )
    transport = DaemonAdbTransport(socket_path)

    result = transport.run("adb", None, ["devices"])

    thread.join(timeout=2)
    assert result.args == ("adb", "devices")
    assert result.stdout == "List of devices attached\n"


def test_daemon_transport_unavailable_raises(tmp_path):
    transport = DaemonAdbTransport(tmp_path / "missing.sock")

    with pytest.raises(AdbError, match="adb daemon unavailable"):
        transport.run("adb", None, ["devices"])


def test_daemon_transport_screenshot_writes_png(tmp_path):
    socket_path = tmp_path / "daemon.sock"
    png = b"\x89PNG\r\n"
    thread = _serve_once(
        socket_path,
        {
            "id": "response",
            "ok": True,
            "png_b64": base64.b64encode(png).decode("ascii"),
        },
    )
    output = tmp_path / "screen.png"

    DaemonAdbTransport(socket_path).screenshot("adb", "serial", output)

    thread.join(timeout=2)
    assert output.read_bytes() == png


def test_daemon_handler_unknown_op_returns_error():
    response = handle_daemon_request({"id": "1", "op": "unknown"})

    assert response["ok"] is False
    assert "unknown daemon op" in response["error"]


def test_default_socket_path_uses_tmp_without_runtime_dir(monkeypatch):
    monkeypatch.delenv("XDG_RUNTIME_DIR", raising=False)

    assert default_socket_path() == Path("/tmp") / f"android-harness-{os.getuid()}" / "daemon.sock"
