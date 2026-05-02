# Delegation System v2.2 — Implementation Spec for OpenCode

**Status:** Tests green at 16/16. Apply all fixes below in one commit, TDD per item.

**Versions:** v2 implemented (current code state). v2.1 lost (overwritten before commit; same fix list as below). v2.2 is the concise authoritative spec.
**Files in scope:** `Tools/agent_coordination/review_daemon.py`, `Tools/agent_coordination/test_daemon_lifecycle.py`, `.opencode/skills/ocode-review-request/SKILL.md`, `AgentCoordination/DELEGATION.md`.

---

## Bugs

**B1 — Timeouts oversized.** [review_daemon.py:47-48](../Tools/agent_coordination/review_daemon.py#L47-L48). Real reviews take 2–5 min; current 1h timeout wastes 55+ min on hung subprocesses. `ORPHAN_AGE < OPENCODE_TIMEOUT` also incorrect.
- `OPENCODE_TIMEOUT = 1800` (30 min)
- `ORPHAN_AGE = 3600` (60 min, 2× timeout)
- Update `--timeout` and `--orphan-age` help strings.

**B2 — Shutdown leaks subprocesses; daemon process can't actually exit.** [review_daemon.py:512-519](../Tools/agent_coordination/review_daemon.py#L512-L519). `Future.cancel()` is a no-op for running tasks; non-daemon worker threads stay blocked in `proc.communicate`. Subprocesses survive daemon "shutdown" and produce ghost completions on next start.
- Add `_active_procs: set[Popen]` + `threading.Lock`.
- Register Popen in `process_request` after construction; `discard` in `finally`.
- In shutdown path, after the soft-wait loop, kill all registered procs (`taskkill /F /T /PID` on Windows, `proc.kill()` elsewhere), then `proc.wait(timeout=5)` to let threads unblock, then `executor.shutdown(wait=False)`.

**B3 — Sidecar `error` key not honored; failed reviews report success.** [review_daemon.py:397-419](../Tools/agent_coordination/review_daemon.py#L397-L419). Skill writes `{"error": "..."}` and exits 0; daemon treats it as success with zero findings.
```python
if sidecar:
    if "error" in sidecar:
        log(f"Request {request_id}: sidecar reports error: {sidecar['error']}")
        move_to_completed(in_progress_path, success=False, failure_reason=sidecar["error"])
        return False
    # ... existing report_path / findings handling
```

**B4 — Lock-file naming via `Path.with_suffix` is fragile.** [review_daemon.py:108](../Tools/agent_coordination/review_daemon.py#L108) and [:118](../Tools/agent_coordination/review_daemon.py#L118). Breaks on request names with extra dots.
```python
def _lock_path(request_path: Path, pid: int) -> Path:
    return request_path.parent / f"{request_path.name}.{pid}.lock"
```
Rewrite `claim_request` and `release_lock` to use `_lock_path`. Cleanup loop parses PID via `stale.name[len(prefix):-len(".lock")]` instead of `Path.suffixes`.

---

## Correctness

**C1 — Orphan retry leaves stale `Status` and `PickedUp` fields.** [review_daemon.py:313-317](../Tools/agent_coordination/review_daemon.py#L313-L317). Add `_clear_status_fields(path, *keys)` helper; call it on the retry branch before the rename back to `pending/`.

**C2 — Stale-lock sweep on daemon startup.** Crash between `claim_request` and `move_to_in_progress` leaves orphan `.lock` in `pending/`. Add `_sweep_stale_locks()` called from `run_daemon` right after `recover_orphans()`. Iterate `PENDING_DIR.glob("*.lock")`, parse PID from filename, unlink if `not _pid_alive(pid)`.

**C3 — OpenCode skill writes `**Status:** failed` directly.** Contradicts v2 invariant.
1. Step 1.5 parent-not-completed branch: write `result.json` with `{"error": "parent request not yet completed"}` and exit. Daemon handles lifecycle.
2. Error Handling section (lines 222-234): replace "exit code" with "the `error` key in `result.json`."
3. Add invariant at top: **"The skill never writes `Status:`, `Completed:`, `PickedUp:`, `Report:`, or `FailureReason:` to the request file. Daemon owns lifecycle; skill owns `result.json` and report contents only."**

**C4 — Shutdown kill must wait for subprocess termination.** Folded into B2's snippet; verify the `proc.wait(timeout=5)` loop is between the kill loop and `executor.shutdown`.

---

## Tests

Add to `test_daemon_lifecycle.py`. Run after each: `pytest Tools/agent_coordination/test_daemon_lifecycle.py -x`.

**T1 — Shutdown with in-flight workers.** Mock opencode sleeps 10s. `run_daemon` in a thread, drop 2 requests, set `_shutdown_requested = True`, assert thread exits within `SHUTDOWN_TIMEOUT + 5s`, mock subprocesses dead, PID file removed.
- *Implementation note:* `signal.signal` only works in main thread. Refactor `run_daemon(install_signal_handlers: bool = True)` and pass `False` from the test.

**T2 — Max-worker bounding.** Set `MAX_WORKERS = 2`, drop 5 requests, slow mock (5s sleep), run one main-loop claim iteration. Assert `len(_active_workers) == 2` and 3 still in `pending/`.

**T3 — Real follow-up parent-context resolution.** Replaces lifecycle-only test. Mock opencode for follow-up reads parent's `report.md` and writes `parent_report_seen: true` in its sidecar. Daemon's completed file references the follow-up's review_dir.

**T4 — Sidecar with `error` key.** Mock writes `{"error": "scope unreachable"}`, exit 0. Assert completed file: `Status: failed`, `FailureReason` contains `"scope unreachable"`, no `Findings` field.

**T5 — Lock naming with edge-case request name.** Use request_id `req_test_v1.2.3`. Assert `claim_request` and `release_lock` work end-to-end.

**T6 — Orphan retry clears stale Status.** In_progress file with `Status: in-progress`, recent `PickedUp`. Run `recover_orphans`. Assert pending/ file no longer contains those fields.

**T7 — Stale-lock sweep.** Drop fake `pending/req_x.md.99999.lock`. Run `_sweep_stale_locks`. Assert lock gone.

---

## Cosmetic

**Cs1 —** [review_daemon.py:270](../Tools/agent_coordination/review_daemon.py#L270): `datetime.now()` → `datetime.now(timezone.utc)`.

**Cs2 —** [review_daemon.py:174-191](../Tools/agent_coordination/review_daemon.py#L174-L191): collapse 2-4 `update_request_status` calls in `move_to_completed` into one call with all fields.

**Cs3 —** Update [DELEGATION.md](DELEGATION.md):
- Add `error` field to `result.json` schema (semantics: triggers failure path with `FailureReason: <error>`).
- Add "Lock files" subsection: `req_*.md.<pid>.lock` are claim markers, swept on daemon start and after each successful claim.
- Flag table: `--timeout` → 1800, `--orphan-age` → 3600. Update example command line.
- Add rationale: "OpenCode reviews typically complete in 2–5 minutes; 30-min ceiling catches stuck subprocesses with headroom."

---

## Order

(One commit. TDD per item.)
1. T6 + C1 — orphan retry clearing
2. T7 + C2 — stale-lock sweep
3. T5 + B4 — lock naming
4. T4 + B3 — sidecar error key (+ skill text)
5. T2 — max-worker bounding (validation only)
6. T1 + B2 + C4 — shutdown kill
7. T3 — real follow-up
8. B1 — timeout constants
9. Cs1, Cs2, Cs3 — cosmetic + docs

---

## When done

Reply with: (1) diff summary (files + LOC), (2) full pytest output, (3) any deviations from this spec with rationale.
