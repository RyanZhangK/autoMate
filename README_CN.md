<div align="center"><a name="readme-top"></a>

<img src="./imgs/logo.png" width="120" height="120" alt="autoMate logo">
<h1>autoMate</h1>
<p><b>🤖 专为没有 API 的桌面软件而生的自动化工具</b></p>

[English](./README.md) | [日本語](./README_JA.md)

[![PyPI](https://img.shields.io/pypi/v/automate-mcp)](https://pypi.org/project/automate-mcp/)
[![License](https://img.shields.io/github/license/yuruotong1/autoMate)](LICENSE)

> 给 Claude 一双手和眼睛——自动化任何桌面软件，哪怕它没有 API

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

autoMate 是一个 MCP Server，让 AI 助手（Claude、GPT 等）能够**直接操控任何桌面软件**——即使那个软件没有 API、没有插件系统、没有任何自动化接口。

**和其他 MCP 的区别：**

| MCP Server | 负责什么 |
|------------|---------|
| filesystem MCP | 文件和文件夹 |
| browser MCP | 网页 |
| Windows MCP | 系统设置和系统调用 |
| **autoMate** | **没有 API 的桌面 GUI 软件** — 剪映、Photoshop、AutoCAD、微信、SAP、公司内部系统… |

**两种使用模式：**

| 模式 | 工作方式 | 需要配置 |
|------|---------|---------|
| **基础模式** | Claude 看屏幕，autoMate 负责点击/输入 | 无——零配置 |
| **云端视觉模式** | autoMate 自己解析界面 + 云端视觉模型推理 | HuggingFace Token + Endpoints |

---

## ✨ 功能特点

- 🖥️ **专为无 API 的桌面软件而生** — 有界面就能自动化
- 📚 **可复用脚本库** — 工作流保存一次，永久复用；一行命令安装社区脚本
- ☁️ **云端视觉** — 云端 OmniParser 解析界面 + UI-TARS 推理，无需本地 GPU
- 🧠 **Claude 知道什么时候该用它** — 明确的使用边界，不会被其他 MCP 替代
- 🤖 **基础使用零配置** — 不需要 API Key，不需要环境变量
- 🌍 **跨平台** — Windows、macOS、Linux（Quicker 只支持 Windows）

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

### OpenClaw（小龙虾）

编辑 `~/.openclaw/openclaw.json`：

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

## ☁️ 云端视觉（可选）

云端视觉为 autoMate 增加了自主界面解析和动作推理能力——**无需本地 GPU**。

使用两个 HuggingFace Inference Endpoints：
- **OmniParser V2** — 从截图中检测所有 UI 元素（图标、按钮、文字）
- **UI-TARS / Qwen-VL** — 视觉语言模型，决定下一步该执行什么操作

### 配置方式

在 MCP 配置中添加环境变量：

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

详细说明见仓库中的 `.env.example`。

### 云端视觉工作流

```
1. warm_endpoints   — 唤醒已缩容到零的 Endpoints（需 1–5 分钟）
2. parse_screen     — 通过云端 OmniParser 检测所有 UI 元素
3. reason_action    — 让视觉语言模型决定下一步点什么/输什么
   — 或 —
   smart_act        — 全自动循环：解析 → 推理 → 执行 → 重复
```

---

## 🛠️ MCP 工具列表

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

**底层桌面控制** — 构建或执行脚本时使用：

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

**内联提示语法：**

| 提示 | 操作 |
|------|------|
| `[click:coord=320,240]` | 点击绝对屏幕坐标 |
| `[type:文字内容]` | 输入文字 |
| `[key:ctrl+s]` | 按快捷键 |
| `[wait:2]` | 等待 2 秒 |
| `[scroll_up]` / `[scroll_down]` | 滚动页面 |

没有提示的步骤，由 AI 视觉模型在运行时自动识别执行。

---

## 📝 常见问题

**Q：跟直接用 Claude 的 computer-use 有什么区别？**  
autoMate 提供持久化、可复用的脚本。一个任务自动化一次之后就保存下来，下次直接 `run_script` 秒执行。云端视觉模式还能让 autoMate 自己解析界面，不依赖 Claude 的视觉能力。

**Q：Claude 有时候还是会用 Windows MCP 或 filesystem MCP 替代我的操作怎么办？**  
升级到 v0.4.0+，新版 server description 已明确告知 Claude 各个 MCP 的使用边界。

**Q：云端视觉需要 GPU 吗？**  
不需要——全部跑在 HuggingFace Inference Endpoints 上，只需要一个 HF Token 和部署好的 Endpoint。

**Q：支持 macOS / Linux 吗？**  
支持，三个平台均可运行。这也是相比 Quicker（仅 Windows）的核心优势。

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
