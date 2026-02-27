# Review Scope: 2026-02-27_141256_general_strategy-workshop-duplication

## Metadata
- **Date:** 2026-02-27 14:12
- **Type:** General Review
- **Description:** strategy-workshop-duplication

## Scope Definition

### Target
- [x] Specific directory: `game/strategy/` (107 files, ~24.6k lines)
- [x] Specific directory: `game/ui/screens/builder/` + workshop/design files (37 files)

### Priorities
- Code duplication and consolidation opportunities
- Copy-paste code / similar functions
- Parallel implementations of similar logic
- Opportunities for shared abstractions
- Cross-layer duplication between strategy and UI

### Exclusions
- All test code
- Non-strategy/workshop production code
- UI rendering-only concerns (only logic duplication)

## Agent Configuration
**Recommended Agents:** 6
**Confirmed Agent Count:** 6

### Selected Agents
| Agent | Role | Status |
|-------|------|--------|
| strategy_fleet_ships | Strategy: Fleet & Ships DRY Analyst | Pending |
| strategy_galaxy_economy | Strategy: Galaxy, Planets & Economy DRY Analyst | Pending |
| strategy_session_turns | Strategy: Session & Turn Logic DRY Analyst | Pending |
| workshop_builder | Workshop/Builder DRY Analyst | Pending |
| cross_layer_duplication | Cross-Layer Duplication Hunter | Pending |
| architecture_consolidation | Architecture Consolidation Reviewer | Pending |
