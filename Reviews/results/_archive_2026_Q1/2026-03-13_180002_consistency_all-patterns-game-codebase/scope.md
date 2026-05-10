# Review Scope: 2026-03-13_180002_consistency_all-patterns-game-codebase

## Metadata
- **Date:** 2026-03-13 18:00
- **Type:** Consistency Review
- **Description:** all-patterns-game-codebase

## Scope Definition

### Target
- [x] Specific directory: `game/`
- **Files:** 429 Python files, ~95,083 lines
- **Subdirectories:** core/, simulation/, strategy/, ai/, ui/

### Priorities
- All pattern categories: error handling, logging, data access, API/interface, naming, file/module organization, testing patterns, configuration
- Goal: Find inconsistencies and recommend standardization

### Exclusions
- tests/ directory (not in scope)
- Projects/, Reviews/ directories
- Non-Python files

## Agent Configuration
**Recommended Agents:** 4 (script) → 6 (user choice, thorough)
**Confirmed Agent Count:** 6

### Selected Agents
| Agent | Role | Finding Prefix | Status |
|-------|------|----------------|--------|
| Pattern Cataloguer | Document all patterns in use | PC | Pending |
| Inconsistency Hunter | Find deviations from common patterns | IH | Pending |
| Style Analyzer | Coding style consistency | SA | Pending |
| Convention Enforcer | Structural conventions | CE | Pending |
| Code Quality Analyst | Quality implications of inconsistencies | CQ | Pending |
| Architecture Reviewer | Architectural pattern consistency | AR | Pending |

## Reference Points
- CLAUDE.md documents architectural principles and key patterns
- Registry Pattern, Ability System, Hull as Component, Two-Stage Aggregation
- Layer separation: Core → Simulation → Strategy → UI
