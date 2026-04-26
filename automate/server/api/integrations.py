"""Integration / tool-connection management.

Two flavours of authentication:
- ``apikey`` — user pastes a token in the UI, we encrypt + store it.
- ``oauth`` — UI hits ``/api/integrations/<id>/connect`` to get an authorize
  URL, browser bounces through the provider, returns to ``/oauth/<id>/callback``
  (handled in ``oauth.py``).
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from ...oauth import OAuthFlow, get_oauth_spec
from ...oauth.flow import PendingState
from ...store import Vault
from ._deps import state

router = APIRouter(tags=["integrations"], prefix="/integrations")


# Built-in catalog so the UI knows what's installable even before any
# connection row exists.
INTEGRATION_CATALOG = [
    # SaaS — international
    {"id": "github",     "display_name": "GitHub",         "category": "DevOps",        "auth": "oauth"},
    {"id": "gitlab",     "display_name": "GitLab",         "category": "DevOps",        "auth": "apikey"},
    {"id": "notion",     "display_name": "Notion",         "category": "Productivity",  "auth": "oauth"},
    {"id": "slack",      "display_name": "Slack",          "category": "Messaging",     "auth": "oauth"},
    {"id": "linear",     "display_name": "Linear",         "category": "Project",       "auth": "oauth"},
    {"id": "jira",       "display_name": "Jira",           "category": "Project",       "auth": "apikey"},
    {"id": "confluence", "display_name": "Confluence",     "category": "Productivity",  "auth": "apikey"},
    {"id": "trello",     "display_name": "Trello",         "category": "Project",       "auth": "apikey"},
    {"id": "asana",      "display_name": "Asana",          "category": "Project",       "auth": "apikey"},
    {"id": "monday",     "display_name": "Monday.com",     "category": "Project",       "auth": "apikey"},
    {"id": "hubspot",    "display_name": "HubSpot",        "category": "CRM",           "auth": "apikey"},
    {"id": "airtable",   "display_name": "Airtable",       "category": "Productivity",  "auth": "apikey"},
    {"id": "stripe",     "display_name": "Stripe",         "category": "Payments",      "auth": "apikey"},
    {"id": "shopify",    "display_name": "Shopify",        "category": "Commerce",      "auth": "apikey"},
    {"id": "telegram",   "display_name": "Telegram",       "category": "Messaging",     "auth": "apikey"},
    {"id": "discord",    "display_name": "Discord",        "category": "Messaging",     "auth": "apikey"},
    {"id": "teams",      "display_name": "Microsoft Teams","category": "Messaging",     "auth": "apikey"},
    {"id": "zoom",       "display_name": "Zoom",           "category": "Meetings",      "auth": "apikey"},
    {"id": "twitter",    "display_name": "Twitter / X",    "category": "Social",        "auth": "apikey"},
    {"id": "sendgrid",   "display_name": "SendGrid",       "category": "Email",         "auth": "apikey"},
    {"id": "mailchimp",  "display_name": "Mailchimp",      "category": "Email",         "auth": "apikey"},
    {"id": "twilio",     "display_name": "Twilio",         "category": "SMS",           "auth": "apikey"},
    {"id": "sentry",     "display_name": "Sentry",         "category": "DevOps",        "auth": "apikey"},
    # SaaS — China
    {"id": "feishu",     "display_name": "飞书 / Lark",    "category": "Messaging",     "auth": "oauth"},
    {"id": "dingtalk",   "display_name": "钉钉",           "category": "Messaging",     "auth": "oauth"},
    {"id": "wecom",      "display_name": "企业微信",       "category": "Messaging",     "auth": "apikey"},
    {"id": "weixin",     "display_name": "微信公众号",     "category": "Messaging",     "auth": "apikey"},
    {"id": "weibo",      "display_name": "微博",           "category": "Social",        "auth": "apikey"},
    {"id": "gitee",      "display_name": "Gitee",          "category": "DevOps",        "auth": "apikey"},
    {"id": "yuque",      "display_name": "语雀",           "category": "Productivity",  "auth": "apikey"},
    {"id": "amap",       "display_name": "高德地图",       "category": "Location",      "auth": "apikey"},
]


class ApiKeyConnect(BaseModel):
    token: str
    metadata: dict | None = None


class OAuthAppCredentials(BaseModel):
    client_id: str
    client_secret: str


@router.get("/catalog")
def catalog():
    return INTEGRATION_CATALOG


@router.get("")
def list_connections(s=Depends(state)):
    by_id = {c["id"]: c for c in s.db.list_connections()}
    out = []
    for entry in INTEGRATION_CATALOG:
        row = by_id.get(entry["id"])
        out.append({
            **entry,
            "status": row["status"] if row else "disconnected",
            "token_set": bool(row and row["token_set"]),
            "metadata": json.loads(row["metadata_json"]) if row else {},
            "updated_at": row["updated_at"] if row else None,
        })
    return out


@router.post("/{cid}/apikey")
def connect_apikey(cid: str, body: ApiKeyConnect, s=Depends(state)):
    entry = next((e for e in INTEGRATION_CATALOG if e["id"] == cid), None)
    if not entry:
        raise HTTPException(404, "unknown integration")
    s.db.upsert_connection(
        id=cid, display_name=entry["display_name"], auth_kind="apikey",
        status="connected", token=body.token, metadata=body.metadata or {},
    )
    return {"ok": True}


@router.post("/{cid}/oauth-app")
def save_oauth_app(cid: str, body: OAuthAppCredentials, s=Depends(state)):
    """Stash the user's registered OAuth app credentials (client_id/secret)."""
    entry = next((e for e in INTEGRATION_CATALOG if e["id"] == cid), None)
    if not entry:
        raise HTTPException(404, "unknown integration")
    existing = s.db.get_connection(cid) or {}
    metadata = json.loads(existing.get("metadata_json", "{}")) if existing else {}
    metadata["client_id"] = body.client_id
    metadata["client_secret_enc"] = s.db.vault.encrypt(body.client_secret)
    s.db.upsert_connection(
        id=cid, display_name=entry["display_name"], auth_kind="oauth",
        status=existing.get("status", "disconnected"),
        metadata=metadata,
    )
    return {"ok": True}


@router.get("/{cid}/connect")
def begin_oauth(cid: str, request: Request, s=Depends(state)):
    spec = get_oauth_spec(cid)
    if not spec:
        raise HTTPException(404, "OAuth not supported for this integration; use /apikey")
    row = s.db.get_connection(cid)
    if not row:
        raise HTTPException(400, "Register your OAuth app credentials first.")
    metadata = json.loads(row["metadata_json"])
    client_id = metadata.get("client_id")
    client_secret_enc = metadata.get("client_secret_enc")
    if not client_id or not client_secret_enc:
        raise HTTPException(400, "Missing OAuth client_id/client_secret. POST /oauth-app first.")
    client_secret = s.db.vault.decrypt(client_secret_enc)

    redirect_uri = f"{request.base_url._url.rstrip('/')}/oauth/{cid}/callback"
    state_token = Vault.random_token()
    OAuthFlow.remember(state_token, PendingState(
        provider_id=cid, redirect_uri=redirect_uri,
        client_id=client_id, client_secret=client_secret, created_at=__import__("time").time(),
    ))
    url = OAuthFlow.authorize_url(spec, client_id=client_id, redirect_uri=redirect_uri, state=state_token)
    return {"authorize_url": url}


@router.post("/{cid}/disconnect")
def disconnect(cid: str, s=Depends(state)):
    s.db.delete_connection(cid)
    return {"ok": True}
