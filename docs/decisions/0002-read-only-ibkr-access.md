# 0002: Read-Only IBKR Access

Status: Accepted

## Context

The project monitors investments and does not need trading or account mutation capability.

## Decision

All IBKR integrations must be read-only. The UI and backend must not expose order placement, cancellation, transfer, or account mutation flows.

## Consequences

- The app can focus on reporting and reconciliation.
- Broker credentials and sessions should use the least privilege available.
- Any write-enabled feature requires a new decision record and explicit security review.
