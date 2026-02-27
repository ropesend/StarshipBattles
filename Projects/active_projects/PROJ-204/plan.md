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
| 2 | Quick Wins & Bug Fixes | CQ-42, CQ-44, CQ-50, CQ-26, CQ-27, CQ-07 | Simple | Pending |
| 3 | Command Handler Consolidation | CQ-40, CQ-41, CQ-43, CQ-45, CQ-48 | Medium | Pending |
| 4 | Strategy Layer Consolidation | CQ-02, CQ-22, CQ-23, CQ-06 | Medium | Pending |
| 5 | Workshop UI Cleanup | CQ-61, CQ-63, CQ-67, CQ-69, CQ-74 | Simple-Medium | Pending |

## Current Status
- **Phase:** Phase 1 Complete
- **Started:** 2026-02-27
- **Baseline Tests:** 12743 passed, 1 skipped
- **Current Tests:** 12778 passed, 1 skipped (+35 new tests)

## Phase 1 Summary
- Created `game/core/patterns/layer_iterator.py` with 4 utility functions
- Created `game/strategy/services/design_cost_calculator.py` for centralized cost calculation
- Refactored 8 files to use new utilities
- Added 35 new unit tests

## Decisions
See [decisions.md](decisions.md)
