# PROJ-204: Strategy & Workshop Duplication Consolidation

## Overview
Consolidate duplicated code across the strategy layer and design workshop UI identified by the general code review (2026-02-27).

**Source Review:** `Reviews/results/2026-02-27_141256_general_strategy-workshop-duplication/report.md`

## Goals
1. Eliminate the highest-impact code duplication in strategy and workshop layers
2. Create shared utilities and abstractions where multiple modules implement the same logic
3. Standardize patterns (layer iteration, command handling, UI panel setup)
4. Fix latent bugs found during review (path stripping, field name inconsistency)

## Scope
- `game/strategy/` - strategy layer production code
- `game/ui/screens/builder/` + workshop/design files - workshop UI code
- `game/core/` - new shared utilities

## Non-Goals
- Test code changes (except to match refactored APIs)
- Full architectural overhaul (AR-01, AR-03, AR-04, AR-05 deferred)
- Cross-layer design loading refactor (CQ-81 deferred - medium risk)

## Phase Structure

| Phase | Focus | Findings | Effort | Status |
|-------|-------|----------|--------|--------|
| 1 | Foundation Utilities | AR-02, CQ-20, CQ-21, CQ-82 | Medium | Complete |
| 2 | Quick Wins & Bug Fixes | CQ-42, CQ-44, CQ-50, CQ-26, CQ-27, CQ-07 | Simple | Complete |
| 3 | Command Handler Consolidation | CQ-40, CQ-41, CQ-43, CQ-45, CQ-48 | Medium | Complete |
| 4 | Strategy Layer Consolidation | CQ-02, CQ-22 | Medium | Complete |
| 5 | Workshop UI Cleanup | CQ-61, CQ-63, CQ-67, CQ-69, CQ-74 | Simple-Medium | Pending |

## Current Status
- **Phase:** Phase 4 Complete
- **Started:** 2026-02-27
- **Baseline Tests:** 12743 passed, 1 skipped
- **Current Tests:** 12815 passed, 1 skipped (+72 new tests total)

## Phase 1 Summary
- Created `game/core/patterns/layer_iterator.py` with 4 utility functions
- Created `game/strategy/services/design_cost_calculator.py` for centralized cost calculation
- Refactored 8 files to use new utilities
- Added 35 new unit tests

## Phase 2 Summary
- Created `strip_start_hex()` in `pathfinding.py` - fixes path stripping bug (CQ-42)
- Created `get_tick_interval()` in `fleet_speed_calculator.py` - centralizes formula (CQ-44)
- Fixed O(N) empire lookup in `TransferCommandHandler` (CQ-50)
- Added `_register_zones_from_system()` and `_rebuild_warp_point_index()` to Galaxy (CQ-26, CQ-27)
- Added `_accumulate_ship_costs()` to FleetResourceAggregator (CQ-07)
- Added 17 new unit tests

## Phase 3 Summary
- Added `_resolve_fleet_required()` to BaseCommandHandler - raises ValueError instead of tuple return
- Added `_resolve_planet_optional()` to BaseCommandHandler - configurable required parameter
- Added `add_move_order_if_needed()` module-level helper for auto-queuing MOVE orders
- Refactored TransferCommandHandler and WarpCommandHandler to use new helper
- Note: ColonizeMissionCommandHandler kept separate due to unique BUG-70 population loading
- Added 9 new unit tests

## Phase 4 Summary
- Added `_verify_and_consume_resources()` to FleetResourceAggregator - generic resource verify/consume
- Refactored 4 methods to use generic helper (movement + warp, check + consume)
- Added `deserialize_list()` to `game/core/json_utils.py` - resilient list deserialization
- Refactored StarSystem.from_dict() (4 loops) and Planet.from_dict() (2 loops)
- Fixed 5 pre-existing cargo test bugs (incorrect mock attribute)
- Added 20 new unit tests (9 for resource aggregator, 11 for deserialize_list)
- Deferred CQ-23 and CQ-06 (lower priority, existing code works)

## Decisions
See [decisions.md](decisions.md)
