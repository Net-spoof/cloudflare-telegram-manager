<div align="center">

# ☁️ Cloudflare Telegram Manager

**A secure, Persian-first Telegram control panel for Cloudflare accounts, DNS, and zone operations.**

[![Version](https://img.shields.io/badge/version-2.7.0-2563eb)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.12-3776ab?logo=python&logoColor=white)](Dockerfile)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed?logo=docker&logoColor=white)](docker-compose.yml)
[![Tests](https://github.com/Net-spoof/cloudflare-telegram-manager/actions/workflows/tests.yml/badge.svg)](https://github.com/Net-spoof/cloudflare-telegram-manager/actions/workflows/tests.yml)

### 🌐 Documentation / مستندات

**[🇮🇷 آموزش کامل فارسی — نصب، اتصال و مدیریت (راست‌چین)](README_FA.md)**

**[🇬🇧 English Guide — Installation, Setup & Operations](README_EN.md)**

</div>

---

## Overview

Cloudflare Telegram Manager is an **unofficial, self-hosted, administrator-only** Telegram bot. Manage several Cloudflare accounts from a private Telegram chat, inspect zones, work with DNS records, search across zones, review selected SSL/network settings, purge cache, and manage DNSSEC with confirmation prompts.

### Key capabilities

- 🌐 Multi-account Cloudflare support with encrypted API token storage
- 🧩 DNS record listing, search, create, edit, delete, BIND import/export
- 🔐 Scoped API tokens, admin allowlist, private-chat credential entry
- 🛡️ Selected zone settings, SSL/network controls, DNSSEC safeguards
- 📱 Persian inline-keyboard interface and built-in onboarding guide
- 🐳 Docker Compose deployment; upgrade preserves <code>.env</code>, the Fernet key and SQLite data
- ✅ Offline regression tests and GitHub Actions CI

## Quick install — Ubuntu

**Requirements:** a Linux VPS (Ubuntu recommended), root/sudo access, Python 3, Git, outbound HTTPS access to Telegram and Cloudflare, and a Telegram bot token from [@BotFather](https://t.me/BotFather). The installer can install Docker if necessary.

~~~bash
sudo apt-get update
sudo apt-get install -y git python3 ca-certificates
sudo git clone https://github.com/Net-spoof/cloudflare-telegram-manager.git /opt/cloudflare-telegram-manager
cd /opt/cloudflare-telegram-manager
sudo bash install.sh
~~~

The installer prompts for <code>TELEGRAM_BOT_TOKEN</code> and numeric <code>TELEGRAM_ADMIN_IDS</code> on first run, generates an encryption key, then builds and starts the Docker service.

~~~bash
cd /opt/cloudflare-telegram-manager
sudo docker compose ps
sudo bash diagnose.sh
~~~

Open your Telegram bot in a **private chat**, send <code>/start</code>, and follow **Cloudflare Accounts → Add account**. Create a **scoped API Token** in [Cloudflare](https://dash.cloudflare.com/profile/api-tokens), not a Global API Key.

> **Already installed a previous version?** Don't clone into your existing project folder or replace <code>.env</code>/<code>data/</code>. See the [Persian upgrade instructions](README_FA.md#upgrade) or [English upgrade guide](README_EN.md#upgrading-without-losing-data).

## Documentation

| Topic | فارسی (RTL) | English |
|---|---|---|
| Requirements & installation | [راهنمای نصب](README_FA.md#install) | [Installation](README_EN.md#installation-on-ubuntu) |
| Telegram BotFather setup | [ساخت ربات](README_FA.md#botfather) | [Bot setup](README_EN.md#creating-your-telegram-bot) |
| Cloudflare API Token + Account ID | [اتصال حساب](README_FA.md#cloudflare) | [Cloudflare connection](README_EN.md#connecting-a-cloudflare-account) |
| Updates, backup and restore | [به‌روزرسانی و بکاپ](README_FA.md#upgrade) | [Upgrade & backups](README_EN.md#upgrading-without-losing-data) |
| Troubleshooting | [رفع خطا](README_FA.md#troubleshooting) | [Troubleshooting](README_EN.md#troubleshooting) |

## Developer checks

~~~bash
python3 test_auth.py
python3 test_v25.py
python3 test_v26.py
python3 test_v27.py
~~~

These are **offline** tests; a successful run does not verify live Telegram or Cloudflare access.

## Important security notes

- Do not commit or share <code>.env</code>, <code>data/</code>, <code>backups/</code>, credentials, or unredacted logs.
- Never expose your Telegram bot token or Cloudflare API token. Restrict Cloudflare token permissions and zone resources to the minimum required.
- Preserve the original <code>ENCRYPTION_KEY</code> when upgrading: changing it prevents decryption of saved Cloudflare tokens.
- Destructive changes to DNS and DNSSEC can interrupt production services. Export DNS records before high-impact operations.
- The project is **not affiliated with Cloudflare or Telegram**, and has not been verified against live Cloudflare accounts in the build environment.

[Changelog](CHANGELOG.md) · [Persian guide](README_FA.md) · [English guide](README_EN.md)
