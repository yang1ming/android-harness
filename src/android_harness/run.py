"""android-harness CLI."""

from __future__ import annotations

import argparse
import code
import json
import runpy
import sys
from pathlib import Path

from . import __version__
from . import helpers
from .admin import doctor, redact_doctor_report, summarize_doctor_report, versioned_doctor_report
from .daemon import daemon_status, daemon_status_report, redact_daemon_status_report, start_daemon, stop_daemon
from .observation import (
    redact_snapshot_device,
    redact_snapshot_paths,
    redact_snapshot_text,
    summarize_snapshot,
    versioned_snapshot,
)
from .smoke import redact_smoke_paths, redact_smoke_report, run_smoke, summarize_smoke_report


VERSION_SCHEMA_VERSION = "android-harness.version.v1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="android-harness")
    parser.add_argument("-s", "--serial", help="ADB device serial")
    parser.add_argument(
        "--transport",
        choices=("subprocess", "daemon"),
        help="ADB transport backend; defaults to ANDROID_HARNESS_TRANSPORT or subprocess",
    )
    parser.add_argument(
        "--no-workspace",
        action="store_true",
        help="do not load agent-workspace/agent_helpers.py",
    )
    subparsers = parser.add_subparsers(dest="command")
    doctor_parser = subparsers.add_parser("doctor", help="check adb and selected device")
    doctor_parser.add_argument(
        "--output",
        type=Path,
        help="write the JSON doctor report to a file",
    )
    doctor_parser.add_argument(
        "--compact",
        action="store_true",
        help="print compact single-line JSON",
    )
    doctor_parser.add_argument(
        "--redact-device",
        action="store_true",
        help="redact selected device identifiers from the doctor report",
    )
    doctor_parser.add_argument(
        "--summary",
        action="store_true",
        help="print a count-based doctor summary for logs and CI",
    )
    snapshot_parser = subparsers.add_parser("snapshot", help="print a JSON state snapshot")
    snapshot_parser.add_argument(
        "--screenshot",
        action="store_true",
        help="include a screenshot path in the snapshot",
    )
    snapshot_parser.add_argument(
        "--page-info",
        action="store_true",
        help="include visible text and clickable element details",
    )
    snapshot_parser.add_argument(
        "--output",
        type=Path,
        help="write the JSON snapshot to a file",
    )
    snapshot_parser.add_argument(
        "--compact",
        action="store_true",
        help="print compact single-line JSON",
    )
    snapshot_parser.add_argument(
        "--redact-text",
        action="store_true",
        help="remove visible UI text and content descriptions from the snapshot",
    )
    snapshot_parser.add_argument(
        "--redact-device",
        action="store_true",
        help="redact selected device identifiers from the snapshot",
    )
    snapshot_parser.add_argument(
        "--redact-paths",
        action="store_true",
        help="redact local filesystem paths from the snapshot",
    )
    snapshot_parser.add_argument(
        "--redact-all",
        action="store_true",
        help="redact text, selected device identifiers, and local filesystem paths from the snapshot",
    )
    snapshot_parser.add_argument(
        "--summary",
        action="store_true",
        help="print a count-based snapshot summary for logs and CI",
    )
    smoke_parser = subparsers.add_parser("smoke", help="run JSON smoke checks")
    smoke_parser.add_argument(
        "--output",
        type=Path,
        help="write the JSON smoke report to a file",
    )
    smoke_parser.add_argument(
        "--compact",
        action="store_true",
        help="print compact single-line JSON",
    )
    smoke_parser.add_argument(
        "--redact-device",
        action="store_true",
        help="redact selected device identifiers from the smoke report",
    )
    smoke_parser.add_argument(
        "--redact-paths",
        action="store_true",
        help="redact local filesystem paths from the smoke report",
    )
    smoke_parser.add_argument(
        "--redact-all",
        action="store_true",
        help="redact selected device identifiers and local filesystem paths from the smoke report",
    )
    smoke_parser.add_argument(
        "--summary",
        action="store_true",
        help="print a count-based smoke summary for logs and CI",
    )
    version_parser = subparsers.add_parser("version", help="print version information")
    version_parser.add_argument(
        "--json",
        action="store_true",
        help="print version information as JSON",
    )
    version_parser.add_argument(
        "--compact",
        action="store_true",
        help="print compact single-line JSON with --json",
    )
    version_parser.add_argument(
        "--output",
        type=Path,
        help="write version output to a file",
    )
    subparsers.add_parser("repl", help="open an interactive Python REPL with helpers")
    exec_parser = subparsers.add_parser("exec", help="execute a Python file with helpers")
    exec_parser.add_argument("file", type=Path)
    daemon_parser = subparsers.add_parser("daemon", help="manage the local adb daemon")
    daemon_subparsers = daemon_parser.add_subparsers(dest="daemon_command")
    daemon_subparsers.add_parser("start", help="start the local adb daemon")
    daemon_subparsers.add_parser("stop", help="stop the local adb daemon")
    daemon_status_parser = daemon_subparsers.add_parser("status", help="show local adb daemon status")
    daemon_status_parser.add_argument(
        "--json",
        action="store_true",
        help="print daemon status as JSON",
    )
    daemon_status_parser.add_argument(
        "--compact",
        action="store_true",
        help="print compact single-line JSON with --json",
    )
    daemon_status_parser.add_argument(
        "--output",
        type=Path,
        help="write daemon status output to a file",
    )
    daemon_status_parser.add_argument(
        "--redact-paths",
        action="store_true",
        help="redact local filesystem paths from daemon status output",
    )

    args = parser.parse_args(argv)

    if args.command == "daemon":
        if args.daemon_command == "start":
            print(start_daemon())
            return 0
        if args.daemon_command == "stop":
            print(stop_daemon())
            return 0
        if args.daemon_command == "status":
            if args.json:
                report = daemon_status_report()
                if args.redact_paths:
                    report = redact_daemon_status_report(report)
                payload = _json_payload(report, compact=args.compact)
            else:
                if args.redact_paths:
                    report = redact_daemon_status_report(daemon_status_report())
                    payload = str(report["status"])
                else:
                    payload = daemon_status()
            _emit_payload(payload, output=args.output)
            return 0
        daemon_parser.print_help()
        return 0

    if args.command == "smoke":
        report = run_smoke(args.serial, transport_name=args.transport)
        if args.summary:
            report = summarize_smoke_report(report)
        elif args.redact_device or args.redact_all:
            report = redact_smoke_report(report)
        if not args.summary and (args.redact_paths or args.redact_all):
            report = redact_smoke_paths(report)
        payload = _json_payload(report, compact=args.compact)
        _emit_payload(payload, output=args.output)
        return 0 if report.get("ok") else 1

    if args.command == "version":
        if args.json:
            report = _version_report()
            payload = _json_payload(report, compact=args.compact)
        else:
            payload = f"android-harness {__version__}"
        _emit_payload(payload, output=args.output)
        return 0

    helpers.set_device(args.serial, transport_name=args.transport)

    if args.command == "doctor":
        report = versioned_doctor_report(doctor(args.serial, transport_name=args.transport).to_dict())
        if args.summary:
            report = summarize_doctor_report(report)
        elif args.redact_device:
            report = redact_doctor_report(report)
        payload = _json_payload(report, compact=args.compact)
        _emit_payload(payload, output=args.output)
        return 0 if report.get("device_ready") else 1

    if args.command == "snapshot":
        snapshot = helpers.state_snapshot(include_screenshot=args.screenshot)
        if args.page_info:
            snapshot["page_info"] = helpers.page_info()
        if args.summary:
            snapshot = summarize_snapshot(snapshot)
        elif args.redact_text or args.redact_all:
            snapshot = redact_snapshot_text(snapshot)
        if args.redact_device or args.redact_all:
            snapshot = redact_snapshot_device(snapshot)
        if args.redact_paths or args.redact_all:
            snapshot = redact_snapshot_paths(snapshot)
        payload = _json_payload(versioned_snapshot(snapshot), compact=args.compact)
        _emit_payload(payload, output=args.output)
        return 0

    if args.command == "repl":
        code.interact(local=_execution_env(load_workspace=not args.no_workspace))
        return 0

    if args.command == "exec":
        env = _execution_env(load_workspace=not args.no_workspace)
        runpy.run_path(str(args.file), init_globals=env)
        return 0

    source = sys.stdin.read()
    if source.strip():
        exec(compile(source, "<android-harness>", "exec"), _execution_env(load_workspace=not args.no_workspace))
        return 0

    parser.print_help()
    return 0


def _execution_env(*, load_workspace: bool = True) -> dict[str, object]:
    env: dict[str, object] = {"__name__": "__android_harness__"}
    for name in helpers.__all__:
        env[name] = getattr(helpers, name)

    workspace = Path.cwd() / "agent-workspace" / "agent_helpers.py"
    if load_workspace and workspace.exists():
        workspace_env = dict(env)
        exec(compile(workspace.read_text(), str(workspace), "exec"), workspace_env)
        for name, value in workspace_env.items():
            if not name.startswith("_"):
                env[name] = value
    return env


def _json_payload(value: object, *, compact: bool = False) -> str:
    if compact:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(value, ensure_ascii=False, indent=2)


def _emit_payload(payload: str, *, output: Path | None = None) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n")
    print(payload)


def _version_report() -> dict[str, str]:
    return {
        "schema_version": VERSION_SCHEMA_VERSION,
        "name": "android-harness",
        "version": __version__,
        "python_version": sys.version.split()[0],
    }


if __name__ == "__main__":
    raise SystemExit(main())
