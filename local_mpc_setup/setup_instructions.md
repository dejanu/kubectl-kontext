# MCP Server Setup

## Prerequisites

- set desired cluster by updating `KUBECONFIG` env var and `kubectl` configured with cluster access
- `uv` — Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- Claude Desktop app (Mac/Windows)
- Both `kubectl-kontext` and `mcp_server.py` installed via `make install-mcp` (places them under `$HOME/.local/bin/kubectl-kontext/`, no `sudo` required)

## How to start the MCP server manually

```bash
uv run mcp_server.py
```

`uv` resolves and installs dependencies automatically from the inline block at the top of `mcp_server.py`. No `pip install` or virtualenv setup required.

## How to connect from Claude Desktop

Claude Desktop manages the MCP server lifecycle via `claude_desktop_config.json`.

> **Note:** Claude Desktop does not expand `~` in paths — use absolute paths only.

1. Run `make install-mcp` to get the exact path, then add it to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kubectl-kontext": {
      "command": "uv",
      "args": [
        "run",
        "/Users/<your-username>/.local/bin/kubectl-kontext/mcp_server.py"
      ],
      "env": {
        "KUBECONFIG": "/Users/<your-username>/.kube/config"
      }
    }
  }
}
```

2. Quit and reopen Claude Desktop.
3. Open a new conversation — the hammer (tools) icon should appear in the input bar.
4. Click it to confirm `get_cluster_report` and `get_current_context` are listed.

## Available tools

| Tool | Description |
|------|-------------|
| `get_cluster_report` | Runs `kubectl-kontext` and returns the full cluster assessment report |
| `get_current_context` | Lists kubeconfig contexts and shows the active one |

## Example prompts

```
What are the top 3 issues in my cluster?

Are there any pods without resource limits?

Is this cluster over-provisioned? Suggest rightsizing.

Which context am I on and what contexts are available?
```

## How it works

`claude_desktop_config.json` is the equivalent of a process supervisor config — Claude Desktop is the supervisor:

1. Claude Desktop starts → reads `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Spawns the MCP server as a child process (`uv run mcp_server.py`)
3. Keeps it running in the background, connected via stdio pipe (not a TCP port)
4. When you chat, Claude calls tools over that pipe on demand
5. Claude Desktop quits → child processes are killed

```bash
# verify the MCP server process is running
ps aux | grep mcp_server.py | grep -v grep
```

