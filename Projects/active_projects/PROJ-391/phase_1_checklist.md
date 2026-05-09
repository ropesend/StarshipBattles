# Phase 1: Three small consolidations

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-391 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Three independent small consolidations: harvester-info, iter-components, formation-serialize. All can ship as one PR.

---

## Tasks

### Task 1.1: Consolidate `_get_harvester_info` into canonical `get_harvester_info`
**File:** `game/strategy/services/planet_economy_projector.py`
**Tests:** `pytest tests/ -k planet_economy_projector`

- [x] Update line 224: replace `_get_harvester_info(...)` call with `get_harvester_info(...)` (LEG-04-007)
- [x] Add `from game.strategy.engine.harvesting_engine import get_harvester_info` if not already present
- [x] If `get_harvester_info` returns `dict | list | None` while caller expects `dict`, add an `isinstance` guard for the list case (or document the assumption — `ResourceHarvester` is always a single dict)
- [x] Delete the local `_get_harvester_info` definition at line 234
- [x] Verify: `grep -n "_get_harvester_info" game/strategy/services/planet_economy_projector.py` returns zero hits

### Task 1.2: Consolidate `_iter_components` into canonical `iter_components`
**File:** `game/ui/screens/battle_setup/spec_compiler.py` and `game/strategy/services/planet_economy_projector.py`
**Tests:** `pytest tests/ -k spec_compiler`

- [x] In `spec_compiler.py`: at line 359, replace `_iter_components(...)` call with `iter_components(...)` (LEG-01-011 / LEG-04-008)
- [x] Add `from game.core.patterns.layer_iterator import iter_components`
- [x] Delete the local `_iter_components` definition at lines 419-427
- [x] In `planet_economy_projector.py:220-231`: replace the manual `for layer_data in design_data.get("layers", {}).values(): if isinstance(layer_data, list): for comp in layer_data:` pattern with `for comp in iter_components(design_data):` (cross-system secondary site, completed under Task 1.1)
- [x] Verify: `grep -rn "_iter_components" .` returns zero hits

### Task 1.3: Move `_formation_to_dict`/`_formation_from_dict` onto `FormationSpec`
**File:** `game/simulation/combat/formation.py`, `game/strategy/data/task_force.py`, `game/simulation/replay/replay_serialization.py`
**Tests:** `pytest tests/ -k formation`

- [x] On `FormationSpec` (in `formation.py`): add `to_dict(self) -> dict` and `@classmethod from_dict(cls, data: dict) -> FormationSpec` per Pattern 17 (Serializable Protocol). Ensure both branches that exist today (`float(p[0])` in `task_force.py` vs `_vec_to_list` in `replay_serialization.py`) are reconciled into one canonical serialization (LEG-01-017)
- [x] In `task_force.py:125-142`: delete `_formation_to_dict`/`_formation_from_dict`; rewrite call sites to use `FormationSpec.to_dict()` / `FormationSpec.from_dict()`
- [x] In `replay_serialization.py:191-213`: delete `_formation_to_dict`/`_formation_from_dict`; rewrite call sites to use the canonical methods. If the layer needs `_vec_to_list` semantics, fold that logic into `FormationSpec.to_dict()` so both layers share it
- [x] Verify: `grep -rn "_formation_to_dict\|_formation_from_dict" .` returns zero hits

### Task 1.4: Final regression
**File:** —
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — confirm baseline preserved
- [ ] Verify: pytest passes; final grep across the repo confirms all 3 legacy helpers are gone

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
