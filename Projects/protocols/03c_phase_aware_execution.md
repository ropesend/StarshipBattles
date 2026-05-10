# PROTOCOL 03c: Phase-Aware Execution with Cumulative Review (Single Project)
**Role:** Project Phase Coordinator

## Configuration

| Variable | Value |
|----------|-------|
| ACTIVE_DIR | Projects/active_projects |
| WORKTREE_BASE | .worktrees/phases/{PROJ-ID} |
| INTEGRATION_WORKTREE_BASE | .worktrees/integration |
| REVIEW_WORKTREE_BASE | AgentCoordination/opencodereview/local/worktrees |
| BRANCH_PREFIX | proj/{PROJ-ID} |
| PROJECT_BRANCH | proj/{PROJ-ID}/main |
| PHASE_BRANCH_FORMAT | proj/{PROJ-ID}/{phase-id} |
| TEMP_BRANCH_FORMAT | tmp/{PROJ-ID}/integrate-{phase-id}-{shortsha} |
| SESSION_DIR | .agent_reports/proj-phase-session/{PROJ-ID}/{phase-id} |
| STATE_FILE | Projects/active_projects/{PROJ-ID}/phase_state.json |
| LEDGER_VIEW | Projects/active_projects/{PROJ-ID}/findings_ledger.md |
| MANIFEST | Projects/active_projects/{PROJ-ID}/manifest.md |
| BUFFER_DEPTH_DEFAULT | 0 |
| OPT_IN_MARKER | "**Execution Protocol:** 03c-phase-aware-execution" in plan.md |

---

**Goal:** Execute a single project's phases with mid-project quality gates,
limited intra-project parallelism, and SHA-pinned cumulative reviews.
Phase dependencies declared at planning time drive execution order. Reviews
fire at every phase boundary against the project branch tip and cover all
phases committed up to that SHA. Independent phases execute in parallel
worktrees; multi-parent phases wait for all parents to be `verified`.

**CRITICAL CONSTRAINTS:**
- All execution work happens on the project branch (`proj/{PROJ-ID}/main`)
  and its phase children. Never on `main`. Project merges to `main` only
  after the rigorous final audit gate passes.
- A phase may not start until eligibility rules are satisfied:
  - Single-parent + `buffer_depth: 0` (default): parent must be `verified`.
  - Single-parent + `buffer_depth: 1` (override): parent `committed` AND
    every ancestor at distance ≥ 2 `verified`.
  - Multi-parent: ALL parents `verified`.
- Each phase completion fires exactly one cumulative review covering all
  phases committed up to the project tip SHA at dispatch time.
- `phase_state.json` is the authoritative state. Markdown views (phase
  checklists, manifest.md, findings_ledger.md) are generated from it.
- Phase workers own only their phase checklist, code, tests, and session
  file. Coordinator (this protocol) owns plan.md, manifest.md, state file,
  findings ledger.
- Reviews are SHA-pinned via the daemon's detached-worktree mode.
  Numeric "phase 1..N" wording is human shorthand only — machine
  semantics use `coverage_set` (set of phase IDs) at a specific
  `project_tip_sha`.

---

## Prerequisites

- The project's `plan.md` contains the opt-in marker
  `**Execution Protocol:** 03c-phase-aware-execution`.
- `phase_state.json` exists at `Projects/active_projects/{PROJ-ID}/`.
  It is created by `claude-proj-start`.
- Each phase checklist (`phase_<id>_checklist.md`) declares
  `**Depends on:**`, `**Review Mode:**`, and (recommended) `**Files (planned):**`.
- The project branch `proj/{PROJ-ID}/main` exists. If this is the first
  execution session, the coordinator creates it from `main`'s tip on
  startup and commits the initial planning artifacts to it.
- `findings_ledger.md` exists (an empty template is fine).

Projects without the opt-in marker fall through to legacy
[03a](03a_continue_working.md) — DO NOT silently apply 03c to them.

---

## Coordinator State

The state file is the single source of truth. `phase_dag.py` /
`pending_reviews.py` are the read paths; `phase_complete.py` /
`spawn_phase_worker.py` / `scrap_phase.py` are the write paths.

```text
phase_state.json
├── schema_version: 1
├── project_id, project_branch, execution_protocol
├── buffer_depth (0 default; 1 requires reason)
├── phases: {<phase_id>: {depends_on, review_mode, planned_files,
│                          status, phase_branch, phase_base_sha,
│                          phase_head_sha, merged_into_project_at_sha,
│                          review_request_id, verifying_review_id,
│                          review_dispatch_failed, scrap_history}}
├── reviews: {<request_id>: {review_sequence, project_tip_sha,
│                             coverage_set, focus_phase, review_mode,
│                             dispatched_at_utc, result_status,
│                             result_path, supersedes, superseded_by}}
├── findings: {<finding_id>: {fingerprint, source_review_id, source_phase,
│                              severity, summary, status,
│                              verifying_review_id, deferred_until_phase,
│                              ...}}
└── audit: {final_audit_request_id, final_audit_status,
            merge_to_main_sha, merge_to_main_at_utc}
```

Phase status enum: `not_started → in_progress → committed → under_review →
verified` (or `scrapped` from any state). The human-readable phase
checklist mirrors this with compatibility-preserving strings:
`Complete (Committed)`, `Complete (Under Review)`, `Complete (Verified)`,
`Scrapped`.

---

## Concurrency Limits

- One phase worker per phase at a time (single worktree at the standard
  path; spawn refuses if a worktree already exists).
- Up to `MAX_WORKERS=5` concurrent OpenCode reviews (daemon limit).
- Up to 3 concurrent live phase worktrees per project recommended (matches
  03b's per-project worker cap). If the DAG would allow more, hand the
  coordinator the eligible-set and let it pick the highest-leverage three.
- File-conflict serialization: among DAG-eligible phases with overlapping
  `planned_files`, only the lexicographically earliest phase_id is
  reported eligible; others block until it advances.

---

## Execution Procedure

### Step 1: Initialize

1. Verify `plan.md` has the opt-in marker. If absent: stop; route to 03a.
2. Read `phase_state.json`; if missing, fail with operator instruction
   to run `claude-proj-start` first.
3. If `proj/{PROJ-ID}/main` does not exist: create it from `main`'s tip
   and commit the planning artifacts (plan.md, phase_<id>_checklist.md
   files, manifest.md skeleton, phase_state.json) onto it.

### Step 2: Compute eligible phases

```bash
python Projects/scripts/phase_dag.py {PROJ-ID} eligible
python Projects/scripts/phase_dag.py {PROJ-ID} status
```

Surface eligible set, current status of every phase, and (when
`buffer_depth: 1`) the "phases built on unverified parents" counter.

### Step 3: Spawn or continue

For each eligible phase the coordinator decides to run now:

```bash
python Projects/scripts/spawn_phase_worker.py {PROJ-ID} {phase-id}
```

This:
- Verifies eligibility (refuses otherwise).
- Creates phase branch from project tip if missing.
- Adds a worktree at `.worktrees/phases/{PROJ-ID}/{phase-id}/`.
- Writes worker context to
  `.agent_reports/proj-phase-session/{PROJ-ID}/{phase-id}/context.md`.
- Sets phase status to `in_progress` in `phase_state.json`.

If the DAG has only one eligible phase and no live siblings, the
coordinator may continue work in the project worktree directly without
spawning — same lifecycle, no extra worktree.

### Step 4: TDD inner loop (delegates to 03a)

The phase worker runs the autonomous TDD loop per
[03a](03a_continue_working.md). Phase workers must NOT edit:
- `plan.md`
- `manifest.md`
- `phase_state.json`
- `findings_ledger.md`

…or any other phase's `phase_<id>_checklist.md`. Their write surface is:
- their own `phase_<id>_checklist.md`,
- code and tests,
- their session file under `SESSION_DIR`.

### Step 5: Lookback hook

At natural pauses inside the inner loop, the worker (and coordinator) run:

```bash
python Projects/scripts/pending_reviews.py {PROJ-ID}
```

If a completed review surfaces unaddressed findings on an ancestor:
- The worker checkpoints WIP and surfaces the finding to the coordinator.
- The coordinator handles remediation per Step 7. Phase workers do NOT
  remediate other phases.

### Step 6: Phase complete

Worker (or coordinator on the worker's behalf) runs:

```bash
python Projects/scripts/phase_complete.py {PROJ-ID} {phase-id} \
    --repo .worktrees/phases/{PROJ-ID}/{phase-id}
```

Atomic-ish sequence:
1. `validate_phase.py` (legacy validator, must pass).
2. Regression tests (`pytest tests/ --testmon`, must pass).
3. Commit phase branch (`{PROJ-ID} phase {phase-id} complete: ...`).
4. Regenerate `manifest.md` from current SHAs.
5. **Temp-integration merge** into project branch:
   - Create `tmp/{PROJ-ID}/integrate-{phase-id}-{shortsha}` from project tip.
   - Merge phase branch into temp.
   - Run validation+tests on temp (already passed in step 2; rerun is a sanity check).
   - **Green:** fast-forward project branch to temp commit. Delete temp branch + worktree.
     Set phase status to `committed`. Record `phase_head_sha` and
     `merged_into_project_at_sha` in state.
   - **Red:** keep phase branch, delete temp, leave phase status as `in_progress`.
     Exit non-zero.
6. **Dispatch cumulative review** (skipped if `--remediation`):
   - Build payload with `checkout` (project_branch + tip SHA + worktree
     path) and `coverage` (project_id, review_sequence, project_tip_sha,
     coverage_set, focus_phase, review_mode).
   - Write payload to
     `AgentCoordination/opencodereview/local/request_payloads/`.
   - Call `Tools/agent_coordination/create_review_request.py --payload-file <p>`.
   - Record review in state. Set phase status to `under_review`.
7. **Partial-state detection:** if the commit succeeds but the review
   dispatch fails, set `review_dispatch_failed: true` on the phase and
   leave `review_request_id` null. Operator must resolve.

### Step 7: Reconcile / verify / remediate

When a review completes (visible via `pending_reviews.py` →
`completed_review_requests/`):

1. Coordinator reads the review's `result.json` sidecar.
2. For each finding:
   - Default status: `open`.
   - Coordinator triages each finding into one of:
     `addressed_pending_review`, `verified` (only via a later cumulative
     review), `deferred_until_phase`, `wontfix_with_rationale`,
     `superseded`.
   - Findings move into the ledger view automatically (the JSON state is
     authoritative; the markdown view is regenerated on demand).
3. If any finding is `addressed_pending_review`:
   - Apply the fix in the originating phase's worktree (or, if the issue
     spans phases, on the project branch).
   - Re-run `phase_complete.py {PROJ-ID} {phase} --remediation`. This
     commits the fix and merges into the project branch but does NOT
     dispatch a fresh review — the next phase's cumulative review will
     re-cover the remediated work.
4. **Scrap-and-restart:** if remediation forces a too-large change in a
   descendant phase, the coordinator runs:
   ```bash
   python Projects/scripts/scrap_phase.py {PROJ-ID} {phase-id} --reason "..."
   # or, when descendants are also too far gone:
   python Projects/scripts/scrap_phase.py {PROJ-ID} {phase-id} --reason "..." --cascade
   ```
   By default, descendants are paused (status reset to `not_started`,
   logged in `scrap_history`). With `--cascade`, descendants are scrapped
   recursively (deepest first).
5. When a review returns clean (no findings outside the ledger), every
   phase in `coverage_set` is marked `verified` with `verifying_review_id`
   set. Earlier reviews whose `coverage_set` is a strict subset are
   automatically superseded.

### Step 8: Project complete & merge to main

When all phases reach `verified` (or terminal-by-ledger state), the
coordinator runs the final audit gate per `claude-proj-audit`:

`validate_audit_ready.py` hard-fails if ANY of:
1. A finding has status `open` or `addressed_pending_review`.
2. A `deferred_until_phase` finding's target phase is ≤ committed coverage and unresolved.
3. The latest clean review's `coverage_set` does not include all non-skipped phases.
4. The project branch tip SHA differs from the audited SHA.

On clean audit:
- Merge `proj/{PROJ-ID}/main` into `main`.
- Record `audit.merge_to_main_sha` and `audit.merge_to_main_at_utc`.
- Hand off to `claude-proj-archive`.

Until clean audit: the project may not merge to main.

---

## Worker Prompt Template

When the coordinator delegates a phase to a worker (or runs it inline as a
single agent), the prompt should include:

```text
You are working on {PROJ-ID} phase {phase-id}.

- Worktree: .worktrees/phases/{PROJ-ID}/{phase-id}/
- Phase branch: proj/{PROJ-ID}/{phase-id} (branched from proj/{PROJ-ID}/main at {phase_base_sha})
- Project branch: proj/{PROJ-ID}/main
- Sibling phases live (if any): {list}
- Buffer depth: {0 or 1}

You may write only:
- Your phase_{phase-id}_checklist.md
- Code and tests
- .agent_reports/proj-phase-session/{PROJ-ID}/{phase-id}/

You may NOT write:
- plan.md, manifest.md, phase_state.json, findings_ledger.md
- Other phases' checklists

Read first (per 03a):
1. docs/01_ARCHITECTURE.md
2. docs/02_PATTERNS.md
3. docs/03_CONVENTIONS.md
4. Task-specific docs from docs/README.md
5. .agent_reports/proj-phase-session/{PROJ-ID}/{phase-id}/context.md
6. Projects/active_projects/{PROJ-ID}/phase_{phase-id}_checklist.md

Run TDD per Projects/protocols/03a_continue_working.md. When the phase is
complete and tests pass, run:
    python Projects/scripts/phase_complete.py {PROJ-ID} {phase-id} \
        --repo .worktrees/phases/{PROJ-ID}/{phase-id}

If you find an issue with an ancestor phase that needs remediation, do NOT
fix it in this worktree. Surface it to the coordinator.
```

---

## Error Handling

| Error | Recovery |
|---|---|
| `validate_phase.py` fails | Phase stays `in_progress`. Worker fixes the checklist or implementation; reruns. |
| Regression tests fail | Same as above. |
| Temp-integration merge conflict | Phase stays `in_progress`. Phase branch needs manual rebase from project tip; usually a sign of file-conflict misdetection. |
| Temp-integration tests fail (after sibling-merged project tip) | Phase stays `in_progress`. Phase branch needs to integrate sibling changes; rebase phase branch onto project tip and rerun. |
| Review dispatch fails after commit | `review_dispatch_failed: true` set on phase. `pending_reviews.py` and `phase_dag.py status` flag this. Operator resolves manually (e.g., daemon restart, then redispatch). |
| Daemon crashes mid-review | Daemon-managed worktrees are leaked under `AgentCoordination/opencodereview/local/worktrees/`. Daemon's startup sweeper prunes orphans. The request itself moves to `failed_review_requests/` after orphan-age timeout; operator decides whether to retry. |
| SHA mismatch (project tip moved between dispatch and worker pickup) | Daemon refuses with `result_status: sha_mismatch`. Coordinator dispatches a fresh review at the new tip. |
| Multiple cumulative reviews in flight that complete out of order | Supersession rules in state apply automatically. An older clean review whose `coverage_set` is a strict subset of a newer clean review is marked `superseded_by`. |
| Worker crashes / context overflow | Phase worktree remains; `cleanup_phase_worktrees.py` lists and (with operator OK) prunes. |

---

## Dashboard

For a single project, `phase_dag.py status` is the dashboard. For a
session that spans multiple projects (rare for 03c since 03c is
single-project), 03b's session dashboard pattern still applies and is
unaffected.

Sample output of `phase_dag.py status`:

```text
# PROJ-XX phase status
  phase_1        status=verified           head=abc12345  review=req_2026...  verifying=req_2026...
  phase_2        status=under_review       head=def67890  review=req_2026...
  phase_3        status=in_progress        head=...                                                          
  phase_4        status=not_started        depends_on=[phase_2, phase_3]
```

---

## Relationship to 03a and 03b

- **[03a](03a_continue_working.md)** is the canonical TDD inner loop —
  used unchanged inside 03c's Step 4. 03a remains valid on its own for
  legacy projects (those without the 03c opt-in marker).
- **[03b](03b_parallel_projects.md)** is inter-project parallelism — 03b
  workers run separate projects in parallel, each project optionally
  using 03c internally. 03c does NOT replace 03b; they nest cleanly.

---

## Key Rules

1. **State file is authoritative.** Never reverse-engineer state from
   prose; never edit phase_state.json by hand mid-flight.
2. **Project branch only.** Execution work never lands on main; merges
   only after audit.
3. **Coverage-set semantics.** When you say "verified", you mean "in the
   coverage_set of a clean review" — not "phase number ≤ N".
4. **No review skipping in v1.** `Review Mode: standard | lightweight`.
   `lightweight` still produces a review record.
5. **Phase workers own their lane.** Coordinator owns shared metadata.
   Don't blur this.
6. **Reliability over throughput.** When in doubt, choose the slower,
   more deterministic option. `buffer_depth: 0` default codifies this.
