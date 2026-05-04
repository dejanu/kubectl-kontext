# MCP Server Setup

## Prerequisites

- set desired cluster by updating `KUBECONFIG` env var and `kubectl` configured with cluster access
- `uv` — Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- Claude Desktop app (Mac/Windows)
- Both `kubectl-kontext` and `mcp_server.py` installed via `make install-mcp` (places them under `$HOME/.local/bin/kubectl-kontext/`, no `sudo` required)

## How to start the MCP server manually

```bash
uv run mcp_server.py

# inspector to debug mcp server
npx @modelcontextprotocol/inspector uv run mcp_server.py
```

No `pip install` or virtualenv setup required, `uv` resolves and installs dependencies automatically from the inline block at the top of `mcp_server.py`.

### Add mcp server to claude desktop:

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

Connectors are MCP servers with a graphical setup flow. Use them for quick integration with supported services. For integrations not listed in Connectors, add MCP servers manually via settings files, Claude Desktop manages the MCP server lifecycle via `claude_desktop_config.json`.

> **Note:** Claude Desktop does not expand `~` in paths — use absolute paths only.

1. Run `make install-mcp` to get the exact path, configure claude-desktop via `~/Library/Application\ Support/Claude/claude_desktop_config.json`:


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
        "KUBECONFIG": "/Users/<your-username>/.local/bin/kubectl-kontext/active-config"
      }
    }
  }
}
```

2. Point the desired kubeconfig to `active-config` used by the `kubectl-kontext` mcp server

```bash
# create/update simlink
ln -sf  <path-to-desired-kubeconfig> /Users/alexandru.dejanu/.local/bin/kubectl-kontext/active-config 
```

### Add mcp server to claude code: 

```bash
#  use --scope user so the config is written to ~/.claude.json and applies across all your Claude Code projects
# (other scopes local, user, or project)

# add mcp server using STDIO and local scope  
claude mcp add kubectl-kontext --scope user -e KUBECONFIG=/Users/<your-username>/.kube/config -- uv run /Users/<your-username>/.local/bin/kubectl-kontext/mcp_server.py

# remove mcp server
claude mcp remove kubectl-kontext
```

## Available tools

Mcp uses [FastMCP](https://gofastmcp.com/getting-started/welcome) framework with stdio transport communication layer to connect MCP servers to clients.

| Tool | Description |
|------|-------------|
| `get_cluster_report` | Runs `kubectl-kontext` and returns the full cluster assessment report |
| `get_current_context` | Lists kubeconfig contexts and shows the active one |
| `switch_context` | Switches the active kubectl context by name (no restart needed) |

## Example prompts

```
What are the top 3 issues in my cluster?

Are there any pods without resource limits?

Is this cluster over-provisioned? Suggest rightsizing.

Which context am I on and what contexts are available?
```




