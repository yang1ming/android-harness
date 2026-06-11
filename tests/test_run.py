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
