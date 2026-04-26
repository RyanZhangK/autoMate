"""钉钉 (DingTalk) integration — Webhook robot."""
from __future__ import annotations
import hashlib
import hmac
import time
import base64
import urllib.parse
from .base import BaseIntegration


class DingTalkIntegration(BaseIntegration):
    name = "dingtalk"
    label = "钉钉 (DingTalk)"
    env_vars = {
        "DINGTALK_WEBHOOK": "Group robot webhook URL (from DingTalk group settings)",
        "DINGTALK_SECRET": "Robot signing secret (optional but recommended)",
    }

    def _signed_url(self) -> str:
        url = self.env("DINGTALK_WEBHOOK")
        secret = self.env("DINGTALK_SECRET")
        if not secret:
            return url
        ts = str(round(time.time() * 1000))
        sign_str = f"{ts}\n{secret}"
        sig = base64.b64encode(
            hmac.new(secret.encode(), sign_str.encode(), digestmod=hashlib.sha256).digest()
        ).decode()
        return f"{url}&timestamp={ts}&sign={urllib.parse.quote_plus(sig)}"

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def dingtalk_send_text(content: str, at_all: bool = False) -> str:
            """
            Send a text message to a 钉钉 group via webhook robot.

            Args:
                content: Message text.
                at_all: Whether to @all members.
            """
            r = integration.post(integration._signed_url(), {
                "msgtype": "text",
                "text": {"content": content},
                "at": {"isAtAll": at_all},
            })
            return integration.ok(r)

        @mcp.tool()
        def dingtalk_send_markdown(title: str, text: str) -> str:
            """
            Send a Markdown message to a 钉钉 group via webhook robot.

            Args:
                title: Card title (shown in notification).
                text: Markdown body content.
            """
            r = integration.post(integration._signed_url(), {
                "msgtype": "markdown",
                "markdown": {"title": title, "text": text},
            })
            return integration.ok(r)

        @mcp.tool()
        def dingtalk_send_link(title: str, text: str, url: str, pic_url: str = "") -> str:
            """
            Send a link card to a 钉钉 group.

            Args:
                title: Link title.
                text: Link description.
                url: Target URL.
                pic_url: Optional thumbnail image URL.
            """
            r = integration.post(integration._signed_url(), {
                "msgtype": "link",
                "link": {"title": title, "text": text, "messageUrl": url, "picUrl": pic_url},
            })
            return integration.ok(r)
