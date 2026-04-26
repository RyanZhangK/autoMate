"""Confluence (Atlassian) integration — pages, spaces, search."""
from __future__ import annotations
import base64
import json
import urllib.error
import urllib.parse
import urllib.request
from .base import BaseIntegration


class ConfluenceIntegration(BaseIntegration):
    name = "confluence"
    label = "Confluence (Atlassian)"
    env_vars = {
        "CONFLUENCE_EMAIL": "Atlassian account email",
        "CONFLUENCE_API_TOKEN": "Atlassian API token",
        "CONFLUENCE_BASE_URL": "Confluence base URL (e.g. https://myorg.atlassian.net)",
    }

    def _headers(self) -> dict:
        creds = base64.b64encode(
            f"{self.env('CONFLUENCE_EMAIL')}:{self.env('CONFLUENCE_API_TOKEN')}".encode()
        ).decode()
        return {"Authorization": f"Basic {creds}", "Accept": "application/json"}

    def _get(self, path: str, params: dict | None = None) -> dict:
        base = self.env("CONFLUENCE_BASE_URL").rstrip("/")
        url = f"{base}/wiki/rest/api/{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=self._headers())
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "msg": e.read().decode()}

    def _post(self, path: str, data: dict) -> dict:
        base = self.env("CONFLUENCE_BASE_URL").rstrip("/")
        url = f"{base}/wiki/rest/api/{path}"
        body = json.dumps(data).encode()
        h = {**self._headers(), "Content-Type": "application/json"}
        req = urllib.request.Request(url, data=body, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "msg": e.read().decode()}

    def register(self, mcp) -> None:
        ok = self.ok

        @mcp.tool()
        def confluence_search_pages(query: str, limit: int = 10) -> str:
            """Search Confluence pages by text. Returns matching pages."""
            return ok(self._get("search", {"cql": f"type=page AND text~\"{query}\"", "limit": limit}))

        @mcp.tool()
        def confluence_get_page(page_id: str) -> str:
            """Get a Confluence page by ID, including its body content."""
            return ok(self._get(f"content/{page_id}", {"expand": "body.storage,version,ancestors"}))

        @mcp.tool()
        def confluence_list_spaces(limit: int = 25) -> str:
            """List all Confluence spaces."""
            return ok(self._get("space", {"limit": limit}))

        @mcp.tool()
        def confluence_list_pages_in_space(space_key: str, limit: int = 25) -> str:
            """List pages in a specific Confluence space."""
            return ok(self._get("content", {"spaceKey": space_key, "type": "page", "limit": limit}))

        @mcp.tool()
        def confluence_create_page(space_key: str, title: str, content_html: str, parent_id: str = "") -> str:
            """Create a new Confluence page. content_html is the page body in HTML."""
            data: dict = {
                "type": "page",
                "title": title,
                "space": {"key": space_key},
                "body": {"storage": {"value": content_html, "representation": "storage"}},
            }
            if parent_id:
                data["ancestors"] = [{"id": parent_id}]
            return ok(self._post("content", data))
