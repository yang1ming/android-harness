"""Local daemon for optional ADB command proxying."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import socket
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
from typing import Any

from .transport import AdbError, SubprocessAdbTransport, default_socket_path


class DaemonUnixServer(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True


class DaemonRequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        server = self.server
        if not isinstance(server, DaemonUnixServer):
            return
        line = self.rfile.readline()
        try:
            request = json.loads(line.decode("utf-8"))
            if not isinstance(request, dict):
                raise ValueError("request must be a JSON object")
            response = handle_daemon_request(request, server=server)
        except Exception as exc:
            response = {"id": None, "ok": False, "error": str(exc)}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8") + b"\n")


def handle_daemon_request(request: dict[str, Any], *, server: DaemonUnixServer | None = None) -> dict[str, Any]:
    request_id = request.get("id")
    op = request.get("op")

    if op == "ping":
        return {"id": request_id, "ok": True, "status": "running"}

    if op == "shutdown":
        if server is not None:
            threading.Thread(target=server.shutdown, daemon=True).start()
        return {"id": request_id, "ok": True, "status": "stopping"}

    if op == "run":
        args = request.get("args")
        if not isinstance(args, list) or not all(isinstance(arg, str) for arg in args):
            return {"id": request_id, "ok": False, "error": "run request requires string args"}
        adb_path = str(request.get("adb_path") or "adb")
        serial = request.get("serial")
        timeout = request.get("timeout", 30)
        text = bool(request.get("text", True))
        try:
            result = SubprocessAdbTransport().run(
                adb_path,
                serial if isinstance(serial, str) else None,
                args,
                timeout=timeout if isinstance(timeout, (int, float)) else 30,
                text=text,
            )
        except Exception as exc:
            return {"id": request_id, "ok": False, "error": str(exc)}
        return {
            "id": request_id,
            "ok": True,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    if op == "screenshot":
        adb_path = str(request.get("adb_path") or "adb")
        serial = request.get("serial")
        timeout = request.get("timeout", 30)
        try:
            with tempfile.NamedTemporaryFile(prefix="android-harness-daemon-", suffix=".png", delete=False) as handle:
                path = Path(handle.name)
            try:
                SubprocessAdbTransport().screenshot(
                    adb_path,
                    serial if isinstance(serial, str) else None,
                    path,
                    timeout=timeout if isinstance(timeout, (int, float)) else 30,
                )
                encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            finally:
                path.unlink(missing_ok=True)
        except Exception as exc:
            return {"id": request_id, "ok": False, "error": str(exc)}
        return {"id": request_id, "ok": True, "png_b64": encoded}

    return {"id": request_id, "ok": False, "error": f"unknown daemon op: {op}"}


def serve(socket_path: Path | None = None) -> None:
    path = socket_path or default_socket_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    if path.exists():
        path.unlink()
    server = DaemonUnixServer(str(path), DaemonRequestHandler)
    try:
        server.serve_forever()
    finally:
        server.server_close()
        path.unlink(missing_ok=True)


def start_daemon(socket_path: Path | None = None) -> str:
    path = socket_path or default_socket_path()
    if _ping(path):
        return f"running: {path}"
    if path.exists():
        path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    cmd = [sys.executable, "-m", "android_harness.daemon", "--serve", "--socket", str(path)]
    subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        if _ping(path):
            return f"started: {path}"
        time.sleep(0.05)
    raise AdbError(f"adb daemon did not start at {path}")


def stop_daemon(socket_path: Path | None = None) -> str:
    path = socket_path or default_socket_path()
    if not path.exists():
        return f"not running: {path}"
    response = _send(path, {"id": "stop", "op": "shutdown"})
    if response.get("ok"):
        return f"stopping: {path}"
    return f"error: {response.get('error', 'unknown error')}"


def daemon_status(socket_path: Path | None = None) -> str:
    path = socket_path or default_socket_path()
    return f"running: {path}" if _ping(path) else f"not running: {path}"


def _ping(path: Path) -> bool:
    try:
        response = _send(path, {"id": "status", "op": "ping"})
    except Exception:
        return False
    return bool(response.get("ok"))


def _send(path: Path, request: dict[str, Any]) -> dict[str, Any]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(2)
        client.connect(str(path))
        client.sendall(json.dumps(request, ensure_ascii=False).encode("utf-8") + b"\n")
        chunks: list[bytes] = []
        while True:
            chunk = client.recv(4096)
            if not chunk:
                break
            if b"\n" in chunk:
                before, _separator, _after = chunk.partition(b"\n")
                chunks.append(before)
                break
            chunks.append(chunk)
    data = b"".join(chunks).decode("utf-8")
    value = json.loads(data)
    if not isinstance(value, dict):
        raise AdbError("daemon response must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m android_harness.daemon")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--socket", type=Path)
    args = parser.parse_args(argv)
    if args.serve:
        serve(args.socket)
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
