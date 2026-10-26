#!/usr/bin/env bash
# Start an image with its default command and check that the server comes up:
# /health answers {"status": "ok"} and /mcp answers an MCP initialize request.
# Usage: docker/smoke-test.sh IMAGE [HOST_PORT]
set -euo pipefail

image="${1:?usage: $0 IMAGE [HOST_PORT]}"
port="${2:-8081}"
name="sympy-mcp-smoke-$$"

cleanup() { docker rm -f "$name" >/dev/null 2>&1 || true; }
fail() {
  echo "FAIL: $1"
  echo "--- container logs ---"
  docker logs "$name" 2>&1 || true
  cleanup
  exit 1
}

docker run -d --name "$name" -p "$port:8081" "$image" >/dev/null

health=""
for _ in $(seq 1 60); do
  if health="$(curl -sf "http://localhost:$port/health")"; then
    break
  fi
  if [ "$(docker inspect -f '{{.State.Running}}' "$name" 2>/dev/null)" != "true" ]; then
    fail "the container exited during startup"
  fi
  sleep 1
done
[[ "$health" == *'"status":"ok"'* ]] || fail "/health did not report ok within 60 s (got: '$health')"
echo "health: $health"

response="$(curl -s -w '\n%{http_code}' -X POST "http://localhost:$port/mcp" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"smoke-test","version":"0"}}}')"
status="${response##*$'\n'}"
[ "$status" = "200" ] || fail "MCP initialize returned HTTP $status"
[[ "$response" == *'"serverInfo"'* ]] || fail "MCP initialize response has no serverInfo"
echo "initialize: $(grep -o '"serverInfo":{[^}]*}' <<<"$response")"

cleanup
echo "Smoke test passed for $image"
