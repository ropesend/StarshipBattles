# Review Report: PROJ-364 Superweapon Spec Table Refactor
**Request ID:** req_20260505_070825_e838b1
**Review Type:** code
**Review Mode:** normal
**Scope:** 5 production files + 4 test files + 1 decisions doc
**Checkout SHA:** Phase 2 on a8a2fc10b (PROJ-359 commit), Phase 3 on 3890fa921
**Date:** 2026-05-05
**Total files reviewed:** 10

---

## Summary

The superweapon spec table refactor is solid. All 5 strategic superweapons have correct, complete `SuperweaponSpec` entries. SELF_DESTRUCT is correctly excluded as a structural outlier. The `precheck_fn` extension is well-justified and necessary for correct failure-message ordering. The LOC concern is acceptable — each method's bulk comes from effect-closure complexity that would be worse if extracted. The DYSON_SPHERE_CREATED event missing `planet_id`/`planet_name` is a real (minor) issue that should be fixed. Phase 2 files are confirmed in HEAD and passing tests.

**Finding counts:** 0 CRIT | 2 MAJ | 2 MIN | 3 NIT

---

## Findings

### CRIT — None

No correctness or data-integrity defects found. The refactor preserves all pre-refactor behavior as pinned by the Phase 1 characterization tests. Sharded test suite (17645) passed.

---

### MAJ-001: DYSON_SPHERE_CREATED event missing `planet_id` and `planet_name`

**File:** `game/strategy/engine/superweapon_order_processor.py:651-655`
**Severity:** MAJ

The `process_create_dyson_sphere` effect closure creates a new Dyson Sphere `Planet` at line 629-648, but the event kwargs returned at lines 651-655 only include `system_name`:

```python
return {
    "event_message": f"Dyson Sphere created in {system.name}",
    "log_message": f"Dyson Sphere created in {system.name}",
    "system_name": system.name,
}
```

Compare with `process_implode_planet` (line 360-365), which correctly includes:
```python
return {
    "event_message": f"Planet {target_planet.name} destroyed",
    ...
    "planet_id": target_planet.id,
    "planet_name": target_planet.name,
}
```

**Impact:**
- The event log UI cannot display *which planet* was created as the Dyson Sphere (only which system)
- Any future replay/audit tooling that correlates planet lifecycle events (created → destroyed) will be missing the creation-side planet reference
- The characterization test `test_superweapon_event_payloads.py:256-297` does NOT assert `planet_id` or `planet_name` for DYSON_SPHERE_CREATED, so this gap is effectively "blessed" by the tests

**Not a replay capture issue:** The current `ReplayStore`/`IReplayCaptureSink` handles battle replays (`ReplaySpec`/`ReplayRecord`), not strategy-layer event log events. However, the event log subscriber model means any future consumer of `DYSON_SPHERE_CREATED` events won't have a planet reference.

**Recommendation:** Add `planet_id` and `planet_name` to the DYSON_SPHERE_CREATED event kwargs. The `dyson` variable at line 629 is already in scope:

```python
return {
    "event_message": f"Dyson Sphere created in {system.name}",
    "log_message": f"Dyson Sphere created in {system.name}",
    "system_name": system.name,
    "planet_id": dyson.id,          # ADD
    "planet_name": dyson.name,      # ADD
}
```

Also add assertions for `planet_id` and `planet_name` in `TestDysonSphereCreatedPayload.test_payload_keys`.

---

### MAJ-002: LOC ceiling exceeded for most `process_*` methods (acceptable)

**Files:**
- `game/strategy/engine/superweapon_order_processor.py:337-369` (process_implode_planet: 33 lines)
- `game/strategy/engine/superweapon_order_processor.py:371-421` (process_stellerate_star: 51 lines)
- `game/strategy/engine/superweapon_order_processor.py:423-490` (process_open_warp_point: 68 lines)
- `game/strategy/engine/superweapon_order_processor.py:492-564` (process_close_warp_point: 73 lines)
- `game/strategy/engine/superweapon_order_processor.py:566-660` (process_create_dyson_sphere: 95 lines)

**Severity:** MAJ (acceptable — justified)

The LOC target of ≤30 per `process_*` was aspirational. Actual methods range 33–95 lines. Each method's bulk comes from:
1. A locally-defined `_effect` closure that captures `self`, `fleet`, `empire`, `galaxy`, `empires`, `spec`, etc.
2. Weapon-specific logic (Dyson atmosphere fallback, warp-point geometry, colony removal iteration) that is genuinely per-weapon.
3. For 3 of the 5 weapons, a `_precheck` closure that executes before the stabilizer block.

**Why extraction would be worse:**
- Extracting each `_effect` to a standalone `_effect_for_create_dyson_sphere()` method would require passing all captured variables as parameters — increasing method signatures by 7+ args
- Splitting into separate modules (`superweapon/implode_planet.py`, `superweapon/stellerate_star.py`, etc.) would create a 5-6 file micro-architecture for a single responsibility (decisions.md line 11 explicitly ruled this out)
- The closures are the idiomatic Python pattern for this use case: define a callback that captures scope, pass it to the shared dispatcher

**Recommendation:** Accept the LOC exceedance. If the 500-line ceiling on `superweapon_order_processor.py` (currently 780 lines) becomes pressing, consider extracting the 3 longest effect closures (`process_open_warp_point`, `process_close_warp_point`, `process_create_dyson_sphere`) to private `_effect_for_*` methods. But this is not urgent.

---

### MIN-001: `precheck_fn` extension not documented in decisions.md

**File:** `Projects/active_projects/PROJ-364/decisions.md`
**Severity:** MIN

The `precheck_fn` parameter on `execute_superweapon()` was added beyond the original plan (which only called for `effect_fn`). It is justified — it preserves the pre-refactor failure-message ordering where weapon-specific early failures (e.g., "Fleet not at a star system", "Target system not found") must precede the ability-ship lookup error. Without it, the shared dispatcher's target-resolution → stabilizer → ability-ship → effect pipeline would either:
1. Skip the weapon-specific checks entirely (wrong behavior), or
2. Require them to be duplicated inside each effect closure (ugly placement after the stabilizer block).

The `precheck_fn` slot runs between target resolution and stabilizer check, which is the correct position to mirror the pre-refactor early-return pattern.

**However**, it is not recorded in decisions.md. The decisions log (line 5-6) references `findings/03` and Phase 1 coverage gaps but doesn't mention `precheck_fn`.

**Recommendation:** Add a row to decisions.md documenting the `precheck_fn` design decision: "2026-05-04 | Added `precheck_fn` to `execute_superweapon` | Preserves pre-refactor failure-message ordering; weapon-specific early failures must precede stabilizer + ability-ship checks."

---

### MIN-002: Inconsistent `empires` default between `process_open_warp_point` and `process_close_warp_point`

**Files:**
- `game/strategy/engine/superweapon_order_processor.py:423-430` (open: `empires: List['Empire'] = None`)
- `game/strategy/engine/superweapon_order_processor.py:492-499` (close: `empires: List['Empire'] = None`)

**Severity:** MIN

Both methods default `empires=None` but then use `empires or []` at the call sites (lines 488, 562). Other `process_*` methods have `empires: List['Empire']` without the default. This is cosmetic but creates a minor inconsistency.

**Observation:** The `None` default exists because `order_processor.py:713-718` passes `empires or []` — so from the dispatcher's perspective, `None` can't actually reach these methods. The `or []` coercion at lines 488/562 is belt-and-suspenders. Consider removing the `= None` default and treating `empires` as required like the other methods.

---

### NIT-001: File-level docstring references wrong project

**File:** `game/strategy/engine/superweapon_order_processor.py:1-10`
**Severity:** NIT

The module docstring says:
```
PROJ-102 Phase 6: Turn execution logic for strategic superweapon orders.
```

The current refactor is PROJ-364. This stale reference could mislead future readers browsing the file history.

**Recommendation:** Update to `PROJ-364 Phase 3: Spec-driven dispatch for strategic superweapon orders.` or similar.

---

### NIT-002: Logger import placement breaks convention

**File:** `game/strategy/engine/superweapon_order_processor.py:21-22`
**Severity:** NIT

```python
from game.strategy.data.order_types import OrderType

logger = logging.getLogger(__name__)
from game.strategy.data.planet import Planet, PlanetType
```

The `logger` assignment at line 21 sits between two import blocks. Standard practice (and the conventions doc §3) puts module-level setup after all imports. This is not a bug but is lintable.

**Recommendation:** Move `logger = logging.getLogger(__name__)` after line 29 (after all imports).

---

### NIT-003: SELF_DESTRUCT confirmed as structural outlier (all checks pass)

**Files:**
- `game/strategy/services/superweapon_registry.py:121-124` (find_superweapon_spec returns None for SELF_DESTRUCT)
- `tests/unit/strategy/services/test_superweapon_registry_contract.py:87` (test_self_destruct_excluded)
- `game/strategy/engine/order_processor.py:722-724` (separate dispatch table entry)
- `game/strategy/engine/superweapon_order_processor.py:662-738` (standalone handler, no spec dependency)

**Status:** Confirmed. SELF_DESTRUCT is:
1. Not in `SUPERWEAPONS` tuple
2. `find_superweapon_spec(OrderType.SELF_DESTRUCT)` returns `None` (verified by test)
3. Has its own lambda in the dispatch table that doesn't pass `component_registry` or `empires`
4. Its `process_self_destruct()` method does not call `execute_superweapon()` — it handles order check, ship ID resolution, removal, and cleanup independently

This is the correct design per decisions.md line 7.

---

## Verification Summary

| Instruction | Status | Detail |
|---|---|---|
| 5 strategic superweapons have correct spec entries | PASS | All 5 entries match decision docs; contract test `TestExpectedSuperweaponSet` validates |
| SELF_DESTRUCT excluded from spec table | PASS | Registry returns None; dispatch table has separate entry; handler is standalone |
| `precheck_fn` extension justified | PASS | Preserves pre-refactor error-ordering; structurally necessary |
| LOC target (≤30) exceeded | ACCEPTED | Effect-closure complexity makes ≤30 unrealistic; extraction would increase coupling |
| DYSON_SPHERE_CREATED missing planet_id/planet_name | MAJ | Fixable in one line; not a replay-capture issue currently but a future-proofing gap |
| Phase 2 files in HEAD and tested | PASS | `superweapon_registry.py` and contract test exist and pass (sharded 17645 green) |

---

## Phase 2 File Presence Confirmation

| File | Path | Status |
|---|---|---|
| SuperweaponRegistry | `game/strategy/services/superweapon_registry.py` (131 lines) | Present, committed under a8a2fc10b |
| Contract tests | `tests/unit/strategy/services/test_superweapon_registry_contract.py` (186 lines) | Present, 13 test methods across 5 classes |
| Cross-link to PROJ-363 | `test_order_types_match_command_specs`, `test_ability_names_match_command_specs` | Passing (or skipping gracefully when COMMAND_SPECS unavailable) |

Both files use `fresh_registries` fixture for the ability-registry consistency test, following the `test_stabilizer_registry.py` pattern as documented in decisions.md line 9.

---

## Test Coverage Analysis

| Test File | Tests | Focus |
|---|---|---|
| `test_superweapon_registry_contract.py` | 13 | Spec shape, expected set, lookup, ability consistency, PROJ-363 cross-link |
| `test_superweapon_order_pop_matrix.py` | 16 | Per-weapon order-pop semantics (success, no-target, no-ship) |
| `test_superweapon_event_payloads.py` | 4 | Event payload key sets for the 4 previously-uncovered event types |
| `test_superweapon_order_processor_gaps.py` | 12 | Stabilizer cancellation (5 weapons), far-end geometry (2), legacy back-compat, SG-003 cleanup, Dyson fallback, reference planet |
| `test_superweapon_edge_cases.py` | 19 | Error paths, colony removal, mission handlers, self-destruct edge cases |

**Total: 64 tests** across 5 files covering the refactor. The gap-fill tests in `test_superweapon_order_processor_gaps.py` pin stabilizer-block behavior for all 5 weapons, which was the primary coverage gap identified in review finding #5.
