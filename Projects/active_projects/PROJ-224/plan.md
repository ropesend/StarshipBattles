# PROJ-224: Core Utilities & Shared Helpers

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-224` to see what to do next
> - Open the phase checklist file for your current phase

## Overview
Create shared utility functions and fix foundational issues that later consolidation projects depend on. This is the first project in a 5-project duplication elimination campaign (PROJ-224 through PROJ-228).

**Source Review:** `Reviews/results/2026-03-24_200858_general_duplication-consolidation-full-codebase/`

## Goals
1. Fix latent bugs caused by duplicated logic
2. Create shared utility functions that eliminate repeated patterns
3. Resolve naming conflicts
4. Delete dead/backward-compat code

## Scope
- `game/core/` — shared utilities, constants, protocols
- `game/simulation/systems/battle_engine.py` — team-alive counting fix
- `game/simulation/battle_controller.py`, `game/simulation/managers/` — state management
- `game/strategy/engine/game_session.py` — facade dispatch
- `game/ui/services/ship_io.py` — path dedup
- Cross-cutting: `_has_attrs`, display names, hex deserialization, angle math

## Findings (17)

### Bug Fixes (Phase 1)
| ID | Severity | Description |
|----|----------|-------------|
| DUP-SYS-004 | MAJOR | Team-alive counting in BattleEngine: `is_battle_over()` and `get_winner()` count derelicts differently |

### Shared Utilities (Phase 2)
| ID | Severity | Description |
|----|----------|-------------|
| DUP-CEA-001 | MAJOR | `_has_attrs()` duplicated in 4 protocol modules → define once in `game/core/protocols.py`, import elsewhere |
| DUP-SIM-004 | MINOR | Same `_has_attrs` in simulation interfaces (subset of CEA-001) |
| DUP-XL-009 | MINOR | `replace('_', ' ').title()` in 9+ locations → create `display_name()` utility |
| DUP-SCR-009 | MAJOR | `EARTH_MASS` constant hardcoded 4+ times → add to `game/core/constants.py` |
| DUP-SD-03 | MINOR | HexCoord deserialization boilerplate → create `hex_from_dict_safe()` utility |
| DUP-SS-04 | MINOR | Slug functions duplicated → single `slugify()` in core |
| DUP-XL-007 | MINOR | atan2-to-degrees inlined in 4 locations → utility or use Vector2.angle_to |

### Constants & Naming Cleanup (Phase 3)
| ID | Severity | Description |
|----|----------|-------------|
| DUP-CEA-003 | MINOR | TICKS_PER_SECOND vs TICK_RATE not derived from each other |
| DUP-CEA-002 | MINOR | TICK_DURATION class constant aliases in AI behaviors |
| DUP-CEA-005 | MINOR | Inline angle normalization in projectile.py |
| DUP-CEA-006 | MINOR | quickstart_builder uses raw json.load() |
| DUP-SYS-003 | MINOR | Two classes named `BattleConfig` → rename core one to `CombatConstants` |

### Minor Cleanup (Phase 4)
| ID | Severity | Description |
|----|----------|-------------|
| DUP-SYS-007 | MINOR | State capture duplication between BattleController and BattleStateManager |
| DUP-SYS-008 | MINOR | "No active battle" guard pattern in BattleService |
| DUP-UIS-004 | MINOR | Ships folder path construction duplicated in ShipIO |
| DUP-SCR-006 | MINOR | Facade-or-session command dispatch pattern |

## Execution Order
**1st of 5 projects** — foundational, no dependencies. PROJ-225 and PROJ-226 depend on utilities created here.

## Success Criteria
- [x] All 7353+ tests pass (13470 passed, 2 skipped — baseline was 13434)
- [x] `_has_attrs` defined once, imported everywhere
- [x] `display_name()` utility exists and is used
- [x] `EARTH_MASS` constant exists in core
- [x] BattleEngine team-alive counting uses single helper
- [x] No `BattleConfig` naming ambiguity (renamed to `BattleTuning` in core)

## Current State
**Last Updated:** 2026-03-24
**Last Agent Action:** Completed all 4 phases — project is complete.
**Next Action:** None — project complete.
**Blockers:** None
**Context for Next Agent:** All phases complete. 13470 tests pass (36 new tests added). Key changes:
- Phase 1: Fixed derelict counting bug in BattleEngine with `_count_alive_teams()` helper
- Phase 2: Created `game/core/string_utils.py` (display_name, slugify), consolidated `_has_attrs`, added `EARTH_MASS`, `hex_from_dict_safe`, `angle_from_vector`
- Phase 3: Derived TICKS_PER_SECOND from TICK_RATE, created `normalize_angle`, replaced raw json.load, renamed core BattleConfig to BattleTuning
- Phase 4: Routed state capture through BattleStateManager, added `_require_engine()` guard helper, extracted `_ensure_ships_folder()`
