# Review Report: 2026-05-05_075713_code_proj-354b-review-replay-background-verification-ph_req-req_20260505_075712_262732

## Metadata
- **Date:** 2026-05-05
- **Type:** code (delegated by Claude Code)
- **Description:** 
- **Agents Used:** 4

## Executive Summary
- **Total Findings:** 44
- **Critical:** 5 | **Major:** 13 | **Minor:** 16 | **Info:** 10
- **Overall Assessment:** Requires Immediate Attention

## Priority Findings (Top 10)

### 1. CRITICAL: Simulation layer imports from Strategy layer (upward dependency)
**ID:** AR-001
**Agent:** Architecture Reviewer
**Location:** `game/simulation/replay/replay_player.py:72-73`
**Effort:** Unknown

**ID:** AR-001
**Location:** `game/simulation/replay/replay_player.py:72-73`
**Issue:** The deferred import `from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer` inside the `_builder` closure of `build_replay_ship_builder()` violates the fundamental architecture rule that no lower layer may import from a higher layer. `game/simulation/replay/` is in the Simulation layer; `game/strategy/data/` is in the Strategy layer. The dependency direction mandated by `docs/01_ARCHI...

---

### 2. CRITICAL: `compute_outcome_diff` treats list and tuple as interchangeable — masks structural type drift
**ID:** CJ-01
**Agent:** Code Quality
**Location:** `Unknown`
**Effort:** Unknown

**ID:** CJ-01

The `_walk` closure at `replay_verifier.py:113` uses `isinstance(exp, (list, tuple)) and isinstance(act, (list, tuple))`, which groups both types into a single handler. If `exp` is `[1, 2, 3]` and `act` is `(1, 2, 3)`, all elements match and zero diffs are produced — the verifier silently passes a replay whose outcome container types differ structurally from the captured original.

This is a deliberate design compromise because `battle_outcome_to_dict` explicitly converts all `Tup...

---

### 3. CRITICAL: `compute_outcome_diff` missing-key / extra-key semantic is untested
**ID:** TC-C01
**Agent:** Test Coverage
**Location:** `Unknown`
**Effort:** Unknown

**ID:** TC-C01

The `_walk` function at `game/simulation/replay/replay_verifier.py:105-108` emits `expected=<value>, actual=None` for keys present in expected but missing from actual, and `expected=None, actual=<value>` for keys present in actual but missing from expected. These are distinct diff shapes from scalar mismatches but no test verifies either path.

`test_dict_key_mismatch_emits_diff` only asserts `total >= 1` — it does not inspect the individual `Difference` objects to confirm the `e...

---

### 4. CRITICAL: `compute_outcome_diff` type-mismatch branch is untested
**ID:** TC-C02
**Agent:** Test Coverage
**Location:** `Unknown`
**Effort:** Unknown

**ID:** TC-C02

The `_walk` function at line 126 checks `type(exp) is not type(act)` before scalar comparison. This catches diverging types at the same path (e.g., `exp=42, act="42"` or `exp=42, act=[42]`). No test exercises this branch.

**Production lines affected:** `replay_verifier.py:126`

**Fix:** Add a test case where expected and actual dicts share a key but the values have different types (e.g., `{"x": 1}` vs `{"x": [1]}`) and assert a diff is emitted.

---

---

### 5. CRITICAL: `compute_outcome_diff` tuple path is untested
**ID:** TC-C03
**Agent:** Test Coverage
**Location:** `Unknown`
**Effort:** Unknown

**ID:** TC-C03

The isinstance check at line 113 handles both `list` and `tuple`. All existing tests use only `list` for sequence comparisons. `tuple` values (which can appear in `BattleOutcome` dicts, e.g., `participating_empires` or `sector_coords`) exercise a different path through the length-mismatch and index-walk branches but are never tested.

**Production lines affected:** `replay_verifier.py:113`

**Fix:** Add a test case with tuples in the dict values to verify the walker treats them i...

---

### 6. MAJOR: Multiple cross-class accesses to ReplayStore private methods
**ID:** AR-002
**Agent:** Architecture Reviewer
**Location:** `Unknown`
**Effort:** Unknown

**ID:** AR-002
**Location:**
- `game/strategy/services/replay_verification_coordinator.py:276,339` — `self._store._replay_dir()  # noqa: SLF001`
- `game/strategy/services/replay_resolver.py:98,136` — `self._store._replay_dir()  # noqa: SLF001`
- `game/strategy/services/replay_resolver.py:106` — `self._store._safe_load(replay_path)  # noqa: SLF001`

**Issue:** Three call sites across two different classes (`ReplayVerificationCoordinator`, `ReplayResolver`) access private (`_`-prefixed) methods of...

---

### 7. MAJOR: Float comparison with strict `!=` — FPU drift produces false-positive diffs
**ID:** CJ-02
**Agent:** Code Quality
**Location:** `Unknown`
**Effort:** Unknown

**ID:** CJ-02

At `replay_verifier.py:126`, the scalar comparison uses `exp != act`. Floating-point values (`ShipOutcome.hp`, `ShipStats.total_damage_taken`, `ModifierApplication.value`, etc.) may differ by sub-ULP amounts between the original battle and a replayed battle due to FPU nondeterminism (different instruction ordering, fused multiply-add differences, Python build flags). Two semantically identical replays can produce failing diffs on float fields.

The serialization layer converts to ...

---

### 8. MAJOR: List length mismatch reports entire list as single diff — consumes cap-slot with large value blobs
**ID:** CJ-03
**Agent:** Code Quality
**Location:** `Unknown`
**Effort:** Unknown

**ID:** CJ-03

At `replay_verifier.py:116`, when list lengths differ, `_record(path, exp, act)` records the entire expected and actual lists as `Difference.expected` / `Difference.actual`. For a deeply nested outcome structure (e.g., a `TeamOutcome.ships` list), this single diff may carry tens of kilobytes of data and consumes one of only 25 diff slots. The per-element diffs on the shared prefix are also recorded, but the length-mismatch diff itself conveys little actionable information beyond "...

---

### 9. MAJOR: `_difference_to_dict` passes through unvalidated `expected`/`actual` values — latent JSON-serializability risk
**ID:** CJ-04
**Agent:** Code Quality
**Location:** `Unknown`
**Effort:** Unknown

**ID:** CJ-04

At `coordinator.py:106-111`, `_difference_to_dict` copies `d.expected` and `d.actual` directly into the sidecar dict. These values are produced by `compute_outcome_diff` and can be full sub-structures (entire lists, entire dicts) in the list-length-mismatch and missing-extra-key cases. While both sides currently derive from `battle_outcome_to_dict` (which emits only JSON-primitive types), the verifier module has no type-level guarantee that `expected`/`actual` are JSON-serializabl...

---

### 10. MAJOR: Worker loop missing outer exception handler
**ID:** ERR-354B-001
**Agent:** Error Handling
**Location:** `Unknown`
**Effort:** Unknown

**ID:** ERR-354B-001

`ReplayVerificationCoordinator._worker_loop` (coordinator.py:250-267) has a `try/finally` wrapped around `_verify_one(record)` but no outer exception handler around the `while True:` loop. If any unexpected exception escapes from the lock-guarded section (e.g., `_idle_event.set()` in the finally at line 267, or a corrupted `_queue` bypassing the `not self._queue` guard at line 257), the worker thread dies silently with `_busy=True` and `_idle_event` unset:

```python
# coor...

---


## Findings by Severity

### Critical (5)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-001 | Simulation layer imports from Strategy l | `game/simulation/replay/replay_` | Unknown |
| CJ-01 | `compute_outcome_diff` treats list and t | `Unknown` | Unknown |
| TC-C01 | `compute_outcome_diff` missing-key / ext | `Unknown` | Unknown |
| TC-C02 | `compute_outcome_diff` type-mismatch bra | `Unknown` | Unknown |
| TC-C03 | `compute_outcome_diff` tuple path is unt | `Unknown` | Unknown |

### Major (13)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-002 | Multiple cross-class accesses to ReplayS | `Unknown` | Unknown |
| CJ-02 | Float comparison with strict `!=` — FPU  | `Unknown` | Unknown |
| CJ-03 | List length mismatch reports entire list | `Unknown` | Unknown |
| CJ-04 | `_difference_to_dict` passes through unv | `Unknown` | Unknown |
| ERR-354B-001 | Worker loop missing outer exception hand | `Unknown` | Unknown |
| ERR-354B-002 | Listener registry accessed without synch | `Unknown` | Unknown |
| TC-M01 | No test for exactly-at-cap diff count (2 | `Unknown` | Unknown |
| TC-M02 | `ReplayVerificationResult` frozen datacl | `Unknown` | Unknown |
| TC-M03 | Race-condition shutdown path in `_on_rec | `Unknown` | Unknown |
| TC-M04 | R6 replay_dir-cleared-mid-verification p | `Unknown` | Unknown |
| TC-M05 | Weak diff assertions in coordinator PASS | `Unknown` | Unknown |
| TC-M06 | `save_json` returning `False` (non-excep | `Unknown` | Unknown |
| TC-M07 | `duration_ms` may be `None` in `Verifica | `Unknown` | Unknown |

### Minor (16)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-003 | Race window between worker start and lis | `game/strategy/services/replay_` | Unknown |
| AR-004 | shutdown docstring claims queue is dropp | `game/strategy/services/replay_` | Unknown |
| CJ-05 | `ReplayStore.delete` does not clean orph | `Unknown` | Unknown |
| CJ-06 | `ReplayStore.delete` returns `True` when | `Unknown` | Unknown |
| CJ-07 | TOCTOU between R6 defensive check and si | `Unknown` | Unknown |
| CJ-08 | `ReplayResolver.resolve` uses lazy metho | `Unknown` | Unknown |
| ERR-354B-003 | delete() orphans sidecar when replay JSO | `Unknown` | Unknown |
| ERR-354B-004 | Eviction skips sidecar cleanup on replay | `Unknown` | Unknown |
| ERR-354B-005 | save_json leaves stale .tmp file on rena | `Unknown` | Unknown |
| ERR-354B-006 | Worker drains queue on shutdown rather t | `Unknown` | Unknown |
| TC-m01 | `start()` idempotence untested | `Unknown` | Unknown |
| TC-m02 | `shutdown_all_coordinators` with multipl | `Unknown` | Unknown |
| TC-m03 | `_unlink_sidecar` error path (OSError) u | `Unknown` | Unknown |
| TC-m04 | `remove_on_record_persisted_listener` fo | `Unknown` | Unknown |
| TC-m05 | `VerificationSidecar.to_dict()` and `fro | `Unknown` | Unknown |
| TC-m06 | `_iter_replay_files` sidecar exclusion h | `Unknown` | Unknown |

### Info (10)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| AR-005 | ReplayStore depends on verification side | `Unknown` | Unknown |
| AR-006 | ReplayVerificationCoordinator faithfully | `game/strategy/services/replay_` | Unknown |
| CJ-09 | `_evict_excess` tie-breaking on `st_mtim | `Unknown` | Unknown |
| CJ-10 | `shutdown_all_coordinators` may miss coo | `Unknown` | Unknown |
| ERR-354B-007 | All broad except annotations present and | `Unknown` | Unknown |
| ERR-354B-008 | Atomic write via tmp-then-rename confirm | `Unknown` | Unknown |
| ERR-354B-009 | Shutdown pattern correctly mirrors refer | `Unknown` | Unknown |
| TC-i01 | Deep mixed nesting not stress-tested in  | `Unknown` | Unknown |
| TC-i02 | `_fallback_ship_builder` parameter of co | `Unknown` | Unknown |
| TC-i03 | Save root set to `None` after persist —  | `Unknown` | Unknown |


## Agent Reports

- [Architecture Reviewer Report](findings/architecture_reviewer_report.md)
- [Code Quality Report](findings/code_quality_report.md)
- [Error Handling Report](findings/error_handling_report.md)
- [Test Coverage Report](findings/test_coverage_report.md)

## Appendix: Statistics

| Metric | Value |
|--------|-------|
| Total Findings | 44 |
| Critical | 5 |
| Major | 13 |
| Minor | 16 |
| Info | 10 |
| Agents Used | 4 |

---
*Report generated: 2026-05-05 01:08*
