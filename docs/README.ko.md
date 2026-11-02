<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# ChatGLM Daily

**Zhipu ChatGLM의 일일 로그인 포인트, 캠페인, 일일 작업, 신규 사용자 작업을 자동화하는 단일 파일 스크립트입니다. 토큰 갱신과 잔액 재조회를 지원합니다.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

<img src="https://img.shields.io/github/v/release/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" />
<img src="https://img.shields.io/github/stars/L0NE-6/ChatGLM-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" />
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />

</div>

> 전체 중국어 문서는 [../README.md](../README.md)에서 확인하세요.

## ✨ 핵심 기능

- `score_activity_open`을 확인한 뒤 `daily_login_score`를 호출합니다.
- 새 포인트 지급, 이미 수령, 캠페인 미개방, 알 수 없는 상태를 구분합니다.
- 회원 포인트 캠페인과 시즌 캠페인을 처리합니다.
- 일일 작업을 `click → complete` 순서로 정산합니다.
- 신규 사용자 작업 완료 상태를 저장해 다음 실행에서 반복 탐색하지 않습니다.
- access token을 갱신하고 교체된 refresh token과 장치 ID를 저장합니다.
- PushPlus, Bark, WeCom, DingTalk 알림을 지원합니다.

## 🚀 최단 설정

저장소 루트에서 의존성을 설치합니다.

```bash
python -m pip install -r requirements.txt
```

Windows 클라이언트 로그인 상태 사용:

```bash
python chatglm_login.py
python chatglm_login.py --paste
python chatglm_login.py --json-file accounts.json
python chatglm_login.py --write-env .env
```

단일 계정:

```text
CHATGLM_TOKEN=ACCESS_TOKEN
CHATGLM_REFRESH_TOKEN=REFRESH_TOKEN
CHATGLM_DEVICE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

다중 계정:

```text
CHATGLM_ACCOUNTS=
메인|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
서브|ACCESS_TOKEN|REFRESH_TOKEN|DEVICE_UUID
```

실행:

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

`CHATGLM_ACCOUNTS`를 설정하고 작업을 만듭니다.

```text
10 8 * * * python3 chatglm_daily.py
```

`chatglm_state.json`에는 갱신된 토큰, 장치 ID, 신규 사용자 작업 상태가 저장됩니다. 쓰기 가능한 영구 디렉터리를 사용하고 필요하면 `CHATGLM_STATE_FILE`로 경로를 지정하세요.

## ☁️ GitHub Actions

워크플로는 [../.github/workflows/daily.yml](../.github/workflows/daily.yml)입니다. 현재 수동 실행이 활성화되어 있고 일정 부분은 주석 상태입니다.

| Secret | 필수 | 용도 |
| :--- | :---: | :--- |
| `CHATGLM_ACCOUNTS` | 둘 중 하나 | 다중 계정 자격 증명 |
| `CHATGLM_TOKEN` | 둘 중 하나 | 단일 계정 access token |
| `CHATGLM_REFRESH_TOKEN` | 선택 | 단일 계정 refresh token |
| `CHATGLM_DEVICE_ID` | 선택 | 단일 계정 UUID |
| `CHATGLM_PROXY` | 선택 | 프록시 |
| `PLUSPLUS_TOKEN` / `BARK_URL` / `WECOM_WEBHOOK` / `DINGTALK_WEBHOOK` | 선택 | 알림 |

정기 실행을 사용하려면 주석을 해제하세요. GitHub cron은 UTC이며 `10 0 * * *`는 베이징 시간 08:10입니다. Actions는 상태 파일을 유지하지 않으므로 refresh token이 교체되면 Secret을 갱신해야 합니다.

## 🔧 주요 환경 변수

| 변수 | 설명 |
| :--- | :--- |
| `CHATGLM_ACCOUNTS` | 다중 계정: `이름\|access\|refresh\|device_id` |
| `CHATGLM_TOKEN` | 단일 계정 access token |
| `CHATGLM_REFRESH_TOKEN` | 단일 계정 refresh token |
| `CHATGLM_DEVICE_ID` | UUID 장치 ID, 가능하면 JWT에서 추출 |
| `CHATGLM_ACCOUNT_JSON` | 계정 JSON 문자열 |
| `CHATGLM_ACCOUNT_FILE` | 계정 JSON 파일 |
| `CHATGLM_STATE_FILE` | 토큰 및 신규 작업 상태 파일 |
| `CHATGLM_PROXY` | HTTP(S) / SOCKS 프록시 |
| `CHATGLM_NO_NOTIFY` | `1`이면 알림 비활성화 |

## 📊 성공 기준

하나 이상의 비게스트 계정이 로그인 포인트 흐름을 완료하고 명확한 지급 또는 이미 수령 결과를 받아야 합니다. 포인트 값이 없거나 해석할 수 없으면 미확인으로 처리하며 0포인트를 성공으로 간주하지 않습니다.

## 🔒 개인정보

- 계정 정보를 수집하거나 업로드하지 않습니다.
- 로그에 전체 access token 또는 refresh token을 출력하지 않습니다.
- `chatglm_state.json`, `.env`, 장치 ID, 로그인 상태를 Git에 커밋하지 마세요.
- Issue를 작성하기 전에 토큰과 계정 식별자를 제거하세요.

## 🔗 링크

- [Releases](https://github.com/L0NE-6/ChatGLM-Daily/releases)
- [Issues](https://github.com/L0NE-6/ChatGLM-Daily/issues)
- [Changelog](../CHANGELOG.md)
- [License](../LICENSE)
