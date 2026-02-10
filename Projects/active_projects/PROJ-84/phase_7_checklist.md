# Phase 7: Cleanup & Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-84 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove any remaining dict references, run full suite, verify complete migration.

---

## Tasks

### Task 7.1: Grep audit for remaining dict access [Simple]
**Tests:** N/A (audit only)

- [ ] Search `game/` for remaining `['components']` on layer data — should return zero hits
- [ ] Search `game/` for remaining `['hp_pool']` on layer data — should return zero hits
- [ ] Search `game/` for remaining `['max_hp_pool']` on layer data — should return zero hits
- [ ] Search `game/` for remaining `['mass']` on layer data (context: layer access only) — should return zero hits
- [ ] Search `game/` for remaining `['radius_pct']` on layer data — should return zero hits
- [ ] Search `game/` for remaining `['max_mass_pct']` on layer data — should return zero hits
- [ ] Search `game/` for remaining `['restrictions']` on layer data — should return zero hits
- [ ] Search `game/` and `tests/` for remaining `isinstance(layer_data, dict)` — should return zero hits (excluding archived/docs)
- [ ] Search for remaining `Dict[str, Any]` layer type annotations in `game/simulation/entities/` — should be zero
- [ ] Fix any stragglers found

**Notes:**

---

### Task 7.2: Final full test suite [Simple]
**Tests:** `pytest tests/ -n 12` AND `pytest simulation_tests/`

- [ ] `pytest tests/ -n 12` — all tests pass (7353+ expected)
- [ ] `pytest simulation_tests/` — all simulation tests pass
- [ ] Record final test count

**Notes:**

---

### Task 7.3: Smoke test [Simple]

- [ ] Manual: launch game, open workshop, verify ship builder loads
- [ ] Manual: select a ship class, add components to layers
- [ ] Manual: verify combat loads without errors (if accessible)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
- [ ] Update plan.md Verification section — check all items
