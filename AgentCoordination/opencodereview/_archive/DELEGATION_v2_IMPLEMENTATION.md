# Delegation System v2 — Implementation Report for OpenCode

**Audience:** OpenCode (you built v1; this is the follow-up to harden it).
**Author:** Claude Code (review of v1, with additional requirements from the user).
**Status:** Implementation pending. Do not start until the user gives the go-ahead.

This document is the single source of truth for the v2 changes. It supersedes
parts of the v1 skills and daemon. Read top to bottom before editing anything.

---

## Context

You created the delegation system in the current uncommitted changes:

- `.claude/skills/claude-delegate-review/SKILL.md`
- `.opencode/skills/ocode-review-request/SKILL.md`
- `Tools/agent_coordination/review_daemon.py`
- `Tools/agent_coordination/Start-ReviewDaemon.ps1`
- `AgentCoordination/{pending,in_progress,completed}_review_requests/`
- `AgentCoordination/DELEGATION.md`
- `opencode.json` (added `ocode-review-request` command)

I reviewed it and found bugs + missing features. The user has confirmed three
new requirements on top of the bug fixes:

1. **Multiple Claude agents must be able to request reviews in parallel.**
2. **Follow-up reviews must be supported** — after reading a report, a Claude
   agent should be able to ask the reviewer to re-evaluate whether issues
   were resolved.
3. **The skill-usage hook must track all Claude skills**, not just `claude-*`.

This report covers (a) bug fixes from v1 and (b) the three new features.

---

## Part 1 — Bug fixes from v1

### Fix 1.1 [CRITICAL]: Stop double-managing the request lifecycle

**Problem.** `review_daemon.py` moves `pending → in_progress` at line 181 and
`in_progress → completed` at line 236. The OpenCode skill
`.opencode/skills/ocode-review-request/SKILL.md` Steps 2 and 6 *also* move
the file. They will fight, throw `FileNotFoundError`, and corrupt the
request file's frontmatter (the skill prepends a `**Status:**` line that
the daemon already wrote, producing duplicates that `update_request_status`'s
regex then rewrites incorrectly).

**Resolution.** Daemon owns the lifecycle. Skill owns content only.

In `.opencode/skills/ocode-review-request/SKILL.md`:

- **Delete Step 2 entirely** (the move to `in_progress`). The daemon has
  already done this before launching `opencode run`. The request file passed
  in the prompt path will already be in `in_progress_review_requests/`.
- **Delete Step 6 entirely** (the move to `completed`). The daemon will move
  the file when `opencode run` exits successfully.
- **Replace Step 6 with: "Write a `result.json` sidecar."** Path:
  `{REVIEW_DIR}/result.json`. Schema:

  ```json
  {
    "request_id": "req_20260502_063000",
    "report_path": "Reviews/results/2026-05-02_063000_general_combat-refactor/report.md",
    "findings": {"critical": 2, "major": 8, "minor": 10, "info": 3},
    "completed_at": "2026-05-02T06:35:00Z",
    "review_dir": "Reviews/results/2026-05-02_063000_general_combat-refactor"
  }
  ```

- The skill should also write the `## Results` section into the request
  file (so a human reading the completed request file sees the summary
  inline), but it must **not** rename or move the file.

In `Tools/agent_coordination/review_daemon.py`:

- After `opencode run` exits successfully, look for the sidecar by scanning
  `Reviews/results/` for any `result.json` whose `request_id` matches. If
  found, copy `report_path` and `findings` into the request file's
  `## Results` section (use `update_request_status` for `Report` and
  `Findings` keys). If not found, log a warning and proceed with a generic
  "completed without sidecar" status.
- Then `move_to_completed`.

### Fix 1.2 [HIGH]: Daemon must recover orphaned `in_progress/` requests on startup

**Problem.** If the daemon dies mid-review, the request file stays in
`in_progress_review_requests/` forever.

**Resolution.** On startup, before entering the main loop, scan
`in_progress_review_requests/`. For each file:

- If the file has a `PickedUp` timestamp older than `--orphan-age` (default:
  2× `OPENCODE_TIMEOUT`, i.e. 7200s), move it to
  `completed_review_requests/` with `Status: failed` and
  `FailureReason: "orphaned by daemon restart"`.
- If younger, move it back to `pending_review_requests/` so it gets retried.

Add `--orphan-age <seconds>` flag.

### Fix 1.3 [HIGH]: Fix the broken trigger snippet (or remove the mechanism)

**Problem.** `.claude/skills/claude-delegate-review/SKILL.md:155-172` runs a
Python `-c` script from bash that contains `$(Get-Date -Format o)`. That's
PowerShell syntax inside a bash context — it doesn't expand, and Python
sees a literal string.

**Resolution.** Remove the trigger-file mechanism entirely from both the
skill and `review_daemon.py` (delete `check_trigger`, `TRIGGER_FILE`, and
the trigger-related main-loop branches). 3-second polling is responsive
enough; the trigger file adds complexity for ~3s of latency savings.

### Fix 1.4 [MEDIUM]: Remove redundant manual skill-usage logging

**Problem.** `.claude/skills/claude-delegate-review/SKILL.md:149-151` calls
`log_skill_usage.py` manually, but the `PreToolUse(Skill)` hook already logs
`claude-*` skills automatically (per CLAUDE.md §"Skill Usage Logging").
Result: every use double-counts.

**Resolution.** Delete the manual log call from the skill.

### Fix 1.5 [MEDIUM]: Drop the manual-fallback "fire OpenCode directly" branch

**Problem.** `.claude/skills/claude-delegate-review/SKILL.md:177-179` says
"if the daemon is not running, fire OpenCode directly with `Start-Process`."
With v2 the skill no longer manages lifecycle, so this branch would leave
files in `pending/` forever and orphan the run.

**Resolution.** Remove that fallback. If the daemon isn't running, the skill
should tell the user "daemon not running, please start it" and stop. Do not
write the request file in that case (it would just sit unprocessed).

### Fix 1.6 [LOW]: Simplify the daemon-liveness check

**Problem.** The Python `-c` snippet at SKILL.md:28 uses
`(_ for _ in ()).throw(FileNotFoundError)` — clever, hard to read.

**Resolution.** Replace with:

```python
python -c "
import os, sys
from pathlib import Path
pid_file = Path('AgentCoordination/local/review_daemon.pid')
if not pid_file.exists():
    print('DAEMON_NOT_RUNNING'); sys.exit(0)
try:
    pid = int(pid_file.read_text().strip())
    os.kill(pid, 0)
    print('DAEMON_RUNNING')
except (OSError, ProcessLookupError, ValueError):
    print('DAEMON_DEAD')
"
```

### Fix 1.7 [LOW]: `update_request_status` regex should be bounded

**Problem.** `re.sub` without `count=1` rewrites every matching line; if the
file ever has duplicate keys (possible during failure recovery), all of
them get clobbered on the same line.

**Resolution.** Pass `count=1` to `re.sub`. Defensive; harmless in the
happy path.

### Fix 1.8 [LOW]: Log rotation

**Problem.** `AgentCoordination/local/review_daemon.log` grows unbounded.

**Resolution.** When the log exceeds 10 MB at daemon startup, rotate to
`review_daemon.log.1` (overwrite if exists). One-line change in
`run_daemon`.

---

## Part 2 — New feature: Parallel review processing

### Requirement

Multiple Claude agents must be able to fire delegation requests at the same
time without backing up the queue. Today the daemon processes requests
sequentially; an in-flight 30-minute review blocks every other request.

### Design

Worker pool inside the daemon. Default 3 concurrent workers, configurable
via `--max-workers <N>`.

### Implementation

1. **Add a `concurrent.futures.ThreadPoolExecutor`** in `run_daemon` with
   `max_workers` from CLI. (Threads are fine here — each worker spends its
   life in `subprocess.Popen.communicate`, which releases the GIL.)
2. **Per-request lock files** to prevent two workers claiming the same
   request during a directory scan race. When claiming a request, atomically:
   - Create `pending_review_requests/req_<id>.lock` using
     `Path.touch(exist_ok=False)`. If it raises `FileExistsError`, another
     worker won this one; skip.
   - Then `move_to_in_progress`. The lock file does **not** move with the
     request — it stays in `pending/` until the request is moved out, then
     gets cleaned up.
   - Cleanup: after `move_to_in_progress`, unlink the lock.
3. **Track active workers.** Add `_active_workers: dict[str, Future]` keyed
   by request_id. On shutdown, wait for in-flight workers up to
   `--shutdown-timeout` (default 60s), then force-kill via `taskkill /T` on
   Windows or `os.killpg` on Unix.
4. **Each worker runs `process_request` independently.** No changes to
   `process_request` itself beyond removing the trigger logic.
5. **Bound queue depth.** If `len(pending) > max_workers * 5`, log a
   warning. Don't refuse; just surface it.

### Test

Extend `test_daemon_lifecycle.py` (which you also need to write — see
Part 4) with a parallel test: drop 5 requests at once, mock `opencode run`
with a script that sleeps 2s and writes a stub `result.json`, assert all 5
complete in <5s wall time.

---

## Part 3 — New feature: Follow-up reviews

### Requirement

After a Claude agent reads a completed review, it must be able to ask the
reviewer to re-evaluate whether the issues were resolved. This may chain
arbitrarily (review → fix → re-review → tweak → re-review). OpenCode
itself stays stateless — the "conversation" is reconstructed from files
each turn.

### Design

Threaded requests via a `Parent:` field. A follow-up request is just a
normal request file with one extra frontmatter key:

```markdown
**Parent:** req_20260502_063000
```

When OpenCode processes a request with a `Parent`, it reads the parent's
request file *and* the parent's report (`result.json` → `report_path`)
before doing anything else, and treats those as authoritative context.

### Implementation

#### 3.1 Update the Claude skill (`claude-delegate-review/SKILL.md`)

Add a new section before "Step 1: Gather Review Requirements":

```markdown
## Follow-Up Reviews

If the user wants to verify that issues from a prior review were fixed,
write a follow-up request. Required fields:

- `**Parent:** req_<id>` — points at the prior request
- `## Scope` — narrower than the parent (the files that changed in
  response to the findings, not the original full scope)
- `## Instructions` — explicitly list the finding IDs to verify, e.g.
  "Confirm CRIT-001 and MAJ-003 from the parent report are resolved.
   Note any regressions introduced by the fixes."

Follow-ups go in `pending_review_requests/` like any other request. The
daemon and OpenCode handle them uniformly.

When you read a completed follow-up, you may chain another follow-up
against *it* (parent points at the follow-up's request_id, not the
original).
```

#### 3.2 Update the OpenCode skill (`ocode-review-request/SKILL.md`)

Add a new "Step 1.5: Resolve Parent Context (if Parent field present)":

```markdown
## Step 1.5: Parent Context

If the request has a `Parent: req_<id>` field:

1. Read `AgentCoordination/completed_review_requests/req_<id>.md`. If not
   in completed/, abort with `Status: failed`, `FailureReason: "parent
   request not yet completed"`.
2. From the parent's `## Results` section, extract the `Report:` and
   `result.json` paths.
3. Read the parent's `result.json` for structured findings.
4. Read the parent's `report.md` for full finding text.
5. Pass both to your review agents as authoritative prior context. The
   review must explicitly:
   - Verify each finding the request asks about (status: resolved /
     partially-resolved / unresolved / regressed).
   - Surface any new issues introduced by the fixes.
6. The follow-up's report.md must include a "Verification Matrix" section
   at the top:

   ```markdown
   ## Verification Matrix
   | Parent Finding | Status | Notes |
   |---|---|---|
   | CRIT-001 | resolved | Fix at game/foo.py:42 addresses root cause |
   | MAJ-003 | partially-resolved | Edge case in bar() still unhandled |
   ```
```

#### 3.3 Sidecar enhancement

The `result.json` for a follow-up adds:

```json
{
  "parent_request_id": "req_20260502_063000",
  "verification": {
    "CRIT-001": "resolved",
    "MAJ-003": "partially-resolved",
    "MAJ-007": "regressed"
  }
}
```

Daemon does not need to interpret this — it's for downstream tooling and
for the next follow-up in the chain.

#### 3.4 No daemon changes required

Threading is filesystem-only. The daemon treats follow-ups as normal
requests; the relationship lives in the request file's frontmatter and the
sidecar.

---

## Part 4 — New feature: Track usage of *all* Claude skills

### Requirement

The current hook in `.claude/settings.json` →
`Tools/agent_coordination/claude_skill_usage_hook.py` only logs skills
whose name starts with `claude-`. The user wants every skill I invoke
tracked, including built-ins (`loop`, `schedule`, `simplify`, `review`,
`security-review`, `init`, `update-config`, etc.) and any future
unprefixed skills.

### Implementation

Edit `Tools/agent_coordination/claude_skill_usage_hook.py`:

1. Find the line that filters skill names to those starting with
   `claude-`. Remove that filter.
2. Pass the raw skill name through to
   `log_skill_usage.py --agent claude --skill <name>`.
3. For built-in skills that have no project file (e.g. `loop`,
   `schedule`), the counter still increments — `log_skill_usage.py`
   should not require a corresponding skill file to exist. Verify this;
   if it does require one, relax that check (or use a `builtin/<name>`
   namespacing convention in the counter file).

### Caveats

- The user-prompt hook (`UserPromptExpansion`) and `PreToolUse(Skill)`
  hook may fire for the same invocation. Today `claude_skill_usage_hook.py`
  presumably dedupes; verify this still holds for unprefixed skills.
- Update `CLAUDE.md` §"Skill Usage Logging" to reflect "all skills, not
  just claude-* prefixed."

### Tests

Add a test in `Tools/agent_coordination/` (or wherever skill-hook tests
live) that simulates a `PreToolUse(Skill)` event for `loop` and
`simplify` and asserts both end up in the counter.

---

## Part 5 — Tests you must write

`Tools/agent_coordination/test_daemon_lifecycle.py` (the file appeared in
git status during the v1 work but doesn't exist on disk). At minimum:

1. **Happy path:** drop a request in `pending/`, run the daemon for one
   iteration with a mocked `opencode run` that writes `result.json`,
   assert request ends up in `completed/` with correct fields.
2. **Parallel processing (Part 2):** drop 5 requests, assert all complete
   in roughly `max(times)`, not `sum(times)`.
3. **Lock file race (Part 2):** start two daemon instances against the
   same queue, drop a single request, assert exactly one processes it.
4. **Orphan recovery (Fix 1.2):** drop a file in `in_progress/` with an
   old `PickedUp` timestamp, start daemon, assert it moves to `completed/`
   with `Status: failed`.
5. **Follow-up (Part 3):** drop a parent request, complete it (mock),
   then drop a follow-up with `Parent:` pointing at it. Assert the mock
   `opencode run` is invoked with the parent's report path resolvable.
6. **Sidecar parsing (Fix 1.1):** assert daemon copies `findings` and
   `report_path` from the sidecar into the completed request file.

Use `pytest` with `tmp_path` for each test's queue dirs. Mock `opencode`
by writing a small Python script that the daemon's `_find_opencode` will
locate via `PATH` manipulation, or by monkeypatching `_find_opencode`.

---

## Part 6 — Implementation order

Do not interleave. Each step should pass tests before moving on.

1. **Fix 1.1 (lifecycle split)** — biggest blast radius, blocks everything.
2. **Fix 1.4, 1.5** (remove dead code in skill).
3. **Fix 1.3** (drop trigger mechanism — simplifies daemon before adding
   workers).
4. **Fix 1.2** (orphan recovery).
5. **Part 2** (worker pool).
6. **Part 3** (follow-ups — content-only changes; depends on Fix 1.1's
   sidecar).
7. **Part 4** (skill-usage hook expansion).
8. **Fixes 1.6–1.8** (cleanup).
9. **Tests** — write incrementally as you go, not all at the end.

---

## Part 7 — Documentation updates required

When you finish, update these in the same commit as the code:

- `AgentCoordination/DELEGATION.md` — document parallel processing,
  follow-ups, and the new sidecar format.
- `CLAUDE.md` §"Skill Usage Logging" — reflect "all skills" change.
- `.claude/skills/claude-delegate-review/SKILL.md` — per Fix 1.3, 1.4,
  1.5, 1.6 and Part 3.1.
- `.opencode/skills/ocode-review-request/SKILL.md` — per Fix 1.1 and
  Part 3.2.
- `docs/` — none of these belong in `docs/` (this is tooling, not game
  architecture). Keep documentation in `AgentCoordination/`.

---

## Open questions for the user (do not assume; ask)

1. **Worker count default.** I'm proposing 3. The user may want 2 (lower
   resource use) or 5+ (heavy parallel agents).
2. **Orphan age default.** I'm proposing 2× `OPENCODE_TIMEOUT` = 7200s.
   Reasonable but check.
3. **Follow-up priority inheritance.** Should a follow-up inherit the
   parent's `Priority:` field, or always be `normal`? My recommendation:
   inherit, with explicit override allowed.
4. **Should follow-ups skip the queue (jump ahead of normal-priority
   requests)?** Probably no — too easy to starve initial reviews — but
   worth confirming.

---

## Out of scope (do not implement now)

- Persistent OpenCode session reuse (would gain ~10s per request, lose
  filesystem-based simplicity).
- Web UI / status dashboard for the daemon.
- Distributed daemon (multiple machines).
- Authentication on the queue (it's a local dev tool).
- Migrating completed requests to a database (filesystem is fine for the
  scale).
