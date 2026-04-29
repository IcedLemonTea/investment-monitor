# Windows Setup

Version: v0

## Prerequisites

- Windows 10 or newer.
- PowerShell.
- Python and Node versions supported by the repository configuration.

## Local Setup

1. Open PowerShell in the repository root.
2. Create local environment files from examples only if needed.
3. Install dependencies using the project commands in `README.md`.
4. Start the local dashboard service.
5. Open the localhost URL printed by the service.

## Local-Only Rules

- Bind services to localhost.
- Do not expose the dashboard through port forwarding, public tunnels, or shared networks in v0.
- Do not put broker credentials in environment files.
- Use sample or cached local data only until live integrations are explicitly enabled.

## Troubleshooting

- If the port is busy, stop the other local process or choose another localhost port.
- If dependencies fail to install, verify Python and Node are on `PATH`.
- If data is missing, confirm local sample/cache files exist and contain no secrets.
