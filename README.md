# autoMate

> A scheduling hub that gives any LLM hands.

autoMate is a small local server with a browser UI. After install you open
`http://127.0.0.1:8765`, plug in an API key for whichever LLM you like, and
connect the SaaS accounts you want it to act on. From that point on, anything
that speaks **HTTP** or **MCP** — Claude Code, Cursor, Cline, Kimi K2, your own
script — can hand autoMate a natural-language request, and autoMate plans,
picks tools, fills in parameters, and executes against your machine, your
browser, and 30+ third-party APIs.

```
┌──────────────────────────────────────────────────────────────────┐
│  Browser UI  ·  http://127.0.0.1:8765                            │
│  models · tool marketplace · live chat · run history             │
└────────────────┬─────────────────────────────────────────────────┘
                 │  HTTP · WebSocket
┌────────────────▼─────────────────────────────────────────────────┐
│  Unified entry point                                              │
│  ┌──────────────┬─────────────────────────────────────────────┐  │
│  │  REST API    │  POST /api/agent/run                        │  │
│  │  WebSocket   │  /api/sessions/ws  (live event stream)      │  │
│  │  MCP (stdio) │  `automate mcp`  (Claude Code, Cursor)      │  │
│  └──────────────┴─────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────┤
│  Agent loop                                                       │
│  · parse NL  · pick tools  · fill args  · execute  · feed back   │
├──────────────────────────────────────────────────────────────────┤
│  Tools                                                            │
│  ┌──────────┬───────────────┬──────────────────┬──────────────┐  │
│  │ shell    │ browser       │ bx.* (your real  │ integrations │  │
│  │ script   │ (Playwright,  │ browser via      │ github,      │  │
│  │ desktop  │ fresh tab)    │ Chrome extension)│ notion, …    │  │
│  └──────────┴───────────────┴──────────────────┴──────────────┘  │
├──────────────────────────────────────────────────────────────────┤
│  ~/.automate/  · SQLite + Fernet-encrypted credentials            │
└──────────────────────────────────────────────────────────────────┘
```

中文文档:[README_CN.md](./README_CN.md)

## Why

You already have a favourite coding assistant. It's good at planning. What it
can't do is reach into _your_ Notion, _your_ GitHub, _your_ shell, _your_
already-logged-in browser. autoMate is the executor that fills that gap. It
lives on your machine, holds your credentials locally, and exposes a single
clean surface that any upstream LLM can call.

- **Bring your own brain.** 25+ LLM providers in the catalog (OpenAI, Anthropic,
  Gemini, Kimi, Qwen, DeepSeek, Doubao, GLM, Yi, MiniMax, Hunyuan, Baichuan,
  StepFun, Mistral, Grok, OpenRouter, Groq, Together, Fireworks, Ollama,
  LM Studio, vLLM, …). Pick one, swap any time.
- **Click-through OAuth.** GitHub, Notion, Slack, Linear, 飞书, 钉钉. No env
  vars to copy-paste. Other integrations use API keys, also one-click and
  encrypted at rest.
- **Local hands, real privileges.** `shell.exec` runs anything the autoMate
  process can run. `script.run` writes Python/Bash/Node and executes.
  `desktop.*` is pyautogui under the hood.
- **Two flavours of browser control.** `browser.*` spawns a fresh Chromium
  tab via Playwright (great for headless tasks). `bx.*` drives **your real
  browser** via the autoMate Chrome extension — your tabs, your cookies, your
  logins. Install once from `extension/`.
- **One process, three doorways.** REST, WebSocket, MCP — same registry, same
  agent. No second deployment.

## Install

Pick whichever path fits.

### 1. pip (recommended for developers)

```bash
pip install 'automate-hub[full]'
automate serve
```

| extra      | what it adds                                                              |
| ---------- | ------------------------------------------------------------------------- |
| `mcp`      | stdio MCP entry (`automate mcp`) for Claude Code / Cursor / Cline.        |
| `browser`  | Playwright. Run `python -m playwright install chromium` after install.    |
| `desktop`  | pyautogui. Skip on headless servers.                                      |
| `full`     | All of the above.                                                         |

### 2. Standalone binary (no Python required)

Download from the [Releases page](https://github.com/yuruotong1/autoMate/releases) —
Windows / macOS (Apple Silicon) / Linux. Unzip and run `./automate/automate serve`.

### 3. Docker

```bash
docker run --rm -p 8765:8765 -v automate-data:/data \
  ghcr.io/yuruotong1/automate:latest
```

Or build it yourself: `docker build -t automate-hub . && docker run -p 8765:8765 automate-hub`.

### 4. Browser extension (one extra step for `bx.*` tools)

After installing autoMate by any of the above, open `chrome://extensions`,
toggle **Developer mode**, click **Load unpacked**, pick the `extension/`
folder. The toolbar badge flips to green **ON** when paired. See
[`extension/README.md`](./extension/README.md).

## Run

```bash
automate serve            # web UI + REST + WebSocket on http://127.0.0.1:8765
automate mcp              # expose tools as a stdio MCP server
automate doctor           # show paths, configured providers, integrations
```

Data lives under `~/.automate/`. Credentials are encrypted with a key at
`~/.automate/secret.key` (chmod 600). Override the location with
`AUTOMATE_HOME=/path`.

## Use it

### From the browser

Open the chat tab, type `git status this repo and summarise what changed`. The
event stream shows the model picking `shell.exec`, the result coming back, and
the final summary. Every run is logged to the History tab.

### From Claude Code / Cursor / Cline / Kimi (MCP)

Add this to your client's MCP config:

```json
{
  "mcpServers": {
    "automate": { "command": "automate", "args": ["mcp"] }
  }
}
```

Now the upstream LLM sees one top-level `automate(prompt)` tool plus every
individual tool — `shell.exec`, `bx.click`, `notion_search`, etc. Use the
prompt-shaped tool when you want autoMate to figure out the steps. Use the
specific tools when the upstream model already has a plan. **They plan, we
execute** — that's the whole division of labour.

### From any HTTP client

```bash
# Natural-language request — autoMate plans + executes.
curl -X POST http://127.0.0.1:8765/api/agent/run \
  -H 'content-type: application/json' \
  -d '{"prompt": "create a GitHub issue in foo/bar titled smoke test"}'

# Or call a single tool directly when you already know what you want.
curl -X POST http://127.0.0.1:8765/api/execute/shell.exec \
  -H 'content-type: application/json' \
  -d '{"args": {"command": "git status"}}'
```

Live progress streams over `ws://127.0.0.1:8765/api/sessions/ws` — send
`{"prompt": "..."}` and receive event objects (`thinking`, `tool_call`,
`tool_result`, `final`).

## What's in the box

**LLM providers (25)** — OpenAI · Anthropic · Google Gemini · xAI Grok ·
Mistral · Cohere · OpenRouter · Groq · Together · Fireworks · DeepInfra ·
DeepSeek · Moonshot Kimi · 通义千问 · 字节豆包 · 智谱 GLM · 百川 · 01.AI Yi ·
MiniMax · 阶跃星辰 · 腾讯混元 · 硅基流动 · Ollama · LM Studio · any
OpenAI-compatible endpoint.

**SaaS integrations (31)** — GitHub · GitLab · Gitee · Notion · Slack · Linear ·
Jira · Confluence · Trello · Asana · Monday.com · HubSpot · Airtable · Stripe ·
Shopify · Telegram · Discord · Microsoft Teams · Zoom · Twitter/X · SendGrid ·
Mailchimp · Twilio · Sentry · 飞书 · 钉钉 · 企业微信 · 微信公众号 · 微博 ·
语雀 · 高德地图.

**Local executors** — `shell.exec` · `shell.cwd` · `script.run` · `script.list` ·
`script.read` · `desktop.screenshot` · `desktop.click` · `desktop.type` ·
`desktop.press` · `desktop.size`.

**Headless browser** (Playwright) — `browser.open` · `browser.click` ·
`browser.type` · `browser.extract` · `browser.screenshot` · `browser.close`.

**Your real browser** (Chrome extension) — `bx.tabs` · `bx.open` · `bx.activate` ·
`bx.close` · `bx.navigate` · `bx.screenshot` · `bx.click` · `bx.type` ·
`bx.extract` · `bx.scroll` · `bx.eval`.

## Project layout

```
autoMate/
├─ automate/              # the package
│  ├─ server/             # FastAPI app, routers, MCP bridge
│  │  └─ api/             # REST + WebSocket endpoints
│  ├─ agent/              # NL → tool-call loop
│  ├─ providers/          # LLM provider catalog + clients
│  ├─ tools/              # shell · script · browser · desktop · bx · adapter
│  ├─ integrations/       # 31 SaaS connectors (github, notion, slack, …)
│  ├─ oauth/              # auth-code flow + provider catalog
│  ├─ store/              # SQLite + Fernet vault
│  ├─ frontend/           # static SPA (Tailwind + Alpine, no build step)
│  ├─ extension_bus.py    # sync ↔ async bridge for the Chrome extension
│  ├─ settings.py · cli.py · version.py
├─ extension/             # Chrome MV3 extension (load unpacked)
├─ packaging/             # PyInstaller spec for binary builds
├─ Dockerfile
└─ pyproject.toml
```

## Adding a new tool

```python
# automate/tools/myfeature.py
from .registry import Tool, ToolRegistry

def register(reg: ToolRegistry) -> None:
    reg.register(Tool(
        name="myfeature.do",
        description="Do the thing.",
        parameters={"type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]},
        handler=lambda x: {"echoed": x},
        category="custom",
    ))
```

Then call `register(reg)` from `automate/tools/registry.py::build_default_registry`.

## Adding a new LLM provider

Append a `ProviderSpec` to `automate/providers/catalog.py`. If the provider
speaks the OpenAI chat-completions schema (most do, including all Chinese
ones), nothing else is needed. The UI picks it up on next reload.

## Status

v1.0 — server, agent loop, MCP bridge, all integrations adapted, OAuth
implemented for GitHub / Notion / Slack / Linear / 飞书 / 钉钉, click-through
flow for the rest. Headless browser via Playwright; live browser via Chrome
extension. Multi-OS distribution: pip, standalone binaries, Docker. Tested
against Python 3.10–3.12.

## License

MIT. See `LICENSE`.
