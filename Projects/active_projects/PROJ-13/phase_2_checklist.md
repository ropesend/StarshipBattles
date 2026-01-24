# Phase 2: Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-13 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add documentation to critical classes and methods
**Priority:** MAJOR - Wait for PROJ-11 completion

---

## Tasks

### Task 2.1: DOC-02 - Document Ship Class [High]
**File:** `game/simulation/entities/ship.py` (1000+ lines)
**Tests:** N/A (documentation only)

**Issue:** Core game entity with ~50 public methods, minimal docstrings.

**Implementation:**
- [ ] Add comprehensive class docstring explaining:
  - Ship architecture (mixins: PhysicsBody, ShipCombatMixin, ShipPhysicsMixin)
  - Layer/component system overview
  - State management approach
  - Usage examples
- [ ] Add docstrings to public methods:
  - `update()` - what does context contain?
  - `add_component()` - validation rules, failure modes
  - `recalculate_stats()` - when to call, side effects
  - `get_components_by_ability()` - usage pattern
- [ ] Document initialization sequence
- [ ] Add type hints to undocumented parameters

**Notes:** 4-6 hours. High value for future maintainability.

---

### Task 2.2: DOC-06 - Document Component Architecture [High]
**File:** `game/simulation/components/component.py` (600+ lines)
**Tests:** N/A (documentation only)

**Issue:** Central class with complex ability/modifier system, no architecture docs.

**Implementation:**
- [ ] Add class docstring explaining:
  - What is a Component?
  - Ability system overview (ability_instances)
  - Modifier system (v2 format, formulas)
  - Damage threshold mechanism
  - Stat calculation contract
- [ ] Document key methods:
  - `_instantiate_abilities()` - lifecycle
  - `apply_modifiers()` - precedence rules
  - `recalculate_stats()` - phase overview
- [ ] Add usage examples
- [ ] Document modifier JSON schema

**Notes:** 3-4 hours. Critical for anyone extending component system.

---

### Task 2.3: DOC-04 - Add Type Hints to Critical Methods [Medium]
**Files:** Multiple (40+ methods missing return types)
**Tests:** Run mypy after changes

**Issue:** Many public methods lack return type hints.

**Priority Files:**
- [ ] `game/simulation/battle_controller.py` (8+ methods)
- [ ] `game/strategy/engine/turn_engine.py` (5+ methods)
- [ ] `game/simulation/entities/ship.py` (15+ methods)
- [ ] `game/simulation/components/component.py` (12+ methods)

**Implementation:**
- [ ] Add return type hints to all public methods in priority files
- [ ] Use Optional[] for nullable returns
- [ ] Use Union[] for multiple return types
- [ ] Run mypy to verify
- [ ] Fix any type errors discovered

**Notes:** 3-4 hours. Enables IDE support and static analysis.

---

### Task 2.4: DOC-01 - Add Module Documentation [Medium]
**Files:** 15 files missing module docstrings

**Issue:** No module-level documentation explaining purpose.

**Implementation:**
- [ ] Add module docstrings to key files:
  - `game/simulation/designs.py`
  - `game/simulation/entities/projectile.py`
  - `game/simulation/formula_system.py`
  - Other files identified in review
- [ ] Explain module purpose, key exports, usage patterns

**Notes:** 2-3 hours. Lower priority than class docs.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Ship class fully documented
- [ ] Component class fully documented
- [ ] Type hints on 40+ methods
- [ ] Module docstrings added
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
