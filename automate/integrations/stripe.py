"""Stripe integration — payments, customers, subscriptions."""
from __future__ import annotations
import urllib.parse
import urllib.request
import json
import os
from .base import BaseIntegration


class StripeIntegration(BaseIntegration):
    name = "stripe"
    label = "Stripe"
    env_vars = {"STRIPE_SECRET_KEY": "Stripe secret key (sk_live_... or sk_test_...)"}

    def _headers(self):
        return {"Authorization": f"Bearer {self.env('STRIPE_SECRET_KEY')}"}

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"https://api.stripe.com/v1/{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=self._headers())
        import urllib.error
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "msg": e.read().decode()}

    def _post_form(self, path: str, data: dict) -> dict:
        url = f"https://api.stripe.com/v1/{path}"
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body, headers={
            **self._headers(),
            "Content-Type": "application/x-www-form-urlencoded",
        })
        import urllib.error
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "msg": e.read().decode()}

    def register(self, mcp) -> None:
        ok = self.ok

        @mcp.tool()
        def stripe_get_balance() -> str:
            """Retrieve the current Stripe account balance."""
            return ok(self._get("balance"))

        @mcp.tool()
        def stripe_list_customers(limit: int = 10, email: str = "") -> str:
            """List Stripe customers. Optionally filter by email."""
            params: dict = {"limit": limit}
            if email:
                params["email"] = email
            return ok(self._get("customers", params))

        @mcp.tool()
        def stripe_create_customer(email: str, name: str = "", phone: str = "") -> str:
            """Create a new Stripe customer."""
            data: dict = {"email": email}
            if name:
                data["name"] = name
            if phone:
                data["phone"] = phone
            return ok(self._post_form("customers", data))

        @mcp.tool()
        def stripe_list_payments(limit: int = 10) -> str:
            """List recent Stripe payment intents."""
            return ok(self._get("payment_intents", {"limit": limit}))

        @mcp.tool()
        def stripe_list_products(limit: int = 10) -> str:
            """List Stripe products."""
            return ok(self._get("products", {"limit": limit, "active": "true"}))

        @mcp.tool()
        def stripe_get_customer(customer_id: str) -> str:
            """Get a specific Stripe customer by ID."""
            return ok(self._get(f"customers/{customer_id}"))

        @mcp.tool()
        def stripe_list_subscriptions(customer_id: str = "", limit: int = 10) -> str:
            """List Stripe subscriptions. Optionally filter by customer_id."""
            params: dict = {"limit": limit}
            if customer_id:
                params["customer"] = customer_id
            return ok(self._get("subscriptions", params))
