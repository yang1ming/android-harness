"""Small ADB backend for Android Harness."""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class AdbError(RuntimeError):
    """Raised when an adb command fails."""


@dataclass(frozen=True)
class AdbResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


class AdbClient:
    """Minimal adb command wrapper.

    The class intentionally keeps behavior close to adb. Higher-level waiting,
    parsing, and policy decisions belong in helpers or plugins.
    """

    def __init__(self, serial: str | None = None, adb_path: str = "adb") -> None:
        self.serial = serial or os.environ.get("ANDROID_SERIAL")
        self.adb_path = adb_path

    def base_args(self) -> list[str]:
        args = [self.adb_path]
        if self.serial:
            args.extend(["-s", self.serial])
        return args

    def run(
        self,
        args: Sequence[str],
        *,
        check: bool = True,
        timeout: float | None = 30,
        text: bool = True,
    ) -> AdbResult:
        cmd = [*self.base_args(), *args]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            check=False,
            timeout=timeout,
            text=text,
        )
        stdout = proc.stdout if isinstance(proc.stdout, str) else proc.stdout.decode("utf-8", "replace")
        stderr = proc.stderr if isinstance(proc.stderr, str) else proc.stderr.decode("utf-8", "replace")
        result = AdbResult(tuple(cmd), proc.returncode, stdout, stderr)
        if check and proc.returncode != 0:
            raise AdbError(f"adb failed ({proc.returncode}): {' '.join(cmd)}\n{stderr.strip()}")
        return result

    def shell(self, args: Sequence[str] | str, *, timeout: float | None = 30) -> str:
        shell_args = [args] if isinstance(args, str) else list(args)
        return self.run(["shell", *shell_args], timeout=timeout).stdout

    def devices(self) -> list[tuple[str, str]]:
        result = self.run(["devices"], check=True)
        devices: list[tuple[str, str]] = []
        for line in result.stdout.splitlines()[1:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 2:
                devices.append((parts[0], parts[1]))
        return devices

    def getprop(self, key: str) -> str:
        return self.shell(["getprop", key]).strip()

    def connect(self, target: str, *, timeout: float | None = 30) -> str:
        server = AdbClient(adb_path=self.adb_path)
        server.serial = None
        result = server.run(["connect", target], timeout=timeout)
        output = (result.stdout or result.stderr).strip()
        if "failed to connect" in output.lower() or "unable to connect" in output.lower():
            raise AdbError(f"adb connect failed: {target}\n{output}")
        return output

    def disconnect(self, target: str | None = None, *, timeout: float | None = 30) -> str:
        args = ["disconnect"]
        if target:
            args.append(target)
        server = AdbClient(adb_path=self.adb_path)
        server.serial = None
        result = server.run(args, timeout=timeout)
        return (result.stdout or result.stderr).strip()

    def tcpip(self, port: int = 5555, *, timeout: float | None = 30) -> str:
        result = self.run(["tcpip", str(port)], timeout=timeout)
        return (result.stdout or result.stderr).strip()

    def screenshot(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        cmd = [*self.base_args(), "exec-out", "screencap", "-p"]
        with target.open("wb") as handle:
            proc = subprocess.run(cmd, stdout=handle, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            stderr = proc.stderr.decode("utf-8", "replace")
            raise AdbError(f"adb failed ({proc.returncode}): {' '.join(cmd)}\n{stderr.strip()}")
        return target

    def pull_text(self, remote_path: str, *, timeout: float | None = 30) -> str:
        result = self.run(["exec-out", "cat", remote_path], timeout=timeout)
        return result.stdout

    def require_available(self) -> None:
        if shutil.which(self.adb_path) is None:
            raise AdbError(f"adb not found on PATH: {self.adb_path}")
