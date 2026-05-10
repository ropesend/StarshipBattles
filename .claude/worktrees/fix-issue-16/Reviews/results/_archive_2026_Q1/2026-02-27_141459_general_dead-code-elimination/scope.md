# Review Scope: Dead Code Elimination

## Metadata
- **Date:** 2026-02-27
- **Type:** General Review
- **Description:** Comprehensive dead code identification across all production code

## Scope Definition

### Target
- [x] Entire production codebase: `game/` directory
- **Files:** 418 Python files, ~87,000 lines

### Priorities
- Unused imports
- Unreachable code
- Commented-out code
- Orphaned files (never imported/used)
- Unused functions, classes, methods
- Dead feature flags
- Unused variables and parameters

### Exclusions
- All test code (`tests/`, `simulation_tests/`)
- `__pycache__` directories
- Non-Python files (JSON data, images, etc.)

## Agent Configuration
**Confirmed Agent Count:** 7

### Selected Agents
| # | Agent | Scope | Files | Status |
|---|-------|-------|-------|--------|
| 1 | DC - UI Screens | `game/ui/screens/` | 126 | Pending |
| 2 | DC - UI Infrastructure | `game/ui/` (non-screens) | 68 | Pending |
| 3 | DC - Strategy | `game/strategy/` | 107 | Pending |
| 4 | DC - Simulation | `game/simulation/` | 73 | Pending |
| 5 | DC - Small Modules | core, ai, engine, research, assets | 41 | Pending |
| 6 | Cross-Module Orphan Finder | All `game/` | 418 | Pending |
| 7 | Unused Imports Sweeper | All `game/` | 418 | Pending |
