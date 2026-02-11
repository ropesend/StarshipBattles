# Phase 2: Type Hint & Return Type Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-107 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add missing type hints to critical public APIs, replace `Any` with specific types in commands module, and standardize `to_dict()` return type annotations.

**Findings:** CON-FND-003, CON-FND-009, CON-SIM-003, CON-STR-002, CON-STR-003, CON-UI2-003

---

## Tasks

### Task 2.1: Add Return Type to AIController.get_engage_distance_multiplier [Simple]
**File:** `game/ai/controller.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [x] Line 97: Add `-> float` return type hint to `get_engage_distance_multiplier(self, policy)`
- [x] Verify: `pytest tests/unit/ai/` passes

**Notes:** Completed - added `-> float` return type.

---

### Task 2.2: Add Return Type Hints to target_evaluator Module-Level Functions [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [x] Line 26: `_is_vector2_like(obj)` -> add `-> bool`
- [x] Line 35: `_get_position(entity)` -> add `-> 'Vector2'` (import Vector2 from game.core.math if not present)
- [x] Line 70: `_get_rotation(entity)` -> add `-> float`
- [x] Line 101: `_get_all_components(entity)` -> add `-> list`
- [x] Verify: `pytest tests/unit/ai/` passes

**Notes:** Completed - all 4 functions now have return type hints.

---

### Task 2.3: Add Return Type Hints to ShipStatsCalculator Methods [Medium]
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/simulation/ -v -k ship_stats`

- [x] Line 68: `calculate(self, ship)` -> add `-> None`
- [x] Line 152: `_phase_sensor_defense_scores(self, ship, component_pool)` -> add `-> None`
- [x] Line 220: `_phase_physics_and_limits(self, ship)` -> add `-> None`
- [x] Line 247: `_phase_stats_aggregation(self, ship, component_pool)` -> add `-> None`
- [x] Line 374: `_phase_resource_allocation(self, ship, component_pool, available_crew, available_life_support)` -> add `-> None`
- [x] Line 412: `_phase_damage_check_and_supply(self, ship)` -> add `-> tuple[list, int, int]`
- [x] Line 456: `_priority_sort_key(self, c)` -> add `-> int`
- [x] Line 466: `_check_mass_limits(self, ship)` -> add `-> None`
- [x] Line 489: `_initialize_resources(self, ship)` -> add `-> None`
- [x] Line 533: `calculate_ability_totals(self, components)` -> add `-> dict`
- [x] Line 540: `_get_ability_total(self, component_list, ability_name)` -> add `-> float`
- [x] Add `from typing import Tuple` import if not present
- [x] Verify: `pytest tests/unit/simulation/ -n 12` passes

**Notes:** Completed - all 11 methods now have return type hints. Used Python 3.9+ `tuple[list, int, int]` syntax.

---

### Task 2.4: Replace `Any` with `HexCoord` in Strategy Commands Module [Simple]
**File:** `game/strategy/engine/commands.py`
**Tests:** `pytest tests/unit/strategy/ -v -k command`

There are 16 occurrences of `target_hex: Any` that should be `target_hex: HexCoord`. Since HexCoord is already imported at line 1, this is a straightforward replacement.

- [x] Line 33: `target_hex: Any # HexCoord` -> `target_hex: HexCoord`
- [x] Line 35: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [x] Line 91: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [x] Line 94: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [x] Line 181: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [x] Line 184: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [x] Line 233: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [x] Line 236: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [x] Line 247: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [x] Line 249: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [x] Line 259: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [x] Line 262: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [x] Line 273: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [x] Line 276: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [x] Line 287: `target_hex: Any  # HexCoord` -> `target_hex: HexCoord`
- [x] Line 289: `target_hex: Any` -> `target_hex: HexCoord` (in __init__)
- [x] If `Any` is no longer used after changes, remove it from the `typing` import on line 2
- [x] Verify: `pytest tests/ -n 12 -k "command"` passes

**Notes:** Completed - Added HexCoord import from game.core.hex_math, replaced all 16 occurrences, removed Any from typing import.

---

### Task 2.5: Standardize `to_dict()` Return Type Annotations in Strategy Layer [Medium]
**File:** Multiple files in `game/strategy/`
**Tests:** `pytest tests/unit/strategy/ -n 12`

Standardize all `to_dict()` methods to return `Dict[str, Any]` (capitalized typing form for consistency with fleet.py pattern).

- [x] `game/strategy/data/planet.py:275`: `-> dict` -> `-> Dict[str, Any]` (add import if needed)
- [x] `game/strategy/data/stars.py:45,89`: `-> dict` -> `-> Dict[str, Any]`
- [x] `game/strategy/data/empire.py:134`: `-> dict` -> `-> Dict[str, Any]`
- [x] `game/strategy/data/galaxy.py:25,63,646`: `-> dict` -> `-> Dict[str, Any]`
- [x] `game/strategy/data/race_config.py:149`: `-> dict` -> `-> Dict[str, Any]`
- [x] `game/strategy/data/design_metadata.py:37`: `-> dict` -> `-> Dict[str, Any]`
- [x] `game/strategy/engine/game_session.py:263`: `-> dict` -> `-> Dict[str, Any]`
- [x] `game/strategy/engine/game_config.py:70,178`: `-> dict` -> `-> Dict[str, Any]`
- [x] `game/strategy/services/fleet_navigation_service.py:110`: `-> dict` -> `-> Dict[str, Any]`
- [x] For each file, ensure `from typing import Dict, Any` is imported
- [x] Leave `game/strategy/events/event_log.py` as-is (uses lowercase `dict[str, Any]` which is Python 3.9+ syntax - both are valid)
- [x] Verify: `pytest tests/unit/strategy/ -n 12` passes

**Notes:** Completed - All 12 `to_dict()` methods updated across 9 files. Added typing imports where needed.

---

### Task 2.6: Add Return Type Hints to BattleUIService Private Methods [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/ -v -k battle_ui`

- [x] Line ~121: `_convert_ship(self, ship)` -> add `-> ShipDTO`
- [x] Line ~200: `_convert_component(self, comp)` -> add `-> ComponentDTO`
- [x] Line ~232: `_convert_projectile(self, proj)` -> add `-> ProjectileDTO`
- [x] Line ~266: `_convert_beam(self, beam)` -> add `-> BeamDTO`
- [x] Verify: All DTO types already imported at top of file (ShipDTO, ComponentDTO, ProjectileDTO, BeamDTO)
- [x] Verify: `pytest tests/unit/ui/ -v` passes

**Notes:** All 4 methods already had return type hints. No changes needed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
