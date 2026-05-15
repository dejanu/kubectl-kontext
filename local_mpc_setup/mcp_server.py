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
        "For structured critical-issues analysis, use the "
        "analyze_cluster_critical_issues prompt."
    ),
)

CLUSTER_ANALYSIS_PROMPT = """\
Analyze the current Kubernetes cluster and produce a structured assessment \
of critical issues and actionable recommendations.

## Required steps

1. Call the `get_current_context` tool and note the active context name.
2. Call the `get_cluster_report` tool and base every finding on that report only \
(do not invent or assume cluster state).

## Report sections to review

Use these `## SECTION` headers from the report:

- `## QUICK SUMMARY (for AI)` — start here for high-level signals
- `## PROBLEM PODS`, `## RECENT WARNING EVENTS`, `## TOP 10 POD RESTARTS`
- `## WORKLOAD READINESS` — Deployments, StatefulSets, DaemonSets, Argo \
Rollouts, HPAs at max replicas
- `## NODES`, `## NODE RESOURCE ALLOCATION`, `## CLUSTER-WIDE RESOURCE TOTALS`, \
`## ACTUAL RESOURCE USAGE`, `## RESOURCE SUMMARY`
- `## PODS WITHOUT RESOURCE LIMITS`, `## PODS WITHOUT RESOURCE REQUESTS`
- `## POD DISRUPTION BUDGETS`, `## RESOURCE QUOTAS`, `## NETWORK POLICIES`, \
`## NODE TAINTS`

## Severity guidance

Classify findings as:

- **P0 (critical)** — immediate risk: NotReady nodes, CrashLoopBackOff or \
long-pending pods, workloads not ready, data-loss or outage risk
- **P1 (high)** — significant degradation: HPAs at max replicas, high restart \
counts, severe recurring warning events, dangerous resource overcommit
- **P2 (medium)** — hygiene or capacity risk: missing limits/requests on \
important workloads, PDB gaps, quota pressure, notable but non-outage issues

Prioritise: pending/failed pods, HPAs at max, high restarts, resource \
overcommitment, and missing limits on production-impacting workloads.

## Output format (markdown)

Use exactly this structure:

# Cluster: <context name from get_current_context>

## Executive summary
(2–4 sentences on overall health and top risks)

## Critical issues
| Severity | Area | Finding | Evidence (section + detail) |
|----------|------|---------|------------------------------|
(list up to 10 rows; if more exist, add a line: "…and N additional issues")

## Recommendations
| Priority | Issue | Action | Risk if ignored |
|----------|-------|--------|-----------------|
(one row per critical/high issue; concrete, actionable steps)

## Observations (non-critical)
(optional bullets for lower-priority or informational items)

## Next steps
(ordered checklist, maximum 5 items)

## Guardrails

- If a report section is empty or metrics-server data is missing, state that \
explicitly; do not fabricate usage or capacity numbers.
- Cite evidence as the report section name plus the specific pod, namespace, \
node, or workload involved.
- Do not suggest destructive kubectl commands (delete, drain, scale-to-zero) \
unless the user explicitly asks.
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
    name="analyze_cluster_critical_issues",
    description=(
        "Analyze the current Kubernetes cluster: fetch report via tools, "
        "list critical issues (P0–P2), and provide prioritized recommendations."
    ),
)
def analyze_cluster_critical_issues() -> str:
    """Analyze cluster health and return critical issues with recommendations."""
    return CLUSTER_ANALYSIS_PROMPT


if __name__ == "__main__":
    mcp.run()
