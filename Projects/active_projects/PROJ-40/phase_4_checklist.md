# Phase 4: Simulation Engine Cleanup

**Status:** Not Started
**Estimated Effort:** 6-8 hours
**Priority:** Medium-High

## Overview
Address issues in `game/simulation/` focusing on layer violations, incomplete implementations, and god class patterns.

---

## Tasks

### 4.1 Fix Component → System Layer Violation (NEW-SIM-005)
**Location:** `game/simulation/components/component.py:253, 297, 309`
**Effort:** Complex

- [ ] Analyze runtime imports of `ResourceConsumption` from systems
- [ ] Create `IResourceConsumption` interface in `game/simulation/interfaces.py`
- [ ] Move ability instantiation to factory pattern
- [ ] Pass dependencies through constructor, not runtime import
- [ ] Update all callers of `_instantiate_abilities()`
- [ ] Run: `pytest tests/unit/simulation/ -v`

---

### 4.2 Implement Mount Validation TODO (NEW-SIM-006)
**Location:** `game/simulation/systems/validator.py:70`
**Effort:** Medium

- [ ] Implement full ship scan for missing mounts in `MountDependencyRule`
- [ ] Check all mount users against available mounts
- [ ] Return validation errors for broken dependencies
- [ ] Add unit tests for mount dependency validation
- [ ] Run: `pytest tests/unit/systems/test_validator.py -v`

---

### 4.3 Implement Projectile Restoration TODO (NEW-SIM-007)
**Location:** `game/simulation/battle_controller.py:493`
**Effort:** Complex

- [ ] Add projectile serialization to `BattleState.to_dict()`
- [ ] Implement projectile deserialization in `load_battle_state()`
- [ ] Serialize: position, velocity, target, damage, owner
- [ ] Add integration test for battle save/load with projectiles
- [ ] Run: `pytest tests/integration/test_save_load.py -v`

---

### 4.4 Document Fleet Integration TODO (NEW-SIM-008)
**Location:** `game/simulation/battle_controller.py:650`
**Effort:** Simple (documentation only)

- [ ] Add clear docstring explaining blocking dependency
- [ ] Reference when `ShipInstance` integration will be available
- [ ] Create issue/task to track completion
- [ ] Or implement if `ShipInstance` is now available

---

### 4.5 Address Ship God Class (NEW-SIM-009)
**Location:** `game/simulation/entities/ship.py:34` (793 lines)
**Effort:** Complex (partial in this phase)

This is a large refactoring effort. In this phase:
- [ ] Document current Ship responsibilities
- [ ] Identify extraction candidates:
  - [ ] `ShipComponentManager` (already exists - verify usage)
  - [ ] `ShipStatsCalculator` (extract stat calculation)
  - [ ] `ShipSerializer` (extract serialization)
- [ ] Create extraction plan in `decisions.md`
- [ ] Extract ONE responsibility as proof of concept
- [ ] Run: `pytest tests/unit/entities/test_ship.py -v`

---

### 4.6 Fix Unused Variable (NEW-SIM-010)
**Location:** `game/simulation/entities/ship.py:55`
**Effort:** Simple

- [ ] Review `hull_equipped` variable assignment
- [ ] Either use it for validation or remove it
- [ ] If keeping, add error handling for failed hull equip
- [ ] Run: `pytest tests/unit/entities/test_ship.py -v`

---

### 4.7 Add Missing Type Hints in stats.py (NEW-SIM-011)
**Location:** `game/simulation/systems/stats.py:452-460`
**Effort:** Simple

- [ ] Add type hint to `_priority_sort_key(c: Component) -> int`
- [ ] Add type hints to `_check_mass_limits()`
- [ ] Add type hints to `_get_ability_total()`
- [ ] Run mypy if available

---

### 4.8 Reduce getattr() Usage (NEW-SIM-012)
**Location:** `game/simulation/systems/stats.py:376, 487-491`
**Effort:** Medium

- [ ] Identify all defensive `getattr()` calls for Ship attributes
- [ ] Ensure Ship.__init__ initializes all expected attributes
- [ ] Convert getattr() to direct attribute access where safe
- [ ] Add type hints to document expected attributes
- [ ] Run: `pytest tests/unit/systems/test_stats.py -v`

---

## Verification

- [ ] Run simulation tests: `pytest tests/unit/simulation/ -v`
- [ ] Run integration tests: `pytest tests/integration/ -v`
- [ ] Verify no circular imports in simulation layer

---

## Notes
- Task 4.1 (layer violation) and 4.5 (god class) are the most complex
- Consider splitting 4.5 into a separate PROJ for full Ship decomposition
- Tasks 4.6, 4.7 are quick wins within this phase
- Document all design decisions in `decisions.md`
