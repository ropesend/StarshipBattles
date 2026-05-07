# Review Scope: 2026-03-13_173626_consistency_all-patterns-game-codebase

## Metadata
- **Date:** 2026-03-13 17:36
- **Type:** Consistency Review
- **Description:** all-patterns-game-codebase

## Scope Definition
Full consistency review of the entire game/ codebase, all pattern categories, focused on finding cleanup targets for a future standardization project.

### Target
- [x] Entire codebase: `game/` directory
- 429 Python files, ~95K lines
- Layers: core/, simulation/, strategy/, ai/, ui/

### Priorities
- Find cleanup targets — identify inconsistencies worth fixing
- Catalog dominant patterns vs. outlier patterns
- Prep for a standardization project

### Pattern Categories
- Error handling patterns
- Logging patterns
- Data access patterns
- API/interface patterns
- Naming conventions
- File/module organization
- Testing patterns
- Configuration patterns

### Reference Points
- CLAUDE.md conventions (type hints, docstrings, small functions, named constants)
- Registry pattern (centralized component/ship/planet registration)
- Ability system (component abilities with stacking rules)
- Two-stage aggregation pattern
- Layer separation (Core → Simulation → Strategy → UI)

### Exclusions
- tests/ directory (unless testing patterns need cross-reference)
- Projects/ and Reviews/ infrastructure

## Agent Configuration
**Recommended Agents:** 6
**Confirmed Agent Count:** 6

### Selected Agents
| Agent | Role | Finding Prefix | Status |
|-------|------|----------------|--------|
| Pattern Cataloguer | Document all patterns in use | PC | Pending |
| Inconsistency Hunter | Find deviations from common patterns | IH | Pending |
| Style Analyzer | Coding style consistency | SA | Pending |
| Convention Enforcer | Structural conventions | CE | Pending |
| Architecture Reviewer | Cross-layer pattern consistency | AR | Pending |
| Code Quality Analyst | Quality implications of inconsistencies | CQ | Pending |

## Notes
- Standardization intent: find cleanup targets, not just document current state
- Goal is to identify which patterns are dominant and which are outliers worth migrating
