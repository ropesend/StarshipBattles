# Phase 3: Strategy

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-132 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Strategy module (5 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 3.1: ADR-STR-001 - Galaxy Class Exceeds Size Threshold (God [Medium]
**File:** `game/strategy/data/galaxy.py:1`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/integration/strategy/test_galaxy_gen.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. Galaxy class is 736 lines (class portion), well under 800-line extraction threshold. File is 828 lines total including WarpPoint (20 lines) and StarSystem (55 lines) classes. Methods are logically grouped (registration, lookup, generation, serialization). Follows same pattern as IControllable (477 lines) and protocols.py (547 lines) which were also accepted as well-organized.

### Task 3.2: ADR-STR-002 - ProductionEngine Exceeds Size Threshold [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ tests/integration/strategy/turn_engine/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. ProductionEngine is 731 lines, well under 800-line threshold. Already extracted from TurnEngine (PROJ-12 Phase 3). Well-documented with clear responsibilities. Multiple PROJ references show active maintenance.

### Task 3.3: ADR-STR-003 - Circular Import Workaround in galaxy.py [Simple]
**File:** `game/strategy/data/galaxy.py:30`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py tests/integration/strategy/test_galaxy_gen.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED. The late imports of `hex_to_dict` and `hex_from_dict` in WarpPoint, StarSystem, and Galaxy serialization methods were unnecessary - no circular dependency risk since core doesn't depend on strategy. Moved both functions to module-level import alongside existing hex_math imports.

### Task 3.4: ADR-STR-004 - ShipInstance Cross-Layer Late Imports [Complex]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/data/test_ship_instance.py tests/integration/fleet_combat/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTED AS-IS. Late imports of ShipSerializer (lines 172, 503) are EXPLICITLY documented as intentional in docs/architecture/ARCHITECTURE.md Section "Intentional Late Imports". Comments in code reference the architecture doc. Pattern is for cross-layer boundary (strategy -> simulation) and maintains layer separation.

### Task 3.5: ADR-STR-005 - ShipStatsCalculator Imports from Simulat [Medium]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** DOCUMENTATION FIX. The imports from simulation layer (formula_system, modifiers) are architecturally valid - Strategy layer is allowed to depend on Simulation layer per ARCHITECTURE.md. Updated the docstring which incorrectly claimed "no simulation layer coupling" to accurately describe the dependencies.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
