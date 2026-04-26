"""Slack integration."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://slack.com/api"


class SlackIntegration(BaseIntegration):
    name = "slack"
    label = "Slack"
    env_vars = {
        "SLACK_BOT_TOKEN": "Bot User OAuth Token (xoxb-...) from api.slack.com/apps",
    }

    def _auth(self) -> dict:
        return {"Authorization": f"Bearer {self.env('SLACK_BOT_TOKEN')}"}

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def slack_send_message(channel: str, text: str) -> str:
            """
            Send a message to a Slack channel.

            Args:
                channel: Channel ID or name (e.g. "#general" or "C01234ABC").
                text: Message text (supports mrkdwn formatting).
            """
            r = integration.post(
                f"{API}/chat.postMessage",
                {"channel": channel, "text": text},
                integration._auth(),
            )
            if not r.get("ok"):
                return f"Error: {r.get('error')}"
            return f"Sent to {r['channel']} at ts={r['message']['ts']}"

        @mcp.tool()
        def slack_list_channels(limit: int = 50) -> str:
            """
            List public Slack channels.

            Args:
                limit: Maximum number of channels to return (default 50).
            """
            r = integration.get(
                f"{API}/conversations.list?limit={limit}&exclude_archived=true",
                integration._auth(),
            )
            channels = r.get("channels", [])
            lines = [f"Found {len(channels)} channel(s):"]
            for c in channels:
                lines.append(f"  #{c['name']} — {c['id']} ({c.get('num_members',0)} members)")
            return "\n".join(lines)

        @mcp.tool()
        def slack_get_messages(channel: str, limit: int = 20) -> str:
            """
            Get recent messages from a Slack channel.

            Args:
                channel: Channel ID.
                limit: Number of messages to retrieve (default 20).
            """
            r = integration.get(
                f"{API}/conversations.history?channel={channel}&limit={limit}",
                integration._auth(),
            )
            messages = r.get("messages", [])
            lines = [f"{len(messages)} message(s) from {channel}:"]
            for m in messages:
                user = m.get("user", m.get("bot_id", "?"))
                lines.append(f"  [{user}] {m.get('text', '')[:120]}")
            return "\n".join(lines)

        @mcp.tool()
        def slack_reply_thread(channel: str, thread_ts: str, text: str) -> str:
            """
            Reply to a Slack thread.

            Args:
                channel: Channel ID.
                thread_ts: Timestamp of the parent message (from slack_get_messages).
                text: Reply text.
            """
            r = integration.post(
                f"{API}/chat.postMessage",
                {"channel": channel, "thread_ts": thread_ts, "text": text},
                integration._auth(),
            )
            return integration.ok({"ok": r.get("ok"), "error": r.get("error")})
