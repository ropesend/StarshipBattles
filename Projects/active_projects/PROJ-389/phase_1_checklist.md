# Phase 1: Migrate 6 callers + delete wrapper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-389 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate 6 production callers of `score_planet_for_race` to `calculate_habitability`, drop the wrapper from the public re-export, and delete the wrapper itself. Both names live in the same module — the wrapper is pure delegation.

---

## Tasks

### Task 1.1: Migrate `population_engine.py` caller
**File:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/ -k population_engine`

- [ ] Replace import + 1 call site at line 139 (`score_planet_for_race(...)` → `calculate_habitability(...)`) (LEG-02-009)
- [ ] Verify: file no longer imports `score_planet_for_race`

### Task 1.2: Migrate `happiness_engine.py` caller
**File:** `game/strategy/engine/happiness_engine.py`
**Tests:** `pytest tests/ -k happiness_engine`

- [ ] Replace import + 1 call site at line 117 (LEG-02-009)
- [ ] Verify: file no longer imports `score_planet_for_race`

### Task 1.3: Migrate `economy_slice.py` caller
**File:** `game/strategy/facade/slices/economy_slice.py`
**Tests:** `pytest tests/ -k economy_slice`

- [ ] Replace import + 1 call site at line 157 (LEG-02-009)
- [ ] Verify: file no longer imports `score_planet_for_race`

### Task 1.4: Migrate `colony_output.py` callers (3 sites)
**File:** `game/strategy/formulas/colony_output.py`
**Tests:** `pytest tests/ -k colony_output`

- [ ] Replace 3 call sites at lines 47, 95, 152 (LEG-02-009)
- [ ] Update the import (or use the module-internal canonical name since both live in `formulas/`)
- [ ] Verify: file no longer references `score_planet_for_race`

### Task 1.5: Migrate `strategy_detail_fmt.py` caller
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/ -k strategy_detail_fmt`

- [ ] Replace import + 1 call site at line 129 (LEG-02-009)
- [ ] Verify: file no longer imports `score_planet_for_race`

### Task 1.6: Update public re-export and delete wrapper
**File:** `game/strategy/formulas/__init__.py` and `game/strategy/formulas/habitability.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] In `__init__.py:9`: drop `score_planet_for_race` from the `from .habitability import ...` re-export list (LEG-02-009)
- [ ] In `habitability.py:99`: delete the `score_planet_for_race` wrapper (and its docstring) (LEG-02-009)
- [ ] Verify: `grep -rn "score_planet_for_race" .` returns zero hits; full sharded suite passes

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
