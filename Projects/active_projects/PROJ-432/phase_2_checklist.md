# Phase 2: Docs + final verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-432 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_1
**Review Mode:** lightweight
**Files (planned):**
- `docs/systems/strategy_layer.md`

**Objective:** Record the alignment in `docs/systems/strategy_layer.md` so future readers can see that `TurnStateSnapshot.restore()` and `SessionPersistenceAdapter.rehydrate_state()` agree on the post-deserialize wiring sequence. Run the full sharded suite as the final verification gate.

---

## Tasks

### Task 2.1: Update `docs/systems/strategy_layer.md` [Simple]
**File:** `docs/systems/strategy_layer.md`

- [ ] Locate the session-lifecycle or save/load subsection.
- [ ] Add a short paragraph stating that `TurnStateSnapshot.restore()` mirrors `SessionPersistenceAdapter.rehydrate_state()` for the four post-deserialize wiring steps: galaxy back-references on each empire, fleet registration with the galaxy fleet registry, order-reference resolution, and pursuer-tracker rebuild. Cite PROJ-219, PROJ-222, and PROJ-432.

### Task 2.2: Final verification [Simple]
**Tests:**

- [ ] `pytest tests/unit/strategy/turn_engine/test_turn_state_snapshot.py` — all green.
- [ ] `pytest tests/unit/strategy/engine/session/test_persistence_adapter.py` — all green.
- [ ] `python Tools/test_sharded/test_sharded.py` — full sharded run green.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] Docs note the alignment
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "All phases complete"
