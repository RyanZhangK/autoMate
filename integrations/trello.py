"""Trello integration."""
from __future__ import annotations
import urllib.parse
from .base import BaseIntegration

API = "https://api.trello.com/1"


class TrelloIntegration(BaseIntegration):
    name = "trello"
    label = "Trello"
    env_vars = {
        "TRELLO_API_KEY": "API key from trello.com/power-ups/admin",
        "TRELLO_TOKEN": "Token generated from trello.com/1/authorize?...",
    }

    def _auth_params(self) -> str:
        return urllib.parse.urlencode({"key": self.env("TRELLO_API_KEY"), "token": self.env("TRELLO_TOKEN")})

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def trello_list_boards() -> str:
            """List all Trello boards for the authenticated member."""
            r = integration.get(f"{API}/members/me/boards?fields=name,shortUrl&{integration._auth_params()}")
            boards = r if isinstance(r, list) else []
            lines = [f"Found {len(boards)} board(s):"]
            for b in boards:
                lines.append(f"  [{b['id']}] {b['name']} — {b.get('shortUrl')}")
            return "\n".join(lines)

        @mcp.tool()
        def trello_list_cards(board_id: str) -> str:
            """
            List all cards on a Trello board.

            Args:
                board_id: Trello board ID (from trello_list_boards).
            """
            r = integration.get(f"{API}/boards/{board_id}/cards?{integration._auth_params()}")
            cards = r if isinstance(r, list) else []
            lines = [f"Found {len(cards)} card(s):"]
            for c in cards:
                lines.append(f"  [{c['id']}] {c['name']} — {c.get('shortUrl')}")
            return "\n".join(lines)

        @mcp.tool()
        def trello_create_card(list_id: str, name: str, desc: str = "", due: str = "") -> str:
            """
            Create a new Trello card.

            Args:
                list_id: Target list ID (get from trello_list_lists).
                name: Card name.
                desc: Card description (Markdown).
                due: Due date in ISO format (e.g. "2025-12-31T00:00:00.000Z").
            """
            params: dict = {"idList": list_id, "name": name, "desc": desc,
                            "key": integration.env("TRELLO_API_KEY"), "token": integration.env("TRELLO_TOKEN")}
            if due:
                params["due"] = due
            r = integration.post(f"{API}/cards", params)
            return integration.ok({"id": r.get("id"), "name": r.get("name"), "url": r.get("shortUrl")})

        @mcp.tool()
        def trello_list_lists(board_id: str) -> str:
            """
            List all lists (columns) on a Trello board.

            Args:
                board_id: Trello board ID.
            """
            r = integration.get(f"{API}/boards/{board_id}/lists?{integration._auth_params()}")
            lists = r if isinstance(r, list) else []
            lines = [f"Found {len(lists)} list(s):"]
            for l in lists:
                lines.append(f"  [{l['id']}] {l['name']}")
            return "\n".join(lines)
