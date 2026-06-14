import time

from android_harness.daemon import daemon_status, start_daemon, stop_daemon


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
