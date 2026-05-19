# Group Execution Protocol — Multi-Machine, Multi-Group Parallel Work

This protocol governs the three group-execution agents (Group A, Group B, Group C)
working in parallel on **separate machines** against the same repository. It is the
single source of truth for git workflow, cross-group coordination, conflict
resolution, path discovery, and codex-consult placement.

The three group-execution prompts
(`Projects/active_projects/Group{A,B,C}_execution_prompt.txt`) defer to this
protocol. If a prompt and this protocol disagree, this protocol wins.

> Last verified: 2026-05-18

---

## 1. Branches and merge model

Each group operates on a dedicated long-lived branch, branched from `main`:

| Group   | Branch      |
|---------|-------------|
| Group A | `group-a`   |
| Group B | `group-b`   |
| Group C | `group-c`   |

Rules:

- **Phase commits land on the group branch only**, never directly on `main`.
- **End-of-project = merge to `main`** (see §3).
- Group branches are re-based onto `main` after every end-of-project merge so
  they stay current.
- `main` is the cross-group source of truth. All cross-group artifact reads go
  through `origin/main`.

## 2. Session start (run once per machine, per session)

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
# Create or sync the group branch
git checkout group-<x> 2>/dev/null \
    || git checkout -b group-<x> origin/group-<x> 2>/dev/null \
    || git checkout -b group-<x>
git rebase main           # keep group branch atop latest main (see §6 if conflicts)
git push --force-with-lease origin group-<x>   # only after a successful rebase
```

Substitute `<x>` with `a`, `b`, or `c`. The `--force-with-lease` is safe because
each group branch has a single writer (the group's agent on a single machine).

## 3. End-of-project: merge group branch into `main`

After all phases close, the codex audit is dispatched, audit-driven extra phases
land, and the project is otherwise ready to mark Complete:

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
git checkout group-<x>
git rebase main                              # resolve any conflicts per §6
git push --force-with-lease origin group-<x>
git checkout main
git merge --no-ff group-<x> -m "Merge group-<x> through PROJ-<N> (end of project)"
git push origin main
git checkout group-<x>
git rebase main                              # bring group branch atop its own merge
git push --force-with-lease origin group-<x>
```

This is the **only** time the group writes to `main`. Phase-level commits never
merge to `main` individually; only end-of-project blocks do. This caps merge
churn at one event per project per group (12 events total).

## 4. After each phase commit

Push immediately:

```bash
git push origin group-<x>
```

Unpushed phase commits are invisible to the other two groups (which fetch
`origin/main` for cross-group reads — but also occasionally fetch other group
branches when investigating collisions). Push every phase, every time.

## 5. Cross-group reads (other groups' plan.md / decisions.md / consults)

Cross-group state is **authoritative on `origin/main`**, not on group branches.
A file on your local group branch is your draft; a file on `origin/main` is the
published state other groups can see.

Before reading another group's artifact:

```bash
git fetch origin main
git show origin/main:Projects/active_projects/PROJ-XXX/plan.md
# Or for multiple files at once, rebase your branch:
git checkout group-<x>
git rebase main
```

When evaluating a sync gate ("is PROJ-454 complete?"), read the dependency
project's `plan.md` from `origin/main`, never from your local working tree.

## 6. Conflict resolution

When `git rebase main` or `git merge` produces conflicts:

### 6.1 Trivial conflicts — resolve directly

- **Whitespace / line endings**: prefer the side that matches repo hooks (LF,
  trailing newline).
- **Append-only logs** (`AgentCoordination/discovered_issues/log.jsonl`):
  concatenate both sides; keep all unique lines.
- **Same-block import additions**: keep both; let `isort`/`ruff` re-order on the
  next commit.
- **Pending doc consolidation files** (see §9): not applicable — each project
  writes a distinct filename.

### 6.2 Non-trivial conflicts — delegate to a subagent

For overlapping production code or shared-test edits, spawn a general-purpose
subagent. Provide:

- The conflicted file's path.
- Both diffs (the rebased commits' changes and main's incoming changes).
- The two relevant project plans (manifest + relevant phase checklist excerpts).
- A directive: "Produce a merge that preserves both projects' intent. If the
  changes are logically incompatible, explain which side should win and why,
  with file:line evidence. Report the resolved file contents; do not write the
  file yourself."

After the subagent reports:

1. Apply the merged version manually (you write the file, not the subagent).
2. Run the targeted pytest for the touched file.
3. Run the full sharded suite before continuing.
4. If sharded fails, iterate: re-spawn the subagent with the failure context.

### 6.3 Forbidden shortcuts

- Never `git checkout --ours` or `--theirs`.
- Never `--strategy-option=ours/theirs`.
- Never delete code you don't understand to make the build pass.
- Never `git push --force` (only `--force-with-lease`, and only against your
  own group branch).

## 7. Waiting protocol — blocked on cross-group dependency

When you hit a cross-group sync gate (e.g., PROJ-450 waiting on PROJ-454/456;
PROJ-459 LOC measurement waiting on PROJ-454; doc consolidation):

1. Update your current project's `plan.md` Current State block:
   `Blocked on <dep>; polling origin/main every 30 minutes.`
2. Commit and push the Blocked annotation so the other groups see your state.
3. Use `ScheduleWakeup` with `delaySeconds=1800` (30 minutes) and a clear reason.
4. On each wake-up:
   - `git fetch origin main`
   - Re-check the gate condition by reading the dependency file from
     `origin/main` per §5.
5. If unblocked: clear the Blocked note (commit + push) and proceed.
6. If still blocked after ~16 wake-ups (≈ 8 wall-clock hours): write a status
   note to `AgentCoordination/Scratchpad/blocked/group-<x>_PROJ-<N>_<UTC-ts>.md`
   describing the gate state, commit your group branch, push, and stop. The
   user/coordinator will intervene. Don't keep polling indefinitely past 8 hours
   — flag it.

While blocked, you may safely:

- Refine the current project's `decisions.md` (no production-code edits).
- Read upstream code state in files the blocked phase will touch (read-only).
- Pre-read the next phase's checklist.
- Run read-only research (LOC measurements that don't depend on the gate, etc.).

While blocked, you may NOT:

- Start any production-code task in the blocked phase.
- Edit cross-group files speculatively.
- Skip the gate and begin the next project — sync gates protect ordering.

## 8. Path discovery — no hardcoded checkout paths

Each agent runs on a different machine with a different checkout path. Hardcoded
paths like `C:\Dev2\StarshipBattles` or `c:\Dev\Starship Battles` are bugs.

### Bash / git-bash

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
```

### PowerShell

```powershell
$REPO_ROOT = git rev-parse --show-toplevel
```

### Python (codex invocation scripts, helpers, anywhere)

```python
import subprocess
from pathlib import Path
REPO_ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
)
```

All paths in group prompts are repo-relative. Convert to absolute via
`REPO_ROOT` at invocation time. Codex-invocation helper scripts (per §10) must
also discover `REPO_ROOT` at runtime; do not paste an absolute path into the
script.

## 9. Documentation consolidation — tracked, file-based, race-free

`docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md` are touched by:

- **PROJ-457** (Group B)
- **PROJ-459** (Group A)
- **PROJ-460** (Group C)

Direct editing during the projects would produce three-way conflicts. Instead:

### 9.1 During project execution — stage, don't edit

When a phase would normally edit either doc file, write the intended edit to a
**tracked staging file**:

`Projects/active_projects/_doc_consolidation/PROJ-<N>_pending.md`

Format (entries can stack within one file):

```markdown
## docs/01_ARCHITECTURE.md
### Anchor: <heading-or-anchor-line>
### Operation: insert-after | replace | append-to-section
### Source: PROJ-<N> Phase <K> — <finding-id-or-rationale>

```diff
... the actual proposed edit, in unified-diff or full-block form ...
```
```

Commit and push the pending file just like any other artifact.

### 9.2 End-of-project — "am I last?" check

When your project (PROJ-457, PROJ-459, or PROJ-460) reaches end-of-project
(all phases complete, audit done, ready to merge to `main`):

```bash
git fetch origin main
git ls-tree --name-only origin/main \
    Projects/active_projects/_doc_consolidation/
```

Look for these three filenames in the output:

- `PROJ-457_pending.md`
- `PROJ-459_pending.md`
- `PROJ-460_pending.md`

**If ALL THREE files are present on `origin/main`**: you are the LAST finisher.
You consolidate. Add an extra phase to your project — call it
"Phase <N+1>: Doc consolidation" — with these tasks:

1. Read all three pending files from `origin/main`.
2. Merge into a single coordinated edit to `docs/01_ARCHITECTURE.md` and
   `docs/02_PATTERNS.md`.
3. Delete all three `PROJ-<N>_pending.md` files (`git rm`).
4. Commit: `PROJ-457 + PROJ-459 + PROJ-460 consolidated doc updates`.
5. Push to your group branch.
6. Proceed with the end-of-project merge to `main` per §3.

**If only one or two files are present**: you are NOT last. Leave your
pending file in place. Close your project per §3 without touching the doc
files. The last finisher applies your staged edits.

### 9.3 Race-condition handling

If two groups both see "all three files present" because of overlapping reads:
the second group's `git rebase main` (per §3) will conflict on the doc files
or fail to find the pending files (already deleted by the first group). On
detecting this, the second group: re-fetches `origin/main`, confirms the docs
were consolidated, deletes its own "Phase <N+1>: Doc consolidation" (no longer
needed), and proceeds with the normal end-of-project merge.

## 10. Codex consult placement — tracked, per-project

Codex audit consults are tracked artifacts (visible across machines), not
scratch. They land **under the audited project**:

`Projects/active_projects/PROJ-<N>/consults/<UTC-ts>_<purpose>/`

Where `<purpose>` is e.g. `end-of-project-audit`, `phase-6-review`, etc.

Each leaf contains:

- `request.md` — the consult/v1 request you build
- `response.md` — codex's atomically-written response
- `log.txt` — partner-invoke log

This replaces the prior convention of writing audits to
`AgentCoordination/Scratchpad/Consult/...` (which is gitignored and invisible
across machines).

### 10.1 Reference invocation pattern (path-discovered)

```python
import json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip()
)
PROJECT = "PROJ-<N>"       # set per consult
PURPOSE = "end-of-project-audit"
ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

LEAF = REPO_ROOT / "Projects" / "active_projects" / PROJECT / "consults" / f"{ts}_{PURPOSE}"
LEAF.mkdir(parents=True, exist_ok=True)

REQUEST = LEAF / "request.md"
RESPONSE = LEAF / "response.md"
LOG = LEAF / "log.txt"

# (write REQUEST.md per consult/v1 schema first)

sys.path.insert(0, str(REPO_ROOT / "Tools" / "agent_coordination"))
import partner_invoke

PROMPT = (
    f"Load the codex-starship-consult-respond skill. Process the consult "
    f"request at {REQUEST}. Honor the permission contract: read-only by "
    f"default; tests only if allow_tests=true (this consult has "
    f"allow_tests=false). Write your response.md atomically (temp+rename) "
    f"at {RESPONSE}. The full schema is in the request body. Final "
    f"ownership belongs to the initiator; you advise, you do not implement."
)

result = partner_invoke.invoke_sync(
    "codex", PROMPT,
    log_path=LOG, repo_root=REPO_ROOT, response_file=RESPONSE,
    sandbox="workspace-write", timeout_sec=2400, model=None,
    expected_from="codex", expected_to="claude",
)
print(json.dumps({
    "exit_status": result.exit_status,
    "error_kind": result.error_kind,
    "return_code": result.return_code,
    "partner_completed": result.partner_completed,
    "response_exists": RESPONSE.exists(),
    "response_bytes": RESPONSE.stat().st_size if RESPONSE.exists() else 0,
}, indent=2))
```

Commit the leaf (`request.md`, `response.md`, `log.txt`) to your group branch
and push.

### 10.2 Request frontmatter

Use the consult/v1 schema. Required frontmatter:

```yaml
---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: <ISO 8601 UTC>
repo_root: <runtime-discovered>      # injected by the invocation script
consult_leaf: <runtime-discovered>   # injected by the invocation script
complete: true
---
```

Inline the canonical consult prompt block from
`AgentCoordination/protocols/consult_prompt_block.md` in the request body's
Constraints section. Read that file with `Read` before building the request;
don't paraphrase it.

## 11. Cross-group test file edits — defensive coordination

Two test files are known to overlap across groups:

- `tests/unit/strategy/engine/test_order_processor_transfer.py` (PROJ-454
  Group B vs PROJ-450 Group A)
- `tests/unit/ui/screens/test_transfer_dialog_characterization.py` (PROJ-456
  Group B vs PROJ-450 Group A)

PROJ-450 is ordered last in Group A specifically to wait for both Group B
projects to complete. Group A's prompt enforces a sync gate before PROJ-450
Phase 1.

Additional defensive measures (apply automatically; no manual STOP needed):

1. **Group B agents must push immediately on every phase commit** so Group A's
   sync gate can see the dependency state on `origin/main`.
2. **Group A's PROJ-450 phase 3 and phase 4 do a fresh
   `git fetch origin main && git rebase main` immediately before opening
   either shared test file.** The rebase pulls in Group B's now-committed
   edits; any conflict goes through §6.
3. Group A's sync-gate check (per the prompt) reads the dependency project's
   `plan.md` from `origin/main`, not from the local working tree.

## 12. discovered_issues/log.jsonl — append-only across groups

The shared discovered-issues log (`AgentCoordination/discovered_issues/log.jsonl`)
is append-only. All three groups append to it. Conflicts on this file are
**trivial** per §6.1: keep both sides, concatenate unique lines.

If `/claude-di-log` is unavailable in your environment, append a single JSONL
line manually (see `AgentCoordination/discovered_issues/README.md` for the
schema) and commit to your group branch.

## 13. Flake retry — sharded-suite failure handling

The sharded test suite has at least one known isolation flake
(`test_colony_owner_id_matches_empire`) and may surface others. A phase-end
sharded failure is **not automatically a STOP**. Apply this sequence:

1. Capture the failing test names from the sharded output.
2. Run each failing test **in isolation**:
   `pytest <path>::<test_name> -v`
3. If every failing test passes in isolation, it is a flake. Retry the full
   sharded suite **once**: `python Tools/test_sharded/test_sharded.py`.
4. If the retry passes: the phase is green. Note the flake in the phase
   commit message (`PROJ-XXX Phase N: <desc> (flake retry: <test>)`) and
   proceed.
5. If any failing test **also fails in isolation**: it is a real regression.
   Investigate — likely from your own changes. Fix; do not retry the sharded
   suite blindly.
6. If the sharded suite fails a **second consecutive time** (after one flake
   retry): STOP and surface to the user. Do not loop indefinitely.

This handles transient/parallel-execution flakes without manual intervention
while still catching real regressions.

## 14. Session-start pre-flight verification

Before doing any project work in a fresh session, run a one-shot
verification to confirm your machine is set up correctly. Fail fast on
config problems rather than discovering them mid-phase.

```bash
# 1. Repo discoverable + on group branch (per §2)
REPO_ROOT=$(git rev-parse --show-toplevel) && echo "REPO_ROOT=$REPO_ROOT"
git branch --show-current   # must be group-<x>

# 2. Baseline sharded suite green on current branch state
python Tools/test_sharded/test_sharded.py
# If RED on a test you didn't touch → flake-retry per §13.
# If RED twice → STOP; your branch is not in a launchable state.

# 3. Git remote auth works (push permission)
git push --dry-run origin group-<x>

# 4. gh CLI authenticated (used for issue/PR ops)
gh auth status

# 5. Codex partner-invoke reachable (skip on first session of PROJ-449;
#    required before the first end-of-project audit)
ls Tools/agent_coordination/partner_invoke.py   # confirm file present
# If this is not the first session, you can skip — past audits already
# proved the path works.
```

If any of these fail, fix the root cause before starting phase work. Do not
work around configuration problems silently.

## 15. Context preservation — subagent use + checkpoint summaries

You will run for many hours across 20+ phases. Main-context fidelity
degrades past ~50% of the context window even with automatic compression.
**Use subagents aggressively to keep main context lean and run-quality high.**

### 15.1 When to delegate to a subagent

Spawn a subagent (via the `Agent` tool, usually `Explore` or
`general-purpose`) for:

- **Multi-file searches** ("find all callers of X across the repo"):
  `Explore` subagent, "medium" or "very thorough" breadth.
- **LOC inventories** (PROJ-459 / PROJ-460 measurement tasks): `Explore`
  with a precise question; have it return only the counts table.
- **Codex audit response reading** when the response is long (>300 lines):
  spawn a `general-purpose` subagent with the response path; ask for a
  ≤300-word summary listing verified issues, false positives, and
  out-of-scope items separately.
- **Cross-group artifact investigation** when you need to read multiple
  files from `origin/main` to understand a collision: spawn a subagent
  with a self-contained brief.
- **Non-trivial merge-conflict resolution** (per §6.2): always spawn a
  subagent.
- **Pre-phase code surveys** ("which test files import X and how"): spawn
  a subagent rather than reading 10 files yourself.

Do **not** delegate work that requires synthesis you'll need to act on —
keep the actual edit, test, and decision-making in main context.
Subagents return summaries; you apply them.

### 15.2 Checkpoint summaries — hedge against context decay

At each of these points, write a concise checkpoint into the current
project's `plan.md` under a `## Checkpoint Log` section (create the
section on first write; append per-checkpoint blocks below):

- **Every 3 completed phases**, OR
- **At every project boundary** (start of project + end of project), OR
- **After any session resume from `ScheduleWakeup` or interruption**

Checkpoint format (target: ≤200 words):

```markdown
### YYYY-MM-DDTHH:MM:SSZ — <trigger: phase-3-complete | project-453-start | resume-from-wait>
- **Done so far**: <one-line summary, last 3 phases or last project>
- **Key decisions**: <any non-obvious choices made; cross-link to decisions.md>
- **Open threads**: <anything mid-flight, blocked, or deferred>
- **Next action**: <concrete next task path: file:line or phase task ID>
- **Cross-group state observed**: <what was on origin/main at last fetch>
```

Commit and push the checkpoint with the next phase commit (no separate
commit needed). The point is: after compression eats your scrollback, you
can re-read recent checkpoints to recover state without losing fidelity.

### 15.3 Why this matters more than usual

This run executes ~16-20 phases per group across ~12 cross-group sync
points. Past ~50 phase boundaries the main agent will have compressed
heavily. Subagents protect you from packing investigation noise into the
window; checkpoints protect you from forgetting why a decision was made
two hours ago. Both compound — use both.

---

## Summary checklist for each group agent

- [ ] §2 — Session start: branch off main; rebase regularly.
- [ ] §4 — Push after every phase commit.
- [ ] §3 — Merge to main at end of each project.
- [ ] §5 — Read cross-group artifacts from `origin/main`, never local tree.
- [ ] §6 — Conflicts: trivial direct; non-trivial via subagent; never
  `--ours/--theirs` shortcuts.
- [ ] §7 — Blocked: poll every 30 minutes via `ScheduleWakeup`; STOP at 8 hrs.
- [ ] §8 — All paths runtime-discovered, never hardcoded.
- [ ] §9 — Doc edits staged to `_doc_consolidation/PROJ-<N>_pending.md`; last
  finisher consolidates.
- [ ] §10 — Codex consults live in `Projects/active_projects/PROJ-<N>/consults/`
  and are committed.
- [ ] §11 — Cross-group test files: fetch + rebase before opening.
- [ ] §12 — discovered_issues log: append-only, conflicts trivially resolved.
- [ ] §13 — Sharded suite RED: isolation-test failing names; if all pass
  alone, retry sharded once; STOP only on second consecutive fail.
- [ ] §14 — Session-start pre-flight: REPO_ROOT, branch, baseline sharded
  green, push auth, gh auth verified before phase work.
- [ ] §15 — Subagents for searches/inventories/audit-summarization/conflicts;
  checkpoint summary every 3 phases and at project boundaries.
