# IBKR Flex Runbook

Version: v0

## Status

IBKR Flex is planned but not live in v0.

## Intended Use

- Import read-only batch reports.
- Reconcile positions, cash, activity, and dividends.
- Provide historical snapshots when Gateway is unavailable.

## v0 Rules

- Do not store Flex tokens in the repository.
- Do not commit downloaded reports.
- Use sanitized fixtures for development.
- Keep imported reports local.

## Future Setup Notes

1. Create a read-only Flex query in IBKR Account Management.
2. Store any token outside source control.
3. Download reports to a local ignored runtime path.
4. Parse into the dashboard snapshot contract.
5. Redact account identifiers in logs and errors.

## Operational Checks

- Confirm report date and timezone.
- Confirm account scope is expected.
- Confirm no credentials or tokens are written to logs.
