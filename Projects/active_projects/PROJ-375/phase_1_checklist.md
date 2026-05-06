# Phase 1: Dead method removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-375 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the 1 verified dead method (DEEP-01-001) identified by audit `2026-05-05_185819_audit_shrink`.

---

## Tasks

### Task 1.1: Delete `_find_shield_component_id` [Simple]
**File:** `game/strategy/engine/planet_action_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_action_engine.py`

The method is a single-line wrapper that delegates to
`_find_ability_component_id(facility, 'PlanetaryShield')`. Verifier confirmed
zero call sites in `game/`, `tests/`, `docs/`, or `data/`; no dynamic
dispatch references. All current tests and production code already invoke
`_find_ability_component_id` directly with `'PlanetaryShield'`.

- [ ] Remove method `_find_shield_component_id` (lines 385-387, 3 LOC)
- [ ] Verify: `pytest tests/unit/strategy/engine/test_planet_action_engine.py` passes
- [ ] Verify: full sharded suite passes (`python Tools/test_sharded/test_sharded.py`)
- [ ] Verify: LOC delta ≈ -3

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-05_185819_audit_shrink/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
