# Architecture

Version: v0

## Scope

The investment monitor is a local-only dashboard for viewing investment data on the same machine that runs the app. v0 does not make live broker calls, does not place trades, and does not store secrets.

## Components

- Dashboard UI: localhost web interface for read-only portfolio views.
- Backend service: local process that serves static assets and normalized data.
- Data adapters: placeholder interfaces for future IBKR Flex files and IBKR Gateway reads.
- Runtime storage: local files for non-secret configuration, cached samples, and logs.

## Data Flow

1. User opens the dashboard on localhost.
2. Backend reads local configuration and local sample/cache data.
3. Backend returns normalized read-only data to the dashboard.
4. Dashboard renders positions, balances, activity, and status without write actions.

## v0 Constraints

- No internet-facing listener.
- No live broker connectivity by default.
- No credentials in source, docs, config, logs, or runtime output.
- No order entry, account mutation, or transfer capability.
