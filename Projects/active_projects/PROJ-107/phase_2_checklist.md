# Phase 2: Type Hint & Return Type Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-107 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing type hints to critical public APIs, replace `Any` with specific types in commands module, and standardize `to_dict()` return type annotations.

**Findings:** CON-FND-003, CON-FND-009, CON-SIM-003, CON-STR-002, CON-STR-003, CON-UI2-003

---

## Tasks

### Task 2.1: Add Return Type to AIController.get_engage_distance_multiplier [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Line 97: Add `-> float` return type hint to `get_engage_distance_multiplier(self, policy)`
- [ ] Verify: `pytest tests/unit/ai/` passes

**Notes:**

---

### Task 2.2: Add Return Type Hints to target_evaluator Module-Level Functions [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] Line 26: `_is_vector2_like(obj)` -> add `-> bool`
- [ ] Line 35: `_get_position(entity)` -> add `-> 'Vector2'` (import Vector2 from game.core.math if not present)
- [ ] Line 70: `_get_rotation(entity)` -> add `-> float`
- [ ] Line 101: `_get_all_components(entity)` -> add `-> list`
- [ ] Verify: `pytest tests/unit/ai/` passes

**Notes:** _safe_distance already has `-> float` annotation.

---

### Task 2.3: Add Return Type Hints to ShipStatsCalculator Methods [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/simulation/ -v -k ship_stats`

- [ ] Line 68: `calculate(self, ship)` -> add `-> None`
- [ ] Line 152: `_phase_sensor_defense_scores(self, ship, component_pool)` -> add `-> None`
- [ ] Line 220: `_phase_physics_and_limits(self, ship)` -> add `-> None`
- [ ] Line 247: `_phase_stats_aggregation(self, ship, component_pool)` -> add `-> None`
- [ ] Line 374: `_phase_resource_allocation(self, ship, component_pool, available_crew, available_life_support)` -> add `-> None`
- [ ] Line 412: `_phase_damage_check_and_supply(self, ship)` -> add `-> Tuple[list, int, int]`
- [ ] Line 456: `_priority_sort_key(self, c)` -> add `-> int`
- [ ] Line 466: `_check_mass_limits(self, ship)` -> add `-> None`
- [ ] Line 489: `_initialize_resources(self, ship)` -> add `-> None`
- [ ] Line 533: `calculate_ability_totals(self, components)` -> add return type hint (check return type of `calculate_ability_totals`)
- [ ] Line 540: `_get_ability_total(self, component_list, ability_name)` -> add return type hint
- [ ] Add `from typing import Tuple` import if not present
- [ ] Verify: `pytest tests/unit/simulation/ -n 12` passes

**Notes:** These are all `-> None` except _phase_damage_check_and_supply which returns a tuple and the ability methods.

---

### Task 2.4: Replace `Any` with `HexCoord` in Strategy Commands Module [Simple]
**File:** `game/strategy/engine/commands.py`
**Tests:** `pytest tests/unit/strategy/ -v -k command`

There are 16 occurrences of `target_hex: Any` that should be `target_hex: HexCoord`. Since HexCoord is already imported at line 1, this is a straightforward replacement.

- [ ] Line 33: `target_hex: Any # HexCoord` -> `target_hex: HexCoord`
- [ ] Line 35: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [ ] Line 91: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [ ] Line 94: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [ ] Line 181: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [ ] Line 184: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [ ] Line 233: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [ ] Line 236: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [ ] Line 247: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [ ] Line 249: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [ ] Line 259: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [ ] Line 262: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [ ] Line 273: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [ ] Line 276: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [ ] Line 287: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [ ] Line 289: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [ ] If `Any` is no longer used after changes, remove it from the `typing` import on line 2
- [ ] Verify: `pytest tests/ -n 12 -k "command"` passes

**Notes:** HexCoord is already imported at line 1.

---

### Task 2.5: Standardize `to_dict()` Return Type Annotations in Strategy Layer [Medium]
**File:** Multiple files in `game/strategy/`
**Tests:** `pytest tests/unit/strategy/ -n 12`

Standardize all `to_dict()` methods to return `Dict[str, Any]` (capitalized typing form for consistency with fleet.py pattern).

- [ ] `game/strategy/data/planet.py:275`: `-> dict` -> `-> Dict[str, Any]` (add import if needed)
- [ ] `game/strategy/data/stars.py:45,89`: `-> dict` -> `-> Dict[str, Any]`
- [ ] `game/strategy/data/empire.py:134`: `-> dict` -> `-> Dict[str, Any]`
- [ ] `game/strategy/data/galaxy.py:25,63,646`: `-> dict` -> `-> Dict[str, Any]`
- [ ] `game/strategy/data/race_config.py:149`: `-> dict` -> `-> Dict[str, Any]`
- [ ] `game/strategy/data/design_metadata.py:37`: `-> dict` -> `-> Dict[str, Any]`
- [ ] `game/strategy/engine/game_session.py:263`: `-> dict` -> `-> Dict[str, Any]`
- [ ] `game/strategy/engine/game_config.py:70,178`: `-> dict` -> `-> Dict[str, Any]`
- [ ] `game/strategy/services/fleet_navigation_service.py:110`: `-> dict` -> `-> Dict[str, Any]`
- [ ] For each file, ensure `from typing import Dict, Any` is imported
- [ ] Leave `game/strategy/events/event_log.py` as-is (uses lowercase `dict[str, Any]` which is Python 3.9+ syntax - both are valid)
- [ ] Verify: `pytest tests/unit/strategy/ -n 12` passes

**Notes:** fleet.py and ship_instance.py already use `Dict[str, Any]`. Standardize everything to match.

---

### Task 2.6: Add Return Type Hints to BattleUIService Private Methods [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/ -v -k battle_ui`

- [ ] Line ~121: `_convert_ship(self, ship)` -> add `-> ShipDTO`
- [ ] Line ~200: `_convert_component(self, comp)` -> add `-> ComponentDTO`
- [ ] Line ~232: `_convert_projectile(self, proj)` -> add `-> ProjectileDTO`
- [ ] Line ~266: `_convert_beam(self, beam)` -> add `-> BeamDTO`
- [ ] Verify: All DTO types already imported at top of file (ShipDTO, ComponentDTO, ProjectileDTO, BeamDTO)
- [ ] Verify: `pytest tests/unit/ui/ -v` passes

**Notes:** The DTO types are already imported in the file header.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
