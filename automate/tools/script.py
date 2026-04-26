"""Write-and-run script tool.

Lets the agent draft a Python or Bash script and execute it in one shot. Files
land in ``~/.automate/scripts/`` so the user can replay or audit them later.
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
import time
from pathlib import Path

from ..settings import PATHS
from .registry import Tool, ToolRegistry


def _safe_name(name: str) -> str:
    keep = "-_." + "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    cleaned = "".join(c if c in keep else "_" for c in name).strip("_") or "script"
    return cleaned[:64]


def _write_and_run(*, language: str, source: str, name: str, args: list[str] | None = None,
                   timeout: int = 180) -> dict:
    PATHS.ensure()
    suffix = {"python": ".py", "bash": ".sh", "node": ".js"}.get(language, ".txt")
    fname = f"{int(time.time())}-{_safe_name(name)}{suffix}"
    path = PATHS.scripts / fname
    path.write_text(source)
    if language == "bash":
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP)

    cmd = {
        "python": [sys.executable, str(path), *(args or [])],
        "bash":   ["bash", str(path), *(args or [])],
        "node":   ["node", str(path), *(args or [])],
    }.get(language)
    if not cmd:
        return {"error": f"unsupported language: {language}"}

    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "path": str(path),
            "exit_code": completed.returncode,
            "stdout": completed.stdout[-8000:],
            "stderr": completed.stderr[-4000:],
        }
    except subprocess.TimeoutExpired:
        return {"path": str(path), "exit_code": -1, "stdout": "", "stderr": f"timed out after {timeout}s"}


def register(reg: ToolRegistry) -> None:
    reg.register(Tool(
        name="script.run",
        description=(
            "Persist source code to ~/.automate/scripts/ then run it. "
            "Use this when a one-shot multi-line script is cleaner than chaining shell.exec calls."
        ),
        parameters={
            "type": "object",
            "properties": {
                "language": {"type": "string", "enum": ["python", "bash", "node"]},
                "source":   {"type": "string", "description": "Full script source."},
                "name":     {"type": "string", "description": "Short label, used in the saved filename."},
                "args":     {"type": "array", "items": {"type": "string"}, "default": []},
                "timeout":  {"type": "integer", "default": 180},
            },
            "required": ["language", "source", "name"],
        },
        handler=_write_and_run,
        category="system",
        danger="high",
    ))

    def _list_scripts() -> dict:
        items = []
        for p in sorted(PATHS.scripts.glob("*"), key=lambda x: x.stat().st_mtime, reverse=True)[:50]:
            items.append({"name": p.name, "size": p.stat().st_size, "mtime": p.stat().st_mtime})
        return {"scripts": items}

    reg.register(Tool(
        name="script.list",
        description="List saved scripts (most recent first, capped at 50).",
        parameters={"type": "object", "properties": {}},
        handler=_list_scripts,
        category="system",
    ))

    def _read_script(name: str) -> dict:
        path = PATHS.scripts / _safe_name(name)
        # Allow caller to pass full filename too
        if not path.exists():
            path = PATHS.scripts / name
        if not path.exists() or not path.is_file():
            return {"error": "not found"}
        return {"name": path.name, "source": path.read_text()}

    reg.register(Tool(
        name="script.read",
        description="Read a previously saved script's source by filename.",
        parameters={
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
        handler=_read_script,
        category="system",
    ))
