<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ChatGLM Daily

**Zhipu ChatGLM のログインポイント、キャンペーン、デイリータスク、初心者タスクを自動化する単一ファイルスクリプトです。トークン更新と残高の再取得にも対応します。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> 完全な中国語ドキュメントは [../README.md](../README.md) を参照してください。

## ✨ 主な機能

- `score_activity_open` を確認してから `daily_login_score` を呼び出します。
- 新規付与、既に受領済み、キャンペーン未開始、状態不明を区別します。
- 会員ポイントキャンペーンと季節キャンペーンを処理します。
- デイリータスクを `click → complete` の順で進めます。
- 初心者タスクの完了状態を保存し、次回以降の重複処理を避けます。
- access token を更新し、ローテーション後の refresh token と端末 ID を保存します。
- PushPlus、Bark、WeCom、DingTalk 通知に対応します。

## 🚀 最短セットアップ

リポジトリのルートで依存関係をインストールします。

```bash
python -m pip install -r requirements.txt
```

Windows クライアントのログイン情報を利用する場合：

```bash
python chatglm_login.py
python chatglm_login.py --paste
python chatglm_login.py --json-file accounts.json
python chatglm_login.py --write-env .env
```

単一アカウント：

```text
CHATGLM_TOKEN=ACCESS_TOKEN
CHATGLM_REFRESH_TOKEN=REFRESH_TOKEN
CHATGLM_DEVICE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

複数アカウント：

```text
CHATGLM_ACCOUNTS=
メイン|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
サブ|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
```

実行：

```bash
python chatglm_daily.py --query
python chatglm_daily.py
python chatglm_daily.py --only 1
python chatglm_daily.py --skip-newbie
python chatglm_daily.py --no-notify
```

## 🐧 Qinglong

```bash
pip3 install requests cryptography
```

環境変数 `CHATGLM_ACCOUNTS` を設定し、タスクを作成します。

```text
10 8 * * * python3 chatglm_daily.py
```

`chatglm_state.json` には更新済みトークン、端末 ID、初心者タスクの完了状態が保存されます。永続的で書き込み可能なディレクトリを使用し、必要なら `CHATGLM_STATE_FILE` を設定してください。

## ☁️ GitHub Actions

ワークフローは [../.github/workflows/daily.yml](../.github/workflows/daily.yml) です。現在は手動実行が有効で、スケジュール部分はコメントアウトされています。

| Secret | 必須 | 用途 |
| :--- | :---: | :--- |
| `CHATGLM_ACCOUNTS` | いずれか | 複数アカウントの認証情報 |
| `CHATGLM_TOKEN` | いずれか | 単一アカウントの access token |
| `CHATGLM_REFRESH_TOKEN` | 任意 | 単一アカウントの refresh token |
| `CHATGLM_DEVICE_ID` | 任意 | 単一アカウントの UUID |
| `CHATGLM_PROXY` | 任意 | プロキシ |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | 任意 | 通知 |

定時実行を使う場合はコメントを外します。GitHub cron は UTC で、`10 0 * * *` は北京時間 08:10 です。Actions は状態ファイルを保持しないため、refresh token が変わったら Secret を更新してください。

## 🔧 主な環境変数

| 変数 | 説明 |
| :--- | :--- |
| `CHATGLM_ACCOUNTS` | 複数アカウント。`名前\|access\|refresh\|device_id` |
| `CHATGLM_TOKEN` | 単一アカウントの access token |
| `CHATGLM_REFRESH_TOKEN` | 単一アカウントの refresh token |
| `CHATGLM_DEVICE_ID` | UUID。可能な場合は JWT から取得 |
| `CHATGLM_ACCOUNT_JSON` | アカウント JSON 文字列 |
| `CHATGLM_ACCOUNT_FILE` | アカウント JSON ファイル |
| `CHATGLM_STATE_FILE` | トークンと初心者タスクの状態ファイル |
| `CHATGLM_PROXY` | HTTP(S) / SOCKS プロキシ |
| `CHATGLM_NO_NOTIFY` | `1` で通知を無効化 |

## 📊 成功条件

少なくとも 1 つの非ゲストアカウントがログインポイント処理を完了し、付与または受領済みの明確な結果を得る必要があります。ポイント値が欠落または解析不能な場合は未確認として扱い、ゼロを成功と見なしません。

## 🔒 プライバシー

- アカウント情報を収集・アップロードしません。
- ログに完全な access token や refresh token を出力しません。
- `chatglm_state.json`、`.env`、端末 ID、ログイン情報を Git にコミットしないでください。
- Issue を投稿する前にトークンとアカウント識別子を削除してください。

## 🔗 リンク

- [Releases](https://github.com/L0NE-6/ChatGLM-Daily/releases)
- [Issues](https://github.com/L0NE-6/ChatGLM-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
