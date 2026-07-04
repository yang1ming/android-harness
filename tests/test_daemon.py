import json
from pathlib import Path
import time

import pytest

from android_harness import daemon
from android_harness.adb import AdbError
from android_harness.daemon import daemon_status, start_daemon, stop_daemon


FIXTURES = Path(__file__).parent / "fixtures"


def test_daemon_lifecycle_start_status_stop(tmp_path):
    socket_path = tmp_path / "daemon.sock"

    try:
        started = start_daemon(socket_path)

        assert started == f"started: {socket_path}"
        assert daemon_status(socket_path) == f"running: {socket_path}"
        assert start_daemon(socket_path) == f"running: {socket_path}"
        assert stop_daemon(socket_path) == f"stopping: {socket_path}"

        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            if daemon_status(socket_path) == f"not running: {socket_path}":
                break
            time.sleep(0.05)

        assert daemon_status(socket_path) == f"not running: {socket_path}"
    finally:
        if daemon_status(socket_path) == f"running: {socket_path}":
            stop_daemon(socket_path)
        socket_path.unlink(missing_ok=True)


def test_daemon_status_and_stop_report_not_running_for_missing_socket(tmp_path):
    socket_path = tmp_path / "missing.sock"

    assert daemon_status(socket_path) == f"not running: {socket_path}"
    assert stop_daemon(socket_path) == f"not running: {socket_path}"


def test_daemon_status_report_matches_public_schema_fixture(monkeypatch):
    socket_path = Path("/tmp/android-harness/daemon.sock")

    monkeypatch.setattr(daemon, "daemon_status", lambda path=None: f"not running: {path}")

    report = daemon.daemon_status_report(socket_path)
    fixture = json.loads((FIXTURES / "daemon_status_v1.json").read_text())

    assert report == fixture


def test_daemon_status_reports_stale_socket(tmp_path):
    socket_path = tmp_path / "daemon.sock"
    socket_path.write_text("stale\n")

    assert daemon_status(socket_path) == f"not running: {socket_path} (stale socket)"
    assert socket_path.exists()


def test_stop_daemon_removes_stale_socket(tmp_path):
    socket_path = tmp_path / "daemon.sock"
    socket_path.write_text("stale\n")

    assert stop_daemon(socket_path) == f"not running: {socket_path} (removed stale socket)"
    assert not socket_path.exists()


def test_start_daemon_removes_stale_socket_before_starting(tmp_path):
    socket_path = tmp_path / "daemon.sock"
    socket_path.write_text("stale\n")

    try:
        assert start_daemon(socket_path) == f"started: {socket_path}"
        assert daemon_status(socket_path) == f"running: {socket_path}"
    finally:
        if daemon_status(socket_path) == f"running: {socket_path}":
            stop_daemon(socket_path)
        socket_path.unlink(missing_ok=True)


def test_start_daemon_error_includes_exit_code_and_log_tail(tmp_path, monkeypatch):
    socket_path = tmp_path / "daemon.sock"

    class FailedProcess:
        returncode = 2

        def poll(self):
            return self.returncode

    def fake_popen(cmd, *, stdin, stdout, stderr, start_new_session):
        stdout.write(b"daemon failed to import module\n")
        stdout.flush()
        return FailedProcess()

    monkeypatch.setattr(daemon.subprocess, "Popen", fake_popen)

    with pytest.raises(AdbError) as exc_info:
        start_daemon(socket_path)

    message = str(exc_info.value)
    assert f"adb daemon did not start at {socket_path}: exited with code 2" in message
    assert f"log: {socket_path}.log" in message
    assert "daemon failed to import module" in message


def test_start_daemon_wraps_process_launch_errors(tmp_path, monkeypatch):
    socket_path = tmp_path / "daemon.sock"

    def fake_popen(cmd, *, stdin, stdout, stderr, start_new_session):
        raise OSError("exec failed")

    monkeypatch.setattr(daemon.subprocess, "Popen", fake_popen)

    with pytest.raises(AdbError) as exc_info:
        start_daemon(socket_path)

    message = str(exc_info.value)
    assert f"adb daemon did not start at {socket_path}: could not launch process: exec failed" in message
    assert f"log: {socket_path}.log" in message
