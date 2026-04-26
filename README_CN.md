# autoMate

> 给任何大模型一双手的调度中枢。

autoMate 是一个本地小服务,自带浏览器界面。安装完打开 `http://127.0.0.1:8765`,
配上你喜欢的大模型 API Key,授权要让它操作的 SaaS 账号 — 从此任何能说 **HTTP**
或 **MCP** 的客户端(Claude Code、Cursor、Cline、Kimi K2、你自己的脚本)都
可以把一段自然语言交给 autoMate,由它去**规划、选工具、抽参数、跑命令**,
落地到你的机器、浏览器和 30+ 第三方 API 上。

```
┌─────────────────────────────────────────────────────────────┐
│  浏览器 UI · http://127.0.0.1:8765                          │
│  模型配置 · 工具市场 · 实时对话 · 历史记录                  │
└────────────────┬────────────────────────────────────────────┘
                 │  HTTP · WebSocket
┌────────────────▼────────────────────────────────────────────┐
│  统一接入层                                                   │
│  ┌──────────────┬───────────────────────────────────────┐   │
│  │  REST API    │  POST /api/agent/run                  │   │
│  │  WebSocket   │  /api/sessions/ws  (执行流实时推送)   │   │
│  │  MCP (stdio) │  `automate mcp`  Claude Code / Cursor │   │
│  └──────────────┴───────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Agent 内核                                                  │
│  · 解析自然语言 · 选工具 · 抽参数 · 反馈循环               │
├─────────────────────────────────────────────────────────────┤
│  工具                                                         │
│  ┌────────────────┬───────────────────┬──────────────────┐  │
│  │ 本地手脚       │ 浏览器            │ 集成市场         │  │
│  │ shell.exec     │ browser.open      │ github.*         │  │
│  │ script.run     │ browser.click     │ notion.*         │  │
│  │ desktop.click  │ browser.extract   │ slack.* 飞书.*   │  │
│  │ desktop.type   │ browser.screenshot│ stripe.* ...     │  │
│  └────────────────┴───────────────────┴──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ~/.automate/  · SQLite + Fernet 加密凭据                    │
└─────────────────────────────────────────────────────────────┘
```

English: [README.md](./README.md)

## 为什么需要 autoMate

你已经有趁手的 AI 编码助手了。它擅长**规划**,但伸不进**你的** Notion、
**你的** GitHub、**你的** Shell、**你的**浏览器会话 — autoMate 就是来填这块
空缺的执行器。它跑在你自己的机器上,凭据从不离开本地,对外只暴露一个干净的
统一接口,任何大模型客户端都能直接调用。

- **大脑自带。** 内置 25+ 模型供应商目录:OpenAI、Anthropic、Gemini、Kimi、
  通义千问、DeepSeek、豆包、智谱 GLM、Yi、MiniMax、混元、百川、阶跃星辰、
  Mistral、Grok、OpenRouter、Groq、Together、Fireworks、Ollama、LM Studio、
  vLLM……随时换。
- **一键 OAuth。** GitHub、Notion、Slack、Linear、飞书、钉钉 都是点一下跳转
  授权,不用手抄环境变量。其他集成走 API Key,也是一键保存,加密落盘。
- **本地真权限。** `shell.exec` 用 autoMate 进程的权限直接跑命令;`script.run`
  能写 Python / Bash / Node 落盘后执行;`browser.*` 用 Playwright 驱动一个真
  Chromium;`desktop.*` 接 pyautogui。
- **一进程三入口。** REST + WebSocket + MCP 共用同一个工具注册表 + 同一个
  Agent。一份代码,三种姿势调。

## 安装

```bash
pip install 'automate-hub[full]'
# 或最小安装(不带 MCP / 浏览器 / 桌面控制):
pip install automate-hub
```

可选 extras:

| extra      | 添加什么                                                            |
| ---------- | ----------------------------------------------------------------- |
| `mcp`      | stdio MCP 入口(`automate mcp`),给 Claude Code / Cursor / Cline 挂载。 |
| `browser`  | Playwright。装完跑一次 `python -m playwright install chromium`。     |
| `desktop`  | pyautogui。无显示器服务器跳过即可。                                   |
| `full`     | 上面全装。                                                           |

## 启动

```bash
automate serve
```

完事 — 浏览器自动打开 `http://127.0.0.1:8765`。第一步选一个 LLM 供应商,
粘贴 API Key,点 "Use this",就能开始用。

```bash
automate doctor    # 查看运行状态、已配模型、已连集成
automate mcp       # 以 stdio MCP 服务的形式跑(给上游 LLM 客户端挂载)
```

数据全在 `~/.automate/`。凭据用 `~/.automate/secret.key`(0600)做对称加密。
想换路径就 `AUTOMATE_HOME=/path`。

## 使用

### 浏览器里

打开 Chat 标签页,输入 `给当前仓库跑 git status 并总结改动`。事件流会展示
模型挑选 `shell.exec` → 工具结果回填 → 最终总结。所有 run 都落到 History。

### 从 Claude Code / Cursor / Cline / Kimi 调(MCP)

在客户端 MCP 配置里加:

```json
{
  "mcpServers": {
    "automate": { "command": "automate", "args": ["mcp"] }
  }
}
```

上游模型就会看到一个顶层的 `automate(prompt)` 工具,以及每一个具体工具
(`shell.exec`、`browser.open`、`notion_search` ……)。

- 想让 autoMate **自己规划**,调 `automate(prompt="...")`。
- 上游模型已经规划好步骤了,直接调具体工具,autoMate 只负责执行。

这就是和 Claude Code / Kimi 的分工:**它们做规划,我们做执行**。

### 从任意 HTTP 客户端

```bash
# 自然语言请求 — autoMate 自己规划并执行。
curl -X POST http://127.0.0.1:8765/api/agent/run \
  -H 'content-type: application/json' \
  -d '{"prompt": "在 foo/bar 仓库新建一个标题为「冒烟测试」的 issue"}'

# 已经知道要调哪个工具,直接来。
curl -X POST http://127.0.0.1:8765/api/execute/shell.exec \
  -H 'content-type: application/json' \
  -d '{"args": {"command": "git status"}}'
```

执行流走 WebSocket:`ws://127.0.0.1:8765/api/sessions/ws`,发 `{"prompt": "..."}`,
收到的是 `thinking` / `tool_call` / `tool_result` / `final` 这几种事件对象。

## 已支持的能力

**LLM 供应商(25 家)** — OpenAI · Anthropic · Google Gemini · xAI Grok ·
Mistral · Cohere · OpenRouter · Groq · Together · Fireworks · DeepInfra ·
DeepSeek · 月之暗面 Kimi · 通义千问 · 字节豆包 · 智谱 GLM · 百川 · 01.AI Yi ·
MiniMax · 阶跃星辰 · 腾讯混元 · 硅基流动 · Ollama · LM Studio · 任意
OpenAI 兼容端点。

**SaaS 集成(31 家)** — GitHub · GitLab · Gitee · Notion · Slack · Linear ·
Jira · Confluence · Trello · Asana · Monday.com · HubSpot · Airtable · Stripe ·
Shopify · Telegram · Discord · Microsoft Teams · Zoom · Twitter/X · SendGrid ·
Mailchimp · Twilio · Sentry · 飞书 · 钉钉 · 企业微信 · 微信公众号 · 微博 ·
语雀 · 高德地图。

**本地执行器** — `shell.exec` · `shell.cwd` · `script.run` · `script.list` ·
`script.read` · `desktop.screenshot` · `desktop.click` · `desktop.type` ·
`desktop.press` · `desktop.size` · `browser.open` · `browser.click` ·
`browser.type` · `browser.extract` · `browser.screenshot` · `browser.close`。

## 加新工具

```python
# automate/tools/myfeature.py
from .registry import Tool, ToolRegistry

def register(reg: ToolRegistry) -> None:
    reg.register(Tool(
        name="myfeature.do",
        description="做那件事。",
        parameters={"type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"]},
        handler=lambda x: {"echoed": x},
        category="custom",
    ))
```

然后在 `automate/tools/registry.py` 的 `build_default_registry` 里调一下
`register(reg)` 即可。

## 加新 LLM 供应商

在 `automate/providers/catalog.py` 追加一个 `ProviderSpec`。如果它兼容 OpenAI
chat-completions 协议(国内厂商基本都兼容),其他什么都不用改 — UI 重载就能
看到它。

## 状态

v1.0 — 服务、Agent 循环、MCP bridge、31 个集成全部接入,GitHub / Notion /
Slack / Linear / 飞书 / 钉钉 OAuth 已实现,其他点一下跳转。浏览器自动化用
Playwright。Python 3.10–3.12 实测通过。

## License

MIT,见 `LICENSE`。
