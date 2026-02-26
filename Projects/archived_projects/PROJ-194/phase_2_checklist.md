# Phase 2: Weapon & Ability Duck Typing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-194 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace getattr/hasattr on weapon abilities and ship sensor methods with direct access. These attributes always exist on their respective classes.

---

## Tasks

### Task 2.1: weapons_viewmodel.py — Ability property & ship method cleanup [Simple]
**File:** `game/ui/screens/builder/weapons_viewmodel.py`
**Tests:** `pytest tests/ --testmon`

Ship sensor method (always exists on Ship):
- [x] Line 304: `if hasattr(ship, 'get_total_sensor_score'):` → Already fixed in Phase 1!
- [x] Line 383: `if hasattr(ship, 'get_total_sensor_score'):` → Already fixed in Phase 1!
- [x] Line 474: `if hasattr(ship, 'get_total_sensor_score'):` → Already fixed in Phase 1!

BeamWeaponAbility properties (always present on BeamWeaponAbility):
- [x] Line 297: `getattr(ab, 'base_accuracy', 2.0)` → `ab.base_accuracy`
- [x] Line 298: `getattr(ab, 'accuracy_falloff', 0.001)` → `ab.accuracy_falloff`
- [x] Line 378: `getattr(ab, 'base_accuracy', 2.0)` → `ab.base_accuracy`
- [x] Line 379: `getattr(ab, 'accuracy_falloff', 0.001)` → `ab.accuracy_falloff`
- [x] Line 470: `getattr(ab, 'base_accuracy', 1.0)` → `ab.base_accuracy`
- [x] Line 471: `getattr(ab, 'accuracy_falloff', 0.0)` → `ab.accuracy_falloff`

WeaponAbility method (always inherited):
- [x] Line 396: `if hasattr(ab, 'get_damage'):` → Removed check, call `ab.get_damage(r)` directly
- [x] Verify: Run tests

**Notes:** All 6 base_accuracy/accuracy_falloff getattrs are guarded by `is_beam` checks, so `ab` is always a BeamWeaponAbility at those points. get_damage() is defined on WeaponAbility base class (line 192 of weapons.py).

---

### Task 2.2: components.py — Ability subtype checks [Simple]
**File:** `game/ui/screens/builder/components.py`
**Tests:** `pytest tests/ --testmon`

- [x] Line 123: `if hasattr(ab, 'base_accuracy'):` → `if c.has_ability('BeamWeaponAbility'):` (then access ab from beam ability)
- [x] Line 125: `if hasattr(ab, 'reload_time'):` → removed check (reload_time is always present on WeaponAbility base class)
- [x] Verify: Run tests

**Notes:** Line 123 is checking for beam-specific properties. The proper pattern is to use the existing `has_ability()` method which is the project convention.

---

### Task 2.3: stats_config.py — Component ability_instances hasattr removal [Simple]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/ --testmon`

- [x] Line 187: `if hasattr(comp, 'ability_instances'):` → removed check (Component.ability_instances is always initialized as [] in __init__)
- [x] Line 362: `if hasattr(comp, 'ability_instances'):` → removed check (same reason)
- [x] Verify: Run tests

**Notes:** Component.__init__ always sets `self.ability_instances = []` (component.py line 154).

---

### Task 2.4: modifier_impact_grid.py — Ability instance/class checks [Simple]
**File:** `game/ui/panels/modifier_impact_grid.py`
**Tests:** `pytest tests/ --testmon`

- [x] Line 165: `if not hasattr(component, 'ability_instances')` → removed check (always present)
- [x] Line 172: `if hasattr(ability_class, 'STAT_BINDINGS'):` → `if getattr(ability_class, 'STAT_BINDINGS', None):` (keep as getattr — STAT_BINDINGS is a class-level optional attribute, not all ability classes define it)
- [x] Verify: Run tests

**Notes:** Line 172 is a legitimate check — not all ability classes define STAT_BINDINGS. Converting hasattr → getattr with None default is the minimal safe change.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
