"""Telegram Bot integration."""
from __future__ import annotations
from .base import BaseIntegration


class TelegramIntegration(BaseIntegration):
    name = "telegram"
    label = "Telegram"
    env_vars = {
        "TELEGRAM_BOT_TOKEN": "Bot token from @BotFather on Telegram",
    }

    def _api(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.env('TELEGRAM_BOT_TOKEN')}/{method}"

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def telegram_send_message(chat_id: str, text: str, parse_mode: str = "Markdown") -> str:
            """
            Send a message via Telegram bot.

            Args:
                chat_id: Chat ID or @username.
                text: Message text.
                parse_mode: "Markdown" (default) or "HTML".
            """
            r = integration.post(integration._api("sendMessage"), {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
            })
            return integration.ok({"ok": r.get("ok"), "message_id": r.get("result", {}).get("message_id")})

        @mcp.tool()
        def telegram_send_photo(chat_id: str, photo_url: str, caption: str = "") -> str:
            """
            Send a photo via Telegram bot.

            Args:
                chat_id: Chat ID or @username.
                photo_url: URL of the photo to send.
                caption: Optional caption text.
            """
            r = integration.post(integration._api("sendPhoto"), {
                "chat_id": chat_id,
                "photo": photo_url,
                "caption": caption,
            })
            return integration.ok({"ok": r.get("ok")})

        @mcp.tool()
        def telegram_get_updates(limit: int = 10) -> str:
            """
            Get recent messages received by the Telegram bot.

            Args:
                limit: Max number of updates to retrieve (default 10).
            """
            r = integration.get(f"{integration._api('getUpdates')}?limit={limit}")
            updates = r.get("result", [])
            lines = [f"{len(updates)} update(s):"]
            for u in updates:
                msg = u.get("message", {})
                sender = msg.get("from", {}).get("username", "?")
                text = msg.get("text", "")
                lines.append(f"  @{sender}: {text[:100]}")
            return "\n".join(lines)

        @mcp.tool()
        def telegram_get_bot_info() -> str:
            """Get basic info about the Telegram bot."""
            r = integration.get(integration._api("getMe"))
            bot = r.get("result", {})
            return integration.ok({
                "id": bot.get("id"),
                "username": bot.get("username"),
                "name": bot.get("first_name"),
            })
