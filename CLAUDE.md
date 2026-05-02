# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kubernetes cluster kontextment toolkit that generates structured reports optimized for AI analysis. Reports follow a summary → metrics → details structure designed for piping into Claude CLI or uploading to claude.ai.

## Key Files

- **`kubectl-kontext`** — Bash kubectl plugin (install to PATH, invoke as `kubectl kontext`). Primary release artifact. Has `--help` and checks for `jq` dependency.
- **`cmd/kubectl-kontext-go/main.go`** — Go port entry point. Dependency checks, wires collector → render → stdout.
- **`internal/collector/collector.go`** — Go Phase 1 + Phase 2: runs all `kubectl` calls in goroutines via `sync.WaitGroup`, writes results to a temp `Cache`.
- **`internal/render/render.go`** — Go Phase 3: typed Go structs for every Kubernetes resource; reads from `Cache` and assembles the report string.
- **`local_mpc_setup/mcp_server.py`** — FastMCP server exposing `get_cluster_report`, `get_current_context`, and `switch_context` tools; calls the Go binary as a subprocess.
- **`go.mod`** — Module `github.com/dejanu/kubectl-kontext`, Go 1.21.

## Running

```bash
kubectl kontext                                    # Report to stdout
./kubectl-kontext                                  # Run directly
kubectl kontext | claude -p 'Analyze this cluster' # Pipe to Claude CLI
kubectl kontext > report.txt                       # Save and upload to claude.ai
kubectl kontext | claude -p 'Analyze...' | glow    # Render markdown in terminal
```

## Dependencies

**Bash plugin (`kubectl-kontext`):**
- `kubectl` with cluster access
- `jq` for JSON processing

**Go port (`cmd/kubectl-kontext-go`):**
- Go 1.21+
- `kubectl` with cluster access
- `jq` (still required at runtime — render layer shells out to it)

**MCP server (`local_mpc_setup/mcp_server.py`):**
- Python with `fastmcp` installed (see `local_mpc_setup/setup_instructions.md`)
- The Go binary (or Bash script) in PATH

**Optional (all variants):**
- Metrics server (for `kubectl top` sections)
- `claude` CLI (for piped analysis)

## Architecture

Two parallel implementations share the same three-phase structure. The Bash script is the primary release artifact; the Go port is in active development alongside it.

**Bash plugin** (`kubectl-kontext`): single file, `set -euo pipefail`, temp directory for caching and parallel execution.

**Go port** (`cmd/kubectl-kontext-go` + `internal/`): `collector` package handles Phases 1–2 with goroutines; `render` package handles Phase 3 with typed structs.

**MCP server** (`local_mpc_setup/mcp_server.py`): FastMCP server that wraps the binary as a tool callable from Claude Desktop or any MCP client.

**Three phases (both implementations):**
1. **Phase 1** — Fetch heavy JSON data in parallel (`pods`, `nodes`, `events`), cached to temp files
2. **Phase 2** — Run independent lightweight kubectl calls in parallel (storageclasses, PDBs, limitranges, quotas, networkpolicies, deployments, statefulsets, daemonsets, rollouts, `kubectl top`)
3. **Phase 3** — Assemble report sequentially from cached data (Bash: `jq`; Go: typed struct parsing)

**Key optimizations:**
- `kubectl get pods -A -o json` fetched once and reused across ~6 sections
- `kubectl get nodes -o json` fetched once and reused across ~4 sections
- ~15 independent kubectl calls run concurrently in Phase 2
- Warning events deduplicated by reason (grouped with counts) to reduce noise
- Deployments and Argo Rollouts filtered: only active (replicas > 0) shown, zero-scale summarized as count
- Argo Rollouts: only non-healthy rollouts listed individually, healthy summarized as count

**Report sections in order:** Quick Summary, Cluster Overview, Nodes, Node Resource Allocation, Cluster-wide Resource Totals, Actual Resource Usage (kubectl top), Resource Summary, Workload Readiness (Deployments, StatefulSets, DaemonSets, Argo Rollouts, Istio sidecar count), Pods without limits/requests, Top memory consumers, Top restarts, Warning events (deduplicated), Problem pods, Storage classes, PDBs, LimitRanges, Quotas, Network Policies, Taints, K3s config.