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
| `free_trips` | Remaining free top/search trips |
| `paid_routes_help` | Paid x402 routes + payTo |

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

## Hermes catalog (stretch)

See `hermes-catalog/manifest.yaml` — PR target: NousResearch/hermes-agent `optional-mcps/robotsshop/`.  
Requires public git URL + pinned ref after publish.

## License

MIT · © AnalogHubris / RobotsShop
