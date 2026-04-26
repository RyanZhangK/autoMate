# autoMate

> 给任何大模型一双手的调度中枢。

autoMate 是一个本地小服务,自带浏览器界面。安装完打开 `http://127.0.0.1:8765`,
配上你喜欢的大模型 API Key,授权要让它操作的 SaaS 账号 — 从此任何能说 **HTTP**
或 **MCP** 的客户端(Claude Code、Cursor、Cline、Kimi K2、你自己的脚本)都
可以把一段自然语言交给 autoMate,由它去**规划、选工具、抽参数、跑命令**,
落地到你的机器、你的浏览器和 30+ 第三方 API 上。

```
┌──────────────────────────────────────────────────────────────────┐
│  浏览器 UI · http://127.0.0.1:8765                               │
│  模型配置 · 工具市场 · 实时对话 · 历史记录                       │
└────────────────┬─────────────────────────────────────────────────┘
                 │  HTTP · WebSocket
┌────────────────▼─────────────────────────────────────────────────┐
│  统一接入层                                                        │
│  ┌──────────────┬─────────────────────────────────────────────┐  │
│  │  REST API    │  POST /api/agent/run                        │  │
│  │  WebSocket   │  /api/sessions/ws  (执行流实时推送)         │  │
│  │  MCP (stdio) │  `automate mcp`  Claude Code / Cursor       │  │
│  └──────────────┴─────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────┤
│  Agent 内核                                                       │
│  · 解析自然语言 · 选工具 · 抽参数 · 反馈循环                    │
├──────────────────────────────────────────────────────────────────┤
│  工具                                                              │
│  ┌──────────┬───────────────┬──────────────────┬──────────────┐  │
│  │ shell    │ browser       │ bx.* (你正在用    │ 集成市场     │  │
│  │ script   │ (Playwright,  │ 的浏览器,通过    │ github       │  │
│  │ desktop  │ 起新标签页)   │ Chrome 扩展)     │ notion 等    │  │
│  └──────────┴───────────────┴──────────────────┴──────────────┘  │
├──────────────────────────────────────────────────────────────────┤
│  ~/.automate/  · SQLite + Fernet 加密凭据                         │
└──────────────────────────────────────────────────────────────────┘
```

English: [README.md](./README.md)

## 为什么需要 autoMate

你已经有趁手的 AI 编码助手了。它擅长**规划**,但伸不进**你的** Notion、
**你的** GitHub、**你的** Shell、**你那个已经登录好的浏览器** — autoMate
就是来填这块空缺的执行器。它跑在你自己的机器上,凭据从不离开本地,对外只
暴露一个干净的统一接口,任何大模型客户端都能直接调用。

- **大脑自带。** 25+ 模型供应商目录:OpenAI、Anthropic、Gemini、Kimi、通义、
  DeepSeek、豆包、智谱 GLM、Yi、MiniMax、混元、百川、阶跃、Mistral、Grok、
  OpenRouter、Groq、Together、Fireworks、Ollama、LM Studio、vLLM……随时换。
- **一键 OAuth。** GitHub、Notion、Slack、Linear、飞书、钉钉 都是点一下跳转
  授权,不用手抄环境变量。其他集成走 API Key,也是一键保存,加密落盘。
- **本地真权限。** `shell.exec` 用 autoMate 进程的权限直接跑命令;`script.run`
  能写 Python / Bash / Node 落盘后执行;`desktop.*` 接 pyautogui。
- **两种浏览器自动化。** `browser.*` 用 Playwright 起一个干净的 Chromium
  (适合无登录态任务);`bx.*` 通过 Chrome 扩展接你**正在用的浏览器** —
  你的标签页、你的 Cookie、你的登录态都能直接用。
- **一进程三入口。** REST + WebSocket + MCP 共用同一个工具注册表 + 同一个
  Agent。一份代码,三种姿势调。

## 安装

挑哪种顺手用哪种。

### 1. pip(开发者推荐)

```bash
pip install 'automate-hub[full]'
automate serve
```

| extra      | 添加什么                                                            |
| ---------- | ----------------------------------------------------------------- |
| `mcp`      | stdio MCP 入口(`automate mcp`),给 Claude Code / Cursor / Cline 挂载。 |
| `browser`  | Playwright。装完跑一次 `python -m playwright install chromium`。     |
| `desktop`  | pyautogui。无显示器服务器跳过即可。                                   |
| `full`     | 上面全装。                                                           |

### 2. 独立二进制(无需 Python)

到 [Releases 页面](https://github.com/yuruotong1/autoMate/releases) 下载对应
平台的包(Windows / macOS Apple Silicon / Linux),解压跑 `./automate/automate serve`。

### 3. Docker

```bash
docker run --rm -p 8765:8765 -v automate-data:/data \
  ghcr.io/yuruotong1/automate:latest
```

或者自己 build:`docker build -t automate-hub . && docker run -p 8765:8765 automate-hub`。

### 4. 浏览器扩展(用 `bx.*` 工具的多一步)

任意方式装好 autoMate 后,打开 `chrome://extensions`,开**开发者模式**,
点 **加载已解压的扩展程序**,选项目里的 `extension/` 文件夹。工具栏图标
徽章变成绿色 **ON** 就连上了。详见 [`extension/README.md`](./extension/README.md)。

## 启动

```bash
automate serve            # 浏览器 UI + REST + WebSocket  http://127.0.0.1:8765
automate mcp              # 把工具暴露成 stdio MCP 服务
automate doctor           # 看路径、已配模型、已连集成
```

数据在 `~/.automate/`,凭据用 `~/.automate/secret.key`(0600)对称加密。
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
(`shell.exec`、`bx.click`、`notion_search` ……)。

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
`desktop.press` · `desktop.size`。

**无头浏览器**(Playwright) — `browser.open` · `browser.click` · `browser.type` ·
`browser.extract` · `browser.screenshot` · `browser.close`。

**接管你的真浏览器**(Chrome 扩展) — `bx.tabs` · `bx.open` · `bx.activate` ·
`bx.close` · `bx.navigate` · `bx.screenshot` · `bx.click` · `bx.type` ·
`bx.extract` · `bx.scroll` · `bx.eval`。

## 项目结构

```
autoMate/
├─ automate/              # 主包
│  ├─ server/             # FastAPI 应用、路由、MCP bridge
│  │  └─ api/             # REST + WebSocket 端点
│  ├─ agent/              # 自然语言 → 工具调用循环
│  ├─ providers/          # 模型供应商目录 + 客户端
│  ├─ tools/              # shell · script · browser · desktop · bx · 适配器
│  ├─ integrations/       # 31 个 SaaS 连接器
│  ├─ oauth/              # 授权码流程 + 供应商目录
│  ├─ store/              # SQLite + Fernet 加密
│  ├─ frontend/           # 静态 SPA (Tailwind + Alpine,无需构建)
│  ├─ extension_bus.py    # Chrome 扩展的 sync ↔ async 桥
│  ├─ settings.py · cli.py · version.py
├─ extension/             # Chrome MV3 扩展(加载已解压的扩展程序)
├─ packaging/             # PyInstaller spec
├─ Dockerfile
└─ pyproject.toml
```

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
Slack / Linear / 飞书 / 钉钉 OAuth 已实现,其他点一下跳转。无头浏览器走
Playwright,真浏览器走 Chrome 扩展。多端分发:pip · 独立二进制 · Docker。
Python 3.10–3.12 实测通过。

## License

MIT,见 `LICENSE`。
