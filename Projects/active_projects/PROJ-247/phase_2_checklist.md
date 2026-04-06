# PROJ-247 Phase 2: Replace id() in Battle Controller and Managers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run: `pytest tests/unit/simulation/ -x && python -m simulation_tests.run_tests --fast --no-history`

## Objective
Replace all `id(ship)` dictionary key usage with `ship.id` (now UUID4).

## Status: Not Started

---

### Task 2.1: Refactor battle_controller.py [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -x`

- [ ] Line 78: Change `_ship_id_map: Dict[int, str]` to `Dict[str, str]`
- [ ] Line 199: Change `if id(ship) not in self._ship_id_map` to `if ship.id not in self._ship_id_map`
- [ ] Line 201: Change `self._ship_id_map[id(ship)]` to `self._ship_id_map[ship.id]`
- [ ] Line 168: Same pattern
- [ ] Line 366: Same pattern (reinforcements)
- [ ] Line 383: Change `id(s)` to `s.id` in callback
- [ ] Lines 459, 480: Same pattern (load_state)
- [ ] Lines 313, 322: Update any map parameter passing

### Task 2.2: Refactor retreat_manager.py [Simple]
**File:** `game/simulation/managers/retreat_manager.py`
**Tests:** `pytest tests/unit/simulation/managers/test_retreat_manager.py -x`

- [ ] Lines 86, 127, 247, 265: Replace `id(ship)` with `ship.id`

### Task 2.3: Refactor battle_state.py [Medium]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/simulation/ -x`

- [ ] Lines 500, 505: Replace `id(proj.owner)` / `id(proj.target)` with `.id`
- [ ] Lines 684, 685, 688: Replace `id(ship)` with `ship.id`
