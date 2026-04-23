"""
Integration framework base class.
Each integration auto-registers its MCP tools when env vars are present.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod


class BaseIntegration(ABC):
    name: str        # e.g. "feishu"
    label: str       # e.g. "飞书 (Feishu)"
    env_vars: dict[str, str]  # env_var_name -> human description

    def is_configured(self) -> bool:
        return all(os.environ.get(k) for k in self.env_vars)

    def env(self, key: str) -> str:
        return os.environ.get(key, "")

    @abstractmethod
    def register(self, mcp) -> None:
        """Register MCP tools onto the FastMCP server."""
        ...

    def config_hint(self) -> str:
        missing = [f"  {k} — {v}" for k, v in self.env_vars.items() if not os.environ.get(k)]
        return f"{self.label} not configured. Set:\n" + "\n".join(missing)

    # ------------------------------------------------------------------
    # Shared HTTP helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get(url: str, headers: dict | None = None) -> dict:
        req = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())

    @staticmethod
    def post(url: str, data: dict, headers: dict | None = None) -> dict:
        body = json.dumps(data).encode()
        h = {"Content-Type": "application/json", **(headers or {})}
        req = urllib.request.Request(url, data=body, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "msg": e.read().decode()}

    @staticmethod
    def patch(url: str, data: dict, headers: dict | None = None) -> dict:
        body = json.dumps(data).encode()
        h = {"Content-Type": "application/json", **(headers or {})}
        req = urllib.request.Request(url, data=body, headers=h, method="PATCH")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "msg": e.read().decode()}

    @staticmethod
    def ok(result: dict) -> str:
        return json.dumps(result, ensure_ascii=False, indent=2)
