#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="${ROOT}/.venv/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "Missing venv. Run: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  exit 1
fi
export TRUST_INDEX_API="${TRUST_INDEX_API:-https://api.robotsshop.io}"
unset PYTHONPATH PYTHONHOME || true
exec env -u PYTHONPATH -u PYTHONHOME "$PY" "$ROOT/trust_index_mcp.py" "$@"
