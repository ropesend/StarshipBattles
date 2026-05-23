# Phase 3: Minor Strategy narrowings + closures

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-482 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow ~11 MINOR `-> Any` returns and missing return annotations across superweapon-handler closures, write services, adapters, decorator factories, design catalog, and the atmosphere_engine mutator helper. Also defines the new `ReplayCaptureContext` type for `simulation_adapter._build_capture_context` (UNCERTAIN item user opted to include).

---

## Tasks

### Task 3.1: open_warp_point superweapon closures [Simple]
**File:** `game/strategy/engine/superweapon_handlers/open_warp_point.py`
**Tests:** `pytest tests/ -k open_warp_point` then `mypy` on file

- [ ] Add `-> SuperweaponResult | None` to `_precheck` closure (line 38)
- [ ] Add `-> dict[str, str]` to `_effect` closure (line 54)
- [ ] Verify: tests pass; `mypy` clean

### Task 3.2: stellerate_star superweapon closures [Simple]
**File:** `game/strategy/engine/superweapon_handlers/stellerate_star.py`
**Tests:** `pytest tests/ -k stellerate` then `mypy` on file

- [ ] Add `-> SuperweaponResult | None` to `_precheck` closure (line 47)
- [ ] Add `-> dict[str, str]` to `_effect` closure (line 54)
- [ ] Verify: tests pass; `mypy` clean

### Task 3.3: close_warp_point superweapon closures [Simple]
**File:** `game/strategy/engine/superweapon_handlers/close_warp_point.py`
**Tests:** `pytest tests/ -k close_warp_point` then `mypy` on file

- [ ] Add `-> SuperweaponResult | None` to `_precheck` closure (line 63)
- [ ] Add `-> dict` to `_effect` closure (line 75)
- [ ] Verify: tests pass; `mypy` clean

### Task 3.4: create_dyson_sphere + implode_planet superweapon closures [Simple]
**Files:** `game/strategy/engine/superweapon_handlers/create_dyson_sphere.py`, `implode_planet.py`
**Tests:** `pytest tests/ -k 'create_dyson or implode_planet'` then `mypy` on files

- [ ] Add `-> SuperweaponResult | None` to `_precheck` closure in `create_dyson_sphere.py` (line 39)
- [ ] Add `-> dict` to `_effect` closure in `create_dyson_sphere.py` (line 51)
- [ ] Add `-> dict` to `_effect` closure in `implode_planet.py` (line 39)
- [ ] Verify: tests pass; `mypy` clean

### Task 3.5: construction_queue handler [Simple]
**File:** `game/strategy/engine/handlers/construction_queue.py`
**Tests:** `pytest tests/ -k construction_queue` then `mypy` on file

- [ ] Add `-> dict | None` to `AddToConstructionQueueCommandHandler._resolve_design_data` (line 106)
- [ ] Verify: tests pass; `mypy` clean

### Task 3.6: planet_write_service.pop_construction_item [Simple]
**File:** `game/strategy/services/planet_write_service.py`
**Tests:** `pytest tests/ -k planet_write_service` then `mypy` on file

- [ ] Narrow `pop_construction_item` (line 125) from `-> Any` to `-> dict | None`. Note: the Protocol `IPlanetMutator.pop_construction_item` lives in `core/protocols/strategy_mutators.py:118` and is being narrowed simultaneously in PROJ-483; coordinate or verify both ends match
- [ ] Verify: tests pass; `mypy` clean

### Task 3.7: replay_verification_coordinator._json_safe [Simple]
**File:** `game/strategy/services/replay_verification_coordinator.py`
**Tests:** `pytest tests/ -k replay_verification` then `mypy` on file

- [ ] Narrow `_json_safe` (line 104) from `-> Any` to `-> str | int | float | bool | list | dict | None`
- [ ] Verify: tests pass; `mypy` clean

### Task 3.8: atmosphere_engine mutator helper [Simple]
**File:** `game/strategy/engine/atmosphere_engine.py`
**Tests:** `pytest tests/ -k atmosphere_engine` then `mypy` on file

- [ ] Narrow `_get_planet_mutator` (line 30) to `-> PlanetWriteService`
- [ ] Verify: tests pass; `mypy` clean

### Task 3.9: simulation_adapter _lookup + _build_capture_context [Medium]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/ -k simulation_adapter` then `mypy` on file

- [ ] Add `-> Ship` to nested `_lookup` (line 488)
- [ ] **New type:** Define `ReplayCaptureContext` (either as a class, `TypedDict`, or `Protocol`) for the data shape returned by `_build_capture_context`. Read the function body (line 426) to identify the dict keys/values; create the type alongside or in `game/strategy/adapters/types.py` if a sibling types module exists
- [ ] Narrow `_build_capture_context` (line 426) from `-> Any` to `-> ReplayCaptureContext`
- [ ] Verify: tests pass; `mypy` clean

### Task 3.10: deployed_group decorator factory [Simple]
**File:** `game/strategy/data/deployed_group.py`
**Tests:** `pytest tests/ -k deployed_group` then `mypy` on file

- [ ] Add `-> Callable[[type], type]` to `_register_type` (line 48)
- [ ] Add `-> type` to inner `deco` (line 49)
- [ ] Verify: tests pass; `mypy` clean

### Task 3.11: design_catalog.load_design_data [Simple]
**File:** `game/strategy/systems/design_catalog.py`
**Tests:** `pytest tests/ -k design_catalog` then `mypy` on file

- [ ] Add `-> DesignLoadResult` to `load_design_data` (line 236)
- [ ] Verify: tests pass; `mypy` clean

### Task 3.12: Phase verification [Simple]
- [ ] Verify: `python Tools/test_sharded/test_sharded.py` passes
- [ ] Verify: `mypy` clean across all touched files

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_210540_type-audit/`. See `findings/source_audit.md` for the link._
