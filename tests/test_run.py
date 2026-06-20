import io

import pytest

from android_harness import run
from android_harness.transport import SubprocessAdbTransport


def test_execution_env_loads_workspace_by_default(tmp_path, monkeypatch):
    workspace = tmp_path / "agent-workspace"
    workspace.mkdir()
    (workspace / "agent_helpers.py").write_text("custom_helper = 'loaded'\n")
    monkeypatch.chdir(tmp_path)

    env = run._execution_env()

    assert env["custom_helper"] == "loaded"


def test_execution_env_can_skip_workspace(tmp_path, monkeypatch):
    workspace = tmp_path / "agent-workspace"
    workspace.mkdir()
    (workspace / "agent_helpers.py").write_text("custom_helper = 'loaded'\n")
    monkeypatch.chdir(tmp_path)

    env = run._execution_env(load_workspace=False)

    assert "custom_helper" not in env


def test_cli_transport_argument_overrides_env_for_doctor(monkeypatch, capsys):
    captured = {}

    class FakeReport:
        def to_dict(self):
            return {"device_ready": True}

    def fake_doctor(serial=None, *, transport_name=None):
        captured["serial"] = serial
        captured["transport_name"] = transport_name
        return FakeReport()

    monkeypatch.setenv("ANDROID_HARNESS_TRANSPORT", "daemon")
    monkeypatch.setattr(run, "doctor", fake_doctor)

    assert run.main(["--transport", "subprocess", "doctor"]) == 0

    assert captured == {"serial": None, "transport_name": "subprocess"}
    assert isinstance(run.helpers.get_client().transport, SubprocessAdbTransport)


def test_cli_no_args_prints_help(monkeypatch, capsys):
    monkeypatch.setattr(run.sys, "stdin", io.StringIO(""))

    assert run.main([]) == 0
    out = capsys.readouterr().out.lower()
    assert "usage:" in out
    assert "doctor" in out and "snapshot" in out and "repl" in out and "exec" in out and "daemon" in out


def test_cli_snapshot_outputs_json_and_uses_device_selection(monkeypatch, capsys):
    captured = {}

    def fake_set_device(serial=None, *, transport_name=None):
        captured["serial"] = serial
        captured["transport_name"] = transport_name

    def fake_state_snapshot(include_screenshot=False):
        captured["include_screenshot"] = include_screenshot
        return {
            "device_info": {"serial": "emulator-5554"},
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Ready"],
            "screenshot": "/tmp/android-harness/screen.png",
        }

    monkeypatch.setattr(run.helpers, "set_device", fake_set_device)
    monkeypatch.setattr(run.helpers, "state_snapshot", fake_state_snapshot)

    assert run.main(["-s", "emulator-5554", "--transport", "daemon", "snapshot", "--screenshot"]) == 0

    out = capsys.readouterr().out
    assert '"schema_version": "android-harness.snapshot.v1"' in out
    assert '"serial": "emulator-5554"' in out
    assert '"screenshot": "/tmp/android-harness/screen.png"' in out
    assert captured == {
        "serial": "emulator-5554",
        "transport_name": "daemon",
        "include_screenshot": True,
    }


def test_cli_unknown_command_fails_with_error(capsys):
    with pytest.raises(SystemExit) as exc:
        run.main(["invalid"])
    captured = capsys.readouterr()
    output = captured.err + captured.out
    assert exc.value.code == 2
    assert "invalid" in output.lower() or output == ""


def test_cli_invalid_transport_fails_with_error(capsys):
    with pytest.raises(SystemExit) as exc:
        run.main(["--transport", "bad", "doctor"])
    captured = capsys.readouterr()
    output = captured.err + captured.out
    assert exc.value.code == 2
    assert "invalid" in output.lower() or output == ""


def test_cli_exec_missing_file_fails_with_error(capsys):
    with pytest.raises(SystemExit) as exc:
        run.main(["exec"])
    captured = capsys.readouterr()
    output = captured.err + captured.out
    assert exc.value.code == 2
    assert "required" in output.lower() or output == ""


def test_cli_daemon_without_subcommand_prints_help(capsys):
    assert run.main(["daemon"]) == 0
    out = capsys.readouterr().out.lower()
    assert "usage:" in out
    assert "start" in out and "stop" in out and "status" in out


def test_cli_daemon_subcommands_dispatch_without_selecting_device(monkeypatch, capsys):
    calls = []

    def fail_set_device(serial=None, *, transport_name=None):
        raise AssertionError("daemon commands should not select an adb device")

    def fake_start_daemon():
        calls.append("start")
        return "started: /tmp/android-harness/daemon.sock"

    def fake_daemon_status():
        calls.append("status")
        return "running: /tmp/android-harness/daemon.sock"

    def fake_stop_daemon():
        calls.append("stop")
        return "stopping: /tmp/android-harness/daemon.sock"

    monkeypatch.setattr(run.helpers, "set_device", fail_set_device)
    monkeypatch.setattr(run, "start_daemon", fake_start_daemon)
    monkeypatch.setattr(run, "daemon_status", fake_daemon_status)
    monkeypatch.setattr(run, "stop_daemon", fake_stop_daemon)

    assert run.main(["daemon", "start"]) == 0
    assert capsys.readouterr().out == "started: /tmp/android-harness/daemon.sock\n"

    assert run.main(["daemon", "status"]) == 0
    assert capsys.readouterr().out == "running: /tmp/android-harness/daemon.sock\n"

    assert run.main(["daemon", "stop"]) == 0
    assert capsys.readouterr().out == "stopping: /tmp/android-harness/daemon.sock\n"

    assert calls == ["start", "status", "stop"]
