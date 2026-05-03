# Codex Review Report: Delegated OpenCode Review System

**Date:** 2026-05-02
**Reviewer:** Codex
**Scope:** Current uncommitted delegation/review system files in `AgentCoordination/`, `.claude/skills/claude-delegate-review/`, `.opencode/skills/ocode-review-request/`, `Tools/agent_coordination/`, `CLAUDE.md`, `AGENTS.md`, and `opencode.json`.
**Status:** Review complete. Implementation fixes still required.

---

## Executive Summary

The overall direction is sound: Claude writes a structured request, a daemon owns filesystem lifecycle, OpenCode owns review content, and each review writes a separate `Reviews/results/` directory. That split is the right shape for independent reviews.

The system is not ready to rely on yet. The most important blocker is the lock design: current request locks prevent duplicate claims only inside one daemon process, not across separate daemon processes. If two daemons run, the same request can be processed twice. The test suite is green, but some tests simulate the daemon rather than exercising the real lifecycle, so the test signal is weaker than it looks.

Based on the latest user decisions:

- Parallel, independent reviews are a hard requirement.
- `--dangerously-skip-permissions` is intentional and should remain.
- `Priority:` has no known product semantics yet.
- The implementation docs should collapse to one final version after fixes.

The recommended final design is: one canonical daemon process with a bounded worker pool, robust concurrent request creation by many Claude agents, unique request IDs, atomic file creation, and a PID guard that prevents accidental second-daemon startup. Multiple daemon instances should only be supported if there is a specific future need; the current design does not need them.

---

## Files Reviewed

- `AgentCoordination/DELEGATION.md`
- `AgentCoordination/DELEGATION_v2_IMPLEMENTATION.md`
- `AgentCoordination/DELEGATION_v2.2_IMPLEMENTATION.md`
- `.claude/skills/claude-delegate-review/SKILL.md`
- `.opencode/skills/ocode-review-request/SKILL.md`
- `Tools/agent_coordination/review_daemon.py`
- `Tools/agent_coordination/Start-ReviewDaemon.ps1`
- `Tools/agent_coordination/test_daemon_lifecycle.py`
- `Tools/agent_coordination/claude_skill_usage_hook.py`
- `tests/unit/tools/test_claude_skill_usage_hook.py`
- `CLAUDE.md`
- `AGENTS.md`
- `opencode.json`

Note: `DELEGATION_v2.1_IMPLEMENTATION.md` was visible in the IDE tabs but was not present on disk during this review.

---

## Confirmed User Decisions

### Parallelism

Separate Claude agents must be able to request separate and independent reviews at the same time.

Recommendation: implement this with one daemon and multiple worker subprocesses. Claude agents should never coordinate with each other; they should only atomically create request files in `pending_review_requests/`. The daemon should provide the concurrency boundary.

### Priority

`Priority:` currently has no clear product meaning.

Recommendation: either remove `Priority:` from the v2.2 protocol, or document it as metadata-only/reserved. Do not parse it in daemon code until queue ordering semantics are intentionally chosen.

### OpenCode Permissions

`--dangerously-skip-permissions` is deliberate.

Recommendation: keep it, but document the queue as a trusted local automation boundary. Do not describe arbitrary request writers as safe. The protocol should say that only trusted local agents/users may write request files because request content is effectively a privileged prompt to OpenCode.

### Version Collapse

The final protocol should collapse to v2.2 or the next final version.

Recommendation: after fixes land, make `AgentCoordination/DELEGATION.md` the canonical operating doc and either delete/archive the implementation-spec drafts or rename the final implementation spec to clearly indicate historical status.

---

## Findings

### CRIT-001: Request Locking Does Not Prevent Cross-Process Duplicate Claims

**Location:** `Tools/agent_coordination/review_daemon.py:109-134`
**Severity:** Critical
**Category:** Concurrency / lifecycle correctness

`claim_request()` creates lock files named `req_x.md.<pid>.lock`. Because the PID is part of the lock filename, separate daemon processes create different lock files for the same request. Both can return `True` and both can process the same request.

This violates the core requirement that multiple agents can safely request reviews in parallel. Even if the recommended architecture is one daemon, the launcher and daemon should defend against accidental second-daemon startup.

**Evidence:** A live foreign-PID lock file did not block a second claim; `claim_request()` returned `True` and left two lock files.

**Recommendation:**

- Prefer a single canonical lock path per request, e.g. `req_x.md.lock`, acquired via atomic create.
- Store owner metadata inside the lock file if PID/debugging information is needed.
- If keeping PID lock names, `claim_request()` must scan existing locks before creating its own and refuse when a live lock exists.
- Add a real cross-process test using two Python processes or two daemon instances against the same queue.
- Add a daemon PID guard in `Start-ReviewDaemon.ps1` and/or daemon startup so users do not accidentally run two daemons.

---

### MAJ-001: `process_request()` Masks `Popen` Startup Failures

**Location:** `Tools/agent_coordination/review_daemon.py:400-473`
**Severity:** Major
**Category:** Error handling

`proc` is assigned inside the `try` block and unconditionally referenced in `finally`. If `subprocess.Popen()` fails before assigning `proc`, the daemon catches the original exception, tries to mark the request failed, then raises `UnboundLocalError` from cleanup.

**Impact:** A missing or invalid executable can leave a request in a bad state and obscure the real failure.

**Recommendation:**

- Initialize `proc: subprocess.Popen[Any] | None = None` before `try`.
- In `finally`, discard only when `proc is not None`.
- Add a regression test where `opencode_cmd` points to a non-existent executable and assert the request ends in `completed/` with `Status: failed`.

---

### MAJ-002: Shutdown Test Does Not Exercise the Real Daemon Shutdown Path

**Location:** `Tools/agent_coordination/test_daemon_lifecycle.py:580-650`
**Severity:** Major
**Category:** Test coverage

The shutdown test manually creates a subprocess and manually copies shutdown logic instead of running `run_daemon()`. The key assertion is also ineffective:

```python
assert proc.poll() is not None or True
```

This can never fail.

**Impact:** The test suite can pass while the real daemon still leaks subprocesses or hangs on shutdown.

**Recommendation:**

- Add `run_daemon(install_signal_handlers: bool = True)` so tests can run it in a thread with signal registration disabled.
- In the test, create one or more pending requests, start the real daemon loop, wait until workers are active, set `_shutdown_requested = True`, and assert:
  - daemon thread exits within `SHUTDOWN_TIMEOUT + buffer`;
  - child processes are dead;
  - `PID_FILE` is removed;
  - no live `_active_procs` remain.
- Delete the `or True` assertion.

---

### MAJ-003: Request ID Generation Can Collide Across Claude Agents

**Location:** `.claude/skills/claude-delegate-review/SKILL.md:100-118`
**Severity:** Major
**Category:** Concurrent request creation

The Claude skill instructs agents to create `req_<timestamp>.md` using second-resolution timestamps. Two Claude agents can create a request in the same second and overwrite or conflict with each other.

**Impact:** This directly undermines the requirement that separate Claude agents can independently request reviews at the same time.

**Recommendation:**

- Use a collision-resistant ID, e.g. `req_YYYYMMDD_HHMMSS_<pid>_<6hex>` or UUID-based suffix.
- Write to a temporary filename first, then atomically rename into `pending_review_requests/`.
- Add a small helper script such as `Tools/agent_coordination/create_review_request.py` so Claude does not hand-roll concurrency-sensitive file creation in prompt text.

---

### MAJ-004: Trusted Queue Boundary Is Not Documented Clearly Enough

**Location:** `Tools/agent_coordination/review_daemon.py:393-397`, `AgentCoordination/DELEGATION.md:201-207`
**Severity:** Major
**Category:** Operational safety

The daemon intentionally invokes OpenCode with `--dangerously-skip-permissions`. That is acceptable per user decision, but the documentation says any agent can write to `pending_review_requests/` and only the file format matters.

With dangerous permissions enabled, request content is not just data; it is privileged instruction to an automated tool. The local trust boundary needs to be explicit.

**Recommendation:**

- Keep `--dangerously-skip-permissions`.
- Document that `pending_review_requests/` is trusted-local only.
- Avoid language implying untrusted agents or arbitrary files can safely enter the queue.
- Optionally add a `Requester:` allowlist or warning-only validation for known local agents (`claude-code`, `codex`, etc.).

---

### MAJ-005: OpenCode Skill May Reference the Wrong Subagent Interface

**Location:** `.opencode/skills/ocode-review-request/SKILL.md:115-124`
**Severity:** Major
**Category:** Protocol executability

The skill says to launch review agents using the "Task tool" with `subagent_type: general`. The shared review protocol uses `general-purpose`, and OpenCode's actual tool surface may differ from Claude Code's.

**Impact:** OpenCode may fail to execute the review swarm as written, even though the daemon lifecycle works.

**Recommendation:**

- Verify OpenCode's actual supported agent/subagent interface.
- Update the skill to match OpenCode terms exactly.
- Add a fallback: if no parallel agent tool exists, run the selected review perspectives sequentially and still produce `report.md` and `result.json`.
- Add a smoke test or manual acceptance step for a real `opencode run /ocode-review-request` invocation.

---

### MED-001: Completed Request Contract Disagrees With Implementation

**Location:** `AgentCoordination/DELEGATION.md:189-199`, `.claude/skills/claude-delegate-review/SKILL.md:234-243`, `Tools/agent_coordination/review_daemon.py:159-198`
**Severity:** Medium
**Category:** Docs / parser contract

Docs and skills say completed request files contain a `## Results` section. The daemon currently appends or updates `**Report:**` and `**Findings:**` fields at EOF, not necessarily under `## Results`.

**Impact:** Follow-up review instructions tell OpenCode to extract data from `## Results`; this may work only accidentally or fail if the parser expects the documented section.

**Recommendation:**

- Make the daemon write a real `## Results` section, or
- Change docs/skills to say result fields live as top-level `**Report:**`, `**Findings:**`, `**Status:**`, etc., and require parsers to search globally.

Prefer writing a real `## Results` section because it is easier for humans to scan.

---

### MED-002: Priority Is Parsed But Undefined

**Location:** `Tools/agent_coordination/review_daemon.py:240-253`, request templates in `.claude/skills/claude-delegate-review/SKILL.md`
**Severity:** Medium
**Category:** Product semantics

The daemon parses `Priority:` but queue ordering uses file creation time. The user does not currently know what priority is supposed to do.

**Recommendation:**

- For v2.2, define `Priority:` as metadata-only/reserved, or remove it from templates.
- If scheduling is later desired, define exact behavior:
  - high before normal before low;
  - FIFO within each priority;
  - no starvation rule for low priority;
  - whether follow-ups inherit parent priority.

Until those semantics exist, do not let the code imply scheduling behavior.

---

### MED-003: Hook Logging Docs and Tests Are Stale Relative to "All Skills" Behavior

**Location:** `CLAUDE.md:67-72`, `Tools/agent_coordination/README.md:115-120`, `tests/unit/tools/test_claude_skill_usage_hook.py:59-64`
**Severity:** Medium
**Category:** Documentation / tests

`CLAUDE.md` and `AGENTS.md` now say all Claude skills are logged. `Tools/agent_coordination/README.md` still says the hook filters to `claude-*`, and the hook test still has a test named `test_main_no_op_for_non_claude_prefix`.

**Recommendation:**

- Update `Tools/agent_coordination/README.md` to "all valid skill names."
- Replace the stale test with assertions that built-in/unprefixed skills such as `loop`, `simplify`, and `review` are passed to `log_skill_usage.py`.
- Add one negative test for invalid skill-name syntax.

---

### MED-004: `review_daemon.py` Exceeds the Production File Size Convention

**Location:** `Tools/agent_coordination/review_daemon.py`
**Severity:** Medium
**Category:** Maintainability

The daemon is 654 lines. It is under `Tools/`, not `game/`, so the strict production 500 LOC ceiling does not directly apply. Still, the file already contains path setup, locking, request parsing, status mutation, sidecar parsing, subprocess management, worker orchestration, daemon lifecycle, CLI parsing, PID/log handling, and orphan recovery.

**Impact:** The concurrency bugs are partly a symptom of too many lifecycle concerns living in one file.

**Recommendation:**

Split after correctness fixes:

- `review_queue.py`: request IDs, atomic writes, locks, lifecycle moves.
- `review_process.py`: OpenCode command construction, subprocess tracking, timeout/kill behavior.
- `review_results.py`: sidecar parsing and completed request rendering.
- `review_daemon.py`: CLI and main loop orchestration only.

Do this only after the current behavioral fixes are pinned by tests.

---

### LOW-001: Launcher Checks for `import opencode`, But Runtime Uses an Executable

**Location:** `Tools/agent_coordination/Start-ReviewDaemon.ps1:28-33`
**Severity:** Low
**Category:** Operator experience

The launcher checks `python -c "import opencode"`, but the daemon uses `shutil.which("opencode")`, `opencode.cmd`, or `opencode.ps1`.

**Impact:** The launcher can warn incorrectly if the executable exists but the Python package import does not, or vice versa.

**Recommendation:**

Check the executable path instead:

```powershell
Get-Command opencode -ErrorAction SilentlyContinue
```

---

### LOW-002: Versioned Implementation Docs Conflict With Final-Doc Goal

**Location:** `AgentCoordination/DELEGATION_v2_IMPLEMENTATION.md`, `AgentCoordination/DELEGATION_v2.2_IMPLEMENTATION.md`
**Severity:** Low
**Category:** Documentation lifecycle

`DELEGATION_v2_IMPLEMENTATION.md` says it is the single source of truth for v2. `DELEGATION_v2.2_IMPLEMENTATION.md` says v2.2 is authoritative. Keeping both live invites future agents to read the wrong one.

**Recommendation:**

After fixes:

- Keep `AgentCoordination/DELEGATION.md` as the operating protocol.
- Keep at most one final implementation note, e.g. `DELEGATION_v2.3_IMPLEMENTATION_FINAL.md`, or archive/delete the drafts.
- Add a short "Historical drafts" note if old docs are retained.

---

## Recommended Final Architecture

### Request Writers

Claude agents only create request files. They do not start OpenCode directly and do not move request files between lifecycle directories.

Required writer behavior:

- Generate a unique request ID with randomness or UUID suffix.
- Write a complete request to a temp file in the same directory.
- Atomically rename the temp file into `pending_review_requests/`.
- Never write directly to `in_progress_review_requests/` or `completed_review_requests/`.

### Daemon

Run one canonical daemon process with a bounded worker pool.

Required daemon behavior:

- Refuse to start if a live daemon PID already exists, unless `--force` is explicit.
- Recover young `in_progress` requests back to pending and old ones to failed completed.
- Sweep stale locks on startup.
- Claim each request atomically.
- Spawn one OpenCode process per claimed request.
- Track subprocesses for timeout and shutdown cleanup.
- Move requests to completed after result processing.

### OpenCode Skill

OpenCode owns review content only.

Required skill behavior:

- Read the request file from `in_progress_review_requests/`.
- Resolve parent context for follow-ups.
- Write `scope.md`, `report.md`, optional `findings/`, and `result.json`.
- Never move request files.
- Never write daemon lifecycle fields directly except through `result.json`.

### Results

Each request gets its own review directory, created by the daemon before launching OpenCode.

Required result behavior:

- `result.json` is the machine-readable contract.
- `report.md` is the human-readable review.
- The completed request gets a `## Results` section containing status, report path, findings summary, and failure reason if any.

---

## Proposed Fix Order

1. Add failing tests for cross-process locking and unique request creation.
2. Fix request ID generation and atomic request writes.
3. Fix lock acquisition so only one daemon/worker can claim a request.
4. Add daemon PID guard to prevent accidental second-daemon startup.
5. Fix `proc` cleanup on `Popen` setup failure.
6. Replace simulated shutdown test with real `run_daemon()` lifecycle test.
7. Align completed request `## Results` contract with daemon output.
8. Verify/update OpenCode subagent instructions and add sequential fallback.
9. Decide whether `Priority:` is metadata-only or removed.
10. Update stale skill logging docs/tests.
11. Collapse delegation docs to final canonical version.
12. Optionally split `review_daemon.py` after behavior is stable.

---

## Suggested Acceptance Tests

### Required Before Trusting Parallel Reviews

- Two request files created in the same second by separate writer calls produce two unique pending files.
- Two daemon processes race to claim one request; exactly one claim succeeds.
- One daemon with `MAX_WORKERS=2` processes two slow requests concurrently and leaves the remaining requests pending until capacity frees.
- Shutdown with active OpenCode subprocesses exits cleanly and kills child process trees.
- `Popen` startup failure moves the request to completed failed and does not raise `UnboundLocalError`.
- Follow-up request with missing parent writes `result.json` with `error`, and daemon moves it to completed failed.
- Follow-up request with completed parent reads parent `report.md` and structured `result.json`.
- Completed request contains a real `## Results` section matching documented examples.

### Useful Manual Smoke Test

Run:

```powershell
.\Tools\agent_coordination\Start-ReviewDaemon.ps1 --max-workers 2 --timeout 600
```

Then create two pending review requests from separate shells within the same second. Confirm:

- both appear as distinct request IDs;
- both move to `in_progress_review_requests/`;
- two distinct `Reviews/results/..._req-.../` directories are created;
- both complete with separate `report.md` and `result.json`;
- completed request files point to the correct reports.

---

## Test Run Observed During Review

Command run:

```powershell
python -m pytest Tools/agent_coordination/test_daemon_lifecycle.py
```

Observed result:

```text
23 passed in 4.17s
```

Caveat: the documented `.venv` directory was absent in this checkout, so the test run used system Python 3.11.9. The green result is useful but not sufficient because several important lifecycle paths are simulated rather than exercised end-to-end.

---

## Final Recommendation

Proceed with v2.2 as the base, but treat this as a hardening pass before use. The key design choice should be "many independent request writers, one concurrent daemon." That gives the desired parallelism without making every Claude agent responsible for process management.

The first fix should be cross-process claim correctness. Once requests cannot collide or double-run, the rest of the system becomes much easier to reason about.
