# Security Model

Version: v0

## Assumptions

- The dashboard runs on a trusted local workstation.
- Access is limited to the local user account.
- Broker integrations are not live in v0.

## Controls

- Localhost-only network binding.
- Read-only data model.
- No order placement paths.
- No secrets stored in the repository.
- Sensitive data excluded from version control.

## Trust Boundaries

- Browser to local backend: trusted local boundary.
- Backend to local files: trusted local boundary with sensitive data handling.
- Backend to broker systems: out of scope for v0.

## Non-Goals

- Multi-user access control.
- Remote hosting.
- Public authentication.
- Trade execution.
- Secrets management beyond avoiding secrets in v0.

## Review Checklist

- Confirm no listener binds to `0.0.0.0`.
- Confirm write or trade actions are absent from UI and backend routes.
- Confirm logs do not include secrets or full account identifiers.
- Confirm sample files are synthetic or sanitized.
