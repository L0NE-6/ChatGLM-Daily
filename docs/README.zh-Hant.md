<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ChatGLM Daily

**智譜清言每日登入積分、活動、每日任務與新手任務單檔自動化，支援權杖續期、積分回讀與多帳號彙總。**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> 完整中文文件請見 [../README.md](../README.md)。

## ✨ 核心能力

- 先查詢 `score_activity_open`，再呼叫 `daily_login_score`。
- 區分本次到帳、今日已領、活動未開啟與狀態未知。
- 處理會員積分活動與季節活動。
- 透過 `click → complete` 結算每日任務。
- 新手任務完成後寫入本地狀態，後續不重複探測。
- 自動續期 access token，保存輪換後的 refresh token 與設備識別。
- 支援 PushPlus、Bark、企業微信與釘釘通知。

## 🚀 最短可行設定

在倉庫根目錄安裝依賴：

```bash
python -m pip install -r requirements.txt
```

Windows 客戶端登入工具：

```bash
python chatglm_login.py
python chatglm_login.py --paste
python chatglm_login.py --json-file accounts.json
python chatglm_login.py --write-env .env
```

單帳號：

```text
CHATGLM_TOKEN=ACCESS_TOKEN
CHATGLM_REFRESH_TOKEN=REFRESH_TOKEN
CHATGLM_DEVICE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

多帳號：

```text
CHATGLM_ACCOUNTS=
主帳號|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
小號|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
```

執行：

```bash
python chatglm_daily.py --query
python chatglm_daily.py
python chatglm_daily.py --only 1
python chatglm_daily.py --skip-newbie
python chatglm_daily.py --no-notify
```

## 🐧 青龍面板

```bash
pip3 install requests cryptography
```

設定 `CHATGLM_ACCOUNTS`，建立任務：

```text
10 8 * * * python3 chatglm_daily.py
```

`chatglm_state.json` 保存續期令牌、設備號與新手任務狀態。請使用可寫且持久化的目錄，或透過 `CHATGLM_STATE_FILE` 指定路徑。

## ☁️ GitHub Actions

工作流為 [../.github/workflows/daily.yml](../.github/workflows/daily.yml)。目前啟用手動觸發，排程區塊預設為註解。

| Secret | 必填 | 用途 |
| :--- | :---: | :--- |
| `CHATGLM_ACCOUNTS` | 二選一 | 多帳號憑證 |
| `CHATGLM_TOKEN` | 二選一 | 單帳號 access token |
| `CHATGLM_REFRESH_TOKEN` | 否 | 單帳號 refresh token |
| `CHATGLM_DEVICE_ID` | 否 | 單帳號設備 UUID |
| `CHATGLM_PROXY` | 否 | 代理 |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | 否 | 通知 |

啟用排程時取消兩行註解。GitHub cron 使用 UTC，`10 0 * * *` 對應北京時間 08:10。Actions 不保留狀態檔；refresh token 輪換後要更新 Secret。

## 🔧 關鍵環境變數

| 變數 | 說明 |
| :--- | :--- |
| `CHATGLM_ACCOUNTS` | 多帳號：`備註\|access\|refresh\|device_id` |
| `CHATGLM_TOKEN` | 單帳號 access token |
| `CHATGLM_REFRESH_TOKEN` | 單帳號 refresh token |
| `CHATGLM_DEVICE_ID` | 單帳號 UUID，缺少時會嘗試從 JWT 讀取 |
| `CHATGLM_ACCOUNT_JSON` | 帳號 JSON 字串 |
| `CHATGLM_ACCOUNT_FILE` | 帳號 JSON 檔案 |
| `CHATGLM_STATE_FILE` | 權杖與新手任務狀態檔 |
| `CHATGLM_PROXY` | HTTP(S) / SOCKS 代理 |
| `CHATGLM_NO_NOTIFY` | `1` 關閉通知 |

## 📊 成功判定

至少一個非訪客帳號完成登入積分流程，並取得明確的到帳或已領結果。缺少或無法解析積分讀數時會標記為未確認，不會把零積分直接當成成功。

## 🔒 隱私

- 不收集或上傳帳號資料。
- 日誌不輸出完整 access token 或 refresh token。
- 不要把 `chatglm_state.json`、`.env`、設備號或登入態提交到 Git。
- 回報問題前請移除權杖與帳號標識。

## 🔗 專案連結

- [Releases](https://github.com/L0NE-6/ChatGLM-Daily/releases)
- [Issues](https://github.com/L0NE-6/ChatGLM-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
