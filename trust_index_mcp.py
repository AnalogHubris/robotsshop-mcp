#!/usr/bin/env python3
"""RobotsShop Trust Index — production MCP server (stdio FastMCP).

Shop brand: RobotsShop · Founder: AnalogHubris · SoulEngine never appears here.

Install:
  cd /path/to/RobotsShop/mcp
  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt

Run (stdio — Claude Desktop / Cursor / Hermes):
  TRUST_INDEX_API=https://api.robotsshop.io python trust_index_mcp.py

Smoke:
  python trust_index_mcp.py --smoke

Hermes:
  hermes mcp add robotsshop --command /path/to/mcp/.venv/bin/python \\
    --args /path/to/mcp/trust_index_mcp.py \\
    --env TRUST_INDEX_API=https://api.robotsshop.io
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import httpx

__version__ = "1.3.0"

API = os.environ.get("TRUST_INDEX_API", "https://api.robotsshop.io").rstrip("/")
SITE = "https://robotsshop.io"
FOUNDER_SITE = "https://analoghubris.com"
CONTACT = "hello@robotsshop.io"
PAY_TO = "0x53831fab63ba75a958115c3b4eb598a10cfcc7e0"
SELLER = "RobotsShop"
USER_AGENT = f"RobotsShop-TrustIndex-MCP/{__version__} (+{SITE})"
DEFAULT_TIMEOUT = float(os.environ.get("TRUST_INDEX_TIMEOUT", "30"))


def _error_payload(kind: str, detail: Any, **extra: Any) -> str:
    body: dict[str, Any] = {
        "ok": False,
        "error": kind,
        "detail": detail,
        "api": API,
        "seller": SELLER,
    }
    body.update(extra)
    return json.dumps(body, indent=2)


def _get(path: str, params: dict | None = None) -> Any:
    url = f"{API}{path}"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    with httpx.Client(timeout=DEFAULT_TIMEOUT, follow_redirects=True, headers=headers) as client:
        r = client.get(url, params=params or {})
        if r.status_code == 402:
            raise RuntimeError(
                "HTTP 402 PAYMENT-REQUIRED — use an x402 client for paid routes "
                f"(see paid_routes_help). url={url}"
            )
        if r.status_code >= 400:
            try:
                detail = r.json()
            except Exception:
                detail = r.text[:500]
            raise RuntimeError(f"HTTP {r.status_code} for {path}: {detail}")
        return r.json()


def tool_stats() -> str:
    """Market summary from free /v0/stats."""
    try:
        data = _get("/v0/stats")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("stats_failed", str(e))


def tool_leaderboard(limit: int = 15, min_score: int = 70) -> str:
    """Free domain leaderboard by average trust score."""
    try:
        limit = max(1, min(100, int(limit)))
        min_score = max(0, min(100, int(min_score)))
        data = _get("/v0/leaderboard", {"limit": limit, "min_score": min_score})
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("leaderboard_failed", str(e), limit=limit, min_score=min_score)


def tool_mismatches(limit: int = 15) -> str:
    """Free sample of payTo integrity failures (listing wallet ≠ live 402)."""
    try:
        limit = max(1, min(100, int(limit)))
        data = _get("/v0/mismatches", {"limit": limit})
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("mismatches_failed", str(e), limit=limit)


def tool_lookup(url: str) -> str:
    """Free single-endpoint trust snapshot from last scan."""
    try:
        url = (url or "").strip()
        if len(url) < 8:
            return _error_payload(
                "invalid_url",
                "url must be a full resource URL (min 8 chars)",
                url=url,
            )
        data = _get("/v0/endpoint", {"url": url})
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("lookup_failed", str(e), url=url)


def tool_endpoint(url: str) -> str:
    """Free single-endpoint trust snapshot by full resource URL (alias of lookup)."""
    try:
        url = (url or "").strip()
        if len(url) < 8:
            return _error_payload(
                "invalid_url",
                "url must be a full resource URL (min 8 chars)",
                url=url,
            )
        data = _get("/v0/endpoint", {"url": url})
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("endpoint_failed", str(e), url=url)


def tool_settlements(
    ok: str = "",
    hashed: str = "",
    verified: str = "",
    offset: int = 0,
    limit: int = 200,
) -> str:
    """Free proof-backed settlement ledger for paid x402 attempts (on-chain receipts)."""
    try:
        params: dict[str, Any] = {"limit": max(1, min(500, int(limit)))}
        if int(offset) > 0:
            params["offset"] = int(offset)
        for flag in ("ok", "hashed", "verified"):
            v = locals().get(flag)
            if v in ("true", "True", "1"):
                params[flag] = "true"
            elif v in ("false", "False", "0"):
                params[flag] = "false"
        data = _get("/v0/settlements", params)
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("settlements_failed", str(e), offset=offset, limit=limit)


def tool_entities(q: str = "") -> str:
    """SpookFiles named-entity search — 892k entities across 6.5M declassified docs."""
    try:
        q = (q or "").strip()
        params = {"q": q} if q else None
        data = _get("/v0/spookfiles/entities", params)
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("entities_failed", str(e), q=q)


def tool_swartzpath(doi: str = "", q: str = "") -> str:
    """Legal OA path. Named for Aaron Swartz. Free. Not Sci-Hub."""
    try:
        params: dict[str, str] = {}
        if (doi or "").strip():
            params["doi"] = doi.strip()
        elif (q or "").strip():
            params["q"] = q.strip()
        data = _get("/v0/swartzpath", params or None)
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("swartzpath_failed", str(e), doi=doi, q=q)


def tool_onramp() -> str:
    """Free→paid agent recipe: mismatches → free trips → depth → residual."""
    try:
        data = _get("/v0/onramp")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("onramp_failed", str(e))


def tool_free_trips() -> str:
    """How many free judgment trips remain today for this caller IP."""
    try:
        data = _get("/v0/free-trips")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _error_payload("free_trips_failed", str(e))


def tool_paid_routes_help() -> str:
    """Paid x402 routes, prices, payTo, Bazaar discovery."""
    return json.dumps(
        {
            "ok": True,
            "brand": SELLER,
            "founder": "AnalogHubris",
            "product": "Trust Index",
            "mcp_version": __version__,
            "api": API,
            "site": SITE,
            "founder_site": FOUNDER_SITE,
            "docs": f"{API}/docs",
            "onramp": f"{API}/v0/onramp",
            "contact": CONTACT,
            "payTo": PAY_TO,
            "network": "eip155:8453",
            "asset": "USDC on Base",
            "free_mcp_tools": [
                "stats",
                "leaderboard",
                "mismatches",
                "lookup",
                "onramp",
                "free_trips",
                "paid_routes_help",
                "swartzpath",
                "settlements",
                "endpoint",
                "entities",
            ],
            "paid_http_x402": {
                "search": {
                    "method": "GET",
                    "path": "/v0/search",
                    "url": f"{API}/v0/search",
                    "price_usdc": "0.001",
                    "free_trips_per_day": 25,
                    "params": [
                        "min_score",
                        "grade",
                        "domain",
                        "q",
                        "exclude_spam",
                        "limit",
                        "offset",
                    ],
                },
                "top": {
                    "method": "GET",
                    "path": "/v0/top",
                    "url": f"{API}/v0/top",
                    "price_usdc": "0.001",
                    "free_trips_per_day": 25,
                    "params": ["n", "min_score", "exclude_spam"],
                },
                "live": {
                    "method": "GET",
                    "path": "/v0/live",
                    "url": f"{API}/v0/live",
                    "price_usdc": "0.005",
                    "params": ["url"],
                },
                "snapshot": {
                    "method": "GET",
                    "path": "/v0/snapshot",
                    "url": f"{API}/v0/snapshot",
                    "price_usdc": "0.10",
                    "params": [],
                },
                "monitor_subscribe": {
                    "method": "POST",
                    "path": "/v0/monitor/subscribe",
                    "url": f"{API}/v0/monitor/subscribe",
                    "price_usdc": "10.00",
                    "term_days": 30,
                    "note": "Residual integrity monitor",
                },
            },
            "note": (
                "Paid routes return HTTP 402 PAYMENT-REQUIRED. "
                "Use an x402 client (Base USDC) with payTo above. "
                "MCP free tools never attach payment. "
                "Start with onramp + mismatches before spending."
            ),
            "bazaar": {
                "merchant": (
                    "https://api.cdp.coinbase.com/platform/v2/x402/discovery/merchant"
                    f"?payTo={PAY_TO}"
                ),
            },
            "integrity": (
                "Independent measurements. No payment attached during probes. "
                "Methodology at /v0/stats."
            ),
        },
        indent=2,
    )


def run_smoke() -> int:
    print("=== RobotsShop Trust Index MCP smoke ===")
    print("API", API)
    print("mcp_version", __version__)
    print("seller", SELLER)
    ok = True
    try:
        s = json.loads(tool_stats())
        if s.get("ok") is False:
            print("stats FAIL", s)
            ok = False
        else:
            print("stats OK as_of", s.get("as_of"), "n", s.get("n_endpoints"), "brand", s.get("brand"))

        lb = json.loads(tool_leaderboard(3))
        if lb.get("ok") is False:
            print("leaderboard FAIL", lb)
            ok = False
        else:
            print("leaderboard OK count", lb.get("count"), "free", lb.get("free"))

        mm = json.loads(tool_mismatches(2))
        if mm.get("ok") is False:
            print("mismatches FAIL", mm)
            ok = False
        else:
            print("mismatches OK count", mm.get("count"), "signal", mm.get("signal"))

        on = json.loads(tool_onramp())
        if on.get("ok") is False:
            print("onramp FAIL", on)
            ok = False
        else:
            print("onramp OK steps", len(on.get("steps") or []), "brand", on.get("brand"))

        ft = json.loads(tool_free_trips())
        if ft.get("ok") is False and ft.get("free") is not True:
            print("free_trips FAIL", ft)
            ok = False
        else:
            print("free_trips OK remaining", ft.get("remaining"), "limit", ft.get("limit_per_day"))

        sample_url = None
        if isinstance(mm, dict) and mm.get("results"):
            sample_url = mm["results"][0].get("resource")
        if not sample_url:
            sample_url = "https://agentattest.hergertsynthora.com/service"
        lu = json.loads(tool_lookup(sample_url))
        if lu.get("ok") is False and "endpoint" not in lu and "resource" not in str(lu):
            print("lookup FAIL", lu)
            ok = False
        else:
            ep = lu.get("endpoint") or lu
            print(
                "lookup OK",
                ep.get("resource") or sample_url,
                "score",
                ep.get("score"),
                "grade",
                ep.get("grade"),
            )

        st = json.loads(tool_settlements(limit=3))
        if st.get("ok") is False and "note" not in st:
            print("settlements FAIL", st)
            ok = False
        else:
            print(
                "settlements OK total_settled",
                st.get("total_settled"),
                "shown",
                st.get("count"),
                "chain_ok",
                "on_chain_proof" in st,
            )

        ep = json.loads(tool_endpoint("https://ai16z.ai/verify"))
        if ep.get("ok") is False and "endpoint" not in ep and "detail" not in ep:
            print("endpoint FAIL", ep)
            ok = False
        else:
            print(
                "endpoint OK url",
                "https://ai16z.ai/verify",
                "looked up",
                "endpoint" in ep or "detail" in ep,
            )

        ents = json.loads(tool_entities("epstein"))
        if ents.get("ok") is False and "graph" not in ents:
            print("entities FAIL", ents)
            ok = False
        else:
            graph = ents.get("graph") or {}
            print(
                "entities OK graph_present",
                graph.get("present"),
                "count",
                graph.get("count"),
                "product",
                ents.get("product"),
            )

        help_body = json.loads(tool_paid_routes_help())
        if help_body.get("brand") != SELLER:
            print("paid_routes_help brand FAIL", help_body.get("brand"))
            ok = False
        else:
            print(
                "paid_routes_help OK payTo",
                help_body.get("payTo"),
                "tools",
                len(help_body.get("free_mcp_tools") or []),
            )

        # swartzpath is METERED at the API ($0.01 doi/q resolve, 2026-08-23+).
        # Free MCP behavior = bare discovery call works; doi/q call surfaces the
        # x402 paid gate (HTTP 402 → error with paid-routes guidance), never a crash.
        sp_bare = json.loads(tool_swartzpath())
        sp_gate = json.loads(tool_swartzpath(doi="10.1371/journal.pone.0000308"))
        if not (sp_bare.get("product") == "Swartzpath"):
            print("swartzpath FAIL bare discovery", {k: sp_bare.get(k) for k in ("product", "error", "ok")})
            ok = False
        elif "PAYMENT-REQUIRED" in (sp_gate.get("detail") or "") or "x402" in (sp_gate.get("detail") or "").lower():
            print("swartzpath OK paid-gate surfaced")
        else:
            print("swartzpath FAIL unexpected", {k: sp_gate.get(k) for k in ("grade", "pdf_url", "error", "ok")})
            ok = False

        if ok:
            print("SMOKE_OK")
            return 0
        print("SMOKE_FAIL")
        return 1
    except Exception as e:
        print("SMOKE_FAIL", type(e).__name__, e)
        return 1


def run_mcp() -> None:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP(
        "robotsshop-trust-index",
        instructions=(
            "RobotsShop Trust Index: independent x402 settlement truth "
            "(liveness, protocol, spam, payTo). Free tools here; paid HTTP at "
            f"{API}. Site {SITE}. Contact {CONTACT}. "
            "Prefer free tools first: onramp → mismatches → free_trips. "
            "Use paid_routes_help before any USDC call. Founder: AnalogHubris."
        ),
    )

    @mcp.tool()
    def stats() -> str:
        """Market summary: gated %, payTo mismatches, score bands, methodology."""
        return tool_stats()

    @mcp.tool()
    def leaderboard(limit: int = 15, min_score: int = 70) -> str:
        """Free domain leaderboard by average trust score (spam filtered)."""
        return tool_leaderboard(limit, min_score)

    @mcp.tool()
    def mismatches(limit: int = 15) -> str:
        """Endpoints where directory payTo does not match live 402 requirements (fraud signal)."""
        return tool_mismatches(limit)

    @mcp.tool()
    def lookup(url: str) -> str:
        """Free single-endpoint trust snapshot by full resource URL."""
        return tool_lookup(url)

    @mcp.tool()
    def onramp() -> str:
        """Free→paid agent recipe: free integrity → free trips → paid depth → residual monitor."""
        return tool_onramp()

    @mcp.tool()
    def settlements(
        ok: str = "",
        hashed: str = "",
        verified: str = "",
        offset: int = 0,
        limit: int = 200,
    ) -> str:
        """Proof-backed settlement ledger for paid x402 attempts. Filters: ok/hashed/verified true|false, offset, limit."""
        return tool_settlements(ok=ok, hashed=hashed, verified=verified, offset=offset, limit=limit)

    @mcp.tool()
    def endpoint(url: str) -> str:
        """Free single-endpoint trust snapshot by full resource URL (SpookFiles/trust lookup)."""
        return tool_endpoint(url)

    @mcp.tool()
    def entities(q: str = "") -> str:
        """SpookFiles named-entity search — 892k named entities across 6.5M declassified docs. Query a person/org/place."""
        return tool_entities(q)

    @mcp.tool()
    def free_trips() -> str:
        """Remaining free judgment trips today (top/search) for this IP."""
        return tool_free_trips()

    @mcp.tool()
    def paid_routes_help() -> str:
        """Paid x402 routes, prices, payTo wallet, residual monitor."""
        return tool_paid_routes_help()

    @mcp.tool()
    def swartzpath(doi: str = "", q: str = "") -> str:
        """Legal OA path to a paper. Named for Aaron Swartz. DOI or title → grade + legal PDF URL if one exists. Not Sci-Hub. Closed stays closed. Free."""
        return tool_swartzpath(doi=doi, q=q)

    @mcp.tool()
    def payto_mismatches(limit: int = 15) -> str:
        """Alias of mismatches — payTo listing vs live 402 fraud signal."""
        return tool_mismatches(limit)

    mcp.run(transport="stdio")


def main() -> int:
    ap = argparse.ArgumentParser(description="RobotsShop Trust Index MCP")
    ap.add_argument("--smoke", action="store_true", help="HTTP free-tool smoke only")
    ap.add_argument("--version", action="store_true", help="Print version and exit")
    args = ap.parse_args()
    if args.version:
        print(__version__)
        return 0
    if args.smoke:
        return run_smoke()
    try:
        run_mcp()
        return 0
    except ImportError as e:
        print(
            "mcp package missing — run: pip install -r requirements.txt",
            file=sys.stderr,
        )
        print(f"ImportError: {e}", file=sys.stderr)
        print("Falling back to --smoke", file=sys.stderr)
        return run_smoke()


if __name__ == "__main__":
    raise SystemExit(main())
