"""Monday.com integration — boards, items, columns."""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from .base import BaseIntegration


class MondayIntegration(BaseIntegration):
    name = "monday"
    label = "Monday.com"
    env_vars = {"MONDAY_API_KEY": "Monday.com API key"}

    def _graphql(self, query: str, variables: dict | None = None) -> dict:
        url = "https://api.monday.com/v2"
        payload: dict = {"query": query}
        if variables:
            payload["variables"] = variables
        body = json.dumps(payload).encode()
        req = urllib.request.Request(url, data=body, headers={
            "Authorization": self.env("MONDAY_API_KEY"),
            "Content-Type": "application/json",
            "API-Version": "2024-01",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "msg": e.read().decode()}

    def register(self, mcp) -> None:
        ok = self.ok

        @mcp.tool()
        def monday_list_boards(limit: int = 10) -> str:
            """List Monday.com boards."""
            q = f"{{ boards(limit: {limit}) {{ id name description state }} }}"
            return ok(self._graphql(q))

        @mcp.tool()
        def monday_list_items(board_id: str, limit: int = 20) -> str:
            """List items (rows) on a Monday.com board."""
            q = f"""{{
              boards(ids: [{board_id}]) {{
                items_page(limit: {limit}) {{
                  items {{
                    id name state
                    column_values {{ id text }}
                  }}
                }}
              }}
            }}"""
            return ok(self._graphql(q))

        @mcp.tool()
        def monday_create_item(board_id: str, item_name: str, group_id: str = "") -> str:
            """Create a new item (row) on a Monday.com board."""
            q = """mutation($board_id: ID!, $item_name: String!, $group_id: String) {
              create_item(board_id: $board_id, item_name: $item_name, group_id: $group_id) {
                id name
              }
            }"""
            variables: dict = {"board_id": board_id, "item_name": item_name}
            if group_id:
                variables["group_id"] = group_id
            return ok(self._graphql(q, variables))

        @mcp.tool()
        def monday_get_item(item_id: str) -> str:
            """Get a specific Monday.com item by ID."""
            q = f"""{{
              items(ids: [{item_id}]) {{
                id name state board {{ id name }}
                column_values {{ id title text }}
              }}
            }}"""
            return ok(self._graphql(q))

        @mcp.tool()
        def monday_list_groups(board_id: str) -> str:
            """List groups (sections) on a Monday.com board."""
            q = f"{{ boards(ids: [{board_id}]) {{ groups {{ id title color }} }} }}"
            return ok(self._graphql(q))
