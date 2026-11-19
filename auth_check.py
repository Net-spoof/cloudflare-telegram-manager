#!/usr/bin/env python3
"""Read-only authentication check for Cloudflare Telegram Manager.

Inside the project container:
  docker compose exec cloudflare-bot python /app/auth_check.py --stored
  docker compose exec cloudflare-bot python /app/auth_check.py --fresh

Does not display, transmit to Telegram, persist or log API token input.
"""
import argparse
import asyncio
from getpass import getpass
import os
import sqlite3
from cryptography.fernet import Fernet, InvalidToken
import httpx

API = "https://api.cloudflare.com/client/v4"


def normalize(value: str) -> str:
    s = value.strip()
    for _ in range(4):
        old = s
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'", "`"):
            s = s[1:-1].strip()
        if s.lower().startswith("authorization:"):
            s = s.partition(":")[2].strip()
        if s.lower().startswith("bearer "):
            s = s[7:].strip()
        if old == s:
            break
    if not s or len(s) > 1024 or not all(33 <= ord(c) <= 126 for c in s) or " " in s:
        raise ValueError("Token input is missing or malformed")
    return s


def selected_account():
    db = sqlite3.connect("file:/app/data/bot.db?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    row = db.execute("SELECT account_id,token_enc FROM cf_accounts ORDER BY active DESC,id LIMIT 1").fetchone()
    db.close()
    if row is None:
        raise ValueError("No Cloudflare account configured")
    return row


async def run():
    ap = argparse.ArgumentParser()
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--stored", action="store_true", help="Test encrypted token saved in the bot")
    group.add_argument("--fresh", action="store_true", help="Test API token pasted privately in SSH (never saved)")
    opts = ap.parse_args()
    account = selected_account()
    if opts.stored:
        cipher = Fernet(os.environ["ENCRYPTION_KEY"].encode())
        value = account["token_enc"]
        try:
            raw = cipher.decrypt(value if isinstance(value, bytes) else value.encode()).decode()
        except InvalidToken:
            print("STORED_TOKEN: encryption key mismatch")
            return
    else:
        raw = getpass("Enter FRESH Cloudflare API token (hidden, never saved): ")
    try:
        token = normalize(raw)
    except ValueError as exc:
        print("TOKEN_INPUT:", exc)
        return
    print("MODE:", "STORED" if opts.stored else "FRESH")
    headers = {"Authorization": "Bearer " + token}
    async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
        for label, path, params in (
            ("TOKEN_VERIFY", "/user/tokens/verify", None),
            ("ZONE_LIST", "/zones", {"account.id": account["account_id"], "per_page": 1}),
        ):
            try:
                response = await client.get(API + path, headers=headers, params=params)
                data = response.json()
                errors = []
                def codes(items):
                    for err in items or []:
                        if isinstance(err,dict):
                            errors.append(err.get("code"))
                            codes(err.get("error_chain"))
                codes(data.get("errors"))
                status = data.get("result", {}).get("status") if isinstance(data.get("result"),dict) else None
                print(f"{label}: HTTP={response.status_code} SUCCESS={data.get('success')} ERRORS={errors} STATUS={status or '-'}")
            except Exception as exc:
                print(f"{label}: TEST_ERROR={type(exc).__name__}")
    print("NOTE: TOKEN_VERIFY may be unavailable for some account-scoped credentials. Zone list success is the app's key check.")


if __name__ == "__main__":
    asyncio.run(run())
