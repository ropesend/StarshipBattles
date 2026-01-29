# Phase 4: Simulation Engine Cleanup

**Status:** Complete
**Estimated Effort:** 5-7 hours
**Priority:** Medium-High

## Overview
Address issues in `game/simulation/` focusing on layer violations, incomplete implementations, and code quality.

> **Note:** This phase was reduced from 10 tasks to 9 after Category 3 audit verification:
> - Task 4.5 (NEW-SIM-009) REMOVED - Ship.py decomposition IS complete (uses mixins & composition)

---

## Tasks

### 4.1 Fix Component → System Layer Violation (NEW-SIM-005)
**Location:** `game/simulation/components/component.py:253, 297, 309`
**Effort:** Complex

- [x] Analyze runtime imports of `ResourceConsumption` from systems
- [x] Use duck typing instead of isinstance() to avoid layer violation
- [x] Replaced `isinstance(ability, ResourceConsumption)` with attribute checks
- [x] Run: `pytest tests/unit/simulation/ -v`

**Notes:** Fixed by using `getattr(ability, 'trigger', None)` and `getattr(ability, 'check_available', None)` instead of importing ResourceConsumption. The factory import at line 279 remains (architectural complexity).

---

### 4.2 Implement Mount Validation TODO (NEW-SIM-006)
**Location:** `game/simulation/systems/validator.py:70`
**Effort:** Medium

- [x] Implement full ship scan for missing mounts in `MountDependencyRule`
- [x] Check all mount users against available mounts
- [x] Return validation errors for broken dependencies
- [x] Add unit tests for mount dependency validation
- [x] Run: `pytest tests/unit/systems/test_validator.py -v`

**Notes:** Added `_validate_full_ship()` method that scans all layers for mount requirements. Created new test file `tests/unit/systems/test_mount_validation.py` with 6 test cases.

---

### 4.3 Implement Projectile Restoration TODO (NEW-SIM-007)
**Location:** `game/simulation/battle_controller.py:493`
**Effort:** Complex

- [x] Add projectile serialization to `BattleState.to_dict()` (already done)
- [x] Implement projectile deserialization in `load_battle_state()`
- [x] Add `to_projectile()` method to `ProjectileState`
- [x] Serialize: position, velocity, target, damage, owner
- [ ] Add integration test for battle save/load with projectiles (deferred)

**Notes:** Added `ProjectileState.to_projectile()` method and restoration logic in `BattleController.load_from_state()`. Resolves owner/target ship references via ship_id lookup.

---

### 4.4 Document Fleet Integration TODO (NEW-SIM-008)
**Location:** `game/simulation/battle_controller.py:650`
**Effort:** Simple (documentation only)

- [x] Add clear docstring explaining blocking dependency
- [x] Reference when `ShipInstance` integration will be available
- [x] Create issue/task to track completion

**Notes:** Added comprehensive docstring to `_apply_results_to_fleet()` explaining PROJ-41 dependency.

---

### ~~4.5 Address Ship God Class (NEW-SIM-009)~~
**Status:** REMOVED - ALREADY COMPLETE
**Reason:** Ship.py (793 lines) is no longer a god class. It now uses proper decomposition:
- `ShipPhysicsMixin` for physics and movement
- `ShipCombatMixin` for combat logic
- `ShipFormation` composition for formation management
- `ShipStatsCalculator` for stats calculation
- `ShipSerializer` for serialization

---

### 4.5 Fix Unused Variable (NEW-SIM-010)
**Location:** `game/simulation/entities/ship.py:55`
**Effort:** Simple

- [x] Review `hull_equipped` variable assignment
- [x] Added warning log when hull equip fails
- [x] Run: `pytest tests/unit/entities/test_ship.py -v`

**Notes:** Removed unused `hull_equipped` tracking variable, added `log_warning()` when default hull creation fails.

---

### 4.7 Add Missing Type Hints in stats.py (NEW-SIM-011)
**Location:** `game/simulation/systems/stats.py:452-460`
**Effort:** Simple

- [x] Add type hint to `_priority_sort_key(c: Any) -> int`
- [x] Add type hints to `_check_mass_limits(ship: Any) -> None`
- [x] Add type hints to `_get_ability_total(component_list: List[Any], ability_name: str) -> Union[int, float, bool]`
- [x] Added `from typing import Any, Dict, List, Union` import

---

### 4.8 Reduce getattr() Usage (NEW-SIM-012)
**Location:** `game/simulation/systems/stats.py:376, 487-491`
**Effort:** Medium

- [x] Identify all defensive `getattr()` calls for Ship attributes
- [x] Initialize `_prev_max_fuel`, `_prev_max_ammo`, `_prev_max_energy`, `_prev_max_shields` in Ship.__init__
- [x] Convert getattr() to direct attribute access in `_initialize_resources()`
- [x] Run: `pytest tests/unit/systems/test_stats.py -v`

**Notes:** Added 4 new attributes to Ship.__init__ and updated stats.py to use direct access.

---

## Verification

- [x] Run simulation tests: `pytest tests/unit/simulation/ -v`
- [x] Run integration tests: `pytest tests/integration/ -v`
- [x] Verify no circular imports in simulation layer

---

## Notes
- Task 4.1 (layer violation) and 4.3 (projectile restoration) were the most complex
- Tasks 4.5, 4.7 were quick wins within this phase
- All tests passing (163 tests)
