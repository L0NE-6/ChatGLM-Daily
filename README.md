# 智谱清言每日签到

单文件青龙脚本，支持智谱清言每日登录积分、活动领取、每日任务、新手任务和积分回读。

## 功能

| 模块 | 内容 |
| :--- | :--- |
| 每日签到 | 先查 `score_activity_open`，再调 `daily_login_score`；区分到账、已领、未开启与状态未知 |
| 活动领取 | 会员积分活动抽奖、季节活动领取 |
| 每日任务 | 读取任务中心，按 `click → complete` 完成并回读积分 |
| 新手任务 | 一次性任务，全部完成后写本地状态，后续不再重复探测 |
| 余额 | 会员信息中的真实积分余额 |
| 多账号 | 每个账号独立令牌、设备号、续期状态和结果 |
| 推送 | PushPlus、Bark、企业微信、钉钉 |

## 快速开始

### 方式一：读取 Windows 客户端登录态

先登录智谱清言桌面客户端，然后在 Windows 上运行：

```bash
pip install requests cryptography
python chatglm_login.py
```

工具会读取客户端 Cookies，解密登录态，并输出：

```text
CHATGLM_ACCOUNTS=
备注|access_token|refresh_token|device_id
```

若客户端占用 Cookies 导致读取失败，先退出客户端再运行。也可以使用：

```bash
python chatglm_login.py --paste
python chatglm_login.py --json-file accounts.json
python chatglm_login.py --write-env .env
```

### 方式二：手动填写环境变量

浏览器登录后，在开发者工具的 Cookies 中读取：

- `chatglm_token`
- `chatglm_refresh_token`

单账号：

```text
CHATGLM_TOKEN=access_token
CHATGLM_REFRESH_TOKEN=refresh_token
CHATGLM_DEVICE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

多账号推荐：

```text
CHATGLM_ACCOUNTS=
主账号|access_token|refresh_token|device_id
小号|access_token|refresh_token|device_id
```

`device_id` 必须是 UUID 形态。登录工具会优先从 JWT 的 `device_id` 声明读取，避免每次请求更换设备身份。

## 运行

```bash
python chatglm_daily.py
python chatglm_daily.py --only 1
python chatglm_daily.py --query
python chatglm_daily.py --skip-newbie
python chatglm_daily.py --no-notify
```

退出码：

- `0`：至少一个账号执行成功
- `1`：账号缺失、全部失败或只匹配到访客账号

## 青龙部署

1. 安装依赖：

```bash
pip3 install requests cryptography
```

2. 在环境变量中填写 `CHATGLM_ACCOUNTS`。
3. 创建任务：

```text
10 8 * * * python3 chatglm_daily.py
```

多账号之间会自动串行执行。续期后的令牌与设备号写入 `chatglm_state.json`，已加入 `.gitignore`。

## GitHub Actions

工作流文件位于 `.github/workflows/daily.yml`。在仓库 Secrets 中填写：

- `CHATGLM_ACCOUNTS` 或单账号三项
- 可选：`PUSHPLUS_TOKEN`、`BARK_URL`、`WECOM_WEBHOOK`、`DINGTALK_WEBHOOK`

公开仓库不建议提交令牌。Actions 运行环境不会保留 `chatglm_state.json`；如果上游轮换了 `refresh_token`，需要重新导出并更新 Secret。长期运行优先使用青龙或部署在可持久化目录的定时任务。

## 环境变量

| 变量 | 必填 | 说明 |
| :--- | :-: | :--- |
| `CHATGLM_ACCOUNTS` | 二选一 | 多账号，每行 `备注\|access\|refresh\|device` |
| `CHATGLM_TOKEN` | 二选一 | 单账号 access token |
| `CHATGLM_REFRESH_TOKEN` | 否 | 单账号 refresh token，可自动续期 |
| `CHATGLM_DEVICE_ID` | 否 | 单账号设备 UUID；缺省时从 JWT 读取 |
| `CHATGLM_ACCOUNT_JSON` | 否 | 账号 JSON 字符串 |
| `CHATGLM_ACCOUNT_FILE` | 否 | 账号 JSON 文件路径 |
| `CHATGLM_STATE_FILE` | 否 | 令牌和新手任务状态文件 |
| `CHATGLM_PROXY` | 否 | HTTP(S)/SOCKS 代理 |
| `CHATGLM_NO_NOTIFY=1` | 否 | 关闭推送 |
| `CHATGLM_BASE_URL` | 否 | 默认 `https://chatglm.cn` |

账号 JSON 支持对象或数组：

```json
{
  "accounts": [
    {
      "name": "主账号",
      "access_token": "…",
      "refresh_token": "…",
      "device_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    }
  ]
}
```

## 推送

配置以下任一通道即可：

| 通道 | 变量 |
| :--- | :--- |
| PushPlus | `PLUSPLUS_TOKEN` |
| Bark | `BARK_URL` |
| 企业微信 | `WECOM_WEBHOOK` 或 `QYWX_TOKEN` |
| 钉钉 | `DINGTALK_WEBHOOK` |

所有通道均为可选，推送失败不会改变签到退出码。

## 请求链路

脚本按客户端形态生成每次请求的签名头：

- `X-Timestamp`
- `X-Nonce`
- `X-Sign`
- `X-Device-Id`
- `X-App-Version: 2.0.7`

设备号会随账号持久化。access token 失效时自动尝试 refresh token，并保存轮换后的令牌。

## 常见问题

<details>
<summary><b>访客账号为什么跳过</b></summary>

游客只能对话，没有积分体系。签到、余额和任务中心只对登录账号开放。
</details>

<details>
<summary><b>登录态失效</b></summary>

先重新运行 `python chatglm_login.py`，再用新值更新 `CHATGLM_ACCOUNTS`。
如果只有 access token 且没有 refresh token，令牌过期后只能重新登录。
</details>

<details>
<summary><b>读取客户端 Cookies 失败</b></summary>

关闭智谱清言客户端后重试，或使用 `--paste`。客户端 Cookies 使用 Windows DPAPI，必须在当前 Windows 用户下读取。
</details>

<details>
<summary><b>活动显示无可领取</b></summary>

活动未开始、已经结束或今天已领取都会返回中性结果，不会把签到判定为失败。
</details>

## 隐私

- 不收集、不上传账号信息；
- 令牌只从环境变量、账号文件或本机状态读取；
- 日志不输出完整 access token 或 refresh token；
- `chatglm_state.json`、`.env` 已加入 `.gitignore`。

## ☕ 支持与投喂

脚本免费使用，不含账号数据。如果它对你有帮助，可以自愿扫码支持：

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>

## License

MIT
