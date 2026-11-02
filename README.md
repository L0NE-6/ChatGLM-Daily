<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🧠 ChatGLM Daily

**智谱清言每日登录积分、活动、每日任务与新手任务单文件自动化，带令牌续期、积分回读和多账号汇总。**

[简体中文](README.md) | [English](docs/README.en.md) | [繁體中文](docs/README.zh-Hant.md) | [日本語](docs/README.ja.md) | [한국어](docs/README.ko.md) | [Português (BR)](docs/README.pt-BR.md)

<a href="https://github.com/L0NE-6/ChatGLM-Daily/releases"><img src="https://img.shields.io/github/v/release/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" alt="Release" /></a>
<img src="https://img.shields.io/github/stars/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" alt="Stars" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/%E9%9D%92%E9%BE%99-Ready-4EAA25?style=for-the-badge" alt="Qinglong" />
<a href="https://github.com/L0NE-6/ChatGLM-Daily/actions/workflows/daily.yml"><img src="https://img.shields.io/github/actions/workflow/status/L0NE-6/ChatGLM-Daily/daily.yml?branch=main&style=for-the-badge&label=Actions&logo=githubactions&logoColor=white" alt="GitHub Actions" /></a>
<img src="https://img.shields.io/github/license/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=License&color=F472B6" alt="License" />
<a href="https://github.com/L0NE-6/ChatGLM-Daily/releases"><img src="https://img.shields.io/badge/%E2%AC%87%20Releases-%E4%B8%8B%E8%BD%BD-2ea44f?style=for-the-badge&logo=github&logoColor=white" alt="Releases Download" /></a>

[✨ 30 秒速览](#-30-秒速览) · [🚀 快速开始](#-快速开始) · [🐧 青龙部署](#-青龙部署) · [☁️ GitHub Actions](#-github-actions) · [🔧 环境变量](#-环境变量) · [❓ 常见问题](#-常见问题) · [✦ 星轨](#-星轨-star-trail)

</div>

---

## ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **用途** | 完成智谱清言每日登录积分、会员/季节活动、每日任务和新手任务。 |
| **输入** | Windows 客户端登录态，或 `CHATGLM_ACCOUNTS` / 单账号 access、refresh、device_id。 |
| **输出** | 每账号签到状态、任务完成数、积分奖励和当前余额。 |
| **部署** | Windows 本地登录工具、青龙面板、GitHub Actions、Linux 定时任务。 |
| **依赖** | Python 3 + `requests`；登录工具额外依赖 `cryptography`。 |
| **成功判据** | 至少一个非访客账号完成签到链路并得到明确到账/已领结果；活动空窗不伪造成功。 |

**核心能力**

- 先查 `score_activity_open`，再调用 `daily_login_score`，区分到账、已领、未开启和状态未知。
- 自动处理会员积分活动与季节活动领取。
- 读取每日任务中心，按 `click → complete` 结算任务。
- 新手任务一次性结算，完成后写入本地状态，后续不反复探测。
- 每个账号独立保存 refresh token、设备号和新手任务状态。
- 支持 PushPlus、Bark、企业微信和钉钉通知。

## 🧭 签到链路

| 模块 | 实际行为 |
| :--- | :--- |
| 每日签到 | 查询活动状态后领取登录积分，并回读余额相关结果 |
| 活动奖励 | 尝试会员积分活动与季节活动；未开始或已领取按中性结果处理 |
| 每日任务 | 读取任务中心，逐项 `click → complete`，记录完成数和奖励积分 |
| 新手任务 | 仅在本地状态未完成时执行；全部完成后持久化，后续跳过 |
| 余额 | 从会员信息读取真实积分余额；无法解析时明确提示，不伪造数字 |
| 多账号 | 令牌、设备号、续期状态和结果均按账号隔离 |

## 🚀 快速开始

**1. 安装依赖**

```bash
python -m pip install -r requirements.txt
```

**2. 方式 A：读取 Windows 客户端登录态**

先登录智谱清言桌面客户端，再在当前 Windows 用户下运行：

```bash
python chatglm_login.py
```

工具会读取客户端 Cookies、解密登录态并输出：

```text
CHATGLM_ACCOUNTS=
备注|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
```

如果客户端占用 Cookies 数据库，先退出客户端重试。其他入口：

```bash
python chatglm_login.py --paste
python chatglm_login.py --json-file accounts.json
python chatglm_login.py --write-env .env
python chatglm_login.py --name 小号
```

**3. 方式 B：手动填写**

浏览器登录后，从开发者工具 Cookies 读取 `chatglm_token`、`chatglm_refresh_token`。单账号：

```text
CHATGLM_TOKEN=ACCESS_TOKEN
CHATGLM_REFRESH_TOKEN=REFRESH_TOKEN
CHATGLM_DEVICE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

多账号：

```text
CHATGLM_ACCOUNTS=
主账号|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
小号|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
```

`device_id` 必须是 UUID 形态。登录工具会优先从 JWT 的 `device_id` 声明读取，避免每次请求更换设备身份。

**4. 运行**

```bash
python chatglm_daily.py
python chatglm_daily.py --query
python chatglm_daily.py --only 1
python chatglm_daily.py --skip-newbie
python chatglm_daily.py --no-notify
```

## ⌨️ 命令行

| 命令 | 作用 |
| :--- | :--- |
| `python chatglm_daily.py` | 完整签到、活动、每日任务和新手任务 |
| `python chatglm_daily.py --query` | 只查询余额和任务进度 |
| `python chatglm_daily.py --only 1` | 只处理第 1 个账号 |
| `python chatglm_daily.py --skip-newbie` | 本轮跳过新手任务 |
| `python chatglm_daily.py --no-notify` | 本轮不发送通知 |

退出码：`0` 表示至少一个账号执行成功；`1` 表示账号缺失、全部失败或只匹配到访客账号。

## 🐧 青龙部署

```bash
pip3 install requests cryptography
```

在青龙环境变量中填写 `CHATGLM_ACCOUNTS`，再创建任务：

```text
10 8 * * * python3 chatglm_daily.py
```

多账号会自动串行执行。续期后的令牌与设备号写入 `chatglm_state.json`，新手任务完成状态也保存在该文件中。该文件已加入 `.gitignore`；青龙环境建议使用可写且持久化的目录。

## ☁️ GitHub Actions

工作流位于 [`.github/workflows/daily.yml`](.github/workflows/daily.yml)。**默认只有手动触发**；定时段目前被注释，公开仓库不会自动空跑。

在仓库 Secrets 中配置：

| Secret | 必填 | 说明 |
| :--- | :---: | :--- |
| `CHATGLM_ACCOUNTS` | 二选一 | 多账号令牌 |
| `CHATGLM_TOKEN` | 二选一 | 单账号 access token |
| `CHATGLM_REFRESH_TOKEN` | 否 | 单账号 refresh token |
| `CHATGLM_DEVICE_ID` | 否 | 单账号设备 UUID |
| `CHATGLM_PROXY` | 否 | HTTP(S) / SOCKS 代理 |
| `PLUSPLUS_TOKEN` | 否 | PushPlus 推送令牌 |
| `BARK_URL` | 否 | Bark 推送地址 |
| `WECOM_WEBHOOK` | 否 | 企业微信机器人 webhook |
| `DINGTALK_WEBHOOK` | 否 | 钉钉机器人 webhook |

需要定时运行时，取消 workflow 中 schedule 两行的注释。示例 cron `10 0 * * *` 对应北京时间 08:10，GitHub cron 本身使用 UTC。

Actions 运行环境不会保留 `chatglm_state.json`；如果上游轮换了 refresh token，需要重新导出并更新 Secret。长期运行优先使用青龙或可持久化目录。

## 🔧 环境变量

### 账号与运行

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `CHATGLM_ACCOUNTS` | 二选一 | 多账号，每行 `备注\|access\|refresh\|device_id` |
| `CHATGLM_TOKEN` | 二选一 | 单账号 access token |
| `CHATGLM_REFRESH_TOKEN` | 否 | 单账号 refresh token，可自动续期 |
| `CHATGLM_DEVICE_ID` | 否 | 单账号设备 UUID；缺省时从 JWT 读取 |
| `CHATGLM_ACCOUNT_JSON` | 否 | 账号 JSON 字符串 |
| `CHATGLM_ACCOUNT_FILE` | 否 | 账号 JSON 文件路径 |
| `CHATGLM_STATE_FILE` | 否 | 令牌和新手任务状态文件，默认 `chatglm_state.json` |
| `CHATGLM_PROXY` | 否 | HTTP(S) / SOCKS 代理 |
| `CHATGLM_NO_NOTIFY` | 否 | 设为 `1` 时关闭推送 |
| `CHATGLM_BASE_URL` | 高级 | 默认 `https://chatglm.cn` |

### 账号 JSON

`CHATGLM_ACCOUNT_FILE` / `CHATGLM_ACCOUNT_JSON` 支持对象或数组：

```json
{
  "accounts": [
    {
      "name": "主账号",
      "access_token": "ACCESS_TOKEN",
      "refresh_token": "REFRESH_TOKEN",
      "device_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  ]
}
```

### 推送

| 通道 | 变量 |
| :--- | :--- |
| PushPlus | `PLUSPLUS_TOKEN` |
| Bark | `BARK_URL` |
| 企业微信 | `WECOM_WEBHOOK` 或 `QYWX_TOKEN` |
| 钉钉 | `DINGTALK_WEBHOOK` |

所有通道均为可选，推送失败不会改变签到退出码。

## 📡 请求链路

脚本按客户端形态生成每次请求的签名头：

- `X-Timestamp`
- `X-Nonce`
- `X-Sign`
- `X-Device-Id`
- `X-App-Version: 2.0.7`

设备号会随账号持久化。access token 失效时自动尝试 refresh token，并保存轮换后的令牌。访客账号没有积分体系，会被明确跳过。

## 📊 输出与判定

- 签到响应缺少或无法解析积分读数时，明确报告“未确认”，不把零积分自动当作成功。
- 活动未开始、已经结束或今天已领取都属于中性结果，不会单独判签到失败。
- 余额与任务进度会尽量回读；上游字段异常时会保留错误提示。
- 多账号分别输出成功、跳过或失败，并以“至少一个账号成功”作为整体成功条件。

## ❓ 常见问题

<details>
<summary><b>访客账号为什么跳过？</b></summary>

游客只能对话，没有积分体系。签到、余额和任务中心只对登录账号开放。
</details>

<details>
<summary><b>登录态失效怎么办？</b></summary>

重新运行 `python chatglm_login.py`，再更新 `CHATGLM_ACCOUNTS`。如果只有 access token 而没有 refresh token，令牌过期后只能重新登录。
</details>

<details>
<summary><b>读取客户端 Cookies 失败怎么办？</b></summary>

客户端 Cookies 使用 Windows DPAPI，必须在当前 Windows 用户下读取。先关闭客户端后重试，或改用 `--paste`。
</details>

<details>
<summary><b>活动显示无可领取是失败吗？</b></summary>

不是。活动未开始、已经结束或今天已领取都会返回中性结果，签到本身仍可能成功。
</details>

## 🔒 隐私说明

- 不收集、不上传账号信息；
- 令牌只从环境变量、账号文件或本机状态读取；
- 日志不输出完整 access token 或 refresh token；
- `chatglm_state.json`、`.env` 已加入 `.gitignore`；
- 不要在 Issue、README、Release 或公开聊天中粘贴登录态。

## ☕ 支持与反馈

脚本免费使用，不含账号数据。如果它对你有帮助，可以自愿扫码支持：

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>

反馈前请移除令牌、设备号和日志中的账号标识，再通过 [Issues](https://github.com/L0NE-6/ChatGLM-Daily/issues) 提交；版本变化见 [Releases](https://github.com/L0NE-6/ChatGLM-Daily/releases)。

## ✦ 星轨 Star Trail

把每日签到变成一条安静的轨道，让每次 Star 留下清晰的信号。

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/ChatGLM-Daily&type=Date&theme=dark" />
  <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/ChatGLM-Daily&type=Date&theme=light" />
  <img alt="ChatGLM Daily Star Trail" src="https://api.star-history.com/svg?repos=L0NE-6/ChatGLM-Daily&type=Date&theme=light" />
</picture>

<div align="center">

[Releases](https://github.com/L0NE-6/ChatGLM-Daily/releases) · [Issues](https://github.com/L0NE-6/ChatGLM-Daily/issues) · [⭐ Star](https://github.com/L0NE-6/ChatGLM-Daily)

</div>
