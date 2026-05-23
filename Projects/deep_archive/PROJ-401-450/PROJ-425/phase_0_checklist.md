# Phase 0: Characterization — freeze current behavior using existing test surfaces

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-425 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** (none — first phase)
**Review Mode:** standard
**Files (planned):**
- `tests/unit/strategy/ship_instance/test_convenience_methods.py` (extend)
- `tests/unit/strategy/ship_instance/test_component_toggles.py` (extend)
- `tests/unit/strategy/ship_instance/test_registries_di.py` (extend)
- `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py` (extend)
- `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` (extend)

**Objective:** Establish the regression baseline. Read TD-06 + the foundation docs. Audit the existing `tests/unit/strategy/ship_instance/` modules and tighten / extend them to cover `create(...)`, stats-cache hit / miss / invalidation, component-toggle invalidation, bridge round-trip, serializer round-trip, and the resource/cargo/display convenience helpers that will later be migrated away. Capture the live attribute names for cargo/consumable managers on `ShipInstance` (TD-06 Verification Summary warns these may not match the write-service's expectations).

---

## Pre-flight (read source)

- [x] Read [TD-06 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-06_ship_instance_slimming.md) end-to-end.
- [x] Read [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) §"Phase Gates" + §"Recommended Linear Order" #4 and #11.
- [x] Read foundation docs: `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`.
- [x] Read `game/strategy/data/ship_instance.py` end-to-end (currently 845 LOC). Note the three substantive non-forwarder blocks (stats cache, component-by-layer inspection, `create(...)` factory) and tally the forwarder count.
- [x] Read each existing delegate skimmed for current API: `ship_consumable_manager.py`, `ship_cargo_manager.py`, `ship_display_formatter.py`, `ship_instance_bridge.py`, `ship_instance_serializer.py`, `ship_instance_write_service.py`, `component_inspector.py`.

---

## Tasks

### Task 0.1: Capture manager / accessor naming on live `ShipInstance` [Simple]
**File:** No production edits — research only. Record findings in `findings_ledger.md`.

- [x] Grep for the canonical names on the entity: `rg -n "self\._cargo_manager|self\._consumable_manager|self\.cargo_manager|self\.consumable_manager" game/strategy/data/ship_instance.py`.
- [x] Grep for the write service's expectations: same patterns in `game/strategy/services/ship_instance_write_service.py`.
- [x] Record in `findings_ledger.md`: **(a)** the actual attribute names on `ShipInstance`; **(b)** any divergence between entity and write service. This becomes the Phase 4 standardization input.
- [x] **Verify:** the ledger entry is concrete enough for a future agent to standardize without re-grepping.

**Notes:**

### Task 0.2: Tighten `create(...)` characterization [Medium]
**File:** `tests/unit/strategy/ship_instance/test_registries_di.py` (extend)
**Tests:** `pytest tests/unit/strategy/ship_instance/test_registries_di.py -v`

- [x] Confirm the file already has create-path coverage or add a small handful of tests asserting: ship is constructed with full-HP components from design; missing-registry failure surfaces with the same error type/message it does today; component count matches design layer count.
- [x] Do **not** invent a parallel characterization file. Extend the existing one.
- [x] **Verify:** new tests pass on `main` (existing tests confirmed green; no new tests needed — coverage already sufficient per ledger).

**Notes:**

### Task 0.3: Tighten stats-cache characterization [Medium]
**File:** `tests/unit/strategy/ship_instance/test_registries_di.py` (extend) — or wherever the existing stats-cache tests live; grep `rg -n "_cached_stats|invalidate" tests/unit/strategy/ship_instance/` to choose.
**Tests:** as chosen above.

- [x] Cover the three behaviors that must stay locked across Phase 1: cache hit (second call returns the same object or equal stats with no recompute side effect); cache miss with missing registry (still raises the same way); cache invalidation after a state mutation that today invalidates (component toggle / repair).
- [x] **Verify:** all three pass on `main`.

**Notes:**

### Task 0.4: Tighten component-toggle invalidation characterization [Simple]
**File:** `tests/unit/strategy/ship_instance/test_component_toggles.py` (extend)
**Tests:** `pytest tests/unit/strategy/ship_instance/test_component_toggles.py -v`

- [x] Assert: toggling a component flips its state; toggling a component invalidates `_cached_stats` (next stats fetch recomputes); repair / full-repair restores hp and invalidates cache. These behaviors will move to the write service in Phase 4 — the tests survive the move.
- [x] **Verify:** passes on `main`.

**Notes:**

### Task 0.5: Tighten bridge + serializer round-trip characterization [Simple]
**Files:** `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py`, `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py`, `tests/unit/strategy/ship_instance/test_serialization.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/test_ship_instance_bridge.py tests/unit/strategy/ship_instance/test_ship_instance_serializer.py tests/unit/strategy/ship_instance/test_serialization.py -v`

- [x] Confirm round-trip tests exist for: `ShipInstance` → dict → `ShipInstance`; `ShipInstance` → `Ship` → `ShipInstance`; `clone()` equality + identity (clone is a fresh instance with equal durable state).
- [x] If any are missing, add the smallest viable version.
- [x] **Verify:** all pass on `main`.

**Notes:**

### Task 0.6: Audit convenience-method coverage [Simple]
**File:** `tests/unit/strategy/ship_instance/test_convenience_methods.py` (extend)
**Tests:** `pytest tests/unit/strategy/ship_instance/test_convenience_methods.py -v`

- [x] Audit whether the display, resource/consumable, and cargo *forwarder* surfaces have at least one test each (so Phase 5/6 sub-batch migrations have a regression gate).
- [x] Add minimal coverage where missing. Do not balloon the file.
- [x] **Verify:** passes on `main`.

**Notes:**

### Task 0.7: Capture baseline test pass + LOC counts in findings_ledger.md [Simple]
**Tests:** none new — recording.

- [x] Run the focused suites listed in TD-06 §"Test Strategy":
  - `pytest tests/unit/strategy/ship_instance/ -x` → 122 passed
  - `pytest tests/unit/strategy/services/test_ship_instance_write_service.py -x`
  - `pytest tests/unit/strategy/fleets/test_ship_instance_roundtrip.py tests/unit/strategy/fleets/test_ship_instance_components.py -x`
- [x] Record pass count + any pre-existing failures in `findings_ledger.md`.
- [x] Record `wc -l game/strategy/data/ship_instance.py` as the slimming baseline (845).
- [x] **Verify:** baseline is captured; no pre-existing failures.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `findings_ledger.md` contains: manager-name findings, baseline pass counts, baseline LOC
- [x] No code in `game/` has been modified — Phase 0 is read + test-tighten only
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 1
