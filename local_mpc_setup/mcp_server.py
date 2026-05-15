#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.0.0"]
# ///
"""
MCP server for kubectl-kontext

MCP server that wraps the kubectl-kontext plugin
and exposes it as tools to Claude Desktop (or any MCP client).

Run with:  uv run mcp_server.py
"""

import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

SCRIPT = Path(__file__).parent / "kubectl-kontext"

mcp = FastMCP(
    "kubectl-kontext",
    instructions=(
        "Kubernetes cluster assessment tool. Call get_cluster_report to fetch "
        "a full health and capacity report from the current cluster. "
        "Prioritise: pending/failed pods, HPAs at max, high restarts, "
        "resource overcommitment, and missing limits. "
        "For structured analysis, use the analyze_cluster prompt."
    ),
)

ANALYZE_CLUSTER_PROMPT = """\
Analyze the current Kubernetes cluster for critical issues and recommendations.

1. Call `get_current_context` — use the active context in your answer.
2. Call `get_cluster_report` — base every finding on that report only (no guessing).

Prioritise: NotReady nodes, problem/pending pods, workloads not ready, HPAs at max, \
high restarts, overcommit, missing limits. Severity: P0 (outage risk), P1 (degraded), \
P2 (hygiene/capacity).

# Cluster: <context>
## Executive summary (2–4 sentences)
## Critical issues (table: Severity | Area | Finding | Evidence — max 10 rows)
## Recommendations (table: Priority | Issue | Action | Risk if ignored)
## Next steps (≤5 items)

Cite report `## SECTION` names as evidence. State if sections are empty or metrics \
are unavailable. No destructive kubectl unless asked.
"""


@mcp.tool()
def get_cluster_report() -> str:
    """Fetch a full Kubernetes cluster assessment report.

    Runs kubectl-kontext against the current kubeconfig context and returns
    a structured report covering: node status, resource allocation,
    workload readiness (Deployments, StatefulSets, DaemonSets, Argo Rollouts),
    HPAs, problem pods, warning events, storage, and network policies.
    """
    if not SCRIPT.exists():
        return f"kubectl-kontext script not found at {SCRIPT}"
    if not SCRIPT.stat().st_mode & 0o111:
        return f"kubectl-kontext script is not executable: {SCRIPT}"

    result = subprocess.run(
        [str(SCRIPT)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if not result.stdout and result.stderr:
        return f"Error running kubectl-kontext:\n{result.stderr}"
    return result.stdout


@mcp.tool()
def get_current_context() -> str:
    """Return the active kubectl context and list all available contexts."""
    current = subprocess.run(
        ["kubectl", "config", "current-context"],
        capture_output=True,
        text=True,
    )
    contexts = subprocess.run(
        ["kubectl", "config", "get-contexts", "--no-headers", "-o", "name"],
        capture_output=True,
        text=True,
    )
    lines = [f"Current: {current.stdout.strip()}"]
    if contexts.stdout.strip():
        lines.append("Available contexts:")
        for ctx in contexts.stdout.strip().splitlines():
            marker = " *" if ctx.strip() == current.stdout.strip() else "  "
            lines.append(f"{marker} {ctx.strip()}")
    return "\n".join(lines)


@mcp.tool()
def switch_context(context_name: str) -> str:
    """Switch the active kubectl context.

    Use get_current_context first to list available contexts,
    then call this with the desired context name.
    """
    result = subprocess.run(
        ["kubectl", "config", "use-context", context_name],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"Failed to switch context: {result.stderr.strip()}"
    return result.stdout.strip()


@mcp.prompt(
    name="analyze_cluster",
    description="Analyze cluster: fetch report, list critical issues (P0–P2), recommendations.",
)
def analyze_cluster() -> str:
    """Analyze cluster health: critical issues and recommendations."""
    return ANALYZE_CLUSTER_PROMPT


if __name__ == "__main__":
    mcp.run()
