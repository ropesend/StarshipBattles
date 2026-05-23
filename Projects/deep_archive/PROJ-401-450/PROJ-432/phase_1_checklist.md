# Phase 1: Mirror the rehydrate wiring inside `restore()`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-432 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/turn_state_snapshot.py`
- `tests/unit/strategy/turn_engine/test_turn_state_snapshot.py`

**Objective:** Add the two missing wiring blocks inside `TurnStateSnapshot.restore()` so the Phase 0 characterization tests pass. The new sequence mirrors `SessionPersistenceAdapter.rehydrate_state()` step-for-step on the post-deserialize wiring (see [design.md](design.md) §"Target shape" for the ordered list).

---

## Tasks

### Task 1.1: Add the `empire.set_galaxy(...)` wiring block [Simple]
**File:** `game/strategy/engine/turn_state_snapshot.py`

- [x] Inside `TurnStateSnapshot.restore()`, immediately after the empires list is rebuilt (and before the `register_fleet` loop), add:
  ```python
  # PROJ-219 (PROJ-432): galaxy back-references for downstream consumers
  # (auto-fleet-registration, capability calculators).
  for empire in session.empires:
      empire.set_galaxy(session.galaxy)
  ```
- [x] Update the method docstring to note that this mirrors `SessionPersistenceAdapter.rehydrate_state()` post-deserialize wiring.
- [x] Run `pytest tests/unit/strategy/turn_engine/test_turn_state_snapshot.py::TestTurnStateSnapshotRestore::test_restore_wires_galaxy_back_refs -x` and confirm green.

### Task 1.2: Add the pursuer-tracker rebuild wiring block [Standard]
**File:** `game/strategy/engine/turn_state_snapshot.py`

- [x] Inside `TurnStateSnapshot.restore()`, after `fleet.resolve_order_references(...)` runs for every fleet, add:
  ```python
  from game.strategy.data.order_types import OrderType
  # PROJ-222 (PROJ-432): rebuild pursuer tracker from resolved order
  # references. Mirrors persistence_adapter.py:188-197.
  for empire in session.empires:
      for fleet in empire.fleets:
          for order in fleet.orders:
              if order.type in (
                  OrderType.MOVE_TO_FLEET,
                  OrderType.JOIN_FLEET,
              ):
                  if hasattr(order.target, "pursuer_tracker"):
                      order.target.pursuer_tracker.add_pursuer(fleet)
  ```
  Local import for `OrderType` is acceptable; the persistence adapter does the same. (Hoisted to a single top-of-method import alongside `Galaxy` / `Empire`.)
- [x] Run `pytest tests/unit/strategy/turn_engine/test_turn_state_snapshot.py::TestTurnStateSnapshotRestore::test_restore_rebuilds_pursuer_trackers -x` and confirm green.

### Task 1.3: Full focused suite + persistence-adapter regression check [Simple]
**Tests:**

- [x] `pytest tests/unit/strategy/turn_engine/test_turn_state_snapshot.py -x` — all green (13 passed).
- [x] `pytest tests/unit/strategy/engine/session/test_persistence_adapter.py -x` — all green (combined 23 passed with snapshot tests, no regressions).
- [x] `pytest tests/integration/ -k "save_load or save or load" -x` — all green (319 passed).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] Both wiring blocks added inside `restore()`
- [x] All Phase 0 tests now pass
- [x] No regressions on persistence-adapter or save/load integration tests
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
