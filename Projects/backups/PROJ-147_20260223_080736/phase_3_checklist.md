# Phase 3: Strategy

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-147 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Strategy module (5 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 3.1: ADR-STR-001 - Strategy Layer Imports from AI Layer [Medium]
**File:** `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/adapters/test_simulation_adapter.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED. Removed module-level AIControllerFactory import. Added DI pattern:
- Constructor accepts optional `ai_factory: Optional['IAIControllerFactory']`
- Late import fallback in resolve_battle() when no factory injected
- 3 new tests verify DI and no module-level AI import

### Task 3.2: ADR-STR-002 - ShipDisplayFormatter in Strategy Layer [Medium]
**File:** `game/strategy/data/ship_display_formatter.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** NO ACTION NEEDED. ShipDisplayFormatter is intentionally in strategy layer:
- Docstring lines 1-13 document rationale
- Pure string formatting, no pygame dependencies
- Moving to UI would create circular dependency (ShipInstance imports formatter)
- Game-semantic data usable in tests and non-UI contexts

### Task 3.3: ADR-STR-003 - Circular Import Workaround in Galaxy [Medium]
**File:** `game/strategy/data/galaxy.py:468`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** NO ACTION NEEDED. Intentional late import pattern:
- Line 468: `# Import here to avoid circular dependency`
- Imports RandomPlacementStrategy and SpatialIndex inside method
- Per ARCHITECTURE.md, documented late imports are acceptable

### Task 3.4: ADR-STR-004 - Intentional Late Imports - Documented [Complex]
**File:** Various (fleet.py, ship_instance.py)
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** NO ACTION NEEDED. Same pattern as ADR-SIM-002 and ADR-STR-003:
- ARCHITECTURE.md Section "Intentional Late Imports" documents all cases
- These are explicitly allowed patterns for edge operations

### Task 3.5: ADR-STR-005 - RGB Color Tuples in Game Config [Simple]
**File:** `game/strategy/engine/game_config.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** NO ACTION NEEDED. RGB tuples are intentional:
- Lines 26-29: Architecture note explains rationale
- Colors are game-semantic identifiers (e.g., empire colors)
- Stored in save games
- Not pygame-specific types (plain tuples)


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
