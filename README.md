<div align="center"><a name="readme-top"></a>

<img src="./imgs/logo.png" width="120" height="120" alt="autoMate logo">
<h1>autoMate</h1>
<p><b>🤖 API Tool Center + Desktop Automation — One MCP, 26 Platforms</b></p>

[中文](./README_CN.md) | [日本語](./README_JA.md)

[![PyPI](https://img.shields.io/pypi/v/automate-mcp)](https://pypi.org/project/automate-mcp/)
[![License](https://img.shields.io/github/license/yuruotong1/autoMate)](LICENSE)

> Connect 飞书, 钉钉, Slack, GitHub, Notion, Telegram, Zoom, Sentry and 18 more — plus full desktop GUI automation

https://github.com/user-attachments/assets/bf27f8bd-136b-402e-bc7d-994b99bcc368

</div>

---

## 💡 What is autoMate?

autoMate is an MCP server that works in **two modes**:

**Mode 1 — API Tool Center:** Set environment variables for the platforms you use — autoMate auto-registers native tools for each one. Send messages, create issues, search contacts, track errors, send emails, query maps — all from one MCP.

**Mode 2 — Desktop GUI Automation:** Give Claude hands and eyes to control any desktop application with no API — 剪映, Photoshop, AutoCAD, SAP, internal tools.

| Mode | Requires | What it does |
|------|---------|-------------|
| **API Tool Center** | Platform env vars (set only what you need) | Native tools for 26 platforms |
| **Desktop Automation** | Nothing (zero-config) | Click, type, screenshot any desktop app |
| **Cloud Vision** | HuggingFace token | Autonomous UI parsing + action reasoning |

---

## ✨ Features

- 🔗 **26 platform integrations** — Chinese and international, zero overhead for unused ones
- 🖥️ **Automates apps with no API** — if it has a GUI, autoMate can drive it
- 📚 **Reusable script library** — save workflows once, run forever
- ☁️ **Cloud Vision** — OmniParser + UI-TARS via HuggingFace, zero local GPU
- 🧠 **Claude knows when to use it** — clear identity prevents autoMate from being bypassed
- 🤖 **Zero config for desktop automation** — no API keys needed to get started
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

### With API integrations

Add env vars for whichever platforms you use:

```json
{
  "mcpServers": {
    "automate": {
      "command": "uvx",
      "args": ["automate-mcp@latest"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-...",
        "GITHUB_TOKEN": "ghp_...",
        "NOTION_API_KEY": "secret_...",
        "FEISHU_APP_ID": "cli_...",
        "FEISHU_APP_SECRET": "...",
        "SENTRY_AUTH_TOKEN": "...",
        "SENTRY_ORG_SLUG": "my-org"
      }
    }
  }
}
```

Only set the ones you need — unused integrations are silently skipped.

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

## 🔗 API Tool Center — 26 Supported Platforms

### Chinese Platforms

| Platform | Env Vars | Tools |
|----------|----------|-------|
| 飞书 (Feishu/Lark) | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` | Send messages, create docs, list chats, create tasks |
| 钉钉 (DingTalk) | `DINGTALK_WEBHOOK`, `DINGTALK_SECRET` | Send text, markdown, link cards via webhook |
| 企业微信 (WeCom) | `WECOM_CORP_ID`, `WECOM_CORP_SECRET`, `WECOM_AGENT_ID` | Send text/markdown, get department users |
| 微信公众号 (WeChat MP) | `WEIXIN_APP_ID`, `WEIXIN_APP_SECRET` | Send template messages, get followers |
| 微博 (Weibo) | `WEIBO_ACCESS_TOKEN` | Post weibo, get timeline, get profile |
| Gitee (码云) | `GITEE_ACCESS_TOKEN` | Create/list issues, create PRs, get repo info |
| 语雀 (Yuque) | `YUQUE_TOKEN` | List knowledge bases, list/get/create docs |
| 高德地图 (Amap) | `AMAP_API_KEY` | Geocode, reverse geocode, POI search, driving routes |

### Messaging & Collaboration

| Platform | Env Vars | Tools |
|----------|----------|-------|
| Slack | `SLACK_BOT_TOKEN` | Send messages, list channels, get history, reply threads |
| Telegram | `TELEGRAM_BOT_TOKEN` | Send messages/photos, get updates, get bot info |
| Discord | `DISCORD_BOT_TOKEN` | Send messages, get messages, list channels, send DMs |
| Microsoft Teams | `TEAMS_WEBHOOK_URL` | Send messages, rich cards, color-coded alerts |
| Zoom | `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET` | Create meetings, list meetings, get meeting details |
| Twitter/X | `TWITTER_BEARER_TOKEN` | Search tweets, get user info, get user tweets |

### DevOps & Engineering

| Platform | Env Vars | Tools |
|----------|----------|-------|
| GitHub | `GITHUB_TOKEN` | Create/list issues, create PRs, search repos, get repo info |
| GitLab | `GITLAB_TOKEN`, `GITLAB_BASE_URL` | Create/list issues, create MRs, list pipelines |
| Sentry | `SENTRY_AUTH_TOKEN`, `SENTRY_ORG_SLUG` | List/get issues, list projects, resolve issues |

### Project Management

| Platform | Env Vars | Tools |
|----------|----------|-------|
| Notion | `NOTION_API_KEY` | Search, create pages, query databases, append blocks |
| Airtable | `AIRTABLE_API_KEY` | List/create/update/search records |
| Linear | `LINEAR_API_KEY` | Create/list issues, list teams, update issues |
| Jira | `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL` | Create/search/get issues, transition status |
| Trello | `TRELLO_API_KEY`, `TRELLO_TOKEN` | List boards/lists/cards, create cards |
| HubSpot | `HUBSPOT_ACCESS_TOKEN` | Create/search contacts, create/list deals |

### Email & Marketing

| Platform | Env Vars | Tools |
|----------|----------|-------|
| SendGrid | `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` | Send emails, bulk send, get delivery stats |
| Twilio | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` | Send SMS, list messages, get account info |
| Mailchimp | `MAILCHIMP_API_KEY` | List audiences, add subscribers, list campaigns |

---

## 🖥️ Desktop Automation Tools

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

**Low-level desktop control:**

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

## ☁️ Cloud Vision (Optional)

Add HuggingFace env vars to enable autonomous screen parsing and action reasoning:

```json
"env": {
  "AUTOMATE_HF_TOKEN": "hf_...",
  "AUTOMATE_SCREEN_PARSER_URL": "https://your-omniparser-endpoint.aws.endpoints.huggingface.cloud",
  "AUTOMATE_ACTION_MODEL_URL": "https://your-uitars-endpoint.aws.endpoints.huggingface.cloud",
  "AUTOMATE_ACTION_MODEL_NAME": "ByteDance-Seed/UI-TARS-1.5-7B",
  "AUTOMATE_HF_NAMESPACE": "your-hf-username",
  "AUTOMATE_SCREEN_PARSER_ENDPOINT": "omniparser-v2",
  "AUTOMATE_ACTION_MODEL_ENDPOINT": "ui-tars-1-5-7b"
}
```

See `.env.example` for the full reference.

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

| Hint | Action |
|------|--------|
| `[click:coord=320,240]` | Click at absolute screen coordinates |
| `[type:hello]` | Type text |
| `[key:ctrl+s]` | Press keyboard shortcut |
| `[wait:2]` | Wait 2 seconds |
| `[scroll_up]` / `[scroll_down]` | Scroll the page |

---

## 📝 FAQ

**Q: Which integrations are active?**  
Only integrations whose env vars are all set. Unset ones are silently skipped — no errors, no overhead.

**Q: How is desktop automation different from browser MCP / Windows MCP?**  
Those MCPs handle web and OS operations. autoMate handles desktop GUI apps with no API — like 剪映, Photoshop, SAP, or any internal tool.

**Q: Do I need a GPU for Cloud Vision?**  
No — everything runs on HuggingFace Inference Endpoints. You only need a HF token and deployed endpoints.

**Q: Does it work on macOS / Linux?**  
Yes — all three platforms are supported.

---

## 🤝 Contributing

<a href="https://github.com/yuruotong1/autoMate/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yuruotong1/autoMate" />
</a>

---

<div align="center">
⭐ Every star encourages the creators and helps more people discover autoMate ⭐
</div>
