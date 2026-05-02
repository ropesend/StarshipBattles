# Agent Delegation System

File-based inter-agent request system. Claude Code writes review/analysis
requests; the daemon dispatches them to OpenCode; OpenCode produces reports.

> **Paths in this doc.** All `pending_review_requests/`, `in_progress_review_requests/`, `completed_review_requests/`, and `local/` paths are relative to `AgentCoordination/opencodereview/` (the directory containing this file). Helper scripts at `Tools/agent_coordination/` are referenced by their full repo-relative path.

## Architecture

```
┌──────────────┐     writes request      ┌──────────────┐     opencode run     ┌──────────────┐
│  Claude Code  │ ───────────────────────→│   Daemon     │ ────────────────────→│   OpenCode   │
│              │    pending_review_       │ (5 workers)  │  passes REVIEW_DIR   │             │
│  /claude-    │    requests/             │              │                     │  writes:     │
│  delegate-   │                         │ manages:     │                     │  report.md   │
│  review      │                         │ pending→     │                     │  result.json │
│             │                         │ in_progress→ │                     │             │
│              │ ←── reads results ──────│ completed    │ ←───────────────────│             │
└──────────────┘   completed_review_     └──────────────┘                     └──────────────┘
                   requests/
```

**Trust boundary.** `pending_review_requests/` is a trusted-local automation queue.
The daemon invokes OpenCode with `--dangerously-skip-permissions`, so request
content is effectively a privileged prompt. Only trusted local agents
(`claude-code`, `codex`) and the project owner should write to this directory.
Do not expose it to untrusted users or remote sources.

## Directories

| Directory | Purpose |
|-----------|---------|
| `pending_review_requests/` | New requests waiting to be processed |
| `in_progress_review_requests/` | Requests currently being processed |
| `completed_review_requests/` | Finished requests with result links |
| `Reviews/results/` | Review output: `report.md`, `result.json`, agent findings |

## Starting the Daemon

In a separate terminal:

```powershell
.\Tools\agent_coordination\Start-ReviewDaemon.ps1
```

Or directly with custom options:

```bash
python Tools/agent_coordination/review_daemon.py --max-workers 5 --timeout 1800 --orphan-age 3600
```

| Flag | Default | Description |
|------|---------|-------------|
| `--poll-interval` | 3 | Seconds between scans |
| `--timeout` | 1800 | Max seconds per opencode run (30 min — reviews complete in 2-5 min) |
| `--max-workers` | 5 | Concurrent review workers |
| `--orphan-age` | 3600 | Seconds before stuck in_progress is declared orphaned (2× timeout) |
| `--shutdown-timeout` | 60 | Seconds to wait for in-flight workers on Ctrl+C |

OpenCode reviews typically complete in 2–5 minutes; the 30-minute timeout ceiling
catches hung subprocesses with headroom. The orphan age of 60 minutes (2× timeout)
ensures a legitimate review that started moments before a daemon crash won't be
declared orphaned on restart.

## Lifecycle

The daemon owns request lifecycle. OpenCode owns content.

```
pending/                in_progress/            completed/
   │  daemon picks up       │  opencode exits       │
   │  moves → in_progress   │  reads result.json    │
   │  creates review_dir    │  moves → completed    │
   │  launches opencode     │                       │
   ▼                       ▼                       ▼
 req_XXX.md  ──────────→  req_XXX.md  ──────────→  req_XXX.md
                         Status: in-progress      ## Results
                         PickedUp: ...            **Status:** completed
                                                  **Report:** Reviews/results/.../report.md
                                                  **Findings:** N total
```

**Orphan recovery:** On startup, the daemon scans `in_progress/`. Requests
older than `--orphan-age` are marked failed and moved to `completed/`.
Younger requests are retried (moved back to `pending/`).

## Request File Format

Requests are created via `Tools/agent_coordination/create_review_request.py`
with a JSON payload file:

```bash
python Tools/agent_coordination/create_review_request.py --payload-file review_payload.json
```

Payload schema:
```json
{
  "type": "code",
  "title": "Combat engine refactor review",
  "scope": "game/simulation/combat/ — all changed files",
  "instructions": "Check for layer violations, error handling, and dead code",
  "context": "Refactored damage calculation in PR #42",
  "expected_deliverable": "Report + result.json sidecar.",
  "parent": "req_20260502_010000_abcdef",
  "requester": "claude-code"
}
```

Only `type`, `title`, `scope`, and `instructions` are required. The helper
prints the request ID to stdout; the request file is written atomically to
`pending_review_requests/`.

### Option B completion contract

When OpenCode finishes, the daemon writes a `## Results` section at EOF:

- The stale top-level `**Status:** in-progress` line (set during pickup) is
  removed.
- The `**PickedUp:** <ts>` line is retained (lifecycle metadata, outside
  `## Results`).
- Any pre-existing `## Results` section is replaced defensively.
- Fields appear in order: `Status`, `Completed`, `Report`, `Findings`,
  `FailureReason` (last two only when applicable).
- `Report` values are raw paths — no backtick wrapping.

```markdown
# Review Request: <title>
**Request ID:** req_<YYYYMMDD>_<HHMMSS>_<6hex>
**Review Type:** code | plan | architecture | tests | security | performance | consistency | general | custom
**Parent:** req_<parent_id>        (follow-up reviews only)
**Created:** <ISO timestamp>
**Requester:** claude-code

## Scope
<files, directories, documents, or conceptual description>

## Instructions
<what to look for, questions to answer, evaluation criteria>

## Context
<why this review, what changed, related systems>

## Expected Deliverable
<what kind of output>
```

### Follow-Up Reviews

A follow-up is a normal request with a `**Parent:**` field pointing at a
prior completed request.

```markdown
# Review Request: Follow-up: Combat engine review
**Request ID:** req_20260502_070000_abcdef
**Review Type:** code
**Parent:** req_20260502_063000_a1b2c3
**Created:** 2026-05-02T07:00:00Z
**Requester:** claude-code

## Scope
- `game/simulation/combat/damage.py` — file with fixes applied

## Instructions
Verify these findings from the parent review:
- CRIT-001 — fixed null pointer in damage calculation
- MAJ-003 — added missing edge case handling for shields

## Context
Fixes applied based on parent review req_20260502_063000.
```

The resulting `report.md` will include a **Verification Matrix** and the
`result.json` will include a `verification` map.

## Sidecar Format (result.json)

Written by OpenCode, read by the daemon:

```json
{
  "request_id": "req_20260502_070000",
  "review_dir": "Reviews/results/2026-05-02_070000_general_combat-refactor_req-20260502_070000",
  "report_path": "Reviews/results/2026-05-02_070000_general_combat-refactor_req-20260502_070000/report.md",
  "findings": {
    "critical": 2,
    "major": 8,
    "minor": 10,
    "info": 3
  },
  "completed_at": "2026-05-02T07:30:00Z",
  "parent_request_id": "req_20260502_063000",
  "verification": {
    "CRIT-001": "resolved",
    "MAJ-003": "partially-resolved"
  }
}
```

If the sidecar contains an `"error"` key, the request is moved to
`completed/` with `Status: failed` and `FailureReason: <error>` regardless
of the opencode exit code:

```json
{
  "request_id": "req_20260502_070000",
  "error": "description of what went wrong"
}
```

## Parallel Processing

The daemon uses a `ThreadPoolExecutor` with configurable worker count.
Each worker claims a request via an atomic lock file
(`req_<id>.<worker_pid>.lock`). Stale locks from dead processes are
automatically cleaned up.

Queue depth is monitored — when pending exceeds `max_workers * 5`, the
daemon logs a warning.

## Lock Files

Each worker claims a request atomically via a lock file in `pending/`:
`req_<id>.md.<pid>.lock`. Lock files are PID-keyed and serve two purposes:

- **Race prevention (within a single daemon):** Two worker threads scanning
  simultaneously cannot claim the same request — `FileExistsError` on
  `touch(exist_ok=False)` ensures exactly one wins. **This protection is
  scoped to a single daemon process.** Locks include the daemon's PID in
  their filename, so two daemons running against the same queue would each
  see the other's locks as foreign and could double-claim. The PID guard
  in `run_daemon` (`--force` to override) prevents accidentally starting a
  second daemon. Multi-daemon operation is intentionally outside the safe
  operating model.
- **Crash recovery:** On startup, `_sweep_stale_locks()` removes lock
  files owned by dead PIDs. Lock files from dead processes are also cleaned
  up lazily when a subsequent claim attempt encounters them.

## Checking Results

Read the completed request file:

```bash
ls AgentCoordination/opencodereview/completed_review_requests/
cat AgentCoordination/opencodereview/completed_review_requests/req_XXX.md
```

The file contains the report path and findings summary in its
`## Results` section.

**Failure path:** Failed reviews have an `"error"` key in `result.json` and
may not produce a `report.md`. Consumers traversing `Reviews/results/` must
not assume `report.md` exists. Always check `result.json` first.

## Adding Support for Other Agents

Any agent can write to `pending_review_requests/`. Only the file format
matters. To invoke OpenCode processing manually (no daemon):

```bash
opencode run "Load the ocode-review-request skill. Process the request at AgentCoordination/opencodereview/pending_review_requests/req_XXX.md. Use review directory: Reviews/results/<custom_dir>/. Write result.json to: Reviews/results/<custom_dir>/result.json"
```
