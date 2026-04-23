<div align="center"><a name="readme-top"></a>

<img src="./imgs/logo.png" width="120" height="120" alt="autoMate logo">
<h1>autoMate</h1>
<p><b>🤖 APIツールセンター + デスクトップ自動化 — 1つのMCPで31プラットフォーム</b></p>

[English](./README.md) | [中文](./README_CN.md)

[![PyPI](https://img.shields.io/pypi/v/automate-mcp)](https://pypi.org/project/automate-mcp/)
[![License](https://img.shields.io/github/license/yuruotong1/autoMate)](LICENSE)

> 31プラットフォームAPI統合 + デスクトップGUI自動化を同時に備える唯一のMCPサーバー — ローカル実行、クラウド依存ゼロ

https://github.com/user-attachments/assets/bf27f8bd-136b-402e-bc7d-994b99bcc368

</div>

---

## 💡 autoMateとは？

autoMateは**2つのモード**を持つMCPサーバーです：

**モード1 — APIツールセンター：** 必要なプラットフォームの環境変数を設定するだけで、そのプラットフォームのネイティブツールが自動登録されます。メッセージ送信、Issue作成、タスク管理、決済処理、連絡先検索 — すべて1つのMCPで。

**モード2 — デスクトップGUI自動化：** ClaudeにAPIなしのデスクトップアプリ（Photoshop、AutoCAD、SAP、社内ツールなど）を操作する手と目を与えます。

| モード | 必要な設定 | 動作内容 |
|--------|-----------|---------|
| **APIツールセンター** | 各プラットフォームの環境変数（必要分のみ） | 31プラットフォームのネイティブツール |
| **デスクトップ自動化** | なし（ゼロ設定） | クリック・入力・スクリーンショット |
| **クラウドビジョン** | HuggingFaceトークン | 自律UI解析 + アクション推論 |

---

## ✨ なぜautoMateを選ぶのか？

| | autoMate | Composio | Zapier MCP | Claude Connectors |
|---|---|---|---|---|
| **セットアップ** | 環境変数を設定するだけ | アカウント作成 + OAuth | Webログイン + URL貼付 | claude.aiログイン |
| **中国プラットフォーム** | 8個（独自） | なし | なし | なし |
| **GUI自動化** | あり | なし | なし | なし |
| **ローカル実行** | はい — 自分のマシンで動作 | いいえ — クラウドのみ | いいえ — クラウドのみ | いいえ — Anthropicクラウド |
| **オープンソース** | はい | ツールはクローズドソース | クローズド | クローズド |
| **コスト** | 無料 | 無料枠 + 有料 | 1コール2タスク | Pro/Enterpriseプラン |

**autoMateの独自ポジション：** ローカルファースト・中国プラットフォーム対応・オープンソース・API統合とデスクトップGUI自動化の組み合わせ — これらをすべて同時に満たす唯一のMCPサーバー。

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
        "STRIPE_SECRET_KEY": "sk_live_...",
        "SENTRY_AUTH_TOKEN": "...",
        "SENTRY_ORG_SLUG": "my-org"
      }
    }
  }
}
```

設定した分だけ有効 — 未設定の統合はエラーなく無視されます。

---

## 🔗 APIツールセンター — 31対応プラットフォーム

### 中国プラットフォーム

| プラットフォーム | 環境変数 | ツール |
|---------------|---------|-------|
| 飞书 (Feishu/Lark) | `FEISHU_APP_ID`, `FEISHU_APP_SECRET` | メッセージ送信、ドキュメント作成、チャット一覧、タスク作成 |
| 钉钉 (DingTalk) | `DINGTALK_WEBHOOK`, `DINGTALK_SECRET` | テキスト・Markdown・リンクカード送信 |
| 企業WeChat (WeCom) | `WECOM_CORP_ID`, `WECOM_CORP_SECRET`, `WECOM_AGENT_ID` | テキスト/Markdown送信、部門メンバー取得 |
| WeChat公式アカウント | `WEIXIN_APP_ID`, `WEIXIN_APP_SECRET` | テンプレートメッセージ送信、フォロワー取得 |
| 微博 (Weibo) | `WEIBO_ACCESS_TOKEN` | 投稿、タイムライン取得、プロフィール取得 |
| Gitee (码云) | `GITEE_ACCESS_TOKEN` | Issue作成/一覧、PR作成、リポジトリ情報 |
| 語雀 (Yuque) | `YUQUE_TOKEN` | ナレッジベース一覧、ドキュメント一覧/取得/作成 |
| 高德地图 (Amap) | `AMAP_API_KEY` | ジオコード、逆ジオコード、POI検索、ドライブルート |

### メッセージ & コラボレーション

| プラットフォーム | 環境変数 | ツール |
|---------------|---------|-------|
| Slack | `SLACK_BOT_TOKEN` | メッセージ送信、チャンネル一覧、履歴取得、スレッド返信 |
| Telegram | `TELEGRAM_BOT_TOKEN` | メッセージ/写真送信、更新取得、Bot情報 |
| Discord | `DISCORD_BOT_TOKEN` | メッセージ送信/取得、チャンネル一覧、DM送信 |
| Microsoft Teams | `TEAMS_WEBHOOK_URL` | メッセージ送信、リッチカード、カラーアラート |
| Zoom | `ZOOM_ACCOUNT_ID`, `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET` | 会議作成、会議一覧、会議詳細取得 |
| Twitter/X | `TWITTER_BEARER_TOKEN` | ツイート検索、ユーザー情報、ユーザーのツイート取得 |
| Twilio | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` | SMS送信、メッセージ一覧、アカウント情報 |

### DevOps & エンジニアリング

| プラットフォーム | 環境変数 | ツール |
|---------------|---------|-------|
| GitHub | `GITHUB_TOKEN` | Issue作成/一覧、PR作成、リポジトリ検索 |
| GitLab | `GITLAB_TOKEN`, `GITLAB_BASE_URL` | Issue作成/一覧、MR作成、パイプライン一覧 |
| Sentry | `SENTRY_AUTH_TOKEN`, `SENTRY_ORG_SLUG` | エラー一覧/取得、プロジェクト一覧、解決済みにする |

### プロジェクト管理 & ナレッジ

| プラットフォーム | 環境変数 | ツール |
|---------------|---------|-------|
| Notion | `NOTION_API_KEY` | 検索、ページ作成、データベースクエリ、ブロック追加 |
| Airtable | `AIRTABLE_API_KEY` | レコードの一覧/作成/更新/検索 |
| Linear | `LINEAR_API_KEY` | Issue作成/一覧、チーム一覧、Issue更新 |
| Jira | `JIRA_EMAIL`, `JIRA_API_TOKEN`, `JIRA_BASE_URL` | Issue作成/検索/取得、ステータス移行 |
| Confluence | `CONFLUENCE_EMAIL`, `CONFLUENCE_API_TOKEN`, `CONFLUENCE_BASE_URL` | ページ検索/取得/作成、Space一覧 |
| Trello | `TRELLO_API_KEY`, `TRELLO_TOKEN` | ボード/リスト/カード一覧、カード作成 |
| Asana | `ASANA_ACCESS_TOKEN` | ワークスペース/プロジェクト/タスク一覧、タスク作成/更新 |
| Monday.com | `MONDAY_API_KEY` | ボード/アイテム一覧、アイテム作成、グループ一覧 |
| HubSpot | `HUBSPOT_ACCESS_TOKEN` | 連絡先作成/検索、商談作成/一覧 |

### 決済 & Eコマース

| プラットフォーム | 環境変数 | ツール |
|---------------|---------|-------|
| Stripe | `STRIPE_SECRET_KEY` | 残高確認、顧客一覧/作成、支払い/サブスクリプション一覧 |
| Shopify | `SHOPIFY_STORE_DOMAIN`, `SHOPIFY_ACCESS_TOKEN` | 商品/注文/顧客一覧、ショップ情報取得 |

### メール & マーケティング

| プラットフォーム | 環境変数 | ツール |
|---------------|---------|-------|
| SendGrid | `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL` | メール送信、一括送信、配信統計取得 |
| Mailchimp | `MAILCHIMP_API_KEY` | オーディエンス一覧、購読者追加、キャンペーン一覧 |

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

## 📝 よくある質問

**Q: どの統合が有効になりますか？**  
環境変数が全て設定されている統合のみ有効になります。未設定の統合はエラーなく無視され、パフォーマンスへの影響もありません。

**Q: ComposioやZapier MCPとの違いは？**  
ComposioとZapier MCPはAPIコールをクラウドサーバー経由で処理し、アカウント作成が必要です。autoMateは完全にローカルで動作し、認証情報が外部に出ることはありません。また、Feishu・DingTalk・WeChatなど中国プラットフォームへの対応と、APIなしアプリ向けのデスクトップGUI自動化機能も備えています。

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
