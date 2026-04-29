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
- After any dashboard data-source, rendering, or UI change, verify the rendered localhost dashboard, not only raw JSON endpoints or unit tests.
- Before saying the dashboard shows real/local data, confirm the visible DOM no longer shows stale mock values where real generated data should appear.
- Use `py scripts/verify_dashboard_render.py` for dashboard render verification on Windows; it uses installed Edge/Chrome headless and avoids Node/Playwright dependency issues.
- Automatically add durable project documentation for user corrections that reveal a missed workflow rule.
- For dashboard UI work, do not make the sidebar a floating card. It must be a structural viewport boundary anchored to the top, bottom, and left edges unless the user explicitly asks for a floating navigation tile.
- Sidebar navigation text and icons must be large enough to read as primary navigation, and the brand mark must use a proper icon, not only initials.
- Related sidebar controls must share the same pill/segmented-control style, dimensions, animation behavior, and visual weight.
- Do not use oversized primary buttons for secondary local actions in the sidebar. Prefer subtle icon buttons near the data they affect, such as refresh beside the timestamp.
- Time-series and risk charts must include visible axes or axis labels, equalized chart heights where charts sit side by side, and correct y-axis domains. Drawdown charts must anchor 0% at the top and scale downward to slightly beyond the maximum drawdown.
- Heatmap colors must encode P&L direction and magnitude on a red-to-green scale. Hide text in heatmap cells that are too small to render legibly and rely on tooltips for details.
- After layout changes, inspect a screenshot for structural alignment, chart overflow, wasted whitespace, and illegible truncated labels before committing.
- Do not add visible controls that do not materially work. Remove useless search/status widgets and inactive benchmark buttons instead of leaving decorative controls on the dashboard.
- Right-column cards must share a strict column width and spacing rhythm. Avoid orphaned low-value status cards that create vertical misalignment; put status details in the sidebar or screen-reader-only health output unless the card earns its space.

## Review priorities

Treat these as severe issues:
- Any trading endpoint or order-related code.
- Any committed secret.
- Any committed real account snapshot.
- Any weakening of `.gitignore`.
- Any dashboard feature that sends data outside localhost.
