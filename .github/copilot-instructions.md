# Copilot Instructions for `kubectl-kontext`

## Architecture Overview
- This repository is a **single-script monolith CLI plugin**:
- Runtime logic lives in `kubectl-kontext` (Bash script).
- Packaging/release helpers live in `Makefile` and `plugins/kontext.yaml`.
- The script is structured as a **3-phase pipeline**:
- Phase 1: fetch heavy cluster JSON once in parallel (`pods`, `nodes`, `events`) and cache to temp files.
- Phase 2: run independent lightweight `kubectl` calls in parallel and cache outputs.
- Phase 3: assemble a single ordered markdown report from cached data (plus a small number of direct informational `kubectl` calls).
- Data processing is shell orchestration + `jq` transforms; there is no internal service boundary, API layer, or multi-package architecture.

## Coding Conventions
- Follow Bash strict mode exactly: `set -euo pipefail`.
- Use Bash-specific conditionals and defaults already used in the script:
- `[[ ... ]]` for tests.
- `${1:-}` style for optional positional args.
- Quote variable expansions and paths (for example `"$TMPDIR"`, `"$PODS_JSON"`).
- Keep global/script variables in uppercase snake case (examples: `TMPDIR`, `PODS_JSON`, `NODES_JSON`, `CLUSTER_NAME`).
- Keep the phased structure explicit with section comments (`Phase 1`, `Phase 2`, `Phase 3`) and markdown section headers in output (`## ...`).
- Continue the existing performance pattern:
- expensive `kubectl ... -o json` calls should be cached and reused.
- independent commands should run in background and synchronize with `wait`.
- Keep `jq` filters deterministic and null-safe (`//`, `?`, guarded parsing helpers) as done in existing filters.
- Keep fallback behavior explicit when optional APIs/resources are missing (for example `rollouts`, `hpa`, metrics-server output).

## Module Boundaries
- `kubectl-kontext` is the **only runtime module**. New runtime behavior should be implemented there.
- `Makefile` is for packaging/release tasks (`archives`, `sha`, `clean`) and should not contain runtime report logic.
- `plugins/kontext.yaml` is Krew distribution metadata only (version, URIs, checksums, platform selectors).
- `.github/workflows/release-on-tag.yml.disabled` is release automation metadata and is currently disabled.
- Boundary rules:
- Do not move report-generation logic into `Makefile`, plugin YAML, or workflow files.
- Do not add build/release concerns into runtime report sections.
- Keep data collection and report assembly within the existing 3-phase script flow.

## Testing Guidelines
- Current state in this repo:
- No unit test framework is present.
- No integration/e2e test suite is present.
- No coverage tooling or thresholds are configured.
- A GitHub Actions workflow exists for release packaging only, and it is disabled.
- Until automated tests are added, every change should at least pass manual integration checks:
- `./kubectl-kontext --help`
- `./kubectl-kontext` against a reachable cluster
- Validate behavior when optional features are unavailable (missing metrics-server, missing Rollouts/HPA APIs).
- For changes that alter parsing or report content, verify key sections still render and that fallback paths produce valid output instead of crashing.

## Anti-Patterns to Avoid
- Avoid adding new heavy `kubectl get ... -o json` calls in later report assembly when cached data can be reused.
- Avoid unguarded stderr suppression (`2>/dev/null`) without explicit fallback or user-visible handling; this can hide real failures.
- Avoid duplicating complex parsing logic (for example repeated CPU/memory parsing snippets) when a shared approach can be reused safely.
- Avoid making the single script even more tightly coupled by interleaving unrelated concerns; preserve clear sectioning and phase separation.
- Avoid introducing output wording/heading inconsistencies and typos in generated report text.

## Dependency Guidelines
- Required runtime dependencies (observed):
- `kubectl`
- `jq` (hard requirement; script exits if missing)
- Optional runtime dependencies (observed):
- metrics-server (`kubectl top` sections)
- `claude` CLI (usage examples only, not required for script execution)
- Packaging/distribution constraints from repository files:
- Krew plugin metadata format in `plugins/kontext.yaml` (`apiVersion: krew.googlecontainertools.github.com/v1alpha2`).
- Current packaged targets in `Makefile`: `darwin-arm64` and `linux-arm64`.
- Keep the implementation in Bash + `kubectl` + `jq`; do not add language/framework dependencies unless repository maintainers intentionally change architecture.
