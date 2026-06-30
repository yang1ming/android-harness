import io
import json

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


def test_execution_env_uses_helpers_public_surface():
    env = run._execution_env(load_workspace=False)

    assert "tap" in env
    assert "type_text" in env
    assert "os" not in env
    assert "re" not in env
    assert "Path" not in env
    assert "AdbClient" not in env
    assert "annotations" not in env


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


def test_cli_doctor_can_print_compact_json_and_write_output(tmp_path, monkeypatch, capsys):
    captured = {}

    class FakeReport:
        def to_dict(self):
            return {
                "adb_available": True,
                "devices": [["emulator-5554", "device"]],
                "selected_serial": "emulator-5554",
                "device_ready": True,
            }

    def fake_doctor(serial=None, *, transport_name=None):
        captured["serial"] = serial
        captured["transport_name"] = transport_name
        return FakeReport()

    output = tmp_path / "reports" / "doctor.json"
    monkeypatch.setattr(run, "doctor", fake_doctor)

    assert run.main(["-s", "emulator-5554", "--transport", "daemon", "doctor", "--compact", "--output", str(output)]) == 0

    stdout = capsys.readouterr().out
    assert "\n" not in stdout.strip()
    assert " " not in stdout.strip()
    stdout_payload = json.loads(stdout)
    file_payload = json.loads(output.read_text())
    assert stdout_payload == file_payload
    assert stdout_payload["selected_serial"] == "emulator-5554"
    assert captured == {"serial": "emulator-5554", "transport_name": "daemon"}


def test_cli_no_args_prints_help(monkeypatch, capsys):
    monkeypatch.setattr(run.sys, "stdin", io.StringIO(""))

    assert run.main([]) == 0
    out = capsys.readouterr().out.lower()
    assert "usage:" in out
    assert "doctor" in out and "snapshot" in out and "smoke" in out and "repl" in out and "exec" in out and "daemon" in out


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


def test_cli_snapshot_can_include_page_info_and_write_output(tmp_path, monkeypatch, capsys):
    def fake_state_snapshot(include_screenshot=False):
        return {
            "device_info": {"serial": "emulator-5554"},
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Ready"],
        }

    def fake_page_info():
        return {
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Ready"],
            "clickable": [
                {
                    "text": "Start",
                    "content_desc": None,
                    "resource_id": "pkg:id/start",
                    "bounds": {"left": 1, "top": 2, "right": 101, "bottom": 202},
                }
            ],
        }

    output = tmp_path / "artifacts" / "snapshot.json"
    monkeypatch.setattr(run.helpers, "set_device", lambda serial=None, *, transport_name=None: None)
    monkeypatch.setattr(run.helpers, "state_snapshot", fake_state_snapshot)
    monkeypatch.setattr(run.helpers, "page_info", fake_page_info)

    assert run.main(["snapshot", "--page-info", "--output", str(output)]) == 0

    stdout_payload = json.loads(capsys.readouterr().out)
    file_payload = json.loads(output.read_text())
    assert stdout_payload == file_payload
    assert stdout_payload["schema_version"] == "android-harness.snapshot.v1"
    assert stdout_payload["page_info"]["clickable"][0]["resource_id"] == "pkg:id/start"


def test_cli_snapshot_can_print_compact_json(monkeypatch, capsys):
    def fake_state_snapshot(include_screenshot=False):
        return {
            "device_info": {"serial": "emulator-5554"},
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Ready"],
        }

    monkeypatch.setattr(run.helpers, "set_device", lambda serial=None, *, transport_name=None: None)
    monkeypatch.setattr(run.helpers, "state_snapshot", fake_state_snapshot)

    assert run.main(["snapshot", "--compact"]) == 0

    out = capsys.readouterr().out
    assert "\n" not in out.strip()
    assert " " not in out.strip()
    assert json.loads(out)["schema_version"] == "android-harness.snapshot.v1"


def test_cli_snapshot_can_redact_text(monkeypatch, capsys):
    def fake_state_snapshot(include_screenshot=False):
        return {
            "device_info": {"serial": "emulator-5554"},
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Secret"],
        }

    def fake_page_info():
        return {
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Secret"],
            "clickable": [
                {
                    "text": "Pay",
                    "content_desc": "Pay now",
                    "resource_id": "pkg:id/pay",
                    "bounds": {"left": 1, "top": 2, "right": 101, "bottom": 202},
                }
            ],
        }

    monkeypatch.setattr(run.helpers, "set_device", lambda serial=None, *, transport_name=None: None)
    monkeypatch.setattr(run.helpers, "state_snapshot", fake_state_snapshot)
    monkeypatch.setattr(run.helpers, "page_info", fake_page_info)

    assert run.main(["snapshot", "--page-info", "--redact-text"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["text_redacted"] is True
    assert payload["visible_texts"] == []
    assert payload["visible_text_count"] == 1
    assert payload["page_info"]["visible_texts"] == []
    assert payload["page_info"]["clickable"][0]["text"] is None
    assert payload["page_info"]["clickable"][0]["content_desc"] is None
    assert payload["page_info"]["clickable"][0]["resource_id"] == "pkg:id/pay"


def test_cli_snapshot_can_print_summary(monkeypatch, capsys):
    def fake_state_snapshot(include_screenshot=False):
        return {
            "device_info": {"serial": "emulator-5554"},
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Secret"],
        }

    def fake_page_info():
        return {
            "current_app": {"package": "com.example", "activity": ".Main"},
            "visible_texts": ["Secret"],
            "clickable": [
                {
                    "text": "Pay",
                    "content_desc": "Pay now",
                    "resource_id": "pkg:id/pay",
                    "bounds": {"left": 1, "top": 2, "right": 101, "bottom": 202},
                }
            ],
        }

    monkeypatch.setattr(run.helpers, "set_device", lambda serial=None, *, transport_name=None: None)
    monkeypatch.setattr(run.helpers, "state_snapshot", fake_state_snapshot)
    monkeypatch.setattr(run.helpers, "page_info", fake_page_info)

    assert run.main(["snapshot", "--page-info", "--summary"]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"] is True
    assert payload["visible_text_count"] == 1
    assert payload["page_info"]["visible_text_count"] == 1
    assert payload["page_info"]["clickable_count"] == 1
    assert "visible_texts" not in payload
    assert "clickable" not in payload["page_info"]


def test_cli_smoke_outputs_json_and_uses_exit_status(tmp_path, monkeypatch, capsys):
    captured = {}

    def fake_run_smoke(serial=None, *, transport_name=None):
        captured["serial"] = serial
        captured["transport_name"] = transport_name
        return {
            "schema_version": "android-harness.smoke.v1",
            "ok": False,
            "transport": transport_name,
            "checks": [{"name": "device_ready", "ok": False}],
        }

    output = tmp_path / "reports" / "smoke.json"
    monkeypatch.setattr(run.helpers, "set_device", lambda serial=None, *, transport_name=None: None)
    monkeypatch.setattr(run, "run_smoke", fake_run_smoke)

    assert run.main(["-s", "emulator-5554", "--transport", "daemon", "smoke", "--compact", "--output", str(output)]) == 1

    stdout_payload = json.loads(capsys.readouterr().out)
    file_payload = json.loads(output.read_text())
    assert stdout_payload == file_payload
    assert stdout_payload["schema_version"] == "android-harness.smoke.v1"
    assert captured == {"serial": "emulator-5554", "transport_name": "daemon"}


def test_cli_smoke_can_redact_device_identifiers(monkeypatch, capsys):
    def fake_run_smoke(serial=None, *, transport_name=None):
        return {
            "schema_version": "android-harness.smoke.v1",
            "ok": False,
            "selected_serial": "emulator-5554",
            "checks": [
                {
                    "name": "device_ready",
                    "ok": False,
                    "detail": "selected device emulator-5554 is offline",
                }
            ],
            "doctor": {
                "selected_serial": "emulator-5554",
                "devices": [["emulator-5554", "offline"]],
                "error": "selected device emulator-5554 is not ready",
            },
        }

    monkeypatch.setattr(run, "run_smoke", fake_run_smoke)

    assert run.main(["smoke", "--redact-device"]) == 1

    out = capsys.readouterr().out
    assert "emulator-5554" not in out
    payload = json.loads(out)
    assert payload["device_redacted"] is True
    assert payload["selected_serial"] == "<redacted-device>"


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
