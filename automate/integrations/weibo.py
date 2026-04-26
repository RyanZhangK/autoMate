"""微博 (Weibo) integration."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://api.weibo.com/2"


class WeiboIntegration(BaseIntegration):
    name = "weibo"
    label = "微博 (Weibo)"
    env_vars = {
        "WEIBO_ACCESS_TOKEN": "OAuth2 access token from open.weibo.com",
    }

    def _auth(self) -> dict:
        return {"Authorization": f"OAuth2 {self.env('WEIBO_ACCESS_TOKEN')}"}

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def weibo_post(text: str) -> str:
            """
            Post a new Weibo (微博).

            Args:
                text: Weibo content (max 140 Chinese characters).
            """
            import urllib.parse
            url = f"{API}/statuses/update.json"
            data = urllib.parse.urlencode({"status": text, "access_token": integration.env("WEIBO_ACCESS_TOKEN")}).encode()
            import urllib.request, json
            req = urllib.request.Request(url, data=data)
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                return integration.ok({"error": str(e)})

        @mcp.tool()
        def weibo_get_timeline(count: int = 20) -> str:
            """
            Get your Weibo home timeline.

            Args:
                count: Number of posts to retrieve (max 100).
            """
            token = integration.env("WEIBO_ACCESS_TOKEN")
            r = integration.get(f"{API}/statuses/home_timeline.json?access_token={token}&count={count}")
            return integration.ok(r)

        @mcp.tool()
        def weibo_get_my_info() -> str:
            """Get current user's Weibo profile."""
            token = integration.env("WEIBO_ACCESS_TOKEN")
            r = integration.get(f"{API}/account/get_uid.json?access_token={token}")
            uid = r.get("uid", "")
            if uid:
                info = integration.get(f"{API}/users/show.json?access_token={token}&uid={uid}")
                return integration.ok(info)
            return integration.ok(r)
