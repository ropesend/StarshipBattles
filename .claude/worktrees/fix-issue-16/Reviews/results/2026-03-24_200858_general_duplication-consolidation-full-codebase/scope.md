# Review Scope: Duplication & Consolidation - Full Codebase

## Metadata
- **Date:** 2026-03-24
- **Type:** General Review
- **Description:** Find all duplicated functionality across 110K LOC vibe-coded codebase

## Scope Definition

### Target
- [x] Entire codebase: `game/` (439 files, ~110K LOC)

### Priorities
1. Copy-pasted functions/methods across files
2. Similar classes that should share a base class
3. Duplicate systems doing the same thing
4. Repeated utility logic that should be extracted
5. Near-identical implementations that could be consolidated

### Exclusions
- `tests/`, `simulation_tests/`

## Agent Configuration
**Confirmed Agent Count:** 12

### Selected Agents
| # | Agent | Scope | Status |
|---|-------|-------|--------|
| 1 | UI Screens Duplication | `game/ui/screens/` | Pending |
| 2 | UI Components & Widgets | `game/ui/components/`, `widgets/`, `panels/`, `utils/` | Pending |
| 3 | UI Services & Renderer | `game/ui/services/`, `renderer/`, `orchestration/`, `research/` | Pending |
| 4 | Strategy Data | `game/strategy/data/` | Pending |
| 5 | Strategy Engine | `game/strategy/engine/`, `facade/`, `events/` | Pending |
| 6 | Strategy Services & Gen | `game/strategy/services/`, `generation/`, `systems/`, etc. | Pending |
| 7 | Simulation Entities | `game/simulation/entities/`, `interfaces/` | Pending |
| 8 | Simulation Components | `game/simulation/components/` | Pending |
| 9 | Simulation Systems & Svc | `game/simulation/systems/`, `services/`, `combat/`, etc. | Pending |
| 10 | Core & Engine & AI | `game/core/`, `engine/`, `ai/`, `research/`, `assets/` | Pending |
| 11 | Cross-Layer Hunter | Full `game/` - cross-layer duplication | Pending |
| 12 | Pattern & Abstraction | Full `game/` - shared abstraction opportunities | Pending |
