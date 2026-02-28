# Phase 3: Command Handler Consolidation

**Findings:** CQ-40, CQ-41, CQ-43, CQ-45, CQ-48
**Effort:** Medium
**Goal:** Eliminate command handler boilerplate (~400 lines)
**Status:** Complete

## Tasks

### 3.1 Extract MissionSetupHelper (CQ-40)
- [x] ~~Create `MissionSetupHelper` class~~ Already exists as `_setup_mission_move()` in superweapon_command_handlers.py
- [x] 5 mission handlers already use it (ImplodePlanet, StellerateStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere)
- [x] ColonizeMissionCommandHandler has unique population-loading logic - kept separate intentionally
- [N/A] Refactor ColonizeMissionCommandHandler to use helper - has specialized BUG-70 population loading
- [N/A] Write test for MissionSetupHelper - already tested via existing mission handler tests
- [x] Run full test suite

### 3.2 Enhance BaseCommandHandler resolution helpers (CQ-41, CQ-45)
- [x] Add `_resolve_fleet_required(session, fleet_id, empire_id=None)` that raises ValueError on error
- [x] Add `_resolve_planet_optional(session, planet_id, required=True)` helper
- [x] Write tests for new resolution helpers (6 tests)
- [x] Run full test suite

### 3.3 Extract movement order helper (CQ-43, CQ-48)
- [x] Create `add_move_order_if_needed(session, fleet, target_hex)` utility function
- [x] Write tests for add_move_order_if_needed (3 tests)
- [x] Refactor `TransferCommandHandler` to use helper
- [x] Refactor `WarpCommandHandler` to use helper
- [x] Run full test suite

## Completion Checklist
- [x] All tasks above completed
- [x] Full test suite passes: 12804 passed, 1 skipped
- [x] All command handlers verified to still pass their specific tests

## Implementation Notes

**Changes Made:**
1. Added `_resolve_fleet_required()` to BaseCommandHandler - raises ValueError instead of returning tuple
2. Added `_resolve_planet_optional()` to BaseCommandHandler - configurable required param
3. Added `add_move_order_if_needed()` as module-level helper function
4. Refactored TransferCommandHandler to use add_move_order_if_needed
5. Refactored WarpCommandHandler to use add_move_order_if_needed
6. Added 9 new unit tests

**Design Decision:**
- ColonizeMissionCommandHandler was NOT refactored to use _setup_mission_move because it has unique
  population auto-loading logic (BUG-70 fix) that doesn't fit the generic pattern. Keeping it
  separate is the cleaner design since it's the only handler with this behavior.

**Lines Saved:**
- ~20 lines per handler that uses add_move_order_if_needed
- New helpers enable future handlers to be more concise
