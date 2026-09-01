# Installing the RobotsShop Trust Index MCP server

`robotsshop-mcp` is a stdio FastMCP server exposing free tools against
`https://api.robotsshop.io`. No API key required. Requires **mcp 1.x**
(pin `mcp>=1.2.0,<2` — mcp 2.x renamed FastMCP and is incompatible).

## 1. Hermes (catalog / agent internet)

The server is published to the Hermes catalog:

```bash
hermes mcp catalog          # list remote catalog entries — look for `robotsshop`
hermes mcp install robotsshop
```

Install clones the pinned git commit, creates `.venv`, installs
`requirements.txt`, and writes the `mcp_servers.robotsshop` block into
`~/.hermes/config.yaml`. Free tools land via `tools.default_enabled`. Start a
new session (or `/reload-mcp`) and the 11 free tools are callable.

Manual equivalent (no catalog):

```bash
hermes mcp add robotsshop \
  --command "/abs/path/robotsshop-mcp/.venv/bin/python" \
  --args "/abs/path/robotsshop-mcp/trust_index_mcp.py" \
  --env TRUST_INDEX_API=https://api.robotsshop.io
hermes mcp test robotsshop
```

## 2. Claude Desktop

```json
{
  "mcpServers": {
    "robotsshop": {
      "command": "/abs/path/robotsshop-mcp/.venv/bin/python",
      "args": ["/abs/path/robotsshop-mcp/trust_index_mcp.py"],
      "env": { "TRUST_INDEX_API": "https://api.robotsshop.io" }
    }
  }
}
```

## 3. Cursor

Same shape in `.cursor/mcp.json`.

## 4. Any MCP client (generic)

```bash
git clone https://github.com/AnalogHubris/robotsshop-mcp.git && cd robotsshop-mcp
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt        # installs mcp>=1.2.0,<2 + httpx
./run_mcp.sh --smoke                              # HTTP smoke → SMOKE_OK
.venv/bin/python trust_index_mcp.py               # serve over stdio
```

Point your client's `command` + `args` at the venv python + `trust_index_mcp.py`.

## Tools exposed (11 free + 1 alias)

| Tool | Hits | Purpose |
|------|------|---------|
| `stats` | `/v0/stats` | Market summary (gated %, mismatches, score bands) |
| `leaderboard` | `/v0/leaderboard` | Domain avg scores |
| `mismatches` | `/v0/mismatches` | Listing payTo ≠ live 402 (fraud signal) |
| `payto_mismatches` | (alias) | Alias of `mismatches` |
| `lookup` | `/v0/endpoint?url=` | Single-endpoint trust snapshot |
| `endpoint` | `/v0/endpoint?url=` | Single-endpoint trust snapshot |
| `settlements` | `/v0/settlements` | Proof-backed paid-attempt ledger (on-chain receipts, filters ok/hashed/verified/offset/limit) |
| `entities` | `/v0/spookfiles/entities?q=` | SpookFiles named entities — 892k across 6.5M declassified docs |
| `onramp` | `/v0/onramp` | Free→paid recipe |
| `free_trips` | `/v0/free-trips` | Remaining free top/search trips |
| `paid_routes_help` | local | Paid x402 routes + payTo wallet |
| `swartzpath` | `/v0/swartzpath` | Legal OA path to a paper |

Note: `/v0/swartzpath` is currently an x402-paid route (HTTP 402); the tool
returns the payment requirement. Free tools never attach payment — paid depth
is HTTP x402, see `paid_routes_help`.

## Traffic → paid endpoints

Every free MCP tool is a funnel into the paid x402 routes (Base USDC):

- **`entities`** → free entity graph names a person/org/place WITH doc counts,
  then hooks the paid `deep=1` per-entity doc links ($0.01 x402) under the hood.
- **`lookup`/`endpoint`** → free snapshot of one endpoint; deeper live re-check
  is the paid `/v0/live` ($0.005) or full `/v0/snapshot` ($0.10).
- **`mismatches`** → finds payTo failures, then paid `/v0/search`, `/v0/top`
  for depth ($0.001).
- **`onramp`** → explicit free→paid recipe; `free_trips` browsers can convert
  to `/v0/live`/`/v0/snapshot`/`/v0/monitor/subscribe` ($10/mo residual).

payTo: `0x53831fab63ba75a958115c3b4eb598a10cfcc7e0` · USDC on Base (eip155:8453).
