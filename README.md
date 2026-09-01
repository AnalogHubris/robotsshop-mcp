# robotsshop-mcp

**RobotsShop Trust Index** — MCP server for agent settlement truth on x402.

| | |
|--|--|
| Shop | https://robotsshop.io |
| API | https://api.robotsshop.io |
| Contact | hello@robotsshop.io |
| Founder | AnalogHubris |
| Agent | [@Digital_Hubris](https://x.com/Digital_Hubris) |

Independent probes: **who actually gets paid** (payTo integrity), not vibes.

## Tools (free)

| Tool | Purpose |
|------|---------|
| `onramp` | Free→paid recipe |
| `mismatches` | Listing payTo ≠ live 402 |
| `stats` | Market summary |
| `leaderboard` | Domain scores |
| `lookup` | One endpoint snapshot |
| `endpoint` | One endpoint snapshot (alias of lookup) |
| `settlements` | Proof-backed paid-attempt ledger (on-chain receipts) |
| `entities` | SpookFiles named-entity search — 892k entities over 6.5M declassified docs |
| `free_trips` | Remaining free top/search trips |
| `paid_routes_help` | Paid x402 routes + payTo |
| `swartzpath` | Legal OA path to a paper |

Paid HTTP (Base USDC) is separate — see `paid_routes_help`. MCP free tools never attach payment.

## Quick start

```bash
git clone https://github.com/AnalogHubris/robotsshop-mcp.git && cd robotsshop-mcp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
./run_mcp.sh --smoke   # → SMOKE_OK
```

### Hermes

```bash
hermes mcp add robotsshop --command "$(pwd)/run_mcp.sh"
hermes mcp test robotsshop
```

### Claude Desktop

```json
{
  "mcpServers": {
    "robotsshop": {
      "command": "/ABS/PATH/robotsshop-mcp/run_mcp.sh",
      "env": { "TRUST_INDEX_API": "https://api.robotsshop.io" }
    }
  }
}
```

### Cursor

Same shape in `.cursor/mcp.json`.

## Env

| Var | Default |
|-----|---------|
| `TRUST_INDEX_API` | `https://api.robotsshop.io` |
| `TRUST_INDEX_TIMEOUT` | `30` |

## Hermes catalog

`hermes-catalog/manifest.yaml` is the Nous approved entry → target
`NousResearch/hermes-agent optional-mcps/robotsshop/`. Install in Hermes:

```bash
hermes mcp catalog          # list remote catalog entries
hermes mcp install robotsshop
```

The catalog clones the pinned git commit, runs `.venv` bootstrap, and enables
the free tools via `tools.default_enabled`. Requires a public git URL + pinned
commit SHA (manifest `install.ref`). Agents get 11 free MCP tools — every one a
preview into the paid x402 depth (`/v0/search`, `/v0/top`, `/v0/live`,
`/v0/snapshot`, `/v0/monitor/subscribe`). `entities` (SpookFiles) is the
traffic hook: free named-entity graph → paid `deep=1` per-entity doc links.

## License

MIT · © AnalogHubris / RobotsShop
