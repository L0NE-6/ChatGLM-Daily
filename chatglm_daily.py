#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱清言每日签到 - 青龙脚本

功能：
  1. 每日登录积分
  2. 会员积分活动与季节活动领取
  3. 每日任务中心
  4. 新手任务中心
  5. 积分余额与任务进度回读

环境变量：
  CHATGLM_ACCOUNTS  多账号，换行或 & 分隔：
                    备注|access_token[|refresh_token[|device_id]]
  CHATGLM_TOKEN     单账号 access_token
  CHATGLM_REFRESH_TOKEN
  CHATGLM_DEVICE_ID
  CHATGLM_ACCOUNT_FILE  可选，JSON 账号文件
  CHATGLM_STATE_FILE    可选，续期与新手任务本地状态文件
  CHATGLM_PROXY         可选，http(s)/socks5 代理
  CHATGLM_NO_NOTIFY=1   关闭推送

命令：
  python chatglm_daily.py
  python chatglm_daily.py --only 1
  python chatglm_daily.py --query
  python chatglm_daily.py --skip-newbie
  python chatglm_daily.py --no-notify

依赖：requests
"""

import base64
import hashlib
import json
import os
import re
import sys
import time
import uuid
from datetime import datetime, timedelta, timezone

import requests
import urllib3

urllib3.disable_warnings()

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

BASE_URL = os.getenv("CHATGLM_BASE_URL", "").strip().rstrip("/") or "https://chatglm.cn"
SIGN_SECRET_PROD = "8a1317a7468aa3ad86e997d08f3f31cb"
SIGN_SECRET_TEST = "befbc3fe57555ffa1daaf52b39be0fbe"
APP_VERSION = "2.0.7"
APP_PLATFORM = "pc"
APP_NAME = "chatglm"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/146.0.0.0 Safari/537.36"
)

PATH_REFRESH = "/chatglm/user-api/user/refresh"
PATH_MEMBER_INFO = "/chatglm/member-api/member/member_info"
PATH_SCORE_ACTIVITY_DRAW = "/chatglm/member-api/member/score_activity_draw"
PATH_DAILY_LOGIN_SCORE = "/chatglm/member-api/member/daily_login_score"
PATH_SUMMER_DAY_CLAIM_STATUS = "/chatglm/member-api/member/summer_day_claim_status"
PATH_SUMMER_DAY_GIVE_SCORE = "/chatglm/member-api/member/summer_day_give_score"
PATH_TASK_CENTER = "/chatglm/agent-api/task/center"
PATH_TASK_CLICK = "/chatglm/agent-api/task/click"
PATH_TASK_COMPLETE = "/chatglm/agent-api/task/complete"

BEIJING = timezone(timedelta(hours=8))
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.getenv("CHATGLM_STATE_FILE", "").strip() or os.path.join(
    SCRIPT_DIR, "chatglm_state.json"
)


class ChatGLMError(Exception):
    pass


def log(message):
    print(str(message), flush=True)


def mask(value, keep=4):
    text = str(value or "")
    if len(text) <= keep:
        return "*" * len(text)
    return "*" * (len(text) - keep) + text[-keep:]


def strip_bearer(token):
    text = str(token or "").strip()
    if text.lower().startswith("bearer "):
        text = text[7:].strip()
    return text


def decode_jwt_claims(token):
    raw = strip_bearer(token)
    parts = raw.split(".")
    if len(parts) < 2:
        return {}
    payload = parts[1].replace("-", "+").replace("_", "/")
    payload += "=" * ((4 - len(payload) % 4) % 4)
    try:
        decoded = base64.b64decode(payload)
        value = json.loads(decoded.decode("utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def claim_text(claims, keys):
    for key in keys:
        value = claims.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            value = json.load(handle)
        return value
    except Exception:
        return default


def save_json(path, value):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temp, path)


def load_state():
    value = load_json(STATE_FILE, {})
    if not isinstance(value, dict):
        value = {}
    value.setdefault("accounts", {})
    value.setdefault("onboarding", {})
    return value


def normalize_account(item, index):
    if not isinstance(item, dict):
        return None
    access = strip_bearer(
        item.get("access_token")
        or item.get("accessToken")
        or item.get("token")
        or ""
    )
    refresh = strip_bearer(
        item.get("refresh_token") or item.get("refreshToken") or ""
    )
    device = str(
        item.get("device_id") or item.get("deviceId") or ""
    ).strip()
    name = str(
        item.get("name") or item.get("nickname") or ("账号%d" % index)
    ).strip()
    if not access and not refresh:
        return None
    return {
        "name": name,
        "access_token": access,
        "refresh_token": refresh,
        "device_id": device,
    }


def accounts_from_json(raw, label):
    try:
        value = json.loads(raw)
    except Exception as exc:
        log("[配置] %s JSON 解析失败：%s" % (label, exc))
        return []
    if isinstance(value, dict):
        if isinstance(value.get("accounts"), list):
            value = value["accounts"]
        else:
            value = [value]
    if not isinstance(value, list):
        return []
    out = []
    for index, item in enumerate(value, 1):
        account = normalize_account(item, index)
        if account:
            out.append(account)
    return out


def load_accounts():
    accounts = []

    account_file = os.getenv("CHATGLM_ACCOUNT_FILE", "").strip()
    if account_file:
        file_value = load_json(account_file, None)
        if file_value is not None:
            accounts.extend(accounts_from_json(json.dumps(file_value), "账号文件"))

    raw_json = os.getenv("CHATGLM_ACCOUNT_JSON", "").strip()
    if raw_json:
        accounts.extend(accounts_from_json(raw_json, "CHATGLM_ACCOUNT_JSON"))

    raw = os.getenv("CHATGLM_ACCOUNTS", "").strip()
    if raw:
        for line in re.split(r"[\r\n&]+", raw):
            line = line.strip()
            if not line:
                continue
            parts = [part.strip() for part in line.split("|")]
            if len(parts) < 2:
                log("[配置] 跳过格式不正确的账号条目")
                continue
            accounts.append(
                {
                    "name": parts[0] or ("账号%d" % (len(accounts) + 1)),
                    "access_token": strip_bearer(parts[1]),
                    "refresh_token": strip_bearer(parts[2]) if len(parts) > 2 else "",
                    "device_id": parts[3] if len(parts) > 3 else "",
                }
            )

    if not accounts:
        token = strip_bearer(os.getenv("CHATGLM_TOKEN", ""))
        refresh = strip_bearer(os.getenv("CHATGLM_REFRESH_TOKEN", ""))
        device = os.getenv("CHATGLM_DEVICE_ID", "").strip()
        if token or refresh:
            accounts.append(
                {
                    "name": "账号1",
                    "access_token": token,
                    "refresh_token": refresh,
                    "device_id": device,
                }
            )

    deduped = []
    seen = set()
    for account in accounts:
        claims = decode_jwt_claims(account.get("access_token"))
        uid = claim_text(claims, ("uid", "user_id", "sub"))
        key = uid or account.get("name") or mask(account.get("access_token"), 8)
        if key in seen:
            key = "%s-%d" % (key, len(deduped) + 1)
        seen.add(key)
        account["_key"] = key
        deduped.append(account)
    return deduped


def x_timestamp(millis=None):
    text = str(int(millis if millis is not None else time.time() * 1000))
    if len(text) < 2:
        return text
    digits = [int(ch) for ch in text]
    checksum = (sum(digits) - digits[-2]) % 10
    return text[:-2] + str(checksum) + text[-1]


def sign_secret():
    lowered = BASE_URL.lower()
    if "test.chatglm.cn" in lowered or "staging" in lowered or "dev" in lowered:
        return SIGN_SECRET_TEST
    if "chatglm.cn" in lowered:
        return SIGN_SECRET_PROD
    return SIGN_SECRET_TEST


def build_headers(token, device_id):
    timestamp = x_timestamp()
    nonce = uuid.uuid4().hex
    sign = hashlib.md5(
        ("%s-%s-%s" % (timestamp, nonce, sign_secret())).encode("utf-8")
    ).hexdigest()
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=utf-8",
        "App-Name": APP_NAME,
        "X-Device-Id": device_id,
        "X-App-Platform": APP_PLATFORM,
        "X-App-Version": APP_VERSION,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Sign": sign,
        "Origin": BASE_URL,
        "Referer": BASE_URL + "/",
        "User-Agent": USER_AGENT,
    }
    token = strip_bearer(token)
    if token:
        headers["Authorization"] = "Bearer " + token
    return headers


def envelope(payload, what):
    status = payload.get("status")
    if status is None:
        return payload.get("result")
    try:
        status = int(status)
    except Exception:
        status = -1
    if status in (0, 200):
        return payload.get("result")
    message = str(payload.get("message") or payload.get("msg") or "上游返回失败")
    raise ChatGLMError("%s失败（status=%s）：%s" % (what, status, message))


class ChatGLMClient:
    def __init__(self, account, state, proxy=None):
        self.name = account.get("name") or "账号"
        self.key = account.get("_key") or self.name
        self.state = state
        saved = (state.get("accounts") or {}).get(self.key, {})
        self.access_token = strip_bearer(
            saved.get("access_token") or account.get("access_token")
        )
        self.refresh_token = strip_bearer(
            saved.get("refresh_token") or account.get("refresh_token")
        )
        claims = decode_jwt_claims(self.access_token)
        self.uid = claim_text(claims, ("uid", "user_id", "sub"))
        self.is_guest = bool(claims.get("is_guest"))
        self.device_id = (
            str(saved.get("device_id") or account.get("device_id") or "").strip()
            or claim_text(claims, ("device_id",))
            or str(uuid.uuid4())
        )
        self.session = requests.Session()
        self.session.verify = False
        proxy = proxy or os.getenv("CHATGLM_PROXY", "").strip()
        if proxy:
            self.session.proxies.update({"http": proxy, "https": proxy})

    def save_tokens(self):
        self.state.setdefault("accounts", {})[self.key] = {
            "name": self.name,
            "uid": self.uid,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "device_id": self.device_id,
            "updated_at": int(time.time()),
        }
        try:
            save_json(STATE_FILE, self.state)
        except Exception as exc:
            log("令牌状态保存失败：%s" % exc)

    def _raw_request(self, method, path, token="", body=None):
        url = BASE_URL + path
        headers = build_headers(token, self.device_id)
        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                json=(body if body is not None else ({} if method == "POST" else None)),
                timeout=30,
            )
        except Exception as exc:
            raise ChatGLMError("请求失败：%s" % exc)
        try:
            payload = response.json()
        except Exception:
            payload = {"status": -1, "message": response.text[:240]}
        return response.status_code, payload

    def refresh(self):
        if not self.refresh_token:
            raise ChatGLMError("登录态已失效，且没有 refresh_token")
        status, payload = self._raw_request(
            "POST", PATH_REFRESH, token=self.refresh_token, body={}
        )
        if status in (401, 403):
            raise ChatGLMError("refresh_token 已失效，请重新登录")
        result = envelope(payload, "令牌续期") or {}
        access = strip_bearer(result.get("access_token"))
        if not access:
            raise ChatGLMError("令牌续期未返回 access_token")
        self.access_token = access
        rotated = strip_bearer(result.get("refresh_token"))
        if rotated:
            self.refresh_token = rotated
        uid = str(result.get("user_id") or "").strip()
        if uid:
            self.uid = uid
        claims = decode_jwt_claims(self.access_token)
        self.is_guest = bool(claims.get("is_guest"))
        claim_device = claim_text(claims, ("device_id",))
        if claim_device:
            self.device_id = claim_device
        self.save_tokens()

    def request(self, method, path, body=None, what="上游请求"):
        if not self.access_token and self.refresh_token:
            self.refresh()
        if not self.access_token:
            raise ChatGLMError("缺少 access_token")

        status, payload = self._raw_request(
            method, path, token=self.access_token, body=body
        )
        payload_status = payload.get("status")
        needs_refresh = status in (401, 403) or str(payload_status) == "40103"
        if needs_refresh and self.refresh_token:
            self.refresh()
            status, payload = self._raw_request(
                method, path, token=self.access_token, body=body
            )
        if status in (401, 403):
            raise ChatGLMError("%s登录态已失效（HTTP %s）" % (what, status))
        if status < 200 or status >= 300:
            message = payload.get("message") or payload.get("msg") or payload
            raise ChatGLMError("%s失败（HTTP %s）：%s" % (what, status, message))
        return payload

    def get(self, path, what="查询"):
        return self.request("GET", path, what=what)

    def post(self, path, body=None, what="提交"):
        return self.request("POST", path, body=body or {}, what=what)

    def task_center(self):
        return envelope(self.get(PATH_TASK_CENTER, "任务中心查询"), "任务中心查询") or {}

    def query_balance(self):
        member = envelope(
            self.get(PATH_MEMBER_INFO, "积分查询"), "积分查询"
        ) or {}
        raw = member.get("left_score", member.get("true_left_score", 0))
        try:
            balance = round(float(raw) / 100.0, 2)
        except Exception:
            balance = None
        return balance, member

    def claim_login(self):
        try:
            payload = self.post(PATH_DAILY_LOGIN_SCORE, {}, "每日登录积分领取")
        except Exception as exc:
            message = str(exc)
            if any(word in message for word in ("10001", "已领", "already")):
                return True, "今日登录积分已领取"
            raise
        status = payload.get("status")
        if str(status) == "10001":
            return True, "今日登录积分已领取"
        result = envelope(payload, "每日登录积分领取") or {}
        if isinstance(result, dict):
            raw = result.get("score", 0)
        elif isinstance(result, (int, float)):
            raw = result
        else:
            raw = 0
        try:
            score = round(float(raw) / 100.0, 2)
        except Exception:
            score = 0.0
        if score > 0:
            return True, "每日登录积分 +%s" % score
        return True, "今日登录积分已领取或活动未开启"

    def claim_bonus(self):
        messages = []
        gained = 0.0
        try:
            payload = self.post(PATH_SCORE_ACTIVITY_DRAW, {}, "积分活动领取")
            status = payload.get("status")
            if str(status) == "0":
                result = envelope(payload, "积分活动领取") or {}
                raw = result.get("score", result.get("reward", 0)) if isinstance(result, dict) else 0
                try:
                    amount = round(float(raw) / 100.0, 2)
                except Exception:
                    amount = 0.0
                if amount > 0:
                    gained += amount
                    messages.append("积分活动 +%s" % amount)
                else:
                    messages.append("积分活动无可领取")
            else:
                messages.append(
                    "积分活动：%s"
                    % str(payload.get("message") or "活动未开启")
                )
        except Exception as exc:
            messages.append("积分活动：%s" % str(exc)[:80])

        try:
            state_payload = self.get(
                PATH_SUMMER_DAY_CLAIM_STATUS, "季节活动状态查询"
            )
            state = envelope(state_payload, "季节活动状态查询") or {}
            claimable = state.get("claimable")
            if claimable is None and "claimed" in state:
                claimable = not bool(state.get("claimed"))
            if claimable:
                claimed = self.post(
                    PATH_SUMMER_DAY_GIVE_SCORE, {}, "季节活动领取"
                )
                envelope(claimed, "季节活动领取")
                messages.append("季节活动已领取")
            else:
                messages.append("季节活动无可领取")
        except Exception as exc:
            messages.append("季节活动：%s" % str(exc)[:80])

        if not messages:
            messages.append("当前没有可领取的活动")
        return gained > 0, "；".join(messages)

    def category(self, center, code):
        categories = center.get("categories")
        if not isinstance(categories, list):
            return None
        for item in categories:
            if isinstance(item, dict) and item.get("code") == code:
                return item
        return None

    def settle_tasks(self, category, label):
        tasks = category.get("tasks") if isinstance(category, dict) else []
        if not isinstance(tasks, list) or not tasks:
            return 0, 0, "%s：没有任务" % label

        claimed = 0
        points = 0
        failures = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            try:
                status = int(task.get("status") or 0)
            except Exception:
                status = 0
            if status >= 3:
                continue
            task_id = str(task.get("task_id") or "").strip()
            title = str(task.get("title") or task_id or "未命名任务")
            if not task_id:
                failures.append("%s缺少 task_id" % title)
                continue
            try:
                self.post(PATH_TASK_CLICK, {"task_id": task_id}, "任务登记")
                payload = self.post(
                    PATH_TASK_COMPLETE, {"task_id": task_id}, "任务结算"
                )
                result = envelope(payload, "任务结算") or {}
                reward = 0
                if isinstance(result, dict):
                    reward = int(
                        ((result.get("reward") or {}).get("points_awarded") or 0)
                    )
                claimed += 1
                points += reward
            except Exception as exc:
                if "登录态已失效" in str(exc):
                    raise
                failures.append("%s：%s" % (title, str(exc)[:80]))
        if failures:
            message = "%s：完成 %d 个，+%d 积分；失败 %s" % (
                label,
                claimed,
                points,
                "；".join(failures[:3]),
            )
        else:
            message = "%s：完成 %d 个，+%d 积分" % (label, claimed, points)
        return claimed, points, message

    def query_snapshot(self):
        balance, member = self.query_balance()
        center = self.task_center()
        daily = self.category(center, "daily") or {}
        newbie = self.category(center, "newbie") or {}
        return (
            "余额 %s | 每日任务 %s/%s | 新手任务 %s/%s"
            % (
                balance if balance is not None else "?",
                (daily.get("progress") or {}).get("done", "?"),
                (daily.get("progress") or {}).get("total", "?"),
                (newbie.get("progress") or {}).get("done", "?"),
                (newbie.get("progress") or {}).get("total", "?"),
            )
        )


def run_account(client, query_only=False, skip_newbie=False):
    if client.is_guest:
        return False, "访客账号没有积分体系，跳过"
    if query_only:
        return True, client.query_snapshot()

    messages = []
    ok, message = client.claim_login()
    messages.append(message)

    bonus_ok, bonus_message = client.claim_bonus()
    messages.append(bonus_message)

    center = client.task_center()
    daily = client.category(center, "daily")
    if daily:
        _, _, message = client.settle_tasks(daily, "每日任务")
        messages.append(message)
    else:
        messages.append("每日任务：当前没有任务")

    if not skip_newbie:
        onboarding = client.state.setdefault("onboarding", {})
        if not onboarding.get(client.key):
            newbie = client.category(center, "newbie")
            if newbie:
                claimed, _, message = client.settle_tasks(newbie, "新手任务")
                messages.append(message)
                refresh = client.task_center()
                after = client.category(refresh, "newbie") or {}
                progress = after.get("progress") or {}
                try:
                    done = int(progress.get("done") or 0)
                    total = int(progress.get("total") or 0)
                except Exception:
                    done, total = 0, 0
                if total > 0 and done >= total:
                    onboarding[client.key] = {
                        "settled_at": int(time.time()),
                        "claimed": claimed,
                    }
                    save_json(STATE_FILE, client.state)
            else:
                messages.append("新手任务：当前没有任务")

    try:
        balance, _ = client.query_balance()
        if balance is not None:
            messages.append("当前积分 %s" % balance)
    except Exception as exc:
        messages.append("余额回读失败：%s" % str(exc)[:80])

    return bool(ok or bonus_ok), "；".join(messages)


def _post_json(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=15, verify=False)
        response.raise_for_status()
        return True
    except Exception as exc:
        log("推送失败：%s" % exc)
        return False


def notify(text, title="智谱清言签到"):
    if os.getenv("CHATGLM_NO_NOTIFY", "").strip() == "1":
        return
    content = text[:1800]

    token = os.getenv("PLUSPLUS_TOKEN", "").strip()
    if token:
        _post_json(
            "https://www.pushplus.plus/send",
            {"token": token, "title": title, "content": content, "template": "txt"},
        )

    bark = os.getenv("BARK_URL", "").strip()
    if bark:
        url = bark.rstrip("/") + "/" + requests.utils.quote(title, safe="")
        _post_json(url, {"body": content})

    wecom = (
        os.getenv("WECOM_WEBHOOK", "").strip()
        or os.getenv("QYWX_TOKEN", "").strip()
    )
    if wecom:
        if "key=" not in wecom and "/send?" not in wecom:
            wecom = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + wecom
        _post_json(wecom, {"msgtype": "text", "text": {"content": title + "\n" + content}})

    ding = os.getenv("DINGTALK_WEBHOOK", "").strip()
    if ding:
        _post_json(ding, {"msgtype": "text", "text": {"content": title + "\n" + content}})


def parse_args():
    only = ""
    query_only = False
    skip_newbie = False
    no_notify = os.getenv("CHATGLM_NO_NOTIFY", "").strip() == "1"
    args = sys.argv[1:]
    for index, arg in enumerate(args):
        if arg == "--only" and index + 1 < len(args):
            only = args[index + 1]
        elif arg == "--query":
            query_only = True
        elif arg == "--skip-newbie":
            skip_newbie = True
        elif arg == "--no-notify":
            no_notify = True
    return only, query_only, skip_newbie, no_notify


def main():
    only, query_only, skip_newbie, no_notify = parse_args()
    accounts = load_accounts()
    if not accounts:
        log("未配置 CHATGLM_ACCOUNTS 或 CHATGLM_TOKEN。")
        log("Windows 可先运行：python chatglm_login.py")
        return 1

    state = load_state()
    lines = []
    succeeded = 0
    selected = 0
    for index, account in enumerate(accounts, 1):
        if only and str(index) != str(only):
            continue
        selected += 1
        client = ChatGLMClient(account, state)
        log("[%s] 开始%s（uid %s）" % (
            client.name,
            "查询" if query_only else "签到",
            client.uid or "?",
        ))
        try:
            ok, message = run_account(
                client, query_only=query_only, skip_newbie=skip_newbie
            )
            succeeded += 1 if ok else 0
            line = "%s %s：%s" % ("成功" if ok else "跳过", client.name, message)
        except Exception as exc:
            line = "失败 %s：%s" % (client.name, str(exc)[:240])
        lines.append(line)
        log(line)
        if index < len(accounts):
            time.sleep(1.0)

    if selected == 0:
        log("没有匹配的账号")
        return 1

    summary = "\n".join(lines)
    log("\n===== 智谱清言签到汇总 =====\n" + summary)
    if not no_notify:
        notify(summary)
    return 0 if succeeded else 1


if __name__ == "__main__":
    sys.exit(main())
