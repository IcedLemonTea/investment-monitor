# Data Classification

Version: v0

## Public

- Project documentation.
- Static dashboard assets.
- Example configuration with placeholder values only.

## Internal Local

- Local dashboard settings.
- Non-secret adapter configuration.
- Generated local logs.
- Derived portfolio summaries.

## Sensitive

- Account identifiers.
- Positions, balances, transactions, and performance history.
- Broker export files such as IBKR Flex reports.

## Secret

- Broker usernames, passwords, API tokens, session cookies, certificates, and two-factor recovery codes.

## Handling Rules

- Do not commit sensitive or secret data.
- Do not log secrets.
- Keep sensitive runtime data on the local machine only.
- Use read-only broker permissions when live integrations are added.
- Treat screenshots and exports from the dashboard as sensitive.
