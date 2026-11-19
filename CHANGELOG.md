# Changelog

## v2.7.0 (2026-11-19)
- Redesigned the Persian home, account, zone, DNS, record, settings, cache and DNSSEC menus.
- Added an in-bot step-by-step guide for scoped Cloudflare API Tokens, Account IDs and troubleshooting.
- Account-detail screen for selection, connectivity tests, token rotation and disconnection.
- Enforced private-chat-only account/token onboarding; `/help`, `/menu`, `/cancel` commands.
- Added confirmations for full cache purge, DNSSEC changes and zone pause/resume; retained DNS deletion confirmation.
- Fixed DNSSEC toggling to use documented `PATCH /zones/{zone_id}/dnssec` with a `status` body.
- Paginate Cloudflare zones and DNS records beyond the first API page (up to 40 API pages).
- Added input validation for Account IDs, IPv4/IPv6, TTL, priority and purge URLs, plus a 2MB BIND import cap.
- Added GitHub-safe `.gitignore`, modern Persian README, CI offline test workflow, and v2.7 regression tests.
- Retained the callback-ID codec, idempotent menu edits, encrypted token storage, and backwards-compatible Docker installer.


## v2.6 (2026-10-25)
- Fixed Telegram `Button_data_invalid` on DNS Record menus, record actions, search results, and any other callback with long IDs.
- Reversible 32-hex-ID to Base64URL callback codec (persistent/restart-safe), plus length validation in button constructor.
- Explicitly handle pagination noop clicks.
- Kept existing `.env`, encryption key, and account database unchanged.

# Cloudflare Telegram Manager v2.5

## Authentication and menu stabilization
- Telegram `Message is not modified` is now treated as a successful no-op for repeat presses of the active-account/menu buttons (and across all other inline-menu edits).
- Selecting the already active account is handled explicitly.
- Cloudflare 6003/6111 errors display a route to the **Replace API Token** control for the selected account; no credentials, database, DNS records or accounts are deleted.
- Cloudflare **Test Connection** now shows whether the account's scoped zone-list request actually works and provides a direct Replace Token action when it does not.
- `auth_check.py` checks the **saved** token and a **freshly pasted** token independently, reporting only HTTP statuses/error codes; the fresh token is entered with no echo and is not stored.
- Add `.dockerignore` so `.env`, encrypted database, and backups never go into Docker build context.
- Keep existing Fernet key, encrypted token values, bot token, admin IDs and SQLite database on update.

### Security
- New/old Cloudflare API tokens are never printed in diagnostics or Telegram messages; the private fresh-token prompt does not persist its input.
- The `TELEGRAM_BOT_TOKEN` shown in old HTTPX logs must be revoked in BotFather regardless of this update. HTTPX INFO logging stays disabled.

## Existing v2.4 features
- All 21 Cloudflare DNS record types, search, multi-account, SSL/Network settings, cache, DNSSEC and DNS import/export are retained.
