# Phase 1: Migrate 6 callers + delete wrapper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-389 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate 6 production callers of `score_planet_for_race` to `calculate_habitability`, drop the wrapper from the public re-export, and delete the wrapper itself. Both names live in the same module — the wrapper is pure delegation.

---

## Tasks

### Task 1.1: Migrate `population_engine.py` caller
**File:** `game/strategy/engine/population_engine.py`
**Tests:** `pytest tests/ -k population_engine`

- [x] Replace import + 1 call site at line 139 (`score_planet_for_race(...)` → `calculate_habitability(...)`) (LEG-02-009)
- [x] Verify: file no longer imports `score_planet_for_race`

### Task 1.2: Migrate `happiness_engine.py` caller
**File:** `game/strategy/engine/happiness_engine.py`
**Tests:** `pytest tests/ -k happiness_engine`

- [x] Replace import + 1 call site at line 117 (LEG-02-009) — also updated module docstring reference
- [x] Verify: file no longer imports `score_planet_for_race`

### Task 1.3: Migrate `economy_slice.py` caller
**File:** `game/strategy/facade/slices/economy_slice.py`
**Tests:** `pytest tests/ -k economy_slice`

- [x] Replace import + 1 call site at line 157 (LEG-02-009)
- [x] Verify: file no longer imports `score_planet_for_race`

### Task 1.4: Migrate `colony_output.py` callers (3 sites)
**File:** `game/strategy/formulas/colony_output.py`
**Tests:** `pytest tests/ -k colony_output`

- [x] Replace 3 call sites at lines 47, 95, 152 (LEG-02-009) — line 47 is in the docstring
- [x] Update the import (or use the module-internal canonical name since both live in `formulas/`)
- [x] Verify: file no longer references `score_planet_for_race`

### Task 1.5: Migrate `strategy_detail_fmt.py` caller
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/ -k strategy_detail_fmt`

- [x] Replace import + 1 call site at line 129 (LEG-02-009) — also updated docstring reference
- [x] Verify: file no longer imports `score_planet_for_race`

### Task 1.6: Update public re-export and delete wrapper
**File:** `game/strategy/formulas/__init__.py` and `game/strategy/formulas/habitability.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] In `__init__.py:9`: drop `score_planet_for_race` from the `from .habitability import ...` re-export list (LEG-02-009)
- [x] In `habitability.py:99`: delete the `score_planet_for_race` wrapper (and its docstring) (LEG-02-009)
- [x] Verify: `grep -rn "score_planet_for_race" .` returns zero hits in production code, tests, and live docs (only history-preserving artifacts under `Reviews/`, `Projects/`, `_marked_for_deletion_*/` retain references); focused suite (226 tests) passes

### Out-of-band cleanup (in same change to keep code+docs consistent — Rule 2)

- [x] `game/strategy/facade/dto/colony_demographic_view.py`: docstring referenced the wrapper — updated to `calculate_habitability`
- [x] `docs/04_SERVICES.md`: 2 references updated
- [x] `docs/systems/strategy_layer.md`: 1 reference updated
- [x] Test files migrated (the wrapper deletion would otherwise break their imports + monkeypatch targets):
  - `tests/unit/strategy/engine/test_happiness_engine.py` (direct import + 18 call sites)
  - `tests/unit/strategy/formulas/test_colony_output.py` (3 monkeypatches + 3 docstring refs)
  - `tests/unit/strategy/engine/test_harvesting_engine_habitability.py` (1 monkeypatch + 1 docstring)
  - `tests/unit/ui/screens/test_strategy_detail_fmt.py` (8 patch targets + 2 docstring refs)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
