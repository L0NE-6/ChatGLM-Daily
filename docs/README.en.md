<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ChatGLM Daily

**A single-file automation for Zhipu ChatGLM daily login points, campaigns, daily tasks, and newcomer tasks, with token renewal and balance readback.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> The complete Chinese documentation is available in [../README.md](../README.md).

## ✨ Core capabilities

- Checks `score_activity_open` before calling `daily_login_score`.
- Distinguishes newly credited points, already claimed, inactive campaigns, and unknown states.
- Settles member point campaigns and seasonal campaign rewards.
- Processes daily tasks through `click → complete`.
- Handles one-time newcomer tasks and stores completion state locally.
- Renews access tokens, persists rotated refresh tokens, and keeps a separate device identity per account.
- Supports PushPlus, Bark, WeCom, and DingTalk notifications.

## 🚀 Quick start

Install dependencies from the repository root:

```bash
python -m pip install -r requirements.txt
```

### Windows client login state

Sign in to the ChatGLM desktop client, then run under the same Windows user:

```bash
python chatglm_login.py
```

The tool decrypts the client cookies and prints:

```text
CHATGLM_ACCOUNTS=
Main|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
```

If the cookie database is locked, exit the client and retry. Other modes:

```bash
python chatglm_login.py --paste
python chatglm_login.py --json-file accounts.json
python chatglm_login.py --write-env .env
```

### Manual environment

Single account:

```text
CHATGLM_TOKEN=ACCESS_TOKEN
CHATGLM_REFRESH_TOKEN=REFRESH_TOKEN
CHATGLM_DEVICE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Multiple accounts:

```text
CHATGLM_ACCOUNTS=
Main|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
Alt|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
```

Run a query or the complete flow:

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

Set `CHATGLM_ACCOUNTS` in the panel, then create:

```text
10 8 * * * python3 chatglm_daily.py
```

Rotated tokens, device IDs, and newcomer completion state are stored in `chatglm_state.json`. Use a writable persistent path; `CHATGLM_STATE_FILE` can override the location.

## ☁️ GitHub Actions

The workflow is [../.github/workflows/daily.yml](../.github/workflows/daily.yml). Manual execution is enabled; the schedule block is commented out by default.

| Secret | Required | Purpose |
| :--- | :---: | :--- |
| `CHATGLM_ACCOUNTS` | One of two | Multi-account credentials |
| `CHATGLM_TOKEN` | One of two | Single-account access token |
| `CHATGLM_REFRESH_TOKEN` | Optional | Single-account refresh token |
| `CHATGLM_DEVICE_ID` | Optional | Single-account device UUID |
| `CHATGLM_PROXY` | Optional | HTTP(S) / SOCKS proxy |
| `PLUSPLUS_TOKEN`, `BARK_URL`, `WECOM_WEBHOOK`, `DINGTALK_WEBHOOK` | Optional | Notifications |

To enable the schedule, uncomment its two lines. The example `10 0 * * *` is 08:10 Beijing time because GitHub cron uses UTC. Actions does not preserve `chatglm_state.json`; update the refresh-token secret after rotation.

## 🔧 Key environment variables

| Variable | Required | Description |
| :--- | :---: | :--- |
| `CHATGLM_ACCOUNTS` | One of two | Records in `name\|access\|refresh\|device_id` format |
| `CHATGLM_TOKEN` | One of two | Single-account access token |
| `CHATGLM_REFRESH_TOKEN` | Optional | Single-account refresh token |
| `CHATGLM_DEVICE_ID` | Optional | UUID device identity; inferred from the JWT when possible |
| `CHATGLM_ACCOUNT_JSON` | Optional | Account JSON string |
| `CHATGLM_ACCOUNT_FILE` | Optional | Account JSON file |
| `CHATGLM_STATE_FILE` | Optional | Token and newcomer-task state file |
| `CHATGLM_PROXY` | Optional | HTTP(S) / SOCKS proxy |
| `CHATGLM_NO_NOTIFY` | Optional | Set to `1` to disable notifications |
| `CHATGLM_BASE_URL` | Advanced | Defaults to `https://chatglm.cn` |

## 📊 Success criteria

At least one non-guest account must complete the login-point flow with a confirmed credited or already-claimed result. A missing or unreadable points value is reported as unconfirmed rather than treated as success. Guest accounts are skipped.

## 🔒 Privacy

- The project does not collect or upload account information.
- Logs do not print complete access or refresh tokens.
- Keep `chatglm_state.json` and `.env` out of Git.
- Store credentials only in local environment variables, GitHub Secrets, or Qinglong variables.
- Remove tokens, device IDs, and account identifiers before opening an issue.

## 🔗 Project links

- [Releases](https://github.com/L0NE-6/ChatGLM-Daily/releases)
- [Issues](https://github.com/L0NE-6/ChatGLM-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
