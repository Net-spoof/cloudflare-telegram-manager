# ☁️ Cloudflare Telegram Manager v2.7.0

A Persian-first, owner-restricted Telegram bot for managing Cloudflare accounts, zones, DNS records, DNSSEC, cache, and selected zone settings.

**📖 [راهنمای کامل فارسی و آموزش اتصال حساب Cloudflare](README_FA.md)**

## Highlights

- Updated Persian inline menus, an account-detail page and built-in connection guide.
- Encrypted multi-account token storage, private-chat-only credential entry, and safer destructive-operation confirmations.
- DNS listing across multiple API pages; 21 DNS record types; Telegram callback data kept within 64 bytes.
- Docker installation and upgrade that preserves an existing `.env`, encryption key and SQLite database.
- Offline regression suite: `python3 test_auth.py && python3 test_v25.py && python3 test_v26.py && python3 test_v27.py`.

**Security:** Never commit `.env`, `data/` or `backups/`. This is an unofficial project and has not been tested against live Cloudflare credentials in this build environment.
