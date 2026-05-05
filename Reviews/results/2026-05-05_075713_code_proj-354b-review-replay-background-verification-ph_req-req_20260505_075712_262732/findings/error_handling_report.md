# PROJ-354B Error Handling Audit Report

**Date:** 2026-05-05
**Scope:** Replay verification system — sidecar I/O, coordinator, ReplayStore listener wiring, thread safety, resource lifecycle.
**Files audited:**
- `game/strategy/services/replay_verification_sidecar.py`
- `game/strategy/services/replay_verification_coordinator.py`
- `game/strategy/services/replay_store.py`
- `game/core/json_utils.py`
- `game/services/llm/background.py`

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 0     |
| MAJOR    | 2     |
| MINOR    | 4     |
| INFO     | 3     |

**Overall assessment:** The code is well-structured with strong isolation patterns (per-listener try/except, broad-catch annotations on all 8 sites, fan-out listener dispatch via snapshot). No crash-the-system or data-loss issues found. Two MAJOR findings relate to thread-safety gaps in the worker loop and the listener registry; both have low practical exploitability under CPython's GIL but represent correctness concerns that should be addressed.

---

#### MAJOR: Worker loop missing outer exception handler
**ID:** ERR-354B-001

`ReplayVerificationCoordinator._worker_loop` (coordinator.py:250-267) has a `try/finally` wrapped around `_verify_one(record)` but no outer exception handler around the `while True:` loop. If any unexpected exception escapes from the lock-guarded section (e.g., `_idle_event.set()` in the finally at line 267, or a corrupted `_queue` bypassing the `not self._queue` guard at line 257), the worker thread dies silently with `_busy=True` and `_idle_event` unset:

```python
# coordinator.py:250-267
def _worker_loop(self) -> None:
    while True:
        with self._queue_signal:
            ...
            record = self._queue.pop(0)      # line 259
            self._busy = True                # line 260
        try:
            self._verify_one(record)          # protected
        finally:
            with self._queue_signal:
                self._busy = False            # line 265
                if not self._queue:
                    self._idle_event.set()    # line 267  <-- if this raises, thread dies
```

After thread death:
- `_busy` stays True, `_idle_event` stays unset.
- `wait_for_idle()` returns False forever (broken test contracts).
- Queued records accumulate but are never verified.
- The coordinator is still in `_active_coordinators` with no worker backing it.

**Fix:** Wrap the entire `while True:` body in `try: ... except Exception: logger.exception(...); break` so the worker exits cleanly rather than dying silently.

**References:** `game/strategy/services/replay_verification_coordinator.py:250-267`

---

#### MAJOR: Listener registry accessed without synchronization
**ID:** ERR-354B-002

`ReplayStore._on_record_persisted_listeners` (a plain `list`) is mutated and read from multiple threads without a lock:
- `persist()` (replay_store.py:272) snapshots via `list(self._on_record_persisted_listeners)` — runs on the battle/simulation thread.
- `remove_on_record_persisted_listener()` (replay_store.py:198-199) checks `callback in ...` then calls `list.remove()` — runs on the main/shutdown thread.
- `add_on_record_persisted_listener()` (replay_store.py:190-191) checks `callback not in ...` then calls `list.append()` — runs during coordinator setup.

The check-then-mutate patterns in `add` and `remove` are non-atomic sequences:

```python
# replay_store.py:198-199
if callback in self._on_record_persisted_listeners:    # read
    self._on_record_persisted_listeners.remove(callback) # mutate
```

Between the `in` check and the `remove`, another thread's `persist()` can snapshot the list — resulting in a listener being invoked after it was logically unregistered. The listener's own shutdown guard (`_shutdown_event.is_set()` check in `_on_record_persisted`) mitigates the practical harm, but the invariant is violated.

**Fix:** Guard all accesses to `_on_record_persisted_listeners` with a `threading.Lock()`, or use a thread-safe collection (e.g., copy-on-write list or `queue.Queue` for the listener dispatch). Alternatively, document that callers must serialize registration/unregistration externally and that snapshot-while-removing is benign due to the shutdown guard.

**References:** `game/strategy/services/replay_store.py:158-160,190-191,198-199,272`

---

#### MINOR: delete() orphans sidecar when replay JSON is absent
**ID:** ERR-354B-003

`ReplayStore.delete()` (replay_store.py:317-332) only cleans the sidecar when the replay JSON file exists:

```python
if path.exists():
    try:
        path.unlink()
    except OSError:
        ...
        return False
    self._unlink_sidecar(rd, replay_id)   # only reached when replay JSON existed
    return True
return False                               # replay JSON missing → sidecar orphaned
```

If the replay JSON was manually removed from the filesystem (e.g., corrupt-file recovery, user action), the sidecar is left orphaned, violating the stated contract: "the sidecar can never outlive its replay record." In normal operation this path is unreachable (replays are only deleted via `delete()` or `_evict_excess`, both of which delete replay + sidecar together).

**Fix:** Add a `self._unlink_sidecar(rd, replay_id)` call before `return False` on line 332 so the sidecar is cleaned up even when the replay JSON is already missing.

**References:** `game/strategy/services/replay_store.py:332`

---

#### MINOR: Eviction skips sidecar cleanup on replay unlink failure
**ID:** ERR-354B-004

`_evict_excess()` (replay_store.py:350-378) uses `continue` inside the `except OSError` block, which skips `_unlink_sidecar` entirely for that record:

```python
for p in files[:excess]:
    try:
        p.unlink()
        deleted += 1
    except OSError:
        logger.exception(...)
        continue                            # skips sidecar cleanup
    replay_id = self._replay_id_from_path(p)
    if replay_id is not None:
        self._unlink_sidecar(rd, replay_id) # never reached for failed unlinks
```

If the replay file cannot be deleted (permissions, filesystem error, file locked on Windows) but the sidecar is deletable, the sidecar survives. This is a partial failure: the replay and sidecar both persist together, so the "sidecar outlives replay" invariant is not violated (the replay still exists). However, the eviction count is also inaccurate — the replay was not evicted but `deleted` is not incremented, so `max_replays_per_save` may be exceeded.

**Fix:** Move the `_unlink_sidecar` call inside a nested try/except so it fires regardless of replay unlink success. Consider whether a failed unlink should count toward the eviction total (`deleted += 1` even on failure if the intent is to bound the file count).

**References:** `game/strategy/services/replay_store.py:368-377`

---

#### MINOR: save_json leaves stale .tmp file on rename failure
**ID:** ERR-354B-005

`save_json()` (json_utils.py:176-204) cleans up the `.tmp` file only on `TypeError`/`ValueError` (serialization failure at line 202-203). On `PermissionError` or generic `OSError` (lines 193/196) the tmp file is not removed:

```python
try:
    ...
    tmp_path.replace(file_path)            # OS rename — may fail
    return True
except PermissionError as e:
    logger.error(...)
    return False                           # tmp_path NOT cleaned
except OSError as e:
    logger.error(...)
    return False                           # tmp_path NOT cleaned
except (TypeError, ValueError) as e:
    logger.error(...)
    tmp_path = file_path.with_suffix(...)
    tmp_path.unlink(missing_ok=True)        # ONLY cleaned here
    return False
```

The tmp file is self-cleaning (the next write to the same target overwrites it), but a pileup of stale tmp files across many failed saves could accumulate. On Windows, `PermissionError` during `replace()` can occur if the target file is opened without sharing flags by another process; the tmp file remains and is harmless but untidy.

**Fix:** Add `tmp_path.unlink(missing_ok=True)` in the `PermissionError` and `OSError` except blocks, or wrap the entire write+rename sequence in a `try/finally` that cleans the tmp path unconditionally on failure.

**References:** `game/core/json_utils.py:193-204`

---

#### MINOR: Worker drains queue on shutdown rather than dropping records
**ID:** ERR-354B-006

The coordinator's `shutdown()` docstring states:

> Records still in the queue at shutdown time are dropped — the worker terminates on the next iteration once the shutdown event is observed.

The worker loop (coordinator.py:255) behaves differently:

```python
if self._shutdown_event.is_set() and not self._queue:
    return          # only exits when shutdown AND queue is empty
```

The worker **drains** the queue before exiting: if `_shutdown_event` is set but `_queue` is not empty, it continues processing. The docstring is wrong. The drain behavior is arguably better (no lost verification work), but the mismatch could mislead readers about what happens at shutdown — especially if queue processing is slow and holds up shutdown past the timeout.

**Fix:** Either update the docstring to say "worker drains the queue before terminating" or add a `max_drain_duration` to bound drain time. If drain is the intended behavior, the comment in `shutdown()` at line 187-188 should also be updated.

**References:** `game/strategy/services/replay_verification_coordinator.py:187-188,255-256`

---

#### INFO: All broad except annotations present and correct
**ID:** ERR-354B-007

The convention from AGENTS.md requires `# Intentional broad catch: <reason>` on every bare `except Exception`. All 8 sites across the audited files are annotated:

| File | Line | Reason |
|------|------|--------|
| `replay_verification_sidecar.py` | 126 | sidecar write must not crash worker |
| `replay_verification_sidecar.py` | 149 | corrupt sidecars must be skipped, not raised |
| `replay_verification_coordinator.py` | 315 | worker must continue past one bad record |
| `replay_store.py` | 86 | corrupt settings must not block capture |
| `replay_store.py` | 267 | capture must not crash |
| `replay_store.py` | 275 | bad subscriber must not block persist |
| `replay_store.py` | 339 | corrupt files must be skipped, not raised |
| `replay_store.py` | 346 | schema mismatches must be skipped |

No audit findings.

---

#### INFO: Atomic write via tmp-then-rename confirmed
**ID:** ERR-354B-008

`save_json()` (json_utils.py:182-189) writes to `<path>.tmp` then calls `tmp_path.replace(file_path)`. On POSIX this is `os.rename` (atomic). On Windows/NTFS, `Path.replace()` uses `MoveFileExW` with `MOVEFILE_REPLACE_EXISTING`, which is also atomic at the filesystem level. Partial writes are impossible: either the original file is intact, or the complete new file is in place. The sidecar write path (`write_verification_sidecar` → `save_json`) inherits this atomicity.

No audit findings.

---

#### INFO: Shutdown pattern correctly mirrors reference implementation
**ID:** ERR-354B-009

`shutdown_all_coordinators()` (coordinator.py:76-92) parallels `shutdown_all_calls()` (background.py:345-368):
- Snapshot under lock, then release before iterating.
- Shared deadline distributes remaining time across workers.
- Non-daemon worker threads are joined; unjoined workers logged as warning.
- Lock ordering: `_coordinator_lock` is never acquired inside `_state_lock` except during `start()`, which acquires `_state_lock` first then `_coordinator_lock` — no inversion with any other code path.

No deadlock risks identified.

---

## Top 5 Priority Issues

| Priority | ID | Severity | Title |
|----------|-----|----------|-------|
| 1 | ERR-354B-001 | MAJOR | Worker loop missing outer exception handler — silent thread death |
| 2 | ERR-354B-002 | MAJOR | Listener registry accessed without synchronization |
| 3 | ERR-354B-003 | MINOR | delete() orphans sidecar when replay JSON is absent |
| 4 | ERR-354B-004 | MINOR | Eviction skips sidecar cleanup on replay unlink failure |
| 5 | ERR-354B-005 | MINOR | save_json leaves stale .tmp file on rename failure |
