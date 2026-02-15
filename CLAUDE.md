# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kubernetes cluster assessment toolkit that generates structured reports optimized for AI analysis. Reports follow a summary → metrics → details structure designed for piping into Claude CLI or uploading to claude.ai.

## Key Files

- **`kubectl-assess`** — kubectl plugin (install to PATH, invoke as `kubectl assess`). Has `--help` and checks for `jq` dependency.

## Running

```bash
kubectl assess                                    # Report to stdout
./kubectl-assess                                  # Run directly
kubectl assess | claude -p 'Analyze this cluster' # Pipe to Claude CLI
kubectl assess > report.txt                       # Save and upload to claude.ai
kubectl assess | claude -p 'Analyze...' | glow    # Render markdown in terminal
```

## Dependencies

- `kubectl` with cluster access
- `jq` for JSON processing
- `claude` CLI (optional, for piped analysis)
- Metrics server (optional, for actual resource usage via `kubectl top`)

## Architecture

Single-file bash script using `set -euo pipefail`. Uses a temp directory for caching and parallel execution.

**Three phases:**
1. **Phase 1** — Fetch heavy JSON data in parallel (`pods`, `nodes`, `events`), cached to temp files
2. **Phase 2** — Run independent lightweight kubectl calls in parallel (storageclasses, PDBs, limitranges, quotas, networkpolicies, deployments, statefulsets, daemonsets, rollouts, `kubectl top`)
3. **Phase 3** — Assemble report sequentially from cached data using `jq` (minimal API calls)

**Key optimizations:**
- `kubectl get pods -A -o json` fetched once and reused across ~6 sections
- `kubectl get nodes -o json` fetched once and reused across ~4 sections
- ~15 independent kubectl calls run concurrently in Phase 2
- Warning events deduplicated by reason (grouped with counts) to reduce noise
- Deployments and Argo Rollouts filtered: only active (replicas > 0) shown, zero-scale summarized as count
- Argo Rollouts: only non-healthy rollouts listed individually, healthy summarized as count

**Report sections in order:** Quick Summary, Cluster Overview, Nodes, Node Resource Allocation, Cluster-wide Resource Totals, Actual Resource Usage (kubectl top), Resource Summary, Workload Readiness (Deployments, StatefulSets, DaemonSets, Argo Rollouts, Istio sidecar count), Pods without limits/requests, Top memory consumers, Top restarts, Warning events (deduplicated), Problem pods, Storage classes, PDBs, LimitRanges, Quotas, Network Policies, Taints, K3s config.