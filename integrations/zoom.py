"""Zoom meeting integration."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://api.zoom.us/v2"


class ZoomIntegration(BaseIntegration):
    name = "zoom"
    label = "Zoom"
    env_vars = {
        "ZOOM_ACCOUNT_ID": "Account ID from marketplace.zoom.us app credentials",
        "ZOOM_CLIENT_ID": "Client ID from marketplace.zoom.us app credentials",
        "ZOOM_CLIENT_SECRET": "Client secret from marketplace.zoom.us app credentials",
    }

    def _get_token(self) -> str:
        import base64, urllib.request, json, urllib.parse
        credentials = base64.b64encode(
            f"{self.env('ZOOM_CLIENT_ID')}:{self.env('ZOOM_CLIENT_SECRET')}".encode()
        ).decode()
        data = urllib.parse.urlencode({
            "grant_type": "account_credentials",
            "account_id": self.env("ZOOM_ACCOUNT_ID"),
        }).encode()
        req = urllib.request.Request(
            "https://zoom.us/oauth/token",
            data=data,
            headers={"Authorization": f"Basic {credentials}", "Content-Type": "application/x-www-form-urlencoded"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode()).get("access_token", "")

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def zoom_create_meeting(topic: str, duration: int = 60, start_time: str = "") -> str:
            """
            Create a Zoom meeting.

            Args:
                topic: Meeting topic/title.
                duration: Meeting duration in minutes (default 60).
                start_time: Meeting start time in ISO 8601 UTC (e.g. "2025-12-01T09:00:00Z"). Empty = instant meeting.
            """
            token = integration._get_token()
            headers = {"Authorization": f"Bearer {token}"}
            payload: dict = {"topic": topic, "type": 1 if not start_time else 2, "duration": duration}
            if start_time:
                payload["start_time"] = start_time
                payload["timezone"] = "UTC"
            r = integration.post(f"{API}/users/me/meetings", payload, headers)
            return integration.ok({
                "id": r.get("id"),
                "topic": r.get("topic"),
                "join_url": r.get("join_url"),
                "start_time": r.get("start_time"),
                "duration": r.get("duration"),
            })

        @mcp.tool()
        def zoom_list_meetings(limit: int = 10) -> str:
            """
            List upcoming scheduled Zoom meetings.

            Args:
                limit: Max meetings to return (default 10).
            """
            import urllib.parse
            token = integration._get_token()
            headers = {"Authorization": f"Bearer {token}"}
            params = urllib.parse.urlencode({"type": "scheduled", "page_size": limit})
            r = integration.get(f"{API}/users/me/meetings?{params}", headers)
            meetings = r.get("meetings", [])
            lines = [f"Found {len(meetings)} meeting(s):"]
            for m in meetings:
                lines.append(f"  [{m['id']}] {m['topic']} — {m.get('start_time', 'instant')} ({m.get('duration')} min)")
            return "\n".join(lines)

        @mcp.tool()
        def zoom_get_meeting(meeting_id: str) -> str:
            """
            Get Zoom meeting details.

            Args:
                meeting_id: Zoom meeting ID.
            """
            token = integration._get_token()
            headers = {"Authorization": f"Bearer {token}"}
            r = integration.get(f"{API}/meetings/{meeting_id}", headers)
            return integration.ok({
                "id": r.get("id"),
                "topic": r.get("topic"),
                "status": r.get("status"),
                "start_time": r.get("start_time"),
                "duration": r.get("duration"),
                "join_url": r.get("join_url"),
                "password": r.get("password"),
            })
