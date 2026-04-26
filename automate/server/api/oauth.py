"""OAuth callback handler.

Lives outside ``/api`` so the redirect URI registered with each provider can
be a clean ``http://127.0.0.1:8765/oauth/<id>/callback``.
"""
from __future__ import annotations

import time

from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse

from ...oauth import OAuthFlow, exchange_code, get_oauth_spec
from ._deps import state as app_state

router = APIRouter(tags=["oauth"])


_RESULT_HTML = """\
<!doctype html>
<html><head><meta charset=utf-8><title>autoMate · {title}</title>
<style>
  body{{font-family:-apple-system,system-ui,sans-serif;max-width:520px;margin:80px auto;color:#111;}}
  h1{{font-size:22px;margin:0 0 12px;}} p{{color:#555;line-height:1.55;}}
  .pill{{display:inline-block;padding:4px 10px;border-radius:999px;font-size:12px;
        background:{bg};color:{fg};margin-bottom:16px;}}
</style></head>
<body><span class=pill>{pill}</span><h1>{title}</h1><p>{body}</p>
<p><a href="/">Return to autoMate</a></p>
<script>setTimeout(()=>window.close(),3000);</script>
</body></html>"""


def _err(title: str, body: str, code: int = 400) -> HTMLResponse:
    return HTMLResponse(_RESULT_HTML.format(
        title=title, pill="Error", bg="#fde8e8", fg="#9b1c1c", body=body,
    ), status_code=code)


@router.get("/oauth/{cid}/callback", response_class=HTMLResponse)
def callback(
    cid: str,
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
    s=Depends(app_state),
):
    spec = get_oauth_spec(cid)
    if error or not spec:
        return _err("Authorization failed", f"Provider returned: <code>{error or 'unknown error'}</code>")
    pending = OAuthFlow.pop(state or "")
    if not pending or pending.provider_id != cid:
        return _err("State mismatch", "The OAuth state token did not match an in-flight request.")
    if not code:
        return _err("Missing code", "No <code>code</code> query parameter.")

    try:
        token_payload = exchange_code(
            spec, code=code, redirect_uri=pending.redirect_uri,
            client_id=pending.client_id, client_secret=pending.client_secret,
        )
    except Exception as e:  # noqa: BLE001
        return _err("Token exchange failed", f"<code>{type(e).__name__}: {e}</code>")

    access_token = token_payload.get(spec.token_field) or token_payload.get("access_token")
    refresh_token = token_payload.get(spec.refresh_field or "")
    expires_in = token_payload.get("expires_in")
    expires_at = (time.time() + float(expires_in)) if expires_in else None

    if not access_token:
        return _err("No access_token in response", f"Raw response: <code>{token_payload}</code>")

    s.db.upsert_connection(
        id=cid, display_name=spec.display_name, auth_kind="oauth",
        status="connected", token=access_token, refresh=refresh_token,
        expires_at=expires_at,
        metadata={"raw": {k: v for k, v in token_payload.items()
                          if k not in {spec.token_field, spec.refresh_field or ""}}},
    )
    return HTMLResponse(_RESULT_HTML.format(
        title=f"{spec.display_name} connected", pill="Success",
        bg="#d1fae5", fg="#065f46",
        body="autoMate now has authorization for this account. You may close this tab.",
    ))
