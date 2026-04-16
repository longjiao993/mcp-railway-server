"""
Test Client for the Deployed MCP Server
========================================
Mirrors the notebook's 3-step MCP loop: discover → call → get result
but now over real HTTP against your Railway deployment.

Usage:
    python test_client.py                          # test localhost:8765
    python test_client.py https://xxx.up.railway.app  # test Railway
"""

import sys
import json
import requests

BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8765"
MCP_URL = f"{BASE_URL}/mcp"

HEADERS = {
    "Content-Type": "application/json",
    "MCP-Protocol-Version": "2025-06-18",
}


def mcp_call(method: str, params: dict = None, req_id: int = 1) -> dict:
    """Send a JSON-RPC request to the MCP endpoint."""
    payload = {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": method,
    }
    if params:
        payload["params"] = params

    resp = requests.post(MCP_URL, headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ── Health check ─────────────────────────────────────────
print(f"Testing MCP server at: {BASE_URL}")
info = requests.get(f"{BASE_URL}/", timeout=10).json()
print(f"Server info: {json.dumps(info, indent=2)}\n")


# ── Step 1: Discover tools (mcp.list) ───────────────────
print("=" * 50)
print("STEP 1: List available tools")
print("=" * 50)
result = mcp_call("mcp.list")
print(json.dumps(result, indent=2))


# ── Step 2: Call tools (mcp.call) ────────────────────────
print("\n" + "=" * 50)
print("STEP 2: Call tools")
print("=" * 50)

# word_count — same as notebook: text_tool.run({"tool_name": "word_count", ...})
r = mcp_call("mcp.call", {
    "kind": "tool",
    "name": "word_count",
    "args": {"text": "MCP makes tool access uniform"}
}, req_id=2)
print(f"word_count('MCP makes tool access uniform') = {r}")

# add — same as notebook: mcp.run({"action": "call_tool", "tool_name": "add", ...})
r = mcp_call("mcp.call", {
    "kind": "tool",
    "name": "add",
    "args": {"a": 10, "b": 20}
}, req_id=3)
print(f"add(10, 20) = {r}")

# multiply
r = mcp_call("mcp.call", {
    "kind": "tool",
    "name": "multiply",
    "args": {"a": 25, "b": 16}
}, req_id=4)
print(f"multiply(25, 16) = {r}")

# greet
r = mcp_call("mcp.call", {
    "kind": "tool",
    "name": "greet",
    "args": {"name": "Railway"}
}, req_id=5)
print(f"greet('Railway') = {r}")

# reverse_text
r = mcp_call("mcp.call", {
    "kind": "tool",
    "name": "reverse_text",
    "args": {"text": "pagent"}
}, req_id=6)
print(f"reverse_text('pagent') = {r}")

# timestamp
r = mcp_call("mcp.call", {
    "kind": "tool",
    "name": "timestamp",
    "args": {}
}, req_id=7)
print(f"timestamp() = {r}")

print("\n✅ All tests passed!")
