# autoMate Relay — Protocol & Threat Model

> Status: protocol is specified and a client is shipped (`automate relay`).
> No public hosted relay is open yet. You can self-host one — see "Implementing
> a relay" below.

## Why a relay

The hub binds to `127.0.0.1`. That keeps your machine safe. It also means a
phone, a remote LLM, or a teammate cannot reach it.

The two alternatives — opening a port on your LAN / WAN, or running an
ngrok-style tunnel — both have downsides. A purpose-built relay solves three
problems:

1. **NAT traversal** — your laptop dials out, the phone hits a public URL.
2. **Auth** — the relay enforces "is this caller allowed to talk to that hub?"
3. **Multi-hub routing** — one relay can fan out to many hubs (one per user).

## Topology

```
   ┌──────────────────┐                      ┌──────────────────┐
   │  Phone / remote  │                      │  Hub (your dev   │
   │  LLM / teammate  │  HTTPS to relay      │  machine)        │
   │                  │ ───────────────────► │                  │
   │                  │                      │   automate       │
   │                  │                      │   relay wss://…  │
   └──────────────────┘                      └─────────┬────────┘
            ▲                                          │
            │           ┌────────────────────┐         │
            │  HTTPS    │   Relay server     │ ◄───────┘
            └───────── ─┤ relay.example.com  │  WebSocket
                        └────────────────────┘  (hub-initiated, persistent)
```

The hub initiates the tunnel — the relay never originates connections to the
user's machine. That's the safety property: the user remains in control of
when the hub is reachable; closing the laptop closes the tunnel.

## Wire protocol

WebSocket, JSON-encoded text frames in both directions.

### Hub → Relay (handshake, on connect)

```json
{ "hello": "automate-hub", "version": "1" }
```

The relay verifies the bearer token from the `Authorization: Bearer …` header
on the WebSocket upgrade request and binds this connection to a hub-id (which
maps to a public URL like `https://relay.example.com/u/<hub-id>/`).

### Relay → Hub (forward an inbound HTTP request)

When a phone hits `https://relay.example.com/u/<hub-id>/api/agent/run`, the
relay sends:

```json
{
  "id": "uuid-1234",
  "kind": "http",
  "method": "POST",
  "path": "/api/agent/run",
  "headers": { "content-type": "application/json", "user-agent": "…" },
  "body": "{\"prompt\":\"git status this repo\"}"
}
```

Body is a UTF-8 string. Binary uploads are out-of-scope for v1.

### Hub → Relay (response)

```json
{
  "id": "uuid-1234",
  "ok": true,
  "status": 200,
  "headers": { "content-type": "application/json" },
  "body": "{\"final\":\"working tree clean\",\"events\":[…]}"
}
```

On error:

```json
{ "id": "uuid-1234", "ok": false, "error": "ConnectionRefusedError: …" }
```

### Future kinds

- `kind: "ws"` — tunnel an inbound WebSocket (e.g. `/api/sessions/ws`). Adds
  `frames` over the tunnel keyed by the same id.
- `kind: "ping"` — keepalive (the WS protocol's own ping/pong is fine in
  practice).

## Threat model

| Threat                               | Mitigation                                                  |
| ------------------------------------ | ----------------------------------------------------------- |
| Relay impersonates the user          | Hub-initiated tunnel; user controls when hub is connected.  |
| Relay snoops on traffic              | v1: relay sees decrypted JSON. v2: end-to-end key exchange. |
| Stolen bearer token                  | Tokens are per-hub; rotate freely via the relay UI.         |
| Relay forwards traffic to wrong hub  | Token → hub-id binding is established at handshake.         |
| Replay of a stolen request           | Caller token (separate from hub token) gates the public URL.|
| Hub forwards malicious response      | The phone sees what it sees — no hub→phone surprise channel.|

## Implementing a relay (self-host)

Minimum viable relay in ~150 lines of FastAPI + websockets:

```python
# pseudo-code, see docs/relay-server-example.py for a full sample
@app.websocket("/tunnel")
async def tunnel(ws: WebSocket):
    token = ws.headers.get("authorization", "").removeprefix("Bearer ")
    hub_id = look_up_hub(token)             # your DB
    if not hub_id:
        await ws.close(code=4401)
        return
    await ws.accept()
    HUBS[hub_id] = ws
    try:
        async for raw in ws:
            msg = json.loads(raw)
            future = PENDING.pop(msg["id"], None)
            if future:
                future.set_result(msg)
    finally:
        HUBS.pop(hub_id, None)

@app.api_route("/u/{hub_id}/{path:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def forward(hub_id: str, path: str, request: Request):
    ws = HUBS.get(hub_id)
    if not ws:
        raise HTTPException(503, "hub offline")
    rid = uuid.uuid4().hex
    fut = asyncio.get_running_loop().create_future()
    PENDING[rid] = fut
    await ws.send_text(json.dumps({
        "id": rid, "kind": "http",
        "method": request.method, "path": "/" + path,
        "headers": dict(request.headers),
        "body": (await request.body()).decode(),
    }))
    resp = await asyncio.wait_for(fut, timeout=120)
    if not resp["ok"]:
        raise HTTPException(502, resp["error"])
    return Response(resp["body"], status_code=resp["status"], headers=resp["headers"])
```

## CLI

```bash
# Open a tunnel to your own (or a public) relay.
automate relay wss://relay.example.com/tunnel --token YOUR_HUB_TOKEN

# Or via env var:
AUTOMATE_RELAY_TOKEN=… automate relay wss://relay.example.com/tunnel
```

The hub still listens on `127.0.0.1:8765` for the local UI; the relay just
adds a second entry point.

## Roadmap

- [ ] End-to-end encryption (libsodium-style box) so the relay never sees plaintext
- [ ] Tunnelled WebSockets so the live event stream works through the relay
- [ ] A small dashboard on the relay listing connected hubs / pending callers
- [ ] Hosted public relay at `wss://relay.automate.dev/tunnel` (paid)
