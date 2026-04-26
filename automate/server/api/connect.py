"""Connection snippets for plugging autoMate into any AI.

Returns ready-to-copy strings that teach an upstream LLM (or its host) how
to call the local autoMate hub. Three flavours:

- ``mcp``       — MCP config for Claude Code / Cursor / Cline / Kimi K2 / etc.
- ``http``      — a system-prompt fragment that says "POST here" — works with
                  any LLM client that can hit URLs.
- ``bridge``    — a shell wrapper + system prompt for tool-less LLMs (Ollama
                  via terminal, basic web-chat) that can only emit text.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from ._deps import state

router = APIRouter(tags=["connect"], prefix="/connect")


_HTTP_PROMPT = """\
You have access to autoMate, a local automation hub that runs on the user's
machine. It can execute shell commands, drive a real browser, control the
desktop, and call 30+ SaaS APIs (GitHub, Notion, Slack, 飞书, ...).

Whenever the user asks for a real-world action, do NOT pretend to do it
yourself. Instead, call:

  POST {base_url}/api/agent/run
  Content-Type: application/json
  Body:    {{"prompt": "<one-line natural-language request>"}}

The response is JSON: {{"final": "<answer or result>"}}.

Use this for anything concrete:
  - reading files, running git/npm/docker, installing packages
  - opening a website and extracting content
  - posting to Slack/钉钉, creating GitHub issues, querying Notion
  - taking screenshots, clicking on the desktop

Don't pre-plan multi-step calls — autoMate plans internally. Just hand it
the user's request as a sentence and use the result.
"""


_MCP_CONFIG = """\
{
  "mcpServers": {
    "automate": {
      "command": "automate",
      "args": ["mcp"]
    }
  }
}"""


_BRIDGE_SH = """\
#!/usr/bin/env bash
# Save as ~/bin/am, chmod +x, add ~/bin to PATH. Usage:  am "list my open tabs"
exec curl -sX POST {base_url}/api/agent/run \\
  -H 'content-type: application/json' \\
  --data-binary "$(printf '%s' "$*" | python3 -c 'import json,sys;print(json.dumps({{"prompt":sys.stdin.read()}}))')" \\
  | python3 -c 'import json,sys;print(json.load(sys.stdin).get("final",""))'
"""


_BRIDGE_PROMPT = """\
You can run real-world tasks on this machine through a local CLI tool called
``am`` (the autoMate bridge). Whenever the user asks for a concrete action:

  1. On a fresh line, output exactly:
       <<<RUN>>> am "<one-line description of what to do>" <<<END>>>
  2. Wait for the next user message — it will contain ``<<<OUTPUT>>>...``
     with the result.
  3. Read it and reply to the user normally.

Use ``am`` for anything that touches the world: files, browser, APIs, scripts.
"""


_DISCOVER_HINT = """\
For AIs that can read OpenAPI:
  schema: {base_url}/openapi.json

The most useful endpoints:
  POST /api/agent/run         — natural-language → planned + executed
  POST /api/execute/<tool>    — call a specific tool by name with JSON args
  GET  /api/tools             — list every available tool, grouped
"""


@router.get("")
def snippets(request: Request, _s=Depends(state)):
    base_url = str(request.base_url).rstrip("/")
    return {
        "base_url": base_url,
        "openapi_url": f"{base_url}/openapi.json",
        "modes": {
            "mcp": {
                "title": "MCP — Claude Code / Cursor / Cline / Kimi K2",
                "subtitle": "Native tool-server protocol. The upstream LLM sees every autoMate tool individually.",
                "format": "json",
                "content": _MCP_CONFIG,
                "instructions": "Add this to your client's MCP config file. Restart the client.",
            },
            "http": {
                "title": "HTTP — any LLM that can call URLs",
                "subtitle": "ChatGPT custom GPTs, autonomous agents, Cline, n8n, Make, Zapier, your own scripts.",
                "format": "text",
                "content": _HTTP_PROMPT.format(base_url=base_url),
                "instructions": "Paste this into the AI's system prompt or instructions field.",
            },
            "bridge": {
                "title": "Bridge script — for AIs that can only emit text (Ollama, basic web chat)",
                "subtitle": "When the LLM can't call HTTP itself, a tiny shell wrapper relays your messages.",
                "format": "shell",
                "content": _BRIDGE_SH.format(base_url=base_url),
                "prompt": _BRIDGE_PROMPT,
                "instructions": "Save the script as `am`, make it executable. Paste the system prompt into your chat. The user (or a thin TUI) acts as the relay between the AI and the script.",
            },
            "discover": {
                "title": "OpenAPI — let the AI explore on its own",
                "subtitle": "For agents that can read schemas (GPT-4 with OpenAPI plugin, custom agents).",
                "format": "text",
                "content": _DISCOVER_HINT.format(base_url=base_url),
                "instructions": "Hand the AI the URL; it discovers the surface itself.",
            },
        },
    }
