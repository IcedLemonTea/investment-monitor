# Connection Options

Version: v0

## Supported in v0

- Local sample data.
- Local cached files.
- Synthetic fixtures for development and tests.

## Planned Options

- IBKR Flex reports for batch account data.
- IBKR Gateway for local read-only account and market data reads.

## Selection Guidance

- Use Flex reports for stable historical snapshots and reconciliation.
- Use Gateway for fresher local read-only views when a user has started and authenticated the gateway.
- Prefer cached data when developing UI features.

## Explicitly Out of Scope

- Live broker calls by default.
- Remote APIs exposed by this app.
- Write-enabled broker sessions.
- Order placement, cancellation, or account transfers.
