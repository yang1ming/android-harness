from android_harness import run


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
