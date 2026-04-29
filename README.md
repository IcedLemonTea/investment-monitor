# Investment Monitor

Local Windows desktop investment monitor for a single IBKR account.

This repository starts with mock/example data only. Live IBKR integrations will be added behind read-only adapters in later phases.

## Goals

- Keep all real portfolio data local.
- Serve a static-style dashboard on localhost.
- Use USD as the source currency with optional MYR display conversion.
- Enforce read-only IBKR access through endpoint policy, tests, and UI constraints.
- Store real generated data under `runtime/` or gitignored `public/data/`.

## Quick Start

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest
ruff check src tests
```

## Target Allocation

| Ticker | Target |
| --- | ---: |
| QLD | 50% |
| TQQQ | 10% |
| AVUV | 20% |
| AVDV | 10% |
| QMOM | 10% |
| CASH_OTHERS | 0% |

## Current Phase

Phase 0: repository governance, mock fixtures, and security tests. No live IBKR calls are implemented.
