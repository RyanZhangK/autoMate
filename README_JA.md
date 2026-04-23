<div align="center"><a name="readme-top"></a>

<img src="./imgs/logo.png" width="120" height="120" alt="autoMate logo">
<h1>autoMate</h1>
<p><b>🤖 APIツールセンター + デスクトップ自動化 — 1つのMCPで14プラットフォーム</b></p>

[English](./README.md) | [中文](./README_CN.md)

[![PyPI](https://img.shields.io/pypi/v/automate-mcp)](https://pypi.org/project/automate-mcp/)
[![License](https://img.shields.io/github/license/yuruotong1/autoMate)](LICENSE)

> Slack、Notion、GitHub、飞书、钉钉、Telegramなど14プラットフォームを接続 + APIなしのデスクトップアプリを制御

https://github.com/user-attachments/assets/bf27f8bd-136b-402e-bc7d-994b99bcc368

</div>

---

## 💡 autoMateとは？

autoMateは**2つのモード**を持つMCPサーバーです：

**モード1 — APIツールセンター：** 環境変数を設定するだけで14のプラットフォームに接続。Claudeが各プラットフォームのネイティブツールを利用できます — Slackにメッセージ送信、GitHubにIssue作成、飞书に通知、Notionデータベースをクエリ — 追加のMCPサーバー不要。

**モード2 — デスクトップGUI自動化：** ClaudeにAPIなしのデスクトップアプリ（Photoshop、AutoCAD、SAP、社内ツールなど）を操作する手と目を与えます。

| モード | 必要な設定 | 動作内容 |
|--------|-----------|---------|
| **APIツールセンター** | 各プラットフォームの環境変数 | 14プラットフォームのネイティブツール |
| **デスクトップ自動化** | なし（ゼロ設定） | クリック・入力・スクリーンショット |
| **クラウドビジョン** | HuggingFaceトークン | 自律UI解析 + アクション推論 |

---

## ✨ 主な機能

- 🔗 **14プラットフォーム統合** — 国内・国際対応、環境変数で自動有効化
- 🖥️ **APIなしアプリを自動化** — GUIがあれば動かせる
- 📚 **再利用可能なスクリプトライブラリ** — ワークフローを一度保存して永久に再利用
- ☁️ **クラウドビジョン** — OmniParser + UI-TARSによる自律UI理解、ローカルGPU不要
- 🧠 **Claudeが使いどころを理解** — 他のMCPに上書きされない明確なアイデンティティ
- 🤖 **デスクトップ自動化はゼロ設定** — APIキー不要
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

### API統合を使う場合

必要なプラットフォームの環境変数を`env`に追加：

```json
{
  "mcpServers": {
    "automate": {
      "command": "uvx",
      "args": ["automate-mcp@latest"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-...",
        "GITHUB_TOKEN": "ghp_...",
        "NOTION_API_KEY": "secret_..."
      }
    }
  }
}
```

設定した分だけ有効になります — 未設定の統合は無視されます。

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

## 🔗 APIツールセンター — 対応プラットフォーム

### 中国プラットフォーム

| プラットフォーム | 環境変数 | ツール |
|---------------|---------|-------|
| 飞书 (Feishu/Lark) | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` | メッセージ送信、ドキュメント作成、チャット一覧、タスク作成 |
| 钉钉 (DingTalk) | `DINGTALK_WEBHOOK`, `DINGTALK_SECRET` | テキスト・Markdown・リンクカード送信 |
| 企業WeChat (WeCom) | `WECOM_CORP_ID`, `WECOM_CORP_SECRET`, `WECOM_AGENT_ID` | テキスト/Markdown送信、部門メンバー取得 |
| WeChat公式アカウント | `WEIXIN_APP_ID`, `WEIXIN_APP_SECRET` | テンプレートメッセージ送信、フォロワー取得 |
| 微博 (Weibo) | `WEIBO_ACCESS_TOKEN` | 投稿、タイムライン取得、プロフィール取得 |

### 国際プラットフォーム

| プラットフォーム | 環境変数 | ツール |
|---------------|---------|-------|
| Slack | `SLACK_BOT_TOKEN` | メッセージ送信、チャンネル一覧、履歴取得、スレッド返信 |
| GitHub | `GITHUB_TOKEN` | Issue作成/一覧、PR作成、リポジトリ検索 |
| Telegram | `TELEGRAM_BOT_TOKEN` | メッセージ/写真送信、更新取得、Bot情報 |
| Discord | `DISCORD_BOT_TOKEN` | メッセージ送信/取得、チャンネル一覧、DM送信 |
| Twitter/X | `TWITTER_BEARER_TOKEN` | ツイート検索、ユーザー情報、ユーザーのツイート取得 |
| Notion | `NOTION_API_KEY` | 検索、ページ作成、データベースクエリ、ブロック追加 |
| Airtable | `AIRTABLE_API_KEY` | レコードの一覧/作成/更新/検索 |
| Linear | `LINEAR_API_KEY` | Issue作成/一覧、チーム一覧、Issue更新 |
| Jira | `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL` | Issue作成/検索/取得、ステータス移行 |

---

## 🖥️ デスクトップ自動化ツール

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

## ☁️ クラウドビジョン（オプション）

HuggingFaceの環境変数を追加することで自律的な画面解析とアクション推論が可能になります：

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

---

## 📝 よくある質問

**Q: どの統合が有効になりますか？**  
環境変数が全て設定されている統合のみ有効になります。未設定の統合はエラーなく無視されます。

**Q: Claudeが他のMCPを使ってしまう**  
v0.4.0以降にアップデートしてください。各MCPの使いどころが明確になりました。

**Q: クラウドビジョンにGPUは必要ですか？**  
不要です。HuggingFace Inference Endpointsで動作するため、HFトークンがあれば十分です。

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
