# Review Scope: Naming Inconsistencies

## Metadata
- **Date:** 2026-01-26
- **Type:** Consistency Review
- **Description:** Find naming inconsistencies across the codebase

## Scope Definition

### Target
- [x] Entire codebase

### Objective
Find areas of the project where multiple names are used to refer to the same thing (e.g., "design studio" vs "ship builder"), and document all examples for remediation planning.

### Priorities
1. Terminology inconsistencies (same concept, different names)
2. File/directory naming inconsistencies
3. Documentation terminology drift
4. Code organization issues (duplicate class definitions)

### Exclusions
- Third-party libraries
- Generated files
- Test fixture data (unless naming is confusing)

## Agent Configuration
**Agent Count:** 3

### Selected Agents
| Agent | Role | Status |
|-------|------|--------|
| Ship Builder/Design Studio Hunter | Find all builder vs workshop vs design terminology | Complete |
| General Naming Inconsistency Hunter | Find other terminology inconsistencies | Complete |
| Codebase Structure Analyzer | Map conventions and find divergences | Complete |

## Notes
- Existing Phase 2 legacy cleanup plan already addresses many shim removals
- Critical issue found: duplicate BattleScene class definitions
