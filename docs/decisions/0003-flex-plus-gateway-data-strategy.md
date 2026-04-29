# 0003: Flex Plus Gateway Data Strategy

Status: Accepted

## Context

Investment monitoring benefits from both stable historical records and fresher account views.

## Decision

Use IBKR Flex reports for batch snapshots and reconciliation, and IBKR Gateway for optional local read-only refreshes.

## Consequences

- Flex can provide durable historical data without requiring a running Gateway.
- Gateway can improve freshness when the user has an active local session.
- v0 will use sample and cached data only; live calls are deferred.
- Both paths must normalize into the same dashboard contract.
