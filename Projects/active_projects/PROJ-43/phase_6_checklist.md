# Phase 6: Simulation Deferred Import Elimination (AR-004, SIM-002)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Restructure simulation modules to eliminate circular dependency chains

---

## Prerequisites
- [ ] Phase 5 complete (registry consolidation)

## Background

**Problem:** Multiple deferred imports (inside function bodies) in simulation layer:
- `game/simulation/entities/ship.py` - 4+ deferred imports
- `game/simulation/systems/stats.py` - 3+ deferred imports

**Key Circular Chains:**
- Ship ↔ ModifierService: Ship adds modifiers, ModifierService validates with Ship
- Ship ↔ ShipSerializer: Serialization needs Ship, Ship needs serialization
- ShipStatsCalculator ↔ Abilities: Stats calculation imports abilities

---

## Tasks

### Task 6.1: Analyze Ship Deferred Imports [Simple]
**File:** `game/simulation/entities/ship.py`
**Tests:** N/A (analysis)

Document all deferred imports:
- [ ] Line 262-263: `WeaponAbility, SeekerWeaponAbility` in max_weapon_range property
- [ ] Line 517: `ModifierService` in add_component()
- [ ] Line 558-559: `ModifierService` in add_components_bulk()
- [ ] Line 588-589: `ShipStatsCalculator` in recalculate_stats()
- [ ] Line 808: `ShipSerializer` in to_dict()
- [ ] Line 827: `ShipSerializer` in from_dict()
- [ ] Document why each deferred import exists
- [ ] Add to findings/phase_6_analysis.md

**Notes:**

---

### Task 6.2: Analyze Stats Deferred Imports [Simple]
**File:** `game/simulation/systems/stats.py`
**Tests:** N/A (analysis)

Document all deferred imports:
- [ ] Line 20: `ResourceStorage, ResourceGeneration` in calculate()
- [ ] Line 172-173: `CombatPropulsion, ManeuveringThruster, etc.` in calculate()
- [ ] Line 429: `WeaponAbility` in _calculate_combat_endurance()
- [ ] Document why each deferred import exists
- [ ] Add to findings/phase_6_analysis.md

**Notes:**

---

### Task 6.3: Create Modifier Applicator Interface [Medium]
**File:** `game/simulation/interfaces/modifier_applicator.py` (NEW)
**Tests:** `pytest tests/unit/simulation/interfaces/`

- [ ] Create `game/simulation/interfaces/` directory
- [ ] Create `IModifierApplicator` protocol:
  - `apply_modifier(component, modifier_id, params)`
  - `remove_modifier(component, modifier_id)`
  - `get_component_modifiers(component)`
- [ ] Create unit tests for interface

**Notes:**

---

### Task 6.4: Refactor Ship-ModifierService Coupling [Complex]
**Files:** `game/simulation/entities/ship.py`, `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship*.py`

**Strategy:** Use mediator pattern or deferred initialization

- [ ] Option A: Move modifier application to ship initialization
- [ ] Option B: Pass ModifierService to Ship via constructor
- [ ] Option C: Create ModifierApplicationMediator
- [ ] Choose approach and implement
- [ ] Move `ModifierService` imports to module level
- [ ] Verify no circular import at module load time
- [ ] Run ship tests

**Notes:**

---

### Task 6.5: Refactor Ship-Serializer Coupling [Medium]
**Files:** `game/simulation/entities/ship.py`, `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship*.py`

**Current issue:** Ship.to_dict() and Ship.from_dict() import ShipSerializer

- [ ] Option A: Make serialization external (ShipSerializer.serialize(ship))
- [ ] Option B: Move serialization to Ship module (avoid separate file)
- [ ] Option C: Keep deferred import (document as intentional)
- [ ] Choose approach and implement
- [ ] Run serialization tests

**Notes:**

---

### Task 6.6: Refactor Stats-Abilities Coupling [Medium]
**Files:** `game/simulation/systems/stats.py`, `game/simulation/components/abilities.py`
**Tests:** `pytest tests/unit/simulation/systems/test_stats*.py`

**Current issue:** Stats calculation imports ability types for isinstance checks

- [ ] Option A: Use protocol/interface instead of isinstance
- [ ] Option B: Move ability type imports to module level with TYPE_CHECKING
- [ ] Option C: Keep deferred imports (document as intentional)
- [ ] Choose approach and implement
- [ ] Run stats tests

**Notes:**

---

### Task 6.7: Document Intentional Late Imports [Simple]
**File:** `docs/ARCHITECTURE.md`
**Tests:** N/A

- [ ] Update architecture doc with any remaining intentional late imports
- [ ] Document why they can't be eliminated
- [ ] Add code comments in files with intentional late imports

**Notes:**

---

### Task 6.8: Integration Testing [Simple]
**Tests:** `pytest tests/integration/simulation/`

- [ ] Run simulation integration tests
- [ ] Verify ship creation works
- [ ] Verify modifier application works
- [ ] Verify save/load works
- [ ] Run full test suite

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Deferred imports reduced (some may remain as intentional)
- [ ] Remaining late imports documented
- [ ] IModifierApplicator interface created
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
