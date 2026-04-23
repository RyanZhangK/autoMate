<div align="center"><a name="readme-top"></a>

<img src="./imgs/logo.png" width="120" height="120" alt="autoMate logo">
<h1>autoMate</h1>
<p><b>🤖 API 工具中心 + 桌面自动化 — 一个 MCP，接入 31 个平台</b></p>

[English](./README.md) | [日本語](./README_JA.md)

[![PyPI](https://img.shields.io/pypi/v/automate-mcp)](https://pypi.org/project/automate-mcp/)
[![License](https://img.shields.io/github/license/yuruotong1/autoMate)](LICENSE)

> 唯一同时具备 31 个平台集成 + 桌面 GUI 自动化的 MCP Server — 本地运行，零云端依赖，API Key 不离开你的机器

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

**模式一 — API 工具中心：** 设置对应平台的环境变量，autoMate 自动注册该平台的原生工具。发消息、创建 Issue、管理任务、处理支付、查询联系人——全部通过同一个 MCP 完成。

**模式二 — 桌面 GUI 自动化：** 让 Claude 拥有双手和眼睛，操控任何没有 API 的桌面软件——剪映、Photoshop、AutoCAD、SAP、企业内部系统。

| 模式 | 需要什么 | 做什么 |
|------|---------|--------|
| **API 工具中心** | 各平台环境变量（按需配置） | 31 个平台的原生工具 |
| **桌面自动化** | 无需任何配置 | 点击、输入、截图，控制任何桌面软件 |
| **云端视觉** | HuggingFace Token | 自主界面解析 + 动作推理 |

---

## ✨ 为什么选择 autoMate？

| | autoMate | Composio | Zapier MCP | Claude Connectors |
|---|---|---|---|---|
| **配置方式** | 设置环境变量即可 | 注册账号 + OAuth | 网页登录 + 复制链接 | claude.ai 登录 |
| **国内平台** | 8 个（独家） | 无 | 无 | 无 |
| **桌面自动化** | 有 | 无 | 无 | 无 |
| **本地运行** | 是 — 运行在你的机器上 | 否 — 仅云端 | 否 — 仅云端 | 否 — Anthropic 云 |
| **开源** | 是 | 工具闭源 | 闭源 | 闭源 |
| **费用** | 免费 | 免费层 + 付费 | 每次调用 2 个 task | Pro/企业版 |

**autoMate 的独特定位：** 市场上唯一同时做到本地优先、国内平台原生支持、开源、并将 API 集成与桌面 GUI 自动化合二为一的 MCP Server。

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
        "GITHUB_TOKEN": "ghp_...",
        "STRIPE_SECRET_KEY": "sk_live_...",
        "AMAP_API_KEY": "..."
      }
    }
  }
}
```

只需配置你用到的平台——未配置的集成会被静默跳过，不产生任何开销。

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

## 🔗 API 工具中心 — 31 个已支持平台

### 国内平台

| 平台 | 环境变量 | 工具能力 |
|------|---------|---------|
| 飞书 (Feishu/Lark) | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` | 发消息、创建文档、查聊天列表、创建任务 |
| 钉钉 (DingTalk) | `DINGTALK_WEBHOOK`, `DINGTALK_SECRET` | 发文本、Markdown、链接卡片（Webhook 机器人） |
| 企业微信 (WeCom) | `WECOM_CORP_ID`, `WECOM_CORP_SECRET`, `WECOM_AGENT_ID` | 发文本/Markdown、查部门成员 |
| 微信公众号 | `WEIXIN_APP_ID`, `WEIXIN_APP_SECRET` | 发模板消息、获取关注者、查用户信息 |
| 微博 | `WEIBO_ACCESS_TOKEN` | 发微博、看时间线、查个人资料 |
| Gitee (码云) | `GITEE_ACCESS_TOKEN` | 创建/查询 Issue、创建 PR、查仓库信息 |
| 语雀 (Yuque) | `YUQUE_TOKEN` | 查知识库、查/获取/创建文档 |
| 高德地图 (Amap) | `AMAP_API_KEY` | 地理编码、逆地理编码、POI 搜索、驾车路线 |

### 消息与协作

| 平台 | 环境变量 | 工具能力 |
|------|---------|---------|
| Slack | `SLACK_BOT_TOKEN` | 发消息、查频道、获取历史、回复 Thread |
| Telegram | `TELEGRAM_BOT_TOKEN` | 发文字/图片、获取更新、查 Bot 信息 |
| Discord | `DISCORD_BOT_TOKEN` | 发消息、查消息、查频道列表、发私信 |
| Microsoft Teams | `TEAMS_WEBHOOK_URL` | 发消息、富文本卡片、彩色告警通知 |
| Zoom | `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET` | 创建会议、查会议列表、获取会议详情 |
| Twitter/X | `TWITTER_BEARER_TOKEN` | 搜索推文、查用户信息、获取用户推文 |
| Twilio | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` | 发短信、查消息记录、查账户信息 |

### DevOps 与工程

| 平台 | 环境变量 | 工具能力 |
|------|---------|---------|
| GitHub | `GITHUB_TOKEN` | 创建/查询 Issue、创建 PR、搜索仓库、查仓库信息 |
| GitLab | `GITLAB_TOKEN`, `GITLAB_BASE_URL` | 创建/查询 Issue、创建 MR、查 Pipeline |
| Sentry | `SENTRY_AUTH_TOKEN`, `SENTRY_ORG_SLUG` | 查/获取错误、查项目列表、标记已解决 |

### 项目管理与知识库

| 平台 | 环境变量 | 工具能力 |
|------|---------|---------|
| Notion | `NOTION_API_KEY` | 搜索、创建页面、查询数据库、追加块 |
| Airtable | `AIRTABLE_API_KEY` | 查/创建/更新/搜索记录 |
| Linear | `LINEAR_API_KEY` | 创建/查询 Issue、查团队列表、更新 Issue |
| Jira | `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL` | 创建/搜索/查询 Issue、流转状态 |
| Confluence | `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN`, `CONFLUENCE_BASE_URL` | 搜索/获取/创建页面、查 Space 列表 |
| Trello | `TRELLO_API_KEY`, `TRELLO_TOKEN` | 查看看板/列表/卡片、创建卡片 |
| Asana | `ASANA_ACCESS_TOKEN` | 查工作区/项目/任务、创建/更新任务 |
| Monday.com | `MONDAY_API_KEY` | 查看看板/条目、创建条目、查分组 |
| HubSpot | `HUBSPOT_ACCESS_TOKEN` | 创建/搜索联系人、创建/查询商机 |

### 支付与电商

| 平台 | 环境变量 | 工具能力 |
|------|---------|---------|
| Stripe | `STRIPE_SECRET_KEY` | 查余额、查/创建客户、查支付记录/订阅 |
| Shopify | `SHOPIFY_STORE_DOMAIN`, `SHOPIFY_ACCESS_TOKEN` | 查产品/订单/客户、获取店铺信息 |

### 邮件与营销

| 平台 | 环境变量 | 工具能力 |
|------|---------|---------|
| SendGrid | `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` | 发邮件、批量发送、查看投递统计 |
| Mailchimp | `MAILCHIMP_API_KEY` | 查受众列表、添加订阅者、查看邮件活动 |

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

---

## 📝 常见问题

**Q：哪些集成是激活的？**  
只有环境变量全部设置的集成才会激活。未配置的平台会被静默跳过，不会报错，也不会影响性能。

**Q：和 Composio、Zapier MCP 有什么区别？**  
Composio 和 Zapier MCP 将你的 API 调用路由到他们的云服务器，需要注册账号。autoMate 完全运行在你的机器上，API Key 不离开本地。此外，autoMate 覆盖了飞书、钉钉、微信、高德等国内平台，这是任何云端 MCP 服务都不支持的。更独特的是，autoMate 还内置了桌面 GUI 自动化，处理没有 API 的应用。

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
