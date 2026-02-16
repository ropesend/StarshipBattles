# Review Scope: 2026-02-16_075913_general_test-suite-cleanup

## Metadata
- **Date:** 2026-02-16 07:59
- **Type:** General Review - Test Suite Cleanup
- **Description:** Identify unnecessary/broken/stale tests across the entire test suite

## Scope Definition

### Target
- [x] Specific directory: `tests/`
- **Files:** ~940 .py files, ~12,000 tests, ~200K LOC

### Priorities
- Find tests for deleted/changed features (STALE)
- Find duplicate/redundant tests (DUPLICATE)
- Find over-mocked tests that don't validate real behavior (OVER-MOCKED)
- Find trivially obvious tests (TRIVIALLY-OBVIOUS)
- Find tests with broken assumptions (BROKEN-ASSUMPTIONS)
- Find unused test infrastructure (VESTIGIAL-SCAFFOLD)
- Flag entire vestigial directories (repro_issues, refactor, projects, etc.)

### Exclusions
- `simulation_tests/` (top-level directory outside tests/)

## Agent Configuration
**Confirmed Agent Count:** 18

### Selected Agents
| # | Agent | Zone | ~Files |
|---|-------|------|--------|
| 1 | unit-strategy-data | tests/unit/strategy/data/ | 27 |
| 2 | unit-strategy-engine | tests/unit/strategy/engine/, turn_engine/, production_engine/, resource_management_engine/ | 40 |
| 3 | unit-strategy-fleet | tests/unit/strategy/fleet/, fleet_movement_engine/, fleet_navigation/, pathfinding/ | 26 |
| 4 | unit-strategy-misc | tests/unit/strategy/ (remaining subdirs) | 99 |
| 5 | unit-ui-screens | tests/unit/ui/screens/ | 52 |
| 6 | unit-ui-panels-services | tests/unit/ui/panels/, services/, left_panel/ | 36 |
| 7 | unit-ui-misc | tests/unit/ui/ (remaining subdirs) | 19 |
| 8 | unit-simulation-components | tests/unit/simulation/components/ | 23 |
| 9 | unit-simulation-battle | tests/unit/simulation/battle_controller/, ship_combat_engine/, combat/ | 20 |
| 10 | unit-simulation-misc | tests/unit/simulation/ (remaining subdirs) | 49 |
| 11 | unit-entities | tests/unit/entities/ | 49 |
| 12 | unit-core | tests/unit/core/ | 57 |
| 13 | unit-ai | tests/unit/ai/ | 31 |
| 14 | unit-research-refactor | tests/unit/research/ + tests/unit/refactor/ | 53 |
| 15 | unit-remaining | tests/unit/ (all other subdirs) | ~100 |
| 16 | integration | tests/integration/ | 115 |
| 17 | vestigial-dirs | tests/repro_issues/, regression/, refactor/, projects/, performance/, infrastructure/ | 36 |
| 18 | cross-cutting-patterns | ALL tests/ (pattern scan only) | 940 |

## Confidence Levels
- **HIGH** - Near-certain removal candidates
- **MEDIUM** - Likely removable, needs verification
- **LOW** - Possibly removable, warrants discussion
