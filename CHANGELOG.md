# Cloudflare Telegram Manager — Current Release

## v2.7.2 · 19 November 2026

**This is the current supported release.** The repository maintains one active release entry; earlier development milestones are available only in Git history.

### Features
- Self-hosted Telegram management of multiple Cloudflare accounts and zones.
- Create, edit, search, delete, import and export DNS records (21 supported record types).
- Zone inspection, selected SSL/network settings, cache purge and DNSSEC management.
- Persian inline-button interface and a step-by-step Cloudflare account onboarding guide.
- `/start`, `/menu`, `/accounts`, `/about`, `/help` and `/cancel` commands, automatically synchronized with Telegram at bot startup.
- Developer and project links in About: [Net-spoof](https://github.com/Net-spoof), [source repository](https://github.com/Net-spoof/cloudflare-telegram-manager), and [Telegram channel](https://t.me/NET_SPOOF).

### Security & reliability
- Administrator allowlist and private-chat-only API credential entry.
- Encrypted Cloudflare token storage with Fernet; scoped-token guidance.
- Confirmation prompts for destructive actions, Cloudflare API response diagnostics and callback-data validation.
- Docker Compose installer with backups and preservation of the existing `.env`, encryption key and SQLite data.
- Offline regression suite and GitHub Actions CI.

### Install
Refer to the [Persian documentation](README_FA.md) or [English setup guide](README_EN.md).

> This is an independent, unofficial project. Do not publish secrets, credentials, `.env`, `data/` or `backups/`. Validate on a non-production zone before making potentially disruptive DNS changes.
