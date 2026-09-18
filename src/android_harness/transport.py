"""ADB transport backends for Android Harness."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from typing import Protocol, Sequence


class AdbError(RuntimeError):
    """Raised when an adb command fails."""


_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@dataclass(frozen=True)
class AdbResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class AdbTransport(Protocol):
    """Execution backend used by AdbClient."""

    def run(
        self,
        adb_path: str,
        serial: str | None,
        args: Sequence[str],
        *,
        timeout: float | None = 30,
        text: bool = True,
    ) -> AdbResult:
        """Run an adb command."""

    def screenshot(
        self,
        adb_path: str,
        serial: str | None,
        path: Path,
        *,
        timeout: float | None = 30,
    ) -> Path:
        """Capture a screenshot to path."""


class SubprocessAdbTransport:
    """ADB transport that shells out to the adb executable."""

    def run(
        self,
        adb_path: str,
        serial: str | None,
        args: Sequence[str],
        *,
        timeout: float | None = 30,
        text: bool = True,
    ) -> AdbResult:
        cmd = _base_args(adb_path, serial, args)
        proc = subprocess.run(
            cmd,
            capture_output=True,
            check=False,
            timeout=timeout,
            text=text,
        )
        stdout = proc.stdout if isinstance(proc.stdout, str) else proc.stdout.decode("utf-8", "replace")
        stderr = proc.stderr if isinstance(proc.stderr, str) else proc.stderr.decode("utf-8", "replace")
        return AdbResult(tuple(cmd), proc.returncode, stdout, stderr)

    def screenshot(
        self,
        adb_path: str,
        serial: str | None,
        path: Path,
        *,
        timeout: float | None = 30,
    ) -> Path:
        cmd = _base_args(adb_path, serial, ["exec-out", "screencap", "-p"])
        proc = subprocess.run(cmd, capture_output=True, check=False, timeout=timeout)
        if proc.returncode != 0:
            stderr = proc.stderr.decode("utf-8", "replace")
            raise AdbError(f"adb failed ({proc.returncode}): {' '.join(cmd)}\n{stderr.strip()}")
        return _write_png(path, proc.stdout)


class DaemonAdbTransport:
    """ADB transport that proxies commands through the local daemon."""

    def __init__(self, socket_path: str | Path | None = None) -> None:
        self.socket_path = Path(socket_path) if socket_path else default_socket_path()

    def run(
        self,
        adb_path: str,
        serial: str | None,
        args: Sequence[str],
        *,
        timeout: float | None = 30,
        text: bool = True,
    ) -> AdbResult:
        request = {
            "id": uuid.uuid4().hex,
            "op": "run",
            "serial": serial,
            "adb_path": adb_path,
            "args": list(args),
            "timeout": timeout,
            "text": text,
        }
        response = self._request(request, timeout=timeout)
        cmd = _base_args(adb_path, serial, args)
        return AdbResult(
            tuple(cmd),
            int(response.get("returncode", 0)),
            str(response.get("stdout", "")),
            str(response.get("stderr", "")),
        )

    def screenshot(
        self,
        adb_path: str,
        serial: str | None,
        path: Path,
        *,
        timeout: float | None = 30,
    ) -> Path:
        request = {
            "id": uuid.uuid4().hex,
            "op": "screenshot",
            "serial": serial,
            "adb_path": adb_path,
            "timeout": timeout,
        }
        response = self._request(request, timeout=timeout)
        encoded = response.get("png_b64")
        if not isinstance(encoded, str):
            raise AdbError("daemon screenshot response missing png_b64")
        try:
            data = base64.b64decode(encoded.encode("ascii"), validate=True)
        except (UnicodeEncodeError, ValueError) as exc:
            raise AdbError("daemon screenshot response contains invalid png_b64") from exc
        return _write_png(path, data)

    def _request(self, request: dict[str, object], *, timeout: float | None = 30) -> dict[str, object]:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                if timeout is not None:
                    client.settimeout(timeout)
                client.connect(str(self.socket_path))
                payload = json.dumps(request, ensure_ascii=False).encode("utf-8") + b"\n"
                client.sendall(payload)
                response = _read_json_line(client)
        except OSError as exc:
            raise AdbError(f"adb daemon unavailable at {self.socket_path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise AdbError(f"invalid adb daemon response: {exc}") from exc

        if not response.get("ok"):
            error = response.get("error", "unknown daemon error")
            raise AdbError(str(error))
        return response


def make_transport(name: str | None = None) -> AdbTransport:
    selected = name or os.environ.get("ANDROID_HARNESS_TRANSPORT") or "subprocess"
    if selected == "subprocess":
        return SubprocessAdbTransport()
    if selected == "daemon":
        return DaemonAdbTransport()
    raise ValueError(f"unknown adb transport: {selected}")


def default_socket_path() -> Path:
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if runtime_dir and os.access(runtime_dir, os.W_OK | os.X_OK):
        return Path(runtime_dir) / "android-harness" / "daemon.sock"
    return Path("/tmp") / f"android-harness-{os.getuid()}" / "daemon.sock"


def _base_args(adb_path: str, serial: str | None, args: Sequence[str]) -> list[str]:
    cmd = [adb_path]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(args)
    return cmd


def _write_png(path: Path, data: bytes) -> Path:
    signature_offset = data.find(_PNG_SIGNATURE)
    if signature_offset < 0:
        raise AdbError("screenshot output does not contain a PNG signature")

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(data[signature_offset:])
        temporary_path.replace(path)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    return path


def _read_json_line(client: socket.socket) -> dict[str, object]:
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
    if not chunks:
        raise AdbError("empty adb daemon response")
    data = b"".join(chunks).decode("utf-8")
    value = json.loads(data)
    if not isinstance(value, dict):
        raise AdbError("adb daemon response must be a JSON object")
    return value
