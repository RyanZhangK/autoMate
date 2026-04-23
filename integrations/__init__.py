"""Integration auto-discovery and registration."""
from __future__ import annotations

# Chinese platforms
from .feishu import FeishuIntegration
from .dingtalk import DingTalkIntegration
from .wecom import WeComIntegration
from .weixin import WeixinIntegration
from .weibo import WeiboIntegration
from .gitee import GiteeIntegration
from .yuque import YuqueIntegration
from .amap import AmapIntegration

# International messaging & collaboration
from .slack import SlackIntegration
from .telegram import TelegramIntegration
from .discord import DiscordIntegration
from .teams import TeamsIntegration
from .zoom import ZoomIntegration

# DevOps & code hosting
from .github_api import GitHubIntegration
from .gitlab import GitLabIntegration
from .sentry import SentryIntegration

# Project management
from .notion import NotionIntegration
from .airtable import AirtableIntegration
from .linear import LinearIntegration
from .jira import JiraIntegration
from .trello import TrelloIntegration
from .hubspot import HubSpotIntegration

# Communication & marketing
from .twitter import TwitterIntegration
from .sendgrid import SendGridIntegration
from .twilio import TwilioIntegration
from .mailchimp import MailchimpIntegration

# Payments & e-commerce
from .stripe import StripeIntegration
from .shopify import ShopifyIntegration

# Additional project management & knowledge
from .confluence import ConfluenceIntegration
from .asana import AsanaIntegration
from .monday import MondayIntegration

ALL_INTEGRATIONS = [
    # Chinese
    FeishuIntegration(),
    DingTalkIntegration(),
    WeComIntegration(),
    WeixinIntegration(),
    WeiboIntegration(),
    GiteeIntegration(),
    YuqueIntegration(),
    AmapIntegration(),
    # Messaging & collaboration
    SlackIntegration(),
    TelegramIntegration(),
    DiscordIntegration(),
    TeamsIntegration(),
    ZoomIntegration(),
    # DevOps
    GitHubIntegration(),
    GitLabIntegration(),
    SentryIntegration(),
    # Project management & knowledge
    NotionIntegration(),
    AirtableIntegration(),
    LinearIntegration(),
    JiraIntegration(),
    ConfluenceIntegration(),
    TrelloIntegration(),
    AsanaIntegration(),
    MondayIntegration(),
    HubSpotIntegration(),
    # Payments & e-commerce
    StripeIntegration(),
    ShopifyIntegration(),
    # Communication & marketing
    TwitterIntegration(),
    SendGridIntegration(),
    TwilioIntegration(),
    MailchimpIntegration(),
]


def register_all(mcp) -> list[str]:
    """Register all configured integrations. Returns list of activated integration labels."""
    registered = []
    for integration in ALL_INTEGRATIONS:
        if integration.is_configured():
            integration.register(mcp)
            registered.append(integration.label)
    return registered


def get_configured_summary() -> str:
    """Return a human-readable summary of which integrations are active."""
    configured = [i for i in ALL_INTEGRATIONS if i.is_configured()]
    unconfigured = [i for i in ALL_INTEGRATIONS if not i.is_configured()]
    lines = []
    if configured:
        lines.append(f"Active ({len(configured)}): " + ", ".join(i.label for i in configured))
    if unconfigured:
        lines.append(f"Inactive ({len(unconfigured)}): " + ", ".join(i.label for i in unconfigured))
    return "\n".join(lines) if lines else "No integrations configured."
