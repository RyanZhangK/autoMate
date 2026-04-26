"""Authorization-code OAuth helper.

A typical click-to-connect flow:

1. UI calls ``GET /api/integrations/<id>/connect`` → server builds an authorize
   URL with a one-time ``state`` token, stashes it in ``OAuthFlow.PENDING``,
   redirects the browser.
2. Provider redirects back to ``/oauth/<id>/callback?code=...&state=...``. The
   server verifies state, calls :func:`exchange_code`, and writes the resulting
   token into the ``connections`` table (encrypted).
3. UI polls ``GET /api/integrations/<id>`` to see the connected status.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass

from ..store import Vault
from .catalog import OAuthSpec


@dataclass
class PendingState:
    provider_id: str
    redirect_uri: str
    client_id: str
    client_secret: str
    created_at: float


class OAuthFlow:
    PENDING: dict[str, PendingState] = {}

    @classmethod
    def remember(cls, state: str, ps: PendingState) -> None:
        cls._gc()
        cls.PENDING[state] = ps

    @classmethod
    def pop(cls, state: str) -> PendingState | None:
        cls._gc()
        return cls.PENDING.pop(state, None)

    @classmethod
    def _gc(cls) -> None:
        now = time.time()
        stale = [k for k, v in cls.PENDING.items() if now - v.created_at > 600]
        for k in stale:
            cls.PENDING.pop(k, None)

    @staticmethod
    def authorize_url(spec: OAuthSpec, *, client_id: str, redirect_uri: str,
                      state: str, scopes: tuple[str, ...] | None = None) -> str:
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }
        scope_list = scopes if scopes is not None else spec.scopes
        if scope_list:
            params["scope"] = " ".join(scope_list)
        params.update(spec.extra_auth_params)
        return f"{spec.authorize_url}?{urllib.parse.urlencode(params)}"


def exchange_code(spec: OAuthSpec, *, code: str, redirect_uri: str,
                  client_id: str, client_secret: str) -> dict:
    body = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(
        spec.token_url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # GitHub returns x-www-form-urlencoded by default
        return dict(urllib.parse.parse_qsl(raw))
