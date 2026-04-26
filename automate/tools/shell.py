"""Privileged shell execution.

This is the most powerful — and most dangerous — tool autoMate ships. It runs
arbitrary commands with the privileges of the autoMate process. The frontend
must surface this clearly and require user confirmation before any agent
invocation in non-trusted modes.
"""
from __future__ import annotations

import os
import shlex
import subprocess

from .registry import Tool, ToolRegistry


def _run(command: str, *, cwd: str | None = None, timeout: int = 120,
         shell: bool = True) -> dict:
    try:
        completed = subprocess.run(
            command if shell else shlex.split(command),
            cwd=cwd or None,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ},
        )
        return {
            "exit_code": completed.returncode,
            "stdout": completed.stdout[-8000:],
            "stderr": completed.stderr[-4000:],
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": f"timed out after {timeout}s"}
    except Exception as e:  # noqa: BLE001
        return {"exit_code": -1, "stdout": "", "stderr": f"{type(e).__name__}: {e}"}


def register(reg: ToolRegistry) -> None:
    reg.register(Tool(
        name="shell.exec",
        description=(
            "Execute a shell command on the host machine with the autoMate process's "
            "privileges. Returns exit code, stdout (last 8KB), stderr (last 4KB). "
            "Use for any task the OS shell can do: git, npm, docker, file ops, "
            "package install, calling other CLIs."
        ),
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command line."},
                "cwd": {"type": "string", "description": "Working directory.", "default": ""},
                "timeout": {"type": "integer", "description": "Max seconds.", "default": 120},
            },
            "required": ["command"],
        },
        handler=lambda command, cwd="", timeout=120: _run(command, cwd=cwd, timeout=timeout),
        category="system",
        danger="high",
    ))

    reg.register(Tool(
        name="shell.cwd",
        description="Return the current working directory of the autoMate server process.",
        parameters={"type": "object", "properties": {}},
        handler=lambda: {"cwd": os.getcwd()},
        category="system",
        danger="low",
    ))
