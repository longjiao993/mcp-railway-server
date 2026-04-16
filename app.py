"""
MCP Server on Railway (Flask)
=============================
Based on Lecture 9 (pagent) — but deployed as a REAL MCP server
that any MCP client (Claude Desktop, Claude.ai, etc.) can connect to.

Uses flask-mcp-server for MCP 2025-06-18 compliance:
  - Unified /mcp endpoint (POST for JSON-RPC, GET for SSE)
  - Tool discovery via mcp.list
  - Tool invocation via mcp.call
"""

import os
import json
from datetime import datetime
from flask import Flask
from flask_mcp_server import mount_mcp, Mcp
from flask_mcp_server.http_integrated import mw_cors

# ── Flask app ────────────────────────────────────────────
app = Flask(__name__)


# ══════════════════════════════════════════════════════════
#  TOOLS — register exactly like @text_server.tool() in the
#  notebook, but now they're exposed over MCP protocol.
# ══════════════════════════════════════════════════════════

@Mcp.tool(name="word_count")
def word_count(text: str) -> int:
    """Count words in a text string."""
    return len(text.split())


@Mcp.tool(name="char_count")
def char_count(text: str) -> int:
    """Count characters (excluding spaces)."""
    return len(text.replace(" ", ""))


@Mcp.tool(name="reverse_text")
def reverse_text(text: str) -> str:
    """Reverse a string."""
    return text[::-1]


@Mcp.tool(name="add")
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@Mcp.tool(name="multiply")
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@Mcp.tool(name="greet")
def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}! Welcome to the MCP server."


@Mcp.tool(name="timestamp")
def timestamp() -> str:
    """Return the current server UTC timestamp."""
    return datetime.utcnow().isoformat() + "Z"


# ══════════════════════════════════════════════════════════
#  HEALTH CHECK — Railway uses this to know the app is up
# ══════════════════════════════════════════════════════════

@app.route("/")
def index():
    return {
        "service": "pagent-mcp-server",
        "status": "healthy",
        "protocol": "MCP 2025-06-18",
        "endpoint": "/mcp",
        "tools": [
            "word_count", "char_count", "reverse_text",
            "add", "multiply", "greet", "timestamp",
        ],
    }


@app.route("/health")
def health():
    return {"status": "ok"}


# ══════════════════════════════════════════════════════════
#  MOUNT MCP — this wires up the /mcp endpoint
# ══════════════════════════════════════════════════════════

mount_mcp(app, url_prefix="/mcp", middlewares=[mw_cors])


# ══════════════════════════════════════════════════════════
#  RUN — Railway sets PORT env var automatically
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    app.run(host="0.0.0.0", port=port, debug=False)
