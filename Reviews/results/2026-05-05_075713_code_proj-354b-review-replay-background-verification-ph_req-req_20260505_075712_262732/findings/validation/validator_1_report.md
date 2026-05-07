# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 11
- **Confirmed:** 11
- **Downgraded:** 0
- **Rejected:** 0
- **Rejection Rate:** 0%

## Verdicts

#### Finding: AR-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified — `game/simulation/replay/replay_player.py:72-73` contains `from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer`. This is a deferred import within the `_builder` closure of `build_replay_ship_builder()`. The simulation layer (`game/simulation/`) importing from the strategy layer (`game/strategy/`) is an upward dependency violation per the layered architecture documented in `01_ARCHITECTURE.md`. While deferred to avoid import-time circular dependencies, the architectural violation remains.

#### Finding: AR-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `ReplayVerificationCoordinator` accesses `self._store._replay_dir()` at lines 276 and 339, each annotated `# noqa: SLF001 — package-internal`. `ReplayResolver` accesses `self._store._replay_dir()` at lines 98 (via wrapper) and 136, and `self._store._safe_load(replay_path)` at line 106, similarly annotated. These are all cross-class accesses to `_`-prefixed (private) methods of `ReplayStore`. The #noqa comments acknowledge the convention violation.

#### Finding: AR-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — In `start()` at line 177, `self._worker.start()` spawns the worker thread while still inside the `self._state_lock` block. The listener registration at line 178 (`self._store.add_on_record_persisted_listener(self._on_record_persisted)`) occurs after the lock is released. Between thread start and listener registration, a replay could be persisted without the listener being notified, missing that replay for background verification. Window is narrow (a few Python bytecodes) but real.

#### Finding: AR-004
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — The `shutdown()` docstring at lines 186-188 states "Records still in the queue at shutdown time are dropped — the worker terminates on the next iteration once the shutdown event is observed." However, `_worker_loop()` at line 255 checks `if self._shutdown_event.is_set() and not self._queue: return` — it only exits when the queue is empty AND shutdown is signaled. If shutdown is set but the queue still contains records, the worker continues processing them. The docstring is inaccurate.

#### Finding: AR-005
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — `replay_store.py:47-50` imports `SIDECAR_FILE_SUFFIX` and `sidecar_path_for_replay` from `game.strategy.services.replay_verification_sidecar`. `ReplayStore` uses these for filtering sidecar files in `_iter_replay_files()` and for unlinking sidecars in `_unlink_sidecar()` and `_evict_excess()`. Both modules are in the same layer (`game/strategy/services/`), and the dependency is noted as justified in the finding.

#### Finding: AR-006
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified — The module-level coordinator registry at lines 67-93 (`_coordinator_lock`, `_active_coordinators` set, and `shutdown_all_coordinators()`) faithfully mirrors the pattern from `game/services/llm/background.py` (`shutdown_all_calls`). The docstring at line 79 explicitly acknowledges this mirroring. Per-instance state lock, shutdown event, and join-with-deadline semantics match the reference implementation.

#### Finding: CJ-01
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified — `compute_outcome_diff` at line 113 groups list and tuple via `isinstance(exp, (list, tuple)) and isinstance(act, (list, tuple))`. When both values match this check (e.g., `exp` is a list, `act` is a tuple), the walker compares element-by-element without ever checking `type(exp) is type(act)`. At the scalar fallback (line 126), `type(exp) is not type(act)` would catch the mismatch — but that line is never reached because the list/tuple handler returns first. A `[1, 2, 3]` vs `(1, 2, 3)` comparison produces zero diffs. The descriptive comment at line 112 says "Both list/tuple" which confirms the intentional grouping.

#### Finding: CJ-02
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — The scalar/leaf comparison at line 126 uses `exp != act` with no epsilon tolerance. Floating-point values (positions, velocities, damage calculations) that differ due to FPU nondeterminism between capture and replay would produce false-positive `Difference` entries. In a replay verification context this may be intentional (any drift = nondeterminism), but the code provides no mechanism to distinguish meaningful FPU drift from acceptable rounding error.

#### Finding: CJ-03
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — At `replay_verifier.py:116`, when `len(exp) != len(act)` for list/tuple values, `_record(path, exp, act)` is called with the entire `exp` and `act` collections as `expected`/`actual`. This consumes one of the (default 25) diff slots with potentially large value blobs (e.g., a list containing hundreds of ship component dicts). The code does then walk shared indices to surface leaf diffs, but the full-collection diff entry is still recorded.

#### Finding: CJ-04
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified — `_difference_to_dict()` at lines 106-111 copies `d.expected` and `d.actual` directly from the `Difference` dataclass into a plain dict: `{"path": list(d.path), "expected": d.expected, "actual": d.actual}`. No `isinstance` checks, no `try/except` wrapping, no sanitization. These values are any `Any` from the diff walker. While in practice both values derive from `battle_outcome_to_dict()` which produces JSON-encodable data, the absence of defensive validation means an unexpected non-serializable value would fail at `save_json()` time rather than being caught earlier.

#### Finding: CJ-05
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified — `ReplayStore.delete()` at lines 317-332 unlinks the sidecar only within the `if path.exists():` block (line 330). When `path.exists()` is `False` (line 332), the method returns `False` without attempting `_unlink_sidecar()`. If the replay JSON file was removed by external means (filesystem corruption, manual deletion) but the sidecar `.verification.json` file persists, calling `delete()` leaves the orphaned sidecar on disk. An explicit `_unlink_sidecar()` call before the `return False` would prevent this.
