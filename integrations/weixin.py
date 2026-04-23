"""微信公众号 (WeChat Official Account) integration."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://api.weixin.qq.com/cgi-bin"


class WeixinIntegration(BaseIntegration):
    name = "weixin"
    label = "微信公众号 (WeChat Official Account)"
    env_vars = {
        "WEIXIN_APP_ID": "公众号 AppID from mp.weixin.qq.com",
        "WEIXIN_APP_SECRET": "公众号 AppSecret from mp.weixin.qq.com",
    }

    def _token(self) -> str:
        r = self.get(
            f"{API}/token?grant_type=client_credential"
            f"&appid={self.env('WEIXIN_APP_ID')}"
            f"&secret={self.env('WEIXIN_APP_SECRET')}"
        )
        return r.get("access_token", "")

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def weixin_send_template_message(openid: str, template_id: str, data: str, url: str = "") -> str:
            """
            Send a template message to a WeChat follower.

            Args:
                openid: Follower's OpenID.
                template_id: Template ID from WeChat MP platform.
                data: JSON string of template data, e.g. '{"key1":{"value":"text"}}'.
                url: Optional URL to open when user taps the message.
            """
            import json
            token = integration._token()
            body: dict = {
                "touser": openid,
                "template_id": template_id,
                "data": json.loads(data),
            }
            if url:
                body["url"] = url
            r = integration.post(f"{API}/message/template/send?access_token={token}", body)
            return integration.ok(r)

        @mcp.tool()
        def weixin_get_followers() -> str:
            """Get the list of followers (OpenIDs) for the WeChat Official Account."""
            token = integration._token()
            r = integration.get(f"{API}/user/get?access_token={token}")
            return integration.ok(r)

        @mcp.tool()
        def weixin_get_user_info(openid: str) -> str:
            """
            Get profile information for a WeChat follower.

            Args:
                openid: Follower's OpenID.
            """
            token = integration._token()
            r = integration.get(
                f"{API}/user/info?access_token={token}&openid={openid}&lang=zh_CN"
            )
            return integration.ok(r)
