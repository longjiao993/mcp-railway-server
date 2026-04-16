# MCP Server on Railway (Flask)

A production MCP (Model Context Protocol) server deployed on Railway, based on the **pagent** framework from Lecture 9.

## What This Does

Your notebook's `MCPServer` was **in-memory only** — tools were registered and called within the same Python process. This project turns it into a **real HTTP server** that any MCP client can connect to remotely:

```
Notebook (in-memory)                   Railway (real HTTP)
─────────────────────                  ─────────────────────
MCPServer("text-analyzer")             Flask + flask-mcp-server
  @server.tool()          ──────►      @Mcp.tool(name="word_count")
  client = MCPClient(server)           POST /mcp  (JSON-RPC)
  client.list_tools()                  curl → mcp.list
  client.call_tool(name, args)         curl → mcp.call
```

## Project Structure

```
mcp-railway-server/
├── app.py              # Flask app with MCP tools
├── requirements.txt    # Python dependencies
├── Procfile            # Railway start command (gunicorn)
├── runtime.txt         # Python version
├── test_client.py      # Test script (mirrors notebook usage)
└── .gitignore
```

---

## Step 1: Test Locally

```bash
cd mcp-railway-server

# Create virtual environment
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Visit `http://localhost:8765` — you should see the JSON health response.

Test with the client:
```bash
python test_client.py
```

Or test with curl:
```bash
# List tools
curl -s -X POST http://localhost:8765/mcp \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -d '{"jsonrpc":"2.0","id":1,"method":"mcp.list"}' | python3 -m json.tool

# Call a tool
curl -s -X POST http://localhost:8765/mcp \
  -H "Content-Type: application/json" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -d '{"jsonrpc":"2.0","id":2,"method":"mcp.call","params":{"kind":"tool","name":"add","args":{"a":10,"b":20}}}' | python3 -m json.tool
```

---

## Step 2: Push to GitHub

```bash
git init
git add .
git commit -m "MCP server for Railway"
git remote add origin https://github.com/YOUR_USER/mcp-railway-server.git
git push -u origin main
```

---

## Step 3: Deploy on Railway

1. Go to [railway.com](https://railway.com) and sign in (GitHub OAuth).
2. Click **"New Project"** → **"Deploy from GitHub Repo"**.
3. Select your `mcp-railway-server` repo.
4. Railway auto-detects Python + `requirements.txt` + `Procfile`. No config needed.
5. Once deployed, go to **Settings → Networking → Generate Domain**.
   - You'll get a URL like: `https://mcp-railway-server-production-xxxx.up.railway.app`

### Verify Deployment

```bash
# Health check
curl https://YOUR-APP.up.railway.app/

# Test with the client
python test_client.py https://YOUR-APP.up.railway.app
```

---

## Step 4: Connect to Claude Desktop

Add this to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on Mac):

```json
{
  "mcpServers": {
    "pagent-tools": {
      "url": "https://YOUR-APP.up.railway.app/mcp"
    }
  }
}
```

Restart Claude Desktop. Your tools (`word_count`, `add`, `multiply`, etc.) will appear in the tool picker.

---

## Adding Your Own Tools

Just add more `@Mcp.tool()` functions in `app.py`:

```python
@Mcp.tool(name="sentiment")
def sentiment(text: str) -> str:
    """Analyze sentiment of the given text."""
    # your logic here
    positive = sum(1 for w in text.lower().split() if w in {"good","great","love","excellent"})
    negative = sum(1 for w in text.lower().split() if w in {"bad","terrible","hate","awful"})
    if positive > negative:
        return "positive"
    elif negative > positive:
        return "negative"
    return "neutral"
```

Push to GitHub → Railway auto-redeploys.

---

## Mapping: Notebook → Production

| Notebook Code | Production Equivalent |
|---|---|
| `MCPServer("text-analyzer")` | `app = Flask(__name__)` |
| `@server.tool()` | `@Mcp.tool(name="...")` |
| `MCPClient(server)` | `requests.post(URL/mcp, json=...)` |
| `client.list_tools()` | `{"method": "mcp.list"}` |
| `client.call_tool(name, args)` | `{"method": "mcp.call", "params": {"kind":"tool", "name":"...", "args":{...}}}` |
| `server.add_resource(uri, content)` | `@Mcp.resource(uri="...")` |
| Runs in Colab process | Runs on Railway at a public URL |

---

## Optional: Add Auth

Set these environment variables in Railway's dashboard (Settings → Variables):

```
FLASK_MCP_AUTH_MODE=apikey
FLASK_MCP_API_KEYS=your-secret-key-here
```

Then clients must include the header: `Authorization: Bearer your-secret-key-here`
