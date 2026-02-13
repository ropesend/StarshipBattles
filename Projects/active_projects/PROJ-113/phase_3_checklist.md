# Phase 3: Strategy

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-113 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Strategy module (8 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 3.1: ADR-STR-008 - ShipDisplayFormatter in Strategy Data Layer [Medium]
**File:** `game/strategy/data/ship_display_formatter.py`
**Tests:** `pytest tests/unit/strategy/test_ship_display_formatter.py`

- [x] Investigate the issue at the specified location
- [x] Document architectural justification (no code change needed)
- [x] Verify: tests pass, no regressions

**Notes:** DOCUMENTED - ShipDisplayFormatter stays in strategy layer because:
1. Moving to UI would create circular dependency (ShipInstance imports it)
2. No pygame/UI framework dependencies - pure string formatting
3. Documented in module docstring with architectural rationale
4. Original decision (PROJ-87): "Avoid circular dependency between strategy data and UI layers"

### Task 3.2: ADR-STR-011 - hex_to_pixel/pixel_to_hex Usage in Galaxy [Simple]
**File:** `game/strategy/data/galaxy.py:5`
**Tests:** `pytest tests/unit/strategy/test_galaxy.py`

- [x] Investigate the issue at the specified location
- [x] Add clarifying comment
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Added comment explaining these are used for geometric calculations (angles, distances), not rendering.

### Task 3.3: ADR-STR-001 - Pervasive Lazy Imports to Avoid Circular [Complex]
**File:** Multiple files (63+ lazy imports)
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Fix design_library.py logger imports (10 lazy imports → 1 module-level)
- [x] Document remaining intentional lazy imports

**Notes:** PARTIALLY FIXED - Moved all logger imports in design_library.py to module level (removed 10 unnecessary lazy imports). Other lazy imports are intentional for circular dependency avoidance - already documented in ARCHITECTURE.md.

### Task 3.4: ADR-STR-002 - Galaxy Circular Dependency with Placement [Medium]
**File:** `game/strategy/data/galaxy.py:354-356`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Verify lazy import is intentional and documented

**Notes:** FALSE POSITIVE - The lazy import in generate_star_systems() is intentional and already documented with comment "Import here to avoid circular dependency". This is an accepted pattern per ARCHITECTURE.md.

### Task 3.5: ADR-STR-007 - FleetBattleAdapter Accesses Private Method [Simple]
**File:** `game/strategy/data/fleet_battle_adapter.py:124`
**Tests:** `pytest tests/unit/strategy/test_fleet_battle_adapter.py`

- [x] Investigate the issue at the specified location
- [x] Rename _trigger_speed_recalculation() to trigger_speed_recalculation()
- [x] Update all callers (Fleet internal + FleetBattleAdapter)
- [x] Update test mock
- [x] Update ARCHITECTURE.md reference
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Renamed to public method since external delegates legitimately need to trigger recalculation.

### Task 3.6: ADR-STR-009 - Color Tuples Embedded in Strategy Game Config [Medium]
**File:** `game/strategy/engine/game_config.py:26-31`
**Tests:** `pytest tests/unit/strategy/test_game_config.py`

- [x] Investigate the issue at the specified location
- [x] Document architectural rationale

**Notes:** DOCUMENTED - Added comment explaining colors are game-semantic identifiers stored in save games. Moving to UI would require save format changes. Colors are intentionally simple RGB tuples (not pygame types).

### Task 3.7: ADR-STR-013 - EmpireEconomyCalculator Provides "Display-Ready" [Simple]
**File:** `game/strategy/engine/empire_economy_calculator.py`
**Tests:** `pytest tests/unit/strategy/test_empire_economy_calculator.py`

- [x] Investigate the issue at the specified location
- [x] Update documentation to remove "display-ready" qualifier
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Removed "display-ready" from docstrings. Now documented as "snapshot of empire economic state".

### Task 3.8: ADR-STR-012 - DesignMetadata Contains sprite_preview Field [Simple]
**File:** `game/strategy/data/design_metadata.py:35`
**Tests:** N/A (info-only)

- [x] Investigate the issue at the specified location
- [x] Add preventive comment for future implementers
- [x] Verify: tests pass, no regressions

**Notes:** DOCUMENTED (PREVENTIVE) - Added comment noting that when sprite_preview is implemented, the preview image should be stored in a separate UI cache, not in strategy-layer metadata.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
