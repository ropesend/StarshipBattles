# Phase 6: Simulation Deferred Import Elimination (AR-004, SIM-002)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Restructure simulation modules to eliminate circular dependency chains

---

## Prerequisites
- [x] Phase 5 complete (registry consolidation)

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

### Task 6.1: Analyze Ship Deferred Imports [Simple] - COMPLETE
**File:** `game/simulation/entities/ship.py`
**Tests:** N/A (analysis)

Document all deferred imports:
- [x] Line 262-263: `WeaponAbility, SeekerWeaponAbility` in max_weapon_range property
- [x] Line 517: `ModifierService` in add_component()
- [x] Line 558-559: `ModifierService` in add_components_bulk()
- [x] Line 588-589: `ShipStatsCalculator` in recalculate_stats()
- [x] Line 808: `ShipSerializer` in to_dict()
- [x] Line 827: `ShipSerializer` in from_dict()
- [x] Document why each deferred import exists
- [x] Add to findings/phase_6_analysis.md

**Notes:** Analysis complete. Found:
- Line 588 ShipStatsCalculator is REDUNDANT (already imported at line 15)
- ModifierService imports are acceptable (edge operations)
- ShipSerializer imports are acceptable (bidirectional coupling is inherent)
- WeaponAbility imports can use duck typing

---

### Task 6.2: Analyze Stats Deferred Imports [Simple] - COMPLETE
**File:** `game/simulation/systems/stats.py`
**Tests:** N/A (analysis)

Document all deferred imports:
- [x] Line 20: `ResourceStorage, ResourceGeneration` in calculate()
- [x] Line 172-173: `CombatPropulsion, ManeuveringThruster, etc.` in calculate()
- [x] Line 337: `ResourceConsumption` in _calculate_combat_endurance() (REDUNDANT)
- [x] Line 429: `WeaponAbility` in _calculate_combat_endurance()
- [x] Document why each deferred import exists
- [x] Add to findings/phase_6_analysis.md

**Notes:** Analysis complete. Found:
- Line 337 ResourceConsumption is REDUNDANT (already imported at line 173)
- ResourceStorage/ResourceGeneration can potentially be moved to module level
- Ability isinstance checks can use duck typing (code already uses get_abilities())

---

### Task 6.3: Create Modifier Applicator Interface [Medium] - SKIPPED
**File:** `game/simulation/interfaces/modifier_applicator.py` (NEW)
**Tests:** `pytest tests/unit/simulation/interfaces/`

- [x] DECISION: Skip interface creation

**Notes:** After analysis, IModifierApplicator interface is NOT RECOMMENDED:
- ModifierService deferred import is acceptable (edge operation, not hot path)
- Interface would add complexity without solving the root issue
- The coupling is legitimate (modifiers need component context)
- See findings/phase_6_analysis.md for full rationale

---

### Task 6.4: Refactor Ship-ModifierService Coupling [Complex] - COMPLETE
**Files:** `game/simulation/entities/ship.py`, `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship*.py`

**Strategy:** Document as intentional deferred import

- [x] DECISION: Option D - Keep deferred import (document as intentional)
- [x] Removed redundant ShipStatsCalculator import at line 588 (already at module level)
- [x] Run ship tests - 19 passed

**Notes:** ModifierService deferred imports in add_component/add_components_bulk are acceptable:
- Only called during component addition (edge operation, not hot path)
- The coupling is legitimate (modifiers need component context)
- Moving to module level would require significant refactoring with little benefit
- Will be documented as intentional in Task 6.7

---

### Task 6.5: Refactor Ship-Serializer Coupling [Medium] - COMPLETE
**Files:** `game/simulation/entities/ship.py`, `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship*.py`

**Current issue:** Ship.to_dict() and Ship.from_dict() import ShipSerializer

- [x] DECISION: Option C - Keep deferred import (document as intentional)
- [x] Serialization tests pass (verified in Task 6.4)

**Notes:** ShipSerializer deferred imports are acceptable:
- Serialization is inherently coupled to Ship (bidirectional dependency)
- Moving serialization into Ship would bloat the class
- External serialization (Option A) would break existing API
- Deferred import is a reasonable pattern for this I/O operation
- Will be documented as intentional in Task 6.7

---

### Task 6.6: Refactor Stats-Abilities Coupling [Medium] - COMPLETE
**Files:** `game/simulation/systems/stats.py`, `game/simulation/components/abilities.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py`

**Current issue:** Stats calculation imports ability types for isinstance checks

- [x] Moved ResourceStorage, ResourceGeneration, ResourceConsumption to module level
- [x] Removed redundant import at line 172-173 (abilities already used via get_abilities)
- [x] Removed redundant import at line 337 (ResourceConsumption)
- [x] Removed unnecessary WeaponAbility import at line 429 (code uses get_abilities)
- [x] Run stats tests - 6 passed
- [x] Run all entity tests - 302 passed

**Notes:** Successfully eliminated 4 deferred imports from stats.py by moving
ResourceStorage/ResourceGeneration/ResourceConsumption to module level. The ability
type imports (CombatPropulsion, etc.) were not needed because the code uses
`comp.get_abilities('CombatPropulsion')` which is name-based, not isinstance-based.

---

### Task 6.7: Document Intentional Late Imports [Simple] - COMPLETE
**File:** `docs/ARCHITECTURE.md`
**Tests:** N/A

- [x] Update architecture doc with remaining intentional late imports
- [x] Document why they can't be eliminated
- [x] Add code comments in ship.py for intentional late imports

**Notes:** Updated docs/ARCHITECTURE.md with detailed section on Ship module late imports:
- WeaponAbility/SeekerWeaponAbility in max_weapon_range (avoids circular with abilities)
- ModifierService in add_component/add_components_bulk (edge operation)
- ShipSerializer in to_dict/from_dict (bidirectional dependency)

Added INTENTIONAL LATE IMPORT comments in ship.py at lines 262, 519, 562, 813, 834

---

### Task 6.8: Integration Testing [Simple] - COMPLETE
**Tests:** `pytest tests/integration/`

- [x] Run integration tests: 192 passed
- [x] Run entity tests: 302 passed
- [x] Run full test suite: 5290 passed, 1 skipped

**Notes:** All tests passing after Phase 6 refactoring.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Deferred imports reduced (5 eliminated, 5 documented as intentional)
- [x] Remaining late imports documented in docs/ARCHITECTURE.md
- [x] IModifierApplicator interface SKIPPED (not recommended after analysis)
- [x] All tests pass: 5290 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 7
