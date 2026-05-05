# Validation Report: Validator 2
## Summary
- **Findings Reviewed:** 11
- **Confirmed:** 9 | **Downgraded:** 0 | **Rejected:** 2

## Verdicts
#### Finding: CJ-06
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `delete()` at `replay_store.py:322-331` calls `_unlink_sidecar()` after `path.unlink()` succeeds, but `_unlink_sidecar` catches OSError internally and never propagates failure. `delete()` unconditionally returns `True` after a successful replay unlink even when sidecar cleanup fails silently. The sidecar is declared "best-effort" in the docstring of `_unlink_sidecar`, so the design is intentional, but the return value is semantically misleading — the caller gets `True` for a partially-completed operation.

#### Finding: CJ-07
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The claim that `_write_sidecar` re-checks `self._store._replay_dir()` but the old directory still exists on disk is incorrect. `ReplayStore._replay_dir()` at `replay_store.py:201-204` checks `self._save_root` (an **in-memory** reference, not disk existence). After `clear_save_root()` sets `_save_root = None`, `_replay_dir()` returns `None` regardless of whether the directory persists on disk. The double-check in `_write_sidecar` correctly gates on the in-memory state. No TOCTOU vulnerability exists.

#### Finding: CJ-08
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `replay_resolver.py:112` has `from game.simulation.replay import REPLAY_SCHEMA_VERSION` inside the `resolve()` method body, while the module already imports from `game.simulation.replay` at the top level (line 23). The lazy import is unnecessary and violates convention. Purely a style issue, no functional impact.

#### Finding: CJ-09
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `_evict_excess` at `replay_store.py:361-364` sorts by `st_mtime` alone. Python's `sorted()` is stable, so ties preserve the input order from `_iter_replay_files()` which uses `rd.glob()` — whose ordering is OS-dependent and non-deterministic across filesystems. In practice, identical `st_mtime` for distinct replay files is extremely unlikely, so the practical impact is negligible. Info severity is appropriate.

#### Finding: CJ-10
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `shutdown_all_coordinators` at `replay_verification_coordinator.py:85-86` snapshots `_active_coordinators` under lock into a `list()`, then iterates the snapshot outside the lock. A coordinator registered after the snapshot (between line 86 and the `coord.shutdown()` calls) would not be shut down. This is a shutdown-time function and no new coordinators should be starting then, but the design provides no enforcement. Info severity is appropriate.

#### Finding: ERR-354B-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `_worker_loop` at `replay_verification_coordinator.py:250-267` has `try/finally` only around `_verify_one` (line 261-267). The outer `while True:` has no exception handler. While the operations outside the `try/finally` (`_queue_signal.wait()`, `_queue.pop(0)`, `_busy = True`, `_idle_event.set()`) are all unlikely to raise, the absence of a safety net means any unexpected exception (e.g., `RuntimeError` from a corrupted condition variable) kills the worker thread silently with no logging. The consequence (permanent loss of background verification until restart) justifies Major severity even though probability is low.

#### Finding: ERR-354B-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `_on_record_persisted_listeners` at `replay_store.py:158-160` is a plain `list` accessed without any lock. Mutations at lines 190-191 (`append`) and 198-199 (`remove`) race with iteration at line 272 (`list(self._on_record_persisted_listeners)`). While `persist()` runs on the main game-loop thread and `add`/`remove` are typically called during init/shutdown on the same thread, the code does not enforce this ordering contract. A concurrent `shutdown_all_coordinators` during an active battle's `on_battle_ended` → `persist` path would produce a real data race. The list-copy snapshot at line 272 prevents `list modified during iteration` errors but does not prevent the atomicity problems of concurrent mutation. Severity is borderline between Major and Minor; I confirm at Major because the codebase has no explicit threading contract documented for this list.

#### Finding: ERR-354B-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `delete()` at `replay_store.py:317-332` gates sidecar cleanup on `path.exists()` (the replay JSON file). If the replay JSON was manually removed from disk, `path.exists()` is `False`, `delete()` returns `False` without calling `_unlink_sidecar`, and the sidecar remains orphaned. The sidecar path is never checked independently. Minor severity is correct — this requires manual tampering with replay files.

#### Finding: ERR-354B-004
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** At `replay_store.py:368-377`, `continue` in the `except OSError` block skips `_unlink_sidecar`, but this is **correct behavior**. If the replay file could not be deleted (`p.unlink()` raised OSError), the replay record still exists on disk. Deleting the sidecar while its parent replay survives would create the inverse orphan (sidecar missing, replay present). The `continue` preserves the invariant that sidecars are only removed alongside successful replay deletion. No bug here.

#### Finding: ERR-354B-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `save_json()` at `json_utils.py:193-204` cleans up the `.tmp` file only in the `except (TypeError, ValueError)` block (lines 199-204). The `except PermissionError` (lines 193-195) and `except OSError` (lines 196-198) blocks do not call `tmp_path.unlink()`. If `tmp_path.replace(file_path)` fails with a non-permission `OSError` (e.g., cross-device rename, disk full), or if `json.dump` writes partially then fails with `OSError`, the `.tmp` file is left behind as stale debris. Also, `PermissionError` is a subclass of `OSError` and is caught first; if the `mkdir` succeeds but the write/rename fails with a permission error, the `.tmp` may exist and is not cleaned. Minor severity is correct — no data loss, just stale temp files.

#### Finding: ERR-354B-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — The `shutdown()` docstring at `replay_verification_coordinator.py:186-188` states "Records still in the queue at shutdown time are dropped — the worker terminates on the next iteration once the shutdown event is observed." However, the implementation at lines 255-256 shows `if self._shutdown_event.is_set() and not self._queue: return`. The worker only returns when BOTH shutdown is signaled AND the queue is empty. If items remain in the queue, the worker continues popping and processing them — it **drains** the queue, not **drops** it. The docstring is wrong; the implementation is arguably better (draining ensures work completes), but the mismatch is a bug in documentation. Minor severity is appropriate.
