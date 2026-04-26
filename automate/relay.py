"""Reverse-tunnel client for the optional autoMate relay.

Why
---
The hub binds to ``127.0.0.1`` for safety. Phones, remote LLMs, or co-workers
can't reach it without either (a) opening a port on the LAN/WAN, or (b) a
reverse tunnel. This module is option (b): the hub dials out to a relay
server it trusts, keeps a persistent WebSocket open, and forwards inbound
HTTP requests that the relay receives back to the local FastAPI app.

The relay server itself is **not** part of this package — see
``docs/relay.md`` for the wire protocol. A public hosted relay is intended
to be a paid service; you can also self-host one for free.

Status
------
Skeleton + CLI flag only. The wire protocol is fully specified, but ship-grade
testing is pending. Treat ``automate relay`` as opt-in beta until further
notice.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import Any

from .settings import SERVER

log = logging.getLogger("automate.relay")


def run(relay_url: str, token: str | None = None, *, local_url: str | None = None) -> int:
    """Connect to a relay and forward HTTP/WS traffic to the local hub.

    Blocks. Returns when the connection is closed without retry. Higher-level
    callers (the CLI) handle reconnect with backoff.
    """
    try:
        import websockets  # type: ignore
        import httpx  # type: ignore
    except ImportError:
        sys.stderr.write(
            "The relay client needs websockets + httpx. Install with:\n"
            "  pip install 'automate-hub[relay]'\n"
        )
        return 1

    base = (local_url or SERVER.base_url).rstrip("/")
    token = token or os.environ.get("AUTOMATE_RELAY_TOKEN", "")

    async def main():
        async with httpx.AsyncClient(base_url=base, timeout=60) as http:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            print(f"  relay  →  dialing {relay_url}", flush=True)
            async with websockets.connect(relay_url, additional_headers=headers) as ws:
                await ws.send(json.dumps({"hello": "automate-hub", "version": "1"}))
                print(f"  relay  →  connected; forwarding to {base}", flush=True)
                async for raw in ws:
                    try:
                        frame = json.loads(raw)
                    except Exception:  # noqa: BLE001
                        continue
                    asyncio.create_task(_handle_frame(ws, http, frame))

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        return 0
    except Exception as e:  # noqa: BLE001
        log.error("relay disconnected: %s", e)
        return 1
    return 0


async def _handle_frame(ws, http, frame: dict[str, Any]) -> None:
    """Translate a relay frame into a local HTTP call and send the response back."""
    rid = frame.get("id")
    kind = frame.get("kind")
    if kind != "http":
        # Future: 'ws' for tunnelling websockets
        await ws.send(json.dumps({"id": rid, "ok": False, "error": f"unknown kind: {kind}"}))
        return
    method = frame.get("method", "GET").upper()
    path = frame.get("path", "/")
    headers = frame.get("headers") or {}
    body = frame.get("body")
    try:
        r = await http.request(method, path, headers=headers, content=body)
        await ws.send(json.dumps({
            "id": rid, "ok": True,
            "status": r.status_code,
            "headers": dict(r.headers),
            "body": r.text,
        }))
    except Exception as e:  # noqa: BLE001
        await ws.send(json.dumps({"id": rid, "ok": False, "error": f"{type(e).__name__}: {e}"}))
