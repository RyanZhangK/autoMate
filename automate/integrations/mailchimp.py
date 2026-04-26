"""Mailchimp email marketing integration."""
from __future__ import annotations
import base64
import urllib.parse
from .base import BaseIntegration


class MailchimpIntegration(BaseIntegration):
    name = "mailchimp"
    label = "Mailchimp"
    env_vars = {
        "MAILCHIMP_API_KEY": "API key from mailchimp.com/account/api/ (ends with -us1, -us6, etc.)",
    }

    def _api(self, path: str) -> str:
        key = self.env("MAILCHIMP_API_KEY")
        dc = key.split("-")[-1] if "-" in key else "us1"
        return f"https://{dc}.api.mailchimp.com/3.0{path}"

    def _auth(self) -> dict:
        encoded = base64.b64encode(f"anystring:{self.env('MAILCHIMP_API_KEY')}".encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def mailchimp_list_audiences() -> str:
            """List all Mailchimp audiences (mailing lists)."""
            r = integration.get(integration._api("/lists?count=20"), integration._auth())
            lists = r.get("lists", [])
            lines = [f"Found {len(lists)} audience(s):"]
            for l in lists:
                stats = l.get("stats", {})
                lines.append(
                    f"  [{l['id']}] {l['name']} — "
                    f"{stats.get('member_count',0)} members, "
                    f"{stats.get('open_rate',0):.1%} open rate"
                )
            return "\n".join(lines)

        @mcp.tool()
        def mailchimp_add_subscriber(list_id: str, email: str, first_name: str = "", last_name: str = "") -> str:
            """
            Add or update a subscriber in a Mailchimp audience.

            Args:
                list_id: Audience/list ID (from mailchimp_list_audiences).
                email: Subscriber email address.
                first_name: First name (optional).
                last_name: Last name (optional).
            """
            import hashlib
            email_hash = hashlib.md5(email.lower().encode()).hexdigest()
            payload: dict = {"email_address": email, "status": "subscribed"}
            if first_name or last_name:
                payload["merge_fields"] = {}
                if first_name: payload["merge_fields"]["FNAME"] = first_name
                if last_name: payload["merge_fields"]["LNAME"] = last_name
            r = integration.put(
                integration._api(f"/lists/{list_id}/members/{email_hash}"),
                payload,
                integration._auth(),
            )
            return integration.ok({"id": r.get("id"), "email": r.get("email_address"), "status": r.get("status")})

        @mcp.tool()
        def mailchimp_list_campaigns(limit: int = 10) -> str:
            """
            List recent Mailchimp campaigns.

            Args:
                limit: Max campaigns to return (default 10).
            """
            params = urllib.parse.urlencode({"count": limit, "sort_field": "create_time", "sort_dir": "DESC"})
            r = integration.get(integration._api(f"/campaigns?{params}"), integration._auth())
            campaigns = r.get("campaigns", [])
            lines = [f"Found {len(campaigns)} campaign(s):"]
            for c in campaigns:
                settings = c.get("settings", {})
                lines.append(
                    f"  [{c['id']}] [{c['status']}] {settings.get('subject_line','(no subject)')} "
                    f"— sent: {c.get('emails_sent',0)}"
                )
            return "\n".join(lines)
