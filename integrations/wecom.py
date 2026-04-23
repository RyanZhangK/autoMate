"""企业微信 (WeCom / WeChat Work) integration."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://qyapi.weixin.qq.com/cgi-bin"


class WeComIntegration(BaseIntegration):
    name = "wecom"
    label = "企业微信 (WeCom)"
    env_vars = {
        "WECOM_CORP_ID": "企业ID (corpid) from WeCom admin console",
        "WECOM_CORP_SECRET": "应用 Secret from WeCom app settings",
        "WECOM_AGENT_ID": "应用 AgentID from WeCom app settings",
    }

    def _token(self) -> str:
        r = self.get(
            f"{API}/gettoken?corpid={self.env('WECOM_CORP_ID')}"
            f"&corpsecret={self.env('WECOM_CORP_SECRET')}"
        )
        return r.get("access_token", "")

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def wecom_send_text(content: str, to_user: str = "@all") -> str:
            """
            Send a text message via 企业微信.

            Args:
                content: Message text.
                to_user: User IDs separated by | or "@all" for everyone.
            """
            token = integration._token()
            r = integration.post(
                f"{API}/message/send?access_token={token}",
                {
                    "touser": to_user,
                    "msgtype": "text",
                    "agentid": int(integration.env("WECOM_AGENT_ID")),
                    "text": {"content": content},
                },
            )
            return integration.ok(r)

        @mcp.tool()
        def wecom_send_markdown(content: str, to_user: str = "@all") -> str:
            """
            Send a Markdown message via 企业微信.

            Args:
                content: Markdown content.
                to_user: User IDs separated by | or "@all".
            """
            token = integration._token()
            r = integration.post(
                f"{API}/message/send?access_token={token}",
                {
                    "touser": to_user,
                    "msgtype": "markdown",
                    "agentid": int(integration.env("WECOM_AGENT_ID")),
                    "markdown": {"content": content},
                },
            )
            return integration.ok(r)

        @mcp.tool()
        def wecom_get_department_users(department_id: int = 1) -> str:
            """
            Get user list from a 企业微信 department.

            Args:
                department_id: Department ID (1 = root).
            """
            token = integration._token()
            r = integration.get(
                f"{API}/user/simplelist?access_token={token}"
                f"&department_id={department_id}&fetch_child=1"
            )
            return integration.ok(r)
