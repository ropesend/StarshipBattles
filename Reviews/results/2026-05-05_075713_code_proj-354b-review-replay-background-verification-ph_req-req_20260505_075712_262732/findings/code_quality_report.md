# Code Quality Report — Replay Verification Diff Engine & Coordinator

**Audit date:** 2025-05-05
**Scope:** `compute_outcome_diff`, Cap-25 truncation, `verify_replay_outcome`, `_difference_to_dict`, `ReplayResolver.resolve`, `_evict_excess` glob-overlap, `ReplayStore.delete` sidecar cleanup, R6 race-condition defense.

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1     |
| MAJOR    | 3     |
| MINOR    | 4     |
| INFO     | 2     |
| **Total** | **10** |

---

## Findings

#### CRITICAL: `compute_outcome_diff` treats list and tuple as interchangeable — masks structural type drift

**ID:** CJ-01

The `_walk` closure at `replay_verifier.py:113` uses `isinstance(exp, (list, tuple)) and isinstance(act, (list, tuple))`, which groups both types into a single handler. If `exp` is `[1, 2, 3]` and `act` is `(1, 2, 3)`, all elements match and zero diffs are produced — the verifier silently passes a replay whose outcome container types differ structurally from the captured original.

This is a deliberate design compromise because `battle_outcome_to_dict` explicitly converts all `Tuple` fields to lists (JSON has no tuple type), so both sides of the comparison are list-typed in practice. However, the verifier's public contract claims "strict and structural" equality, and a reader not intimately familiar with the serialization layer would reasonably expect `[1,2,3] != (1,2,3)` to produce a diff. If a future field is serialized differently (e.g., a raw tuple leaks into the outcome dict), the verifier would silently suppress the mismatch.

**Recommendation:** Add an explicit design note in the docstring explaining that list/tuple unification is intentional and predicated on the JSON-only data contract. Alternatively, add a stricter mode that distinguishes them, gated by a keyword flag.

---

#### MAJOR: Float comparison with strict `!=` — FPU drift produces false-positive diffs

**ID:** CJ-02

At `replay_verifier.py:126`, the scalar comparison uses `exp != act`. Floating-point values (`ShipOutcome.hp`, `ShipStats.total_damage_taken`, `ModifierApplication.value`, etc.) may differ by sub-ULP amounts between the original battle and a replayed battle due to FPU nondeterminism (different instruction ordering, fused multiply-add differences, Python build flags). Two semantically identical replays can produce failing diffs on float fields.

The serialization layer converts to `float()` explicitly, but the replayed engine produces fresh values that may not be bit-identical to the captured values even with the same PRNG seed.

**Recommendation:** Accept a configurable `epsilon` parameter (default e.g. `1e-9` relative or absolute) and use `math.isclose` for float-float comparisons. Non-float scalars continue to use `!=`.

---

#### MAJOR: List length mismatch reports entire list as single diff — consumes cap-slot with large value blobs

**ID:** CJ-03

At `replay_verifier.py:116`, when list lengths differ, `_record(path, exp, act)` records the entire expected and actual lists as `Difference.expected` / `Difference.actual`. For a deeply nested outcome structure (e.g., a `TeamOutcome.ships` list), this single diff may carry tens of kilobytes of data and consumes one of only 25 diff slots. The per-element diffs on the shared prefix are also recorded, but the length-mismatch diff itself conveys little actionable information beyond "counts differ."

**Recommendation:** Replace the full-value diff with a synthetic diff that records the length discrepancy explicitly (e.g., `expected={"__len__": len(exp)}`, `actual={"__len__": len(act)}`) or introduce a dedicated `Difference` field for count mismatches. Walk the shared prefix as currently done.

---

#### MAJOR: `_difference_to_dict` passes through unvalidated `expected`/`actual` values — latent JSON-serializability risk

**ID:** CJ-04

At `coordinator.py:106-111`, `_difference_to_dict` copies `d.expected` and `d.actual` directly into the sidecar dict. These values are produced by `compute_outcome_diff` and can be full sub-structures (entire lists, entire dicts) in the list-length-mismatch and missing-extra-key cases. While both sides currently derive from `battle_outcome_to_dict` (which emits only JSON-primitive types), the verifier module has no type-level guarantee that `expected`/`actual` are JSON-serializable. A future change could inject a `Vector2`, `Enum`, or `datetime` object into the diff payload, causing `save_json` to fail at sidecar-write time — silently (the error is caught at `save_json:199` and returns `False`).

**Recommendation:** Add a JSON-serializability sanitization step in `_difference_to_dict`, or alternatively in `_write_sidecar`, that converts known non-JSON types (enums via `.value`, `Vector2` via its list form, etc.) to safe equivalents. At minimum, document the contract that `Difference.expected`/`actual` are guaranteed JSON-safe by the verifier.

---

#### MINOR: `ReplayStore.delete` does not clean orphaned sidecar when replay file is already absent

**ID:** CJ-05

At `replay_store.py:317-332`, the `delete` method returns `False` (early) if the replay file does not exist on disk, without attempting to unlink the sidecar. An orphaned sidecar — e.g., from a previous partial deletion, or from a manual file-system operation — will persist indefinitely. The UI has no way to discover or remove these orphans.

**Recommendation:** After checking `path.exists()`, always call `_unlink_sidecar(rd, replay_id)` regardless of whether the replay file is present. Return `True` if either the replay file or the sidecar was deleted, `False` only if neither existed.

---

#### MINOR: `ReplayStore.delete` returns `True` when sidecar unlink fails silently

**ID:** CJ-06

At `replay_store.py:324-331`, if `path.unlink()` succeeds but `_unlink_sidecar` fails (e.g., `OSError` on a locked sidecar file), the method returns `True`. The caller (and eventual UI) believes the deletion was complete, but a stale sidecar remains on disk. `_unlink_sidecar` logs the error but the `delete` return value does not reflect the partial failure.

**Recommendation:** Return `True` only if BOTH the replay file and the sidecar were successfully deleted (or the sidecar was already absent). Consider returning a richer result (e.g., `(bool, bool)` or a dataclass) that surfaces the sidecar outcome separately.

---

#### MINOR: TOCTOU between R6 defensive check and sidecar write

**ID:** CJ-07

At `coordinator.py:330-352`, `_write_sidecar` re-checks `self._store._replay_dir()` to defend against the save root being cleared mid-verification (race R6). However, the captured `rd` Path object is already a resolved path on disk. Between the check and the `write_verification_sidecar(rd, sidecar)` call, `clear_save_root()` can set `_save_root = None` but the old directory still exists on the filesystem — so the sidecar IS written to the old (now-detached) directory anyway. The check prevents sidecar writes only when `_save_root` was `None` *before* the check, not when it becomes `None` *after* the check.

**Recommendation:** Accept that clearing the save root does not delete the directory, so writing to a captured Path is harmless. Alternatively, pass a snapshot of the save root (`None`-guard) into the worker before the long-running verification task, so no re-check is needed.

---

#### MINOR: `ReplayResolver.resolve` uses lazy method-level import of `REPLAY_SCHEMA_VERSION`

**ID:** CJ-08

At `replay_resolver.py:112`, the import `from game.simulation.replay import REPLAY_SCHEMA_VERSION` is inside the `resolve` method body rather than at module top. This is already available from `game.simulation.replay` in the module's own top-level imports at line 23, but `REPLAY_SCHEMA_VERSION` is not one of them (the top-level import only pulls `ReplayRecord` and `compute_components_registry_hash`). The lazy import works correctly but is atypical and adds a minor per-call overhead of a repeated import.

**Recommendation:** Add `REPLAY_SCHEMA_VERSION` to the top-level import from `game.simulation.replay` at line 23.

---

#### INFO: `_evict_excess` tie-breaking on `st_mtime` is non-deterministic within same-second writes

**ID:** CJ-09

At `replay_store.py:361-364`, `_evict_excess` sorts replay files by `p.stat().st_mtime` to identify the oldest for deletion. `save_json` writes via atomic temp-file rename, which assigns the current filesystem timestamp to the new file. On filesystems with 1-second timestamp granularity (or when many replays are captured in rapid succession), multiple files can share the same `st_mtime`. Python's `sorted` is stable, preserving iteration order from `glob`, which is filesystem-dependent and non-deterministic.

**Recommendation:** Use a composite sort key of `(st_mtime, filename)`. The filename contains the `replay_id` (UUID hex) which provides a stable tie-breaker. This is defensive and unlikely to matter in practice (cap is 50, tie requires same-second bulk captures).

---

#### INFO: `shutdown_all_coordinators` may miss coordinators registered after snapshot

**ID:** CJ-10

At `coordinator.py:85-86`, `shutdown_all_coordinators` takes a set snapshot under `_coordinator_lock`, then iterates outside the lock with a shared deadline. If a new coordinator is started (via `start()` on line 180) between the snapshot and the deadline, it will not receive a `shutdown()` call and its daemon thread will continue running. During process shutdown, the OS terminates the process, so this is benign. During a mid-session reset/reconfig, orphaned worker threads could accumulate.

**Recommendation:** Loop with re-check under lock until the active set is empty, or add the snapshot+shutdown loop to the call-site's lifecycle guarantees.

---

## Top 5 Priority Issues

1. **CJ-01 (CRITICAL)** — List/tuple interchangeability in `compute_outcome_diff` violates the "strict and structural" contract. Mitigation is simple: docstring clarification or optional strict-mode flag.
2. **CJ-02 (MAJOR)** — Float `!=` comparison causes false-positive verification failures due to FPU drift, undermining trust in the verifier's "PASSED" signal.
3. **CJ-03 (MAJOR)** — Coarse length-mismatch diffs waste the 25-diff cap with large blobs, reducing effective diff visibility for the user.
4. **CJ-06 (MINOR)** — `delete` returning `True` after sidecar cleanup failure leaves the UI unaware of orphaned sidecar files.
5. **CJ-05 (MINOR)** — Orphaned sidecars from already-deleted replays are never cleaned up, accumulating over time.
