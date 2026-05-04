# Agents: Bash plugin only

This document applies **only** to the release artifact **`kubectl-kontext`** (the single-file Bash kubectl plugin). It does **not** govern the Go port, MCP server, or user scripts elsewhere in the repo.

**Working on something else?**

| Area | Where to look |
|------|----------------|
| Go implementation (`cmd/`, `internal/`) | `CLAUDE.md`, `go.mod` |
| MCP / Claude Desktop (`local_mpc_setup/`) | `local_mpc_setup/setup_instructions.md`, `.cursor/rules/mcp-server-setup.mdc` |
| Human-facing install and piping examples | `Readme.md` |

---

## 1. Project overview (Bash plugin)

The Bash plugin **`kubectl-kontext`** generates a structured Kubernetes cluster assessment report for AI consumption. For a wider repo picture, see **`CLAUDE.md`**.

---

## 2. Repository map (relevant to this doc)

```
kubectl-kontext          Bash plugin — primary edit target for tasks covered here
Makefile                 archives, sha, release, clean; other targets may touch Go/MCP
plugins/kontext.yaml     Krew manifest — version and sha256 per platform
Readme.md                Install instructions and usage examples
```

Release tarballs and checksums for the **Bash script** live at the repository root. The repo also contains **Go** sources and **`local_mpc_setup/`** (Python MCP); those are out of scope for the rules below unless you are explicitly tasked there—then use the table at the top.

---

## 3. Architecture principles (Bash plugin)

- **All plugin logic lives in one file:** `kubectl-kontext`. Do not add second sources of truth for the Bash release path.
- **Three-phase structure must be preserved:**
  1. Phase 1 — parallel fetch of heavy JSON (`pods`, `nodes`, `events`)
  2. Phase 2 — parallel fetch of lightweight resources
  3. Phase 3 — sequential assembly from `$TMPDIR` cache
- **New kubectl calls belong in Phase 2** (if independent) or Phase 1 (if the data is reused across multiple sections).
- **Phase 3 reads only from `$TMPDIR`** — no new `kubectl` calls in the assembly block.
- **No new hard dependencies for the Bash plugin.** `jq` and `kubectl` are the only permitted tools. Do not introduce Python, Ruby, or other interpreters **into `kubectl-kontext`** (the repo’s MCP code is separate).
- **Output is plain text to stdout.** Do not add flags, config files, or persistent state **in the Bash plugin**.

---

## 4. Coding conventions

- `set -euo pipefail` is active — every command must either succeed or explicitly handle failure.
- Optional resources use `|| echo '{"items":[]}' > file` or `|| echo fallback` to prevent hard exits.
- `jq` filters are inline heredoc-style strings passed directly to `jq -r '...'`; keep them self-contained.
- Resource parsing uses locally-defined `jq` functions (`parse_cpu`, `parse_mem`, `fmt_cpu`, `fmt_mem`); reuse these patterns when adding resource calculations — do not inline duplicate logic.
- Section headers use `## SECTION NAME` (uppercase, two hashes) for AI parseability — match this exactly.
- `column -t` is applied after `@tsv` output for tabular sections; maintain this pattern.
- `head -N` is used to cap long lists (e.g., top 10, top 30) — apply the same cap to any new list section.
- Background jobs use named `pid_*` variables only in Phase 1; Phase 2 uses a bare `wait` after all jobs.
- *(inconsistent - verify before applying)* Some sections cache to `.txt`, others to `.json`; match the format to whether the consumer is `cat` (text) or `jq` (JSON).

---

## 5. Canonical development commands

**Run:**
```bash
./kubectl-kontext          # run directly against current kubeconfig context
kubectl kontext            # run as kubectl plugin (requires script in PATH)
```

**Install to PATH:**
```bash
cp kubectl-kontext /usr/local/bin/ && chmod +x /usr/local/bin/kubectl-kontext
# or
export PATH="$PATH:$(pwd)"
```

**Build release tarballs (Bash artifact):**
```bash
make archives              # produces kubectl-kontext-darwin-arm64.tar.gz etc.
make sha                   # prints sha256 per platform
make release               # archives + sha
make clean                 # removes *.tar.gz
```

**Lint / typecheck / test:** Not defined for the Bash plugin. No test suite exists.

---

## 6. Validation workflow

No automated test or lint pipeline is defined. For **Bash plugin** changes, the manual validation sequence is:

1. **Syntax check:** `bash -n kubectl-kontext` — must produce no errors.
2. **Dry run:** `./kubectl-kontext` against a real or local cluster — inspect output for malformed sections.
3. **Help flag:** `./kubectl-kontext --help` — must exit 0 and print usage.
4. **Dependency guard:** temporarily rename `jq` or remove it from PATH; script must exit with the expected error message.
5. **Build check:** `make archives` — must produce tarballs without error.

There is no CI active (the workflow file is disabled). All validation is local.

---

## 7. Definition of done

A **Bash plugin** change is complete when:

- `bash -n kubectl-kontext` passes with no syntax errors
- `./kubectl-kontext --help` exits cleanly
- Output from `./kubectl-kontext` includes all expected `## SECTION NAME` headers with no malformed or empty blocks introduced by the change
- The three-phase structure is intact (Phase 1 → Phase 2 → Phase 3)
- `make archives` succeeds if the Krew manifest or Makefile was touched
- The human has been given a plain summary of what changed and why

---

## 8. Safety boundaries

**Autonomous** (no confirmation needed):
- Edit logic inside `kubectl-kontext` that adds, modifies, or fixes report sections
- Fix `jq` filter errors or shell quoting issues
- Update section headers or output formatting
- Run `bash -n kubectl-kontext` and `./kubectl-kontext --help`
- Run `make archives` or `make clean`

**Ask first** (confirm with human before proceeding):
- Changing the three-phase execution structure
- Adding a new hard dependency for the Bash plugin (anything beyond `jq`, `kubectl`, standard POSIX utilities)
- Modifying `plugins/kontext.yaml` (version bump, sha256 update, platform changes)
- Updating `Makefile` targets or platform list
- Re-enabling or modifying `.github/workflows/release-on-tag.yml.disabled`

**Never:**
- Commit or stage `report.md`, `computev2-ovh-*.md`, or any file containing real cluster data
- Add a `.gitignore` entry that would silently suppress cluster report files without explicit human instruction
- Push to remote or create releases without explicit instruction
- Modify `plugins/kontext.yaml` sha256 values without running `shasum -a 256` on the actual artifact
- Introduce persistent state, config files, or side effects outside `$TMPDIR` **inside the Bash plugin**

---

## 9. Recommended agent workflow

For **Bash plugin** tasks, follow this sequence:

1. **Inspect** — read `kubectl-kontext` in full; skim `Readme.md` / `CLAUDE.md` if you need repo context
2. **Understand** — identify which phase and which section the change affects
3. **Plan** — determine the minimal edit; check that it respects phase boundaries and conventions
4. **Confirm if needed** — if the change touches structure, dependencies, or release artifacts, state the plan and ask before editing
5. **Implement** — make the targeted change; reuse existing `jq` helper functions where applicable
6. **Validate** — run the sequence in §6 (syntax check → dry run → help flag → build check)
7. **Summarize** — report what was changed, which sections are affected, and the validation results
