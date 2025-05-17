#!/usr/bin/env bash
set -euo pipefail

# ─────── CONFIG ───────
PORT=8000
BIN="$PWD/bin/surreal"
DB_URL="http://127.0.0.1:$PORT"
REQS="requirements.lock"
WHEELHOUSE="wheelhouse"
PYTHON="python3.11"
# ──────────────────────

# make sure we pick up any local vendored wheels and binaries
export PATH="$PWD/bin:$PATH"
export PIP_NO_INDEX=1
export PIP_FIND_LINKS="$PWD/$WHEELHOUSE"

echo "🛠  Installing dependencies from $WHEELHOUSE"
$PYTHON -m pip install -r "$REQS"

echo "🧹  Killing any existing SurrealDB instances"
pkill -f "$BIN" 2>/dev/null || true

echo "🚀  Launching SurrealDB (memory mode) on $DB_URL"
"$BIN" start memory \
  --user root --pass root \
  --allow-guests \
  --bind 127.0.0.1:"$PORT" \
  --log debug &
DB_PID=$!

# ensure the DB process is cleaned up on script exit
trap 'echo "🛑  Shutting down SurrealDB"; kill $DB_PID 2>/dev/null || true' EXIT INT TERM

echo -n "⏳  Waiting for SurrealDB to be healthy"
until "$BIN" isready --endpoint "$DB_URL" --log none &>/dev/null; do
  sleep 0.3
  echo -n "."
done
echo " ✅"

sleep 1

# Bootstrap the IAM store as root (for HTTP, for /rpc via HTTP endpoint)

curl -s -X POST \
  -H "Accept: application/json" \
  -u root:root \
  -d 'DEFINE NAMESPACE test; DEFINE DATABASE test; DEFINE USER guest ON NAMESPACE test PASSWORD "guest"; GRANT ALL PERMISSIONS ON NAMESPACE test TO guest;' \
  "http://127.0.0.1:8000/sql" >/dev/null

curl -u root:root http://127.0.0.1:8000/info



echo "🧪  Running tests with pytest"
$PYTHON -m pytest -q
