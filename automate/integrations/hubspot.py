"""HubSpot CRM integration."""
from __future__ import annotations
from .base import BaseIntegration

API = "https://api.hubapi.com"


class HubSpotIntegration(BaseIntegration):
    name = "hubspot"
    label = "HubSpot"
    env_vars = {
        "HUBSPOT_ACCESS_TOKEN": "Private app access token from app.hubspot.com/private-apps",
    }

    def _auth(self) -> dict:
        return {"Authorization": f"Bearer {self.env('HUBSPOT_ACCESS_TOKEN')}"}

    def register(self, mcp) -> None:
        integration = self

        @mcp.tool()
        def hubspot_create_contact(email: str, firstname: str = "", lastname: str = "", company: str = "", phone: str = "") -> str:
            """
            Create a HubSpot contact.

            Args:
                email: Contact email address.
                firstname: First name.
                lastname: Last name.
                company: Company name.
                phone: Phone number.
            """
            props = {"email": email}
            if firstname: props["firstname"] = firstname
            if lastname: props["lastname"] = lastname
            if company: props["company"] = company
            if phone: props["phone"] = phone
            r = integration.post(f"{API}/crm/v3/objects/contacts", {"properties": props}, integration._auth())
            return integration.ok({"id": r.get("id"), "email": email})

        @mcp.tool()
        def hubspot_search_contacts(query: str, limit: int = 10) -> str:
            """
            Search HubSpot contacts by name, email, or company.

            Args:
                query: Search query string.
                limit: Max results (default 10).
            """
            r = integration.post(
                f"{API}/crm/v3/objects/contacts/search",
                {"query": query, "limit": limit, "properties": ["email", "firstname", "lastname", "company"]},
                integration._auth(),
            )
            results = r.get("results", [])
            lines = [f"Found {r.get('total', len(results))} contact(s):"]
            for c in results:
                props = c.get("properties", {})
                name = f"{props.get('firstname','')} {props.get('lastname','')}".strip()
                lines.append(f"  [{c['id']}] {name} — {props.get('email','')} ({props.get('company','')})")
            return "\n".join(lines)

        @mcp.tool()
        def hubspot_create_deal(name: str, stage: str = "appointmentscheduled", amount: str = "") -> str:
            """
            Create a HubSpot deal.

            Args:
                name: Deal name.
                stage: Pipeline stage ID (default "appointmentscheduled").
                amount: Deal amount (optional).
            """
            props: dict = {"dealname": name, "dealstage": stage, "pipeline": "default"}
            if amount:
                props["amount"] = amount
            r = integration.post(f"{API}/crm/v3/objects/deals", {"properties": props}, integration._auth())
            return integration.ok({"id": r.get("id"), "name": name, "stage": stage})

        @mcp.tool()
        def hubspot_list_deals(limit: int = 20) -> str:
            """
            List recent HubSpot deals.

            Args:
                limit: Max deals to return (default 20).
            """
            import urllib.parse
            params = urllib.parse.urlencode({"limit": limit, "properties": "dealname,dealstage,amount,closedate"})
            r = integration.get(f"{API}/crm/v3/objects/deals?{params}", integration._auth())
            deals = r.get("results", [])
            lines = [f"Found {len(deals)} deal(s):"]
            for d in deals:
                props = d.get("properties", {})
                lines.append(f"  [{d['id']}] {props.get('dealname')} — stage: {props.get('dealstage')} amount: {props.get('amount','?')}")
            return "\n".join(lines)
