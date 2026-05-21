"""android-harness CLI."""

from __future__ import annotations

import argparse
import code
import json
import runpy
import sys
from pathlib import Path

from . import helpers
from .admin import doctor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="android-harness")
    parser.add_argument("-s", "--serial", help="ADB device serial")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("doctor", help="check adb and selected device")
    subparsers.add_parser("repl", help="open an interactive Python REPL with helpers")
    exec_parser = subparsers.add_parser("exec", help="execute a Python file with helpers")
    exec_parser.add_argument("file", type=Path)

    args = parser.parse_args(argv)
    helpers.set_device(args.serial)

    if args.command == "doctor":
        report = doctor(args.serial).to_dict()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("device_ready") else 1

    if args.command == "repl":
        code.interact(local=_execution_env())
        return 0

    if args.command == "exec":
        env = _execution_env()
        runpy.run_path(str(args.file), init_globals=env)
        return 0

    source = sys.stdin.read()
    if source.strip():
        exec(compile(source, "<android-harness>", "exec"), _execution_env())
        return 0

    parser.print_help()
    return 0


def _execution_env() -> dict[str, object]:
    env: dict[str, object] = {"__name__": "__android_harness__"}
    for name in dir(helpers):
        if name.startswith("_"):
            continue
        env[name] = getattr(helpers, name)

    workspace = Path.cwd() / "agent-workspace" / "agent_helpers.py"
    if workspace.exists():
        workspace_env = dict(env)
        exec(compile(workspace.read_text(), str(workspace), "exec"), workspace_env)
        for name, value in workspace_env.items():
            if not name.startswith("_"):
                env[name] = value
    return env


if __name__ == "__main__":
    raise SystemExit(main())
