# IBKR Gateway Runbook

Version: v0

## Status

IBKR Gateway is planned but not live in v0.

## Intended Use

- Read local account data from a user-started Gateway session.
- Refresh positions, balances, and market values.
- Keep broker access read-only.

## v0 Rules

- No automatic Gateway login.
- No stored broker credentials.
- No order placement or account mutation APIs.
- No network exposure beyond localhost.

## Future Setup Notes

1. Install IBKR Gateway manually.
2. Enable API access only for trusted local clients.
3. Use read-only API settings where available.
4. Bind the app to localhost.
5. Add adapter safeguards that reject write operations.

## Operational Checks

- Confirm the Gateway session belongs to the expected user.
- Confirm API access is local-only.
- Confirm logs redact account identifiers.
- Stop the Gateway when monitoring is complete.
