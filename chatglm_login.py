#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智谱清言登录态读取工具

路径：
  python chatglm_login.py                读取 Windows 客户端登录态
  python chatglm_login.py --paste        粘贴 access_token/refresh_token
  python chatglm_login.py --json-file a.json
  python chatglm_login.py --write-env .env

Windows 客户端 Cookie 使用 Chromium os_crypt（DPAPI + AES-256-GCM）。
读取时会复制 Cookies 数据库及其 WAL/SHM 副本，客户端保持运行也能尝试读取。
"""

import argparse
import base64
import ctypes
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import uuid
from ctypes import wintypes

try:
    sys.stdout.reconfigure(errors="replace")
except Exception:
    pass

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except Exception as exc:
    AESGCM = None
    AES_IMPORT_ERROR = str(exc)
else:
    AES_IMPORT_ERROR = ""

ACCESS_COOKIE = "chatglm_token"
REFRESH_COOKIE = "chatglm_refresh_token"


def log(message):
    print(str(message), flush=True)


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
        value = json.loads(base64.b64decode(payload).decode("utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def claim_text(claims, keys):
    for key in keys:
        value = claims.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def client_dirs():
    dirs = []
    roots = [
        os.getenv("APPDATA", ""),
        os.path.expanduser("~"),
    ]
    for root in roots:
        if not root:
            continue
        for name in ("chatglm", "智谱清言", "ZPHZ"):
            path = os.path.join(root, name)
            if os.path.isdir(path) and path not in dirs:
                dirs.append(path)
    return dirs


def cookies_path():
    for folder in client_dirs():
        path = os.path.join(folder, "Network", "Cookies")
        if os.path.isfile(path):
            return path
    return ""


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_ubyte)),
    ]


def dpapi_unprotect(data):
    if os.name != "nt":
        raise RuntimeError("DPAPI 仅支持 Windows")
    buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    source = DATA_BLOB(
        len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte))
    )
    target = DATA_BLOB()
    crypt32 = ctypes.windll.crypt32
    kernel32 = ctypes.windll.kernel32
    crypt32.CryptUnprotectData.argtypes = [
        ctypes.POINTER(DATA_BLOB),
        ctypes.POINTER(wintypes.LPWSTR),
        ctypes.POINTER(DATA_BLOB),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(DATA_BLOB),
    ]
    crypt32.CryptUnprotectData.restype = wintypes.BOOL
    kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
    kernel32.LocalFree.restype = wintypes.HLOCAL
    ok = crypt32.CryptUnprotectData(
        ctypes.byref(source), None, None, None, None, 0, ctypes.byref(target)
    )
    if not ok:
        raise ctypes.WinError()
    try:
        return ctypes.string_at(target.pbData, target.cbData)
    finally:
        kernel32.LocalFree(
            ctypes.cast(target.pbData, wintypes.HLOCAL)
        )


def os_crypt_key(cookies):
    user_data = os.path.dirname(os.path.dirname(cookies))
    local_state = os.path.join(user_data, "Local State")
    if not os.path.isfile(local_state):
        raise RuntimeError("找不到客户端 Local State")
    with open(local_state, "r", encoding="utf-8") as handle:
        value = json.load(handle)
    encoded = (
        value.get("os_crypt", {}).get("encrypted_key", "")
        if isinstance(value, dict)
        else ""
    )
    if not encoded:
        raise RuntimeError("Local State 中没有 os_crypt.encrypted_key")
    blob = base64.b64decode(encoded)
    if not blob.startswith(b"DPAPI"):
        raise RuntimeError("客户端密钥前缀不是 DPAPI")
    key = dpapi_unprotect(blob[5:])
    if len(key) != 32:
        raise RuntimeError("客户端 AES 密钥长度异常")
    return key


def decrypt_chromium_value(raw, key):
    if os.name != "nt":
        raise RuntimeError("Chromium os_crypt 解密仅支持 Windows")
    if AESGCM is None:
        raise RuntimeError("缺少 cryptography 依赖：%s" % AES_IMPORT_ERROR)
    if not raw:
        return ""
    if raw[:3] not in (b"v10", b"v11"):
        raise RuntimeError("不支持的 Chromium Cookie 密文版本")
    if len(raw) <= 3 + 12 + 16:
        raise RuntimeError("Chromium Cookie 密文长度异常")
    nonce = raw[3:15]
    ciphertext = raw[15:]
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8", "strict")


def read_client_cookies():
    path = cookies_path()
    if not path:
        raise RuntimeError(
            "没有找到智谱清言客户端 Cookies，请先登录客户端，或使用 --paste"
        )
    key = os_crypt_key(path)
    temp_dir = tempfile.mkdtemp(prefix="chatglm-cookie-")
    copy_path = os.path.join(temp_dir, "Cookies")
    connection = None
    try:
        shutil.copy2(path, copy_path)
        for suffix in ("-wal", "-shm"):
            source = path + suffix
            if os.path.isfile(source):
                shutil.copy2(source, copy_path + suffix)
        connection = sqlite3.connect(copy_path)
        rows = connection.execute(
            "SELECT name, value, encrypted_value FROM cookies "
            "WHERE name IN (?, ?)",
            (ACCESS_COOKIE, REFRESH_COOKIE),
        ).fetchall()
    except sqlite3.Error as exc:
        raise RuntimeError("读取客户端 Cookies 失败：%s；请退出客户端后重试" % exc)
    finally:
        if connection is not None:
            connection.close()
        shutil.rmtree(temp_dir, ignore_errors=True)

    values = {}
    for name, plain, encrypted in rows:
        if plain and str(plain).strip():
            values[name] = str(plain).strip()
            continue
        if encrypted:
            values[name] = decrypt_chromium_value(bytes(encrypted), key).strip()
    access = strip_bearer(values.get(ACCESS_COOKIE, ""))
    refresh = strip_bearer(values.get(REFRESH_COOKIE, ""))
    if not access and not refresh:
        raise RuntimeError("客户端里没有智谱清言登录 Cookie，访客账号无法签到")
    return access, refresh


def normalize_record(record, name):
    if not isinstance(record, dict):
        return None
    access = strip_bearer(
        record.get("access_token")
        or record.get("accessToken")
        or record.get("token")
        or ""
    )
    refresh = strip_bearer(
        record.get("refresh_token") or record.get("refreshToken") or ""
    )
    device = str(
        record.get("device_id") or record.get("deviceId") or ""
    ).strip()
    if not device and access:
        device = claim_text(
            decode_jwt_claims(access), ("device_id",)
        )
    if not access and not refresh:
        return None
    if not device:
        device = str(uuid.uuid4())
        log("[提示] 令牌没有 device_id 声明，已生成新的设备号")
    return {
        "name": str(record.get("name") or record.get("nickname") or name),
        "access_token": access,
        "refresh_token": refresh,
        "device_id": device,
    }


def read_json_file(path):
    with open(path, "r", encoding="utf-8") as handle:
        value = json.load(handle)
    if isinstance(value, dict) and isinstance(value.get("accounts"), list):
        value = value["accounts"]
    elif isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        raise RuntimeError("JSON 应为账号对象或账号数组")
    accounts = []
    for index, item in enumerate(value, 1):
        account = normalize_record(item, "账号%d" % index)
        if account:
            accounts.append(account)
    return accounts


def read_paste():
    log("粘贴账号 JSON，或格式：备注|access_token|refresh_token|device_id")
    try:
        text = input().strip()
    except EOFError:
        return []
    if not text:
        return []
    if text.startswith("{") or text.startswith("["):
        value = json.loads(text)
        if isinstance(value, dict) and isinstance(value.get("accounts"), list):
            value = value["accounts"]
        elif isinstance(value, dict):
            value = [value]
        return [
            account
            for index, item in enumerate(value, 1)
            if (account := normalize_record(item, "账号%d" % index))
        ]
    parts = [part.strip() for part in text.split("|")]
    record = {
        "name": parts[0] if parts else "账号1",
        "access_token": parts[1] if len(parts) > 1 else "",
        "refresh_token": parts[2] if len(parts) > 2 else "",
        "device_id": parts[3] if len(parts) > 3 else "",
    }
    account = normalize_record(record, "账号1")
    return [account] if account else []


def env_value(accounts):
    return "\n".join(
        "%s|%s|%s|%s"
        % (
            account["name"],
            account["access_token"],
            account["refresh_token"],
            account["device_id"],
        )
        for account in accounts
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paste", action="store_true")
    parser.add_argument("--json-file", default="")
    parser.add_argument("--write-env", default="")
    parser.add_argument("--name", default="账号1")
    args = parser.parse_args()

    try:
        if args.json_file:
            accounts = read_json_file(args.json_file)
        elif args.paste:
            accounts = read_paste()
        else:
            access, refresh = read_client_cookies()
            account = normalize_record(
                {
                    "name": args.name,
                    "access_token": access,
                    "refresh_token": refresh,
                },
                args.name,
            )
            accounts = [account] if account else []
    except Exception as exc:
        log("读取失败：%s" % exc)
        return 1

    if not accounts:
        log("没有可用的登录账号")
        return 1

    value = env_value(accounts)
    if args.write_env:
        with open(args.write_env, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("CHATGLM_ACCOUNTS=" + value + "\n")
        try:
            os.chmod(args.write_env, 0o600)
        except Exception:
            pass
        log("已写入 %s（请勿提交到 Git）" % args.write_env)

    log("\nCHATGLM_ACCOUNTS=<\n%s\n>" % value)
    log("每个账号的 access_token 会自动尝试续期；请妥善保存 refresh_token。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
