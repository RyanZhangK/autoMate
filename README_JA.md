<div align="center"><a name="readme-top"></a>

<img src="./imgs/logo.png" width="120" height="120" alt="autoMate logo">
<h1>autoMate</h1>
<p><b>🤖 APIのないデスクトップアプリを自動化するMCPサーバー</b></p>

[English](./README.md) | [中文](./README_CN.md)

[![PyPI](https://img.shields.io/pypi/v/automate-mcp)](https://pypi.org/project/automate-mcp/)
[![License](https://img.shields.io/github/license/yuruotong1/autoMate)](LICENSE)

> Claudeに手と目を — APIがなくても、どんなデスクトップアプリも自動化できる

https://github.com/user-attachments/assets/bf27f8bd-136b-402e-bc7d-994b99bcc368

</div>

---

## 💡 autoMateとは？

autoMateはMCPサーバーです。AIアシスタント（Claude、GPTなど）が**APIのないデスクトップアプリを直接操作**できるようになります。

**他のMCPとの違い：**

| MCPサーバー | 自動化対象 |
|------------|----------|
| filesystem MCP | ファイルとフォルダ |
| browser MCP | Webページ |
| Windows MCP | OS設定・システムコール |
| **autoMate** | **APIのないデスクトップGUIアプリ** — Photoshop、AutoCAD、SAP、社内ツール… |

**2つの動作モード：**

| モード | 動作方法 | 必要な設定 |
|--------|---------|-----------|
| **基本モード** | Claudeが画面を見て、autoMateがクリック/入力 | なし — ゼロ設定 |
| **クラウドビジョン** | autoMateが自律的にUI解析 + クラウドVLM推論 | HFトークン + エンドポイント |

---

## ✨ 主な機能

- 🖥️ **APIなしアプリを自動化** — GUIがあれば動かせる
- 📚 **再利用可能なスクリプトライブラリ** — ワークフローを一度保存して永久に再利用
- ☁️ **クラウドビジョン** — OmniParser + UI-TARSによる自律UI理解、ローカルGPU不要
- 🧠 **Claudeが使いどころを理解** — 他のMCPに上書きされない明確なアイデンティティ
- 🤖 **基本利用はゼロ設定** — APIキー・環境変数不要
- 🌍 **クロスプラットフォーム** — Windows、macOS、Linux

---

## 🔌 セットアップ

> **前提：** `pip install uv`

### Claude Desktop

**Settings → Developer → Edit Config** を開いて追加：

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

Claude Desktopを再起動すれば完了。`@latest`により毎回起動時に自動更新されます。

### OpenClaw

`~/.openclaw/openclaw.json` を編集：

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

設定 → MCPサーバー → 追加：

```json
{
  "automate": {
    "command": "uvx",
    "args": ["automate-mcp@latest"]
  }
}
```

---

## ☁️ クラウドビジョン（オプション）

クラウドビジョンにより、autoMateが自律的に画面解析とアクション推論を行います。**ローカルGPU不要**。

2つのHuggingFace Inference Endpointsを使用：
- **OmniParser V2** — スクリーンショットからUI要素（アイコン・ボタン・テキスト）を検出
- **UI-TARS / Qwen-VL** — 次に実行するアクションを推論するビジョン言語モデル

### 設定

MCPの設定に環境変数を追加：

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

詳細はリポジトリの `.env.example` を参照。

---

## 🛠️ MCPツール

**スクリプトライブラリ** — 一度保存すれば永久に再利用：

| ツール | 説明 |
|--------|------|
| `list_scripts` | 保存済みスクリプト一覧 |
| `run_script` | 名前でスクリプトを実行 |
| `save_script` | ワークフローをスクリプトとして保存 |
| `show_script` | スクリプトの内容を表示 |
| `delete_script` | スクリプトを削除 |
| `install_script` | URLまたはコミュニティライブラリからインストール |

**クラウドビジョン** — 自律的なUI理解（HF設定が必要）：

| ツール | 説明 |
|--------|------|
| `cloud_vision_config` | クラウドビジョンの設定状態を確認 |
| `warm_endpoints` | スケールゼロのHFエンドポイントを起動 |
| `parse_screen` | クラウドOmniParserでUI要素を検出 |
| `reason_action` | VLMに次のアクションを推論させる |
| `smart_act` | 全自動ループ：解析 → 推論 → 実行 → 繰り返し |

**低レベルデスクトップ制御：**

| ツール | 説明 |
|--------|------|
| `screenshot` | 画面をキャプチャしてbase64 PNGで返す |
| `click` | 座標をクリック |
| `double_click` | 座標をダブルクリック |
| `type_text` | テキストを入力（CJK対応） |
| `press_key` | キーまたはキーコンボを押す |
| `scroll` | 上下スクロール |
| `mouse_move` | カーソルを移動（クリックなし） |
| `drag` | ある位置から別の位置にドラッグ |

---

## 📝 よくある質問

**Q: Claudeがautomateの代わりに他のMCPを使ってしまう**  
v0.4.0以降にアップデートしてください。各MCPの使いどころが明確になりました。

**Q: クラウドビジョンにGPUは必要ですか？**  
不要です。HuggingFace Inference Endpointsで動作するため、HFトークンとデプロイ済みエンドポイントがあれば十分です。

**Q: macOS / Linuxで動作しますか？**  
はい。3プラットフォーム全てで動作します。

---

## 🤝 コントリビュート

<a href="https://github.com/yuruotong1/autoMate/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yuruotong1/autoMate" />
</a>

---

<div align="center">
⭐ スターは制作者への励ましであり、より多くの人々がautoMateを発見する機会です ⭐
</div>
