"""Notion integration."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"


class NotionIntegration(BaseIntegration):
    name = "notion"
    label = "Notion"
    env_vars = {
        "NOTION_API_KEY": "Integration token from notion.so/my-integrations",
    }

    def _auth(self) -> dict:
        return {
            "Authorization": f"Bearer {self.env('NOTION_API_KEY')}",
            "Notion-Version": VERSION,
        }

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def notion_search(query: str, filter_type: str = "") -> str:
            """
            Search Notion pages and databases.

            Args:
                query: Search query string.
                filter_type: Optional "page" or "database" to filter results.
            """
            body: dict = {"query": query}
            if filter_type in ("page", "database"):
                body["filter"] = {"value": filter_type, "property": "object"}
            r = integration.post(f"{API}/search", body, integration._auth())
            results = r.get("results", [])
            lines = [f"Found {len(results)} result(s):"]
            for item in results[:10]:
                title = ""
                props = item.get("properties", {})
                if "title" in props:
                    title_parts = props["title"].get("title", [])
                    title = "".join(t.get("plain_text", "") for t in title_parts)
                elif item.get("object") == "database":
                    db_title = item.get("title", [])
                    title = "".join(t.get("plain_text", "") for t in db_title)
                lines.append(f"  [{item['object']}] {title} — {item['id']}")
            return "\n".join(lines)

        @mcp.tool()
        def notion_create_page(parent_id: str, title: str, content: str = "") -> str:
            """
            Create a new Notion page.

            Args:
                parent_id: ID of the parent page or database.
                title: Page title.
                content: Optional plain text content for the first paragraph.
            """
            body: dict = {
                "parent": {"page_id": parent_id},
                "properties": {
                    "title": {"title": [{"text": {"content": title}}]}
                },
            }
            if content:
                body["children"] = [{
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"text": {"content": content}}]},
                }]
            r = integration.post(f"{API}/pages", body, integration._auth())
            return integration.ok({"id": r.get("id"), "url": r.get("url")})

        @mcp.tool()
        def notion_query_database(database_id: str, filter_json: str = "") -> str:
            """
            Query a Notion database.

            Args:
                database_id: Database ID.
                filter_json: Optional JSON filter string per Notion API spec.
            """
            import json
            body: dict = {}
            if filter_json:
                body["filter"] = json.loads(filter_json)
            r = integration.post(f"{API}/databases/{database_id}/query", body, integration._auth())
            results = r.get("results", [])
            lines = [f"Found {len(results)} row(s):"]
            for item in results[:20]:
                props = item.get("properties", {})
                name = next(
                    (
                        "".join(t.get("plain_text", "") for t in v.get("title", []))
                        for v in props.values()
                        if v.get("type") == "title"
                    ),
                    item["id"],
                )
                lines.append(f"  {name} — {item['id']}")
            return "\n".join(lines)

        @mcp.tool()
        def notion_append_block(page_id: str, content: str, block_type: str = "paragraph") -> str:
            """
            Append a block to an existing Notion page.

            Args:
                page_id: Target page ID.
                content: Text content to append.
                block_type: "paragraph", "heading_1", "heading_2", "bulleted_list_item", "to_do".
            """
            block: dict = {
                "object": "block",
                "type": block_type,
                block_type: {"rich_text": [{"text": {"content": content}}]},
            }
            if block_type == "to_do":
                block[block_type]["checked"] = False
            r = integration.patch(
                f"{API}/blocks/{page_id}/children",
                {"children": [block]},
                integration._auth(),
            )
            return integration.ok(r)
