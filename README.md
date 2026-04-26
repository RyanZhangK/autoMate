# autoMate

> A scheduling hub that gives any LLM hands.

autoMate is a small local server with a browser UI. After install you open
`http://127.0.0.1:8765`, plug in an API key for whichever LLM you like, and
connect the SaaS accounts you want it to act on. From that point on, anything
that speaks **HTTP** or **MCP** — Claude Code, Cursor, Cline, Kimi K2, your own
script — can hand autoMate a natural-language request, and autoMate plans,
picks tools, fills in parameters, and executes against your machine, browsers
and 30+ third-party APIs.

```
┌─────────────────────────────────────────────────────────────┐
│  Browser UI  ·  http://127.0.0.1:8765                       │
│  models · tool marketplace · live chat · run history        │
└────────────────┬────────────────────────────────────────────┘
                 │  HTTP · WebSocket
┌────────────────▼────────────────────────────────────────────┐
│  Unified entry point                                         │
│  ┌──────────────┬───────────────────────────────────────┐   │
│  │  REST API    │  POST /api/agent/run                  │   │
│  │  WebSocket   │  /api/sessions/ws  (live event stream)│   │
│  │  MCP (stdio) │  `automate mcp`  (Claude Code, Cursor)│   │
│  └──────────────┴───────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Agent loop                                                  │
│  · parse NL request  · choose tools  · extract args  · loop │
├─────────────────────────────────────────────────────────────┤
│  Tools                                                       │
│  ┌────────────────┬───────────────────┬──────────────────┐  │
│  │ Local hands    │ Browser           │ Integrations     │  │
│  │ shell.exec     │ browser.open      │ github.*         │  │
│  │ script.run     │ browser.click     │ notion.*         │  │
│  │ desktop.click  │ browser.extract   │ slack.* feishu.* │  │
│  │ desktop.type   │ browser.screenshot│ stripe.* …       │  │
│  └────────────────┴───────────────────┴──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ~/.automate/  · SQLite + Fernet-encrypted credentials       │
└─────────────────────────────────────────────────────────────┘
```

中文文档:[README_CN.md](./README_CN.md)

## Why

You already have a favourite coding assistant. It's good at planning. What it
can't do is reach into _your_ Notion, _your_ GitHub, _your_ shell, _your_
running browser session. autoMate is the executor that fills that gap. It
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
  process can run. `script.run` writes Python/Bash/Node and executes. `browser.*`
  drives a real Chromium tab via Playwright. `desktop.*` is pyautogui under
  the hood.
- **One process, three doorways.** REST, WebSocket, MCP — same registry, same
  agent. No second deployment.

## Install

```bash
pip install 'automate-hub[full]'
# or, for a minimal install (no MCP/browser/desktop):
pip install automate-hub
```

Optional extras:

| extra      | what it adds                                                              |
| ---------- | ------------------------------------------------------------------------- |
| `mcp`      | stdio MCP server entry (`automate mcp`) for Claude Code / Cursor / Cline. |
| `browser`  | Playwright. Run `python -m playwright install chromium` after install.    |
| `desktop`  | pyautogui. Skip on headless servers.                                      |
| `full`     | All of the above.                                                         |

## Run

```bash
automate serve
```

That's it. The browser opens to `http://127.0.0.1:8765`. The first thing it
asks is which LLM provider to use — paste a key, hit "Use this", you're done.

```bash
automate doctor    # show paths, configured providers, integrations
automate mcp       # start a stdio MCP server (for upstream LLM clients)
```

Data lives under `~/.automate/`. Credentials are encrypted with a key at
`~/.automate/secret.key` (chmod 600). Override with `AUTOMATE_HOME=/path`.

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
individual tool — `shell.exec`, `browser.open`, `notion_search`, etc. Use the
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

**Local executors** — `shell.exec`, `shell.cwd`, `script.run`, `script.list`,
`script.read`, `desktop.screenshot`, `desktop.click`, `desktop.type`,
`desktop.press`, `desktop.size`, `browser.open`, `browser.click`,
`browser.type`, `browser.extract`, `browser.screenshot`, `browser.close`.

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
flow for the rest. Browser execution via Playwright. Tested against Python
3.10–3.12.

## License

MIT. See `LICENSE`.
