# Phase 3: Command Handler Consolidation

**Findings:** CQ-40, CQ-41, CQ-43, CQ-45, CQ-48
**Effort:** Medium
**Goal:** Eliminate command handler boilerplate (~400 lines)

## Tasks

### 3.1 Extract MissionSetupHelper (CQ-40)
- [ ] Create `MissionSetupHelper` class (or standalone function) in command handler module
- [ ] Implement `setup_mission_move(session, fleet, target_hex)` - shared mission move logic
- [ ] Refactor `ColonizeMissionCommandHandler` to use helper
- [ ] Refactor `ImplodePlanetMissionCommandHandler` to use helper
- [ ] Refactor `StellerateStarMissionCommandHandler` to use helper
- [ ] Refactor `OpenWarpPointMissionCommandHandler` to use helper
- [ ] Refactor `CloseWarpPointMissionCommandHandler` to use helper
- [ ] Refactor `CreateDysonSphereMissionCommandHandler` to use helper
- [ ] Write test for MissionSetupHelper
- [ ] Run full test suite

### 3.2 Enhance BaseCommandHandler resolution helpers (CQ-41, CQ-45)
- [ ] Add `_resolve_fleet_required(session, fleet_id)` that raises/returns on error
- [ ] Add `_resolve_planet_optional(session, planet_id, required=False)` helper
- [ ] Refactor command handlers to use enhanced helpers (prioritize handlers with most boilerplate)
- [ ] Standardize error messages for fleet/planet resolution
- [ ] Run full test suite

### 3.3 Extract movement order helper (CQ-43, CQ-48)
- [ ] Create `CommandHelper.add_move_order_if_needed(session, fleet, target_hex)` utility
- [ ] Refactor `ColonizeCommandHandler` to use helper
- [ ] Refactor `TransferCommandHandler` to use helper
- [ ] Refactor `WarpCommandHandler` to use helper
- [ ] Refactor mission handlers that queue move orders
- [ ] Run full test suite

## Completion Checklist
- [ ] All tasks above completed
- [ ] Full test suite passes
- [ ] All command handlers verified to still pass their specific tests
