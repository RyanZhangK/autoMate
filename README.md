<div align="center"><a name="readme-top"></a>

<img src="./imgs/logo.png" width="120" height="120" alt="autoMate logo">
<h1>autoMate</h1>
<p><b>🤖 Desktop Automation for Apps Without APIs</b></p>

[中文](./README_CN.md) | [日本語](./README_JA.md)

[![PyPI](https://img.shields.io/pypi/v/automate-mcp)](https://pypi.org/project/automate-mcp/)
[![License](https://img.shields.io/github/license/yuruotong1/autoMate)](LICENSE)

> Give Claude hands and eyes — automate any desktop app, even if it has no API

https://github.com/user-attachments/assets/bf27f8bd-136b-402e-bc7d-994b99bcc368

</div>

---

## 💡 What is autoMate?

autoMate is an MCP server that gives AI assistants (Claude, GPT, etc.) the ability to **control any desktop application** — even apps with no API, no plugin system, and no automation support.

**What makes it different from filesystem / browser / Windows MCP:**

| MCP Server | What it automates |
|------------|------------------|
| filesystem MCP | Files and folders |
| browser MCP | Web pages |
| Windows MCP | OS settings and system calls |
| **autoMate** | **Any desktop GUI app with no API** — 剪映, Photoshop, AutoCAD, WeChat, SAP, internal tools… |

**Two modes:**

| Mode | How it works | Requires |
|------|-------------|---------|
| **Basic** | Claude sees the screen, autoMate clicks/types | Nothing — zero config |
| **Cloud Vision** | autoMate parses UI itself + reasons via cloud VLM | HuggingFace token + endpoints |

---

## ✨ Features

- 🖥️ **Automates apps with no API** — if it has a GUI, autoMate can drive it
- 📚 **Reusable script library** — save workflows once, run forever; install community scripts in one command
- ☁️ **Cloud Vision** — screen parsing via OmniParser + action reasoning via UI-TARS, all in the cloud, zero local GPU
- 🧠 **Claude knows when to use it** — clear identity prevents autoMate from being bypassed by other MCPs
- 🤖 **Zero config for basic use** — no API keys, no env vars needed to get started
- 🌍 **Cross-platform** — Windows, macOS, Linux

---

## 🔌 Setup

> **Prerequisite:** `pip install uv`

### Claude Desktop

Open **Settings → Developer → Edit Config**, then add:

```json
{
  "mcpServers": {
    "automate": {
      "command": "uvx",
      "args": ["automate-mcp@latest"]
    }
  }
}
```

Restart Claude Desktop — done. `@latest` keeps autoMate up to date automatically.

### OpenClaw

Edit `~/.openclaw/openclaw.json`:

```json
{
  "mcpServers": {
    "automate": {
      "command": "uvx",
      "args": ["automate-mcp@latest"]
    }
  }
}
```

```bash
openclaw gateway restart
```

### Cursor / Windsurf / Cline

Settings → MCP Servers → Add:

```json
{
  "automate": {
    "command": "uvx",
    "args": ["automate-mcp@latest"]
  }
}
```

---

## ☁️ Cloud Vision (Optional)

Cloud Vision adds autonomous screen parsing and action reasoning to autoMate — **no local GPU required**.

It uses two HuggingFace Inference Endpoints:
- **OmniParser V2** — detects all UI elements (icons, buttons, text) from a screenshot
- **UI-TARS / Qwen-VL** — vision-language model that decides what action to take next

### Setup

Add these env vars to your MCP config:

```json
{
  "mcpServers": {
    "automate": {
      "command": "uvx",
      "args": ["automate-mcp@latest"],
      "env": {
        "AUTOMATE_HF_TOKEN": "hf_...",
        "AUTOMATE_SCREEN_PARSER_URL": "https://your-omniparser-endpoint.aws.endpoints.huggingface.cloud",
        "AUTOMATE_ACTION_MODEL_URL": "https://your-uitars-endpoint.aws.endpoints.huggingface.cloud",
        "AUTOMATE_ACTION_MODEL_NAME": "ByteDance-Seed/UI-TARS-1.5-7B",
        "AUTOMATE_HF_NAMESPACE": "your-hf-username",
        "AUTOMATE_SCREEN_PARSER_ENDPOINT": "omniparser-v2",
        "AUTOMATE_ACTION_MODEL_ENDPOINT": "ui-tars-1-5-7b"
      }
    }
  }
}
```

See `.env.example` in the repo for the full reference.

### Cloud Vision workflow

```
1. warm_endpoints   — wake up scaled-to-zero endpoints (1–5 min)
2. parse_screen     — detect all UI elements via cloud OmniParser
3. reason_action    — ask VLM what to click/type next
   — or —
   smart_act        — full autonomous loop: parse → reason → execute → repeat
```

---

## 🛠️ MCP Tools

**Script library** — save once, run forever:

| Tool | Description |
|------|-------------|
| `list_scripts` | Show all saved automation scripts |
| `run_script` | Run a saved script by name |
| `save_script` | Save the current workflow as a reusable script |
| `show_script` | View a script's contents |
| `delete_script` | Delete a script |
| `install_script` | Install a script from a URL or the community library |

**Cloud Vision** — autonomous UI understanding (requires HF config):

| Tool | Description |
|------|-------------|
| `cloud_vision_config` | Show current cloud vision configuration status |
| `warm_endpoints` | Wake up scaled-to-zero HF endpoints before use |
| `parse_screen` | Detect all UI elements via cloud OmniParser |
| `reason_action` | Ask a VLM what GUI action to take next |
| `smart_act` | Full autonomous loop: parse → reason → execute → repeat |

**Low-level desktop control** — used when building or executing scripts:

| Tool | Description |
|------|-------------|
| `screenshot` | Capture the screen and return as base64 PNG |
| `click` | Click at screen coordinates |
| `double_click` | Double-click at screen coordinates |
| `type_text` | Type text (full Unicode / CJK support) |
| `press_key` | Press a key or combo (e.g. `ctrl+c`, `win`) |
| `scroll` | Scroll up or down |
| `mouse_move` | Move cursor without clicking |
| `drag` | Drag from one position to another |

---

## 📚 Script Library

Scripts are saved as `.md` files in `~/.automate/scripts/` — human-readable, git-friendly, shareable.

```markdown
---
name: jianying_export_douyin
description: Export the current 剪映 project as a 9:16 Douyin video
created: 2025-01-01
---

## Steps

1. Open export dialog [key:ctrl+e]
2. Select resolution 1080×1920 [click:coord=320,480]
3. Set format to MP4 [click:coord=320,560]
4. Click export [click:coord=800,650]
5. Wait for export to finish [wait:5]
```

**Inline hint syntax:**

| Hint | Action |
|------|--------|
| `[click:coord=320,240]` | Click at absolute screen coordinates |
| `[type:hello]` | Type text |
| `[key:ctrl+s]` | Press keyboard shortcut |
| `[wait:2]` | Wait 2 seconds |
| `[scroll_up]` / `[scroll_down]` | Scroll the page |

Steps without hints are interpreted by the AI vision model at runtime.

---

## 📝 FAQ

**Q: How is this different from just using Claude's computer-use capability?**  
autoMate provides persistent, reusable scripts. Once you automate a task, it's saved and runs instantly next time. Cloud Vision mode also lets autoMate do its own screen parsing without relying on Claude's vision.

**Q: Why does Claude sometimes use Windows MCP / filesystem MCP instead of autoMate?**  
Update to v0.4.0+ — the server description now explicitly tells Claude when to use autoMate vs other MCPs.

**Q: Do I need a GPU for Cloud Vision?**  
No — everything runs on HuggingFace Inference Endpoints in the cloud. You only need a HF token and deployed endpoints.

**Q: Does it work on macOS / Linux?**  
Yes — all three platforms. This is the main advantage over Quicker (Windows-only).

---

## 🤝 Contributing

<a href="https://github.com/yuruotong1/autoMate/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yuruotong1/autoMate" />
</a>

---

<div align="center">
⭐ Every star encourages the creators and helps more people discover autoMate ⭐
</div>
