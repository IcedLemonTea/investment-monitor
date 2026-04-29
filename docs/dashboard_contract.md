# Dashboard Contract

Version: v0

## Purpose

Define the local read-only data shape expected by the dashboard before live integrations exist.

## Views

- Overview: account totals, cash, net liquidation value, and update status.
- Positions: symbol, quantity, cost basis, market value, unrealized gain/loss.
- Activity: local imported transactions and dividends.
- Status: data source, freshness, and warnings.

## Backend Guarantees

- Responses are read-only snapshots.
- Missing values are returned as `null` or omitted consistently.
- Currency values include currency codes.
- Timestamps use ISO 8601 with timezone where available.
- Errors avoid secrets and full account identifiers.

## UI Guarantees

- No trade, transfer, or account mutation controls.
- Clear stale-data indicators.
- Sensitive data remains local to the browser session and local backend.

## Example Snapshot

```json
{
  "asOf": "2026-04-29T00:00:00+08:00",
  "source": "sample",
  "accounts": [],
  "positions": [],
  "activity": [],
  "warnings": []
}
```
