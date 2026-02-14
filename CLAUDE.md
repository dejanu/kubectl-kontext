# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kubernetes cluster assessment toolkit that generates structured reports optimized for AI analysis. Reports follow a summary → metrics → details structure designed for piping into Claude CLI.

## Key Files

- **`kubectl-assess`** — kubectl plugin (install to PATH, invoke as `kubectl assess`). Has `--help` and checks for `jq` dependency.

## Running

```bash
kubectl assess                                    # Report to stdout
./kubectl-assess                                  # Run directly
kubectl assess | claude -p 'Analyze this cluster' # Pipe to Claude manually
kubectl assess --analyze                          # Built-in comprehensive analysis
kubectl assess --health                           # Quick health check
kubectl assess --security                         # Security-focused review
kubectl assess --capacity                         # Capacity planning
kubectl assess --analyze --model opus -o out.md   # Choose model, save to file
```

## Dependencies

- `kubectl` with cluster access
- `jq` for JSON processing
- `claude` CLI (only required for `--analyze`/`--health`/`--security`/`--capacity` modes)

## Architecture

Single-file bash script using `set -euo pipefail`. All kubectl output is captured in a subshell (`REPORT=$( { ... } 2>&1 )`) with `2>/dev/null` and fallbacks on every kubectl call to handle missing resources gracefully.

**Two code paths:**
1. **No mode flag** — prints raw report to stdout for external piping
2. **With mode flag** (`--analyze`, `--health`, `--security`, `--capacity`) — pipes report through `claude` CLI using built-in prompt templates from `get_prompt()`

**Report sections in order:** Quick Summary, Analysis Context (severity thresholds), Cluster Overview, Nodes, Node Resource Allocation, Cluster-wide Resource Totals, Resource Summary, Pods without limits/requests, Top memory consumers, Top restarts, Warning events, Problem pods, Storage classes, PDBs, LimitRanges, Quotas, Network Policies, Taints, K3s config.

**Prompt templates** (`get_prompt` function) define structured output formats for each analysis mode. Each template references the "ANALYSIS CONTEXT" thresholds embedded in the report so Claude can calibrate severity consistently.