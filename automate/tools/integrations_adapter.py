"""Bridge the existing ``integrations/`` package into the new tool registry.

Strategy
--------
Each integration class still expects ``register(mcp)`` and reads credentials from
``os.environ``. Instead of rewriting all 30+ of them we:

1. Hydrate ``os.environ`` from the ``connections`` table on startup so the
   existing code finds its keys/tokens.
2. Pass a tiny shim that mimics ``FastMCP.tool()`` so each ``@mcp.tool()`` call
   ends up registering a ``Tool`` in our registry (with auto-derived JSON schema
   from the function signature + docstring).

This means a new SaaS connector can be dropped into ``integrations/`` without
touching the rest of the codebase.
"""
from __future__ import annotations

import inspect
import os
from typing import Any, Callable, get_type_hints

from ..store import get_db
from .registry import Tool, ToolRegistry


# Map connection id → which env vars receive the stored credentials.
# This is the minimum metadata to bridge old env-var style integrations.
CONNECTION_ENV_MAP: dict[str, list[str]] = {
    "github":     ["GITHUB_TOKEN"],
    "gitlab":     ["GITLAB_TOKEN"],
    "gitee":      ["GITEE_TOKEN"],
    "notion":     ["NOTION_API_KEY"],
    "slack":      ["SLACK_BOT_TOKEN"],
    "telegram":   ["TELEGRAM_BOT_TOKEN"],
    "discord":    ["DISCORD_BOT_TOKEN"],
    "linear":     ["LINEAR_API_KEY"],
    "jira":       ["JIRA_API_TOKEN"],
    "confluence": ["CONFLUENCE_API_TOKEN"],
    "trello":     ["TRELLO_API_KEY"],
    "asana":      ["ASANA_PAT"],
    "monday":     ["MONDAY_API_TOKEN"],
    "hubspot":    ["HUBSPOT_TOKEN"],
    "stripe":     ["STRIPE_API_KEY"],
    "shopify":    ["SHOPIFY_TOKEN"],
    "sendgrid":   ["SENDGRID_API_KEY"],
    "twilio":     ["TWILIO_AUTH_TOKEN"],
    "mailchimp":  ["MAILCHIMP_API_KEY"],
    "twitter":    ["TWITTER_BEARER_TOKEN"],
    "sentry":     ["SENTRY_AUTH_TOKEN"],
    "airtable":   ["AIRTABLE_API_KEY"],
    "feishu":     ["FEISHU_APP_ID", "FEISHU_APP_SECRET"],
    "dingtalk":   ["DINGTALK_WEBHOOK"],
    "wecom":      ["WECOM_WEBHOOK"],
    "weixin":     ["WEIXIN_APP_ID", "WEIXIN_APP_SECRET"],
    "weibo":      ["WEIBO_ACCESS_TOKEN"],
    "yuque":      ["YUQUE_TOKEN"],
    "amap":       ["AMAP_KEY"],
    "zoom":       ["ZOOM_ACCOUNT_ID", "ZOOM_CLIENT_ID", "ZOOM_CLIENT_SECRET"],
    "teams":      ["TEAMS_WEBHOOK"],
}


def _hydrate_env_from_connections() -> set[str]:
    """Push stored credentials into os.environ so integration classes can find them.

    Returns the set of connection ids whose credentials were loaded.
    """
    db = get_db()
    loaded: set[str] = set()
    for conn in db.list_connections():
        if conn["status"] != "connected":
            continue
        decrypted = db.get_connection(conn["id"], decrypt=True)
        if not decrypted:
            continue
        token = decrypted.get("token")
        if not token:
            continue
        # Multi-key tokens are stored as "k1=v1\nk2=v2" — apply field-wise.
        env_vars = CONNECTION_ENV_MAP.get(conn["id"], [])
        if "=" in token and "\n" in token:
            for line in token.splitlines():
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()
        elif env_vars:
            os.environ[env_vars[0]] = token
        loaded.add(conn["id"])
    return loaded


def _derive_schema(fn: Callable) -> dict:
    """Build a JSON schema from a function signature + docstring."""
    try:
        hints = get_type_hints(fn)
    except Exception:  # noqa: BLE001
        hints = {}
    sig = inspect.signature(fn)
    props: dict[str, dict] = {}
    required: list[str] = []
    type_map = {str: "string", int: "integer", float: "number", bool: "boolean"}
    for pname, param in sig.parameters.items():
        if pname == "self":
            continue
        ptype = hints.get(pname, str)
        prop: dict[str, Any] = {"type": type_map.get(ptype, "string")}
        if param.default is inspect.Parameter.empty:
            required.append(pname)
        else:
            prop["default"] = param.default
        props[pname] = prop
    schema = {"type": "object", "properties": props}
    if required:
        schema["required"] = required
    return schema


class _MCPShim:
    """Quacks like FastMCP for the purposes of @mcp.tool() decoration."""

    def __init__(self, registry: ToolRegistry, connection_id: str, category: str):
        self.registry = registry
        self.connection_id = connection_id
        self.category = category

    def tool(self, *_a, **_k):
        def deco(fn: Callable) -> Callable:
            doc = inspect.getdoc(fn) or ""
            description = doc.split("\n\nArgs:")[0].strip() or fn.__name__
            try:
                self.registry.register(Tool(
                    name=fn.__name__,
                    description=description,
                    parameters=_derive_schema(fn),
                    handler=fn,
                    category=self.category,
                    requires=[self.connection_id],
                    danger="low",
                ))
            except ValueError:
                # Tool name clash — keep going so one bad apple doesn't kill the rest.
                pass
            return fn
        return deco


def register(reg: ToolRegistry) -> None:
    """Mount all configured integrations onto the new registry."""
    loaded = _hydrate_env_from_connections()
    try:
        from ..integrations import ALL_INTEGRATIONS
    except ImportError:
        return
    for integration in ALL_INTEGRATIONS:
        if integration.name not in loaded and not integration.is_configured():
            continue
        category = f"integration:{integration.name}"
        try:
            integration.register(_MCPShim(reg, integration.name, category))
        except Exception:  # noqa: BLE001
            # An integration's registration shouldn't be allowed to take down the server.
            continue
