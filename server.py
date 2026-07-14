#!/usr/bin/env python3
"""RobotsShop Trust Index MCP — public package entrypoint.

stdio FastMCP. Free tools only (no payment attached).
API default: https://api.robotsshop.io
"""
from __future__ import annotations

# Re-export main server from monorepo path when developing locally;
# in the published package this file IS the server (copy of trust_index_mcp).
import runpy
from pathlib import Path

# Prefer sibling trust_index_mcp.py (same dir in package)
_here = Path(__file__).resolve().parent
_server = _here / "trust_index_mcp.py"
if _server.exists():
    runpy.run_path(str(_server), run_name="__main__")
else:
    raise SystemExit("trust_index_mcp.py missing next to server.py")
