#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"
echo '===== CLOUDFLARE BOT SAFE DIAGNOSTIC ====='
echo 'Date (UTC):' ; date -u +%FT%TZ
if [[ -f .env ]]; then
  for k in TELEGRAM_BOT_TOKEN TELEGRAM_ADMIN_IDS ENCRYPTION_KEY DATA_DIR; do
    if grep -Eq "^${k}=.+$" .env; then echo "$k: SET"; else echo "$k: MISSING"; fi
  done
else
  echo '.env: MISSING'
fi
echo '===== DATA DIRECTORY ====='
stat -c 'path=%n owner=%u:%g mode=%a' data 2>/dev/null || true
stat -c 'path=%n owner=%u:%g mode=%a' data/bot.db 2>/dev/null || true
python3 - <<'PYCODE'
from pathlib import Path
import sqlite3
p=Path('data/bot.db')
if not p.exists():
    print('SQLite database: MISSING')
else:
    try:
        db=sqlite3.connect(f'file:{p}?mode=ro',uri=True)
        tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        print('SQLite tables:', ', '.join(sorted(tables)) or 'none')
        if 'cf_accounts' in tables:
            print('Configured Cloudflare account count:',db.execute('SELECT count(*) FROM cf_accounts').fetchone()[0])
        print('SQLite integrity:', db.execute('PRAGMA quick_check').fetchone()[0])
    except Exception as e:
        print('SQLite error TYPE:',type(e).__name__)
PYCODE
echo '===== CONTAINER ====='
docker compose ps || true
echo '===== AUTHENTICATION HEALTH (NO SECRETS OUTPUT) ====='
if docker compose config --services 2>/dev/null | grep -qx 'cloudflare-bot'; then
  docker compose run -T --rm --no-deps --entrypoint python cloudflare-bot - <<'PYCODE' || true
import os,sqlite3
from cryptography.fernet import Fernet,InvalidToken
import httpx
try:
    conn=sqlite3.connect('file:/app/data/bot.db?mode=ro',uri=True)
    rows=conn.execute('SELECT token_enc FROM cf_accounts').fetchall()
    f=Fernet(os.environ.get('ENCRYPTION_KEY','').encode())
    good=bad=0
    for (enc,) in rows:
        try:
            f.decrypt(enc if isinstance(enc,bytes) else enc.encode())
            good+=1
        except InvalidToken:
            bad+=1
    print(f'Encrypted Cloudflare tokens: valid={good} unmatched_key={bad}')
except Exception as e:
    print('Encrypted token diagnostic:',type(e).__name__)
try:
    token=os.environ['TELEGRAM_BOT_TOKEN']
    r=httpx.get(f'https://api.telegram.org/bot{token}/getMe',timeout=8.0)
    result=r.json()
    print('Telegram API getMe:', 'OK' if result.get('ok') is True else 'FAILED', 'HTTP',r.status_code)
except Exception as e:
    print('Telegram API getMe:',type(e).__name__)
PYCODE
fi
echo '===== ERROR TYPES (SECRETS REMOVED) ====='
# Only error categories, not entire logs or API payloads.
docker compose logs --no-color --tail=120 2>/dev/null | grep -E 'KeyError:|OperationalError:|InvalidToken|PermissionError:|Conflict:|Forbidden:|Unauthorized|telegram.error|httpx\.|Traceback|ERROR|ModuleNotFoundError|sqlite3' | sed -E 's/[A-Za-z0-9_-]{32,}/[REDACTED]/g; s/(token|secret|key)[=:][^ ]+/\1=[REDACTED]/Ig' | tail -n40 || true
echo '===== DONE ====='
