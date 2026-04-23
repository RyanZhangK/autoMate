"""Integration auto-discovery and registration."""
from __future__ import annotations

from .feishu import FeishuIntegration
from .dingtalk import DingTalkIntegration
from .wecom import WeComIntegration
from .weixin import WeixinIntegration
from .weibo import WeiboIntegration
from .notion import NotionIntegration
from .slack import SlackIntegration
from .github_api import GitHubIntegration
from .telegram import TelegramIntegration
from .discord import DiscordIntegration
from .twitter import TwitterIntegration
from .airtable import AirtableIntegration
from .linear import LinearIntegration
from .jira import JiraIntegration

ALL_INTEGRATIONS = [
    FeishuIntegration(),
    DingTalkIntegration(),
    WeComIntegration(),
    WeixinIntegration(),
    WeiboIntegration(),
    NotionIntegration(),
    SlackIntegration(),
    GitHubIntegration(),
    TelegramIntegration(),
    DiscordIntegration(),
    TwitterIntegration(),
    AirtableIntegration(),
    LinearIntegration(),
    JiraIntegration(),
]


def register_all(mcp) -> list[str]:
    """Register all configured integrations with the MCP server. Returns list of registered integration names."""
    registered = []
    for integration in ALL_INTEGRATIONS:
        if integration.is_configured():
            integration.register(mcp)
            registered.append(integration.label)
    return registered


def get_configured_summary() -> str:
    """Return a human-readable summary of which integrations are configured."""
    configured = [i for i in ALL_INTEGRATIONS if i.is_configured()]
    unconfigured = [i for i in ALL_INTEGRATIONS if not i.is_configured()]
    lines = []
    if configured:
        lines.append(f"Active ({len(configured)}): " + ", ".join(i.label for i in configured))
    if unconfigured:
        lines.append(f"Inactive ({len(unconfigured)}): " + ", ".join(i.label for i in unconfigured))
    return "\n".join(lines) if lines else "No integrations configured."
