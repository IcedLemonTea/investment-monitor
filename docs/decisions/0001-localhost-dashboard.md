# 0001: Localhost Dashboard

Status: Accepted

## Context

v0 needs a simple way to inspect investment data without creating a remote service or multi-user system.

## Decision

Run the dashboard and backend on localhost only.

## Consequences

- Setup stays simple for a single workstation.
- Sensitive portfolio data stays local.
- Remote access, hosting, and public authentication are out of scope.
- Any future remote mode requires a separate security review.
