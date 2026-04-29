# AGENTS.md

## Mission

Build a local-only, read-only IBKR investment monitor that generates a localhost static-style dashboard from normalized portfolio snapshots.

## User context

- Single retail IBKR account.
- Live account data will be added later.
- Windows desktop.
- Localhost only.
- Direct commits to main.
- No trading functionality.
- USD source currency with optional MYR display toggle.
- Target allocation:
  - QLD 50%
  - TQQQ 10%
  - AVUV 20%
  - AVDV 10%
  - QMOM 10%
  - Cash/Others 0%

## Hard rules

- Do not add order placement, order modification, order cancellation, or order preview.
- Do not add buy/sell/rebalance execution buttons.
- Do not call live IBKR APIs in tests or CI.
- Do not commit `.env`, local config, runtime data, SQLite databases, logs, tokens, cookies, or generated real dashboard data.
- Use an explicit endpoint allowlist for IBKR HTTP calls.
- Block all non-allowlisted endpoints.
- Keep the dashboard local-only.
- Keep real generated data under `runtime/` or gitignored `public/data/`.

## Engineering rules

- Prefer Python for the poller.
- Prefer static HTML/CSS/JS for the dashboard.
- Vendor browser dependencies locally; do not use CDN scripts.
- Write dashboard JSON atomically.
- Add tests for every normalizer, parser, endpoint policy, and snapshot schema.
- Update docs when changing data contracts or connection behavior.

## Review priorities

Treat these as severe issues:
- Any trading endpoint or order-related code.
- Any committed secret.
- Any committed real account snapshot.
- Any weakening of `.gitignore`.
- Any dashboard feature that sends data outside localhost.
