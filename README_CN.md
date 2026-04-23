<div align="center"><a name="readme-top"></a>

<img src="./imgs/logo.png" width="120" height="120" alt="autoMate logo">
<h1>autoMate</h1>
<p><b>🤖 API 工具中心 + 桌面自动化 — 一个 MCP，接入 14 个平台</b></p>

[English](./README.md) | [日本語](./README_JA.md)

[![PyPI](https://img.shields.io/pypi/v/automate-mcp)](https://pypi.org/project/automate-mcp/)
[![License](https://img.shields.io/github/license/yuruotong1/autoMate)](LICENSE)

> 一个 MCP，连接飞书、钉钉、Slack、GitHub、Notion 等 14 个平台，同时控制任何没有 API 的桌面软件

https://github.com/user-attachments/assets/bf27f8bd-136b-402e-bc7d-994b99bcc368

</div>

> **特别声明：** autoMate 项目仍处于快速迭代阶段。更深入的设计思考与 AI+RPA 研究笔记，会在 [知识星球「AI桐木和他的贵人们」](https://t.zsxq.com/x1cCW) 中分享。

<div align="center">
<a href="https://t.zsxq.com/x1cCW" target="_blank" rel="noopener noreferrer">
  <img src="./imgs/knowledge.png" width="150" height="150" alt="知识星球二维码">
</a>
</div>

---

## 💡 autoMate 是什么？

autoMate 是一个 MCP Server，提供**两种核心能力**：

**模式一 — API 工具中心：** 通过设置环境变量，接入 14 个主流平台（国内 + 国际）。Claude 获得每个平台的原生工具——发 Slack 消息、创建 GitHub Issue、发飞书通知、查 Notion 数据库，无需安装额外的 MCP Server。

**模式二 — 桌面 GUI 自动化：** 让 Claude 拥有双手和眼睛，操控任何没有 API 的桌面软件——剪映、Photoshop、AutoCAD、SAP、微信、企业内部系统。

| 模式 | 需要什么 | 做什么 |
|------|---------|--------|
| **API 工具中心** | 各平台的环境变量 | 14 个平台的原生工具 |
| **桌面自动化** | 无需任何配置 | 点击、输入、截图，控制任何桌面软件 |
| **云端视觉** | HuggingFace Token | 自主界面解析 + 动作推理 |

---

## ✨ 功能特点

- 🔗 **14 个平台集成** — 国内国际全覆盖，配置环境变量自动激活
- 🖥️ **专为无 API 的桌面软件而生** — 有界面就能自动化
- 📚 **可复用脚本库** — 工作流保存一次，永久复用
- ☁️ **云端视觉** — 云端 OmniParser 解析界面 + UI-TARS 推理，无需本地 GPU
- 🧠 **Claude 知道什么时候用它** — 明确的使用边界，不会被其他 MCP 替代
- 🤖 **桌面自动化零配置** — 不需要 API Key，开箱即用
- 🌍 **跨平台** — Windows、macOS、Linux

---

## 🔌 接入方式

> **前提：** `pip install uv`

### Claude Desktop

打开 **Settings → Developer → Edit Config**，添加：

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

重启 Claude Desktop 即可。`@latest` 会在每次重启时自动更新到最新版本。

### 带 API 集成的配置

在 `env` 中添加你需要的平台环境变量：

```json
{
  "mcpServers": {
    "automate": {
      "command": "uvx",
      "args": ["automate-mcp@latest"],
      "env": {
        "FEISHU_APP_ID": "cli_...",
        "FEISHU_APP_SECRET": "...",
        "DINGTALK_WEBHOOK": "https://oapi.dingtalk.com/robot/send?access_token=...",
        "SLACK_BOT_TOKEN": "xoxb-...",
        "GITHUB_TOKEN": "ghp_..."
      }
    }
  }
}
```

只需配置你用到的平台——未配置的集成会被静默跳过。

### Cursor / Windsurf / Cline

设置 → MCP Servers → 添加：

```json
{
  "automate": {
    "command": "uvx",
    "args": ["automate-mcp@latest"]
  }
}
```

---

## 🔗 API 工具中心 — 已支持平台

### 国内平台

| 平台 | 环境变量 | 工具能力 |
|------|---------|---------|
| 飞书 (Feishu/Lark) | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` | 发消息、创建文档、查聊天列表、创建任务 |
| 钉钉 (DingTalk) | `DINGTALK_WEBHOOK`, `DINGTALK_SECRET` | 发文本、Markdown、链接卡片（Webhook 机器人） |
| 企业微信 (WeCom) | `WECOM_CORP_ID`, `WECOM_CORP_SECRET`, `WECOM_AGENT_ID` | 发文本/Markdown、查部门成员 |
| 微信公众号 | `WEIXIN_APP_ID`, `WEIXIN_APP_SECRET` | 发模板消息、获取关注者、查用户信息 |
| 微博 | `WEIBO_ACCESS_TOKEN` | 发微博、看时间线、查个人资料 |

### 国际平台

| 平台 | 环境变量 | 工具能力 |
|------|---------|---------|
| Slack | `SLACK_BOT_TOKEN` | 发消息、查频道、获取历史、回复 Thread |
| GitHub | `GITHUB_TOKEN` | 创建/查询 Issue、创建 PR、搜索仓库、查仓库信息 |
| Telegram | `TELEGRAM_BOT_TOKEN` | 发文字/图片、获取更新、查 Bot 信息 |
| Discord | `DISCORD_BOT_TOKEN` | 发消息、查消息、查频道列表、发私信 |
| Twitter/X | `TWITTER_BEARER_TOKEN` | 搜索推文、查用户信息、获取用户推文 |
| Notion | `NOTION_API_KEY` | 搜索、创建页面、查询数据库、追加块 |
| Airtable | `AIRTABLE_API_KEY` | 查/创建/更新/搜索记录 |
| Linear | `LINEAR_API_KEY` | 创建/查询 Issue、查团队列表、更新 Issue |
| Jira | `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL` | 创建/搜索/查询 Issue、流转状态 |

---

## 🖥️ 桌面自动化工具

**脚本库** — 保存一次，永久复用：

| 工具 | 说明 |
|------|------|
| `list_scripts` | 查看所有已保存的自动化脚本 |
| `run_script` | 按名称执行已保存的脚本 |
| `save_script` | 将当前工作流保存为可复用脚本 |
| `show_script` | 查看脚本内容 |
| `delete_script` | 删除脚本 |
| `install_script` | 从 URL 或社区动作库安装脚本 |

**云端视觉** — 自主界面理解（需配置 HF 环境变量）：

| 工具 | 说明 |
|------|------|
| `cloud_vision_config` | 查看云端视觉配置状态 |
| `warm_endpoints` | 唤醒已缩容的 HF Endpoints |
| `parse_screen` | 通过云端 OmniParser 检测 UI 元素 |
| `reason_action` | 让视觉语言模型决定下一步操作 |
| `smart_act` | 全自动循环：解析 → 推理 → 执行 → 重复 |

**底层桌面控制：**

| 工具 | 说明 |
|------|------|
| `screenshot` | 截取屏幕，返回 base64 PNG |
| `click` | 点击屏幕坐标 |
| `double_click` | 双击屏幕坐标 |
| `type_text` | 输入文字（支持中文及全 Unicode） |
| `press_key` | 按键或组合键（如 `ctrl+c`、`win`） |
| `scroll` | 上下滚动 |
| `mouse_move` | 移动鼠标（不点击） |
| `drag` | 从一个位置拖拽到另一个位置 |

---

## ☁️ 云端视觉（可选）

在 MCP 配置中添加 HuggingFace 环境变量，启用自主界面解析和动作推理：

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

详细说明见仓库中的 `.env.example`。

---

## 📚 脚本库

脚本以 `.md` 文件保存在 `~/.automate/scripts/`，人类可读、Git 可管理、可分享。

```markdown
---
name: jianying_export_douyin
description: 将当前剪映项目导出为抖音 9:16 竖版视频
created: 2025-01-01
---

## Steps

1. 打开导出对话框 [key:ctrl+e]
2. 选择分辨率 1080×1920 [click:coord=320,480]
3. 设置格式为 MP4 [click:coord=320,560]
4. 点击导出按钮 [click:coord=800,650]
5. 等待导出完成 [wait:5]
```

| 提示 | 操作 |
|------|------|
| `[click:coord=320,240]` | 点击绝对屏幕坐标 |
| `[type:文字内容]` | 输入文字 |
| `[key:ctrl+s]` | 按快捷键 |
| `[wait:2]` | 等待 2 秒 |
| `[scroll_up]` / `[scroll_down]` | 滚动页面 |

---

## 📝 常见问题

**Q：哪些集成是激活的？**  
只有环境变量全部设置的集成才会激活。未配置的平台会被静默跳过，不会报错。

**Q：和 filesystem MCP / browser MCP 有什么区别？**  
那些 MCP 负责文件操作和网页。autoMate 专门处理没有 API 的桌面软件——如剪映、Photoshop、SAP、企业内部系统。

**Q：云端视觉需要 GPU 吗？**  
不需要——全部跑在 HuggingFace Inference Endpoints 上，只需要一个 HF Token。

**Q：支持 macOS / Linux 吗？**  
支持，三个平台均可运行。

---

## 🤝 参与共建

每一个优秀的开源项目都凝聚着集体的智慧。无论是修复 bug、贡献脚本，还是改进文档，欢迎参与。

<a href="https://github.com/yuruotong1/autoMate/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yuruotong1/autoMate" />
</a>

---

<div align="center">
⭐ 每一个 Star 都是对创作者的鼓励，也是让更多人发现并受益于 autoMate 的机会 ⭐
</div>
