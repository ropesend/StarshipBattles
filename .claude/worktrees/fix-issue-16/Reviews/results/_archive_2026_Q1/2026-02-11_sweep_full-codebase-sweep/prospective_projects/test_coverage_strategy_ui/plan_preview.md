# PROJ-XX: Test Coverage -- Strategy and UI

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-XX` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-XX [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Strategy Data Layer Tests | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy Engine Tests | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI Framework Tests | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Screen Tests (Strategy) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. UI Screen Tests (Combat and Builder) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Planning
**Last Action:** Project created from sweep findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Write unit and integration tests for all untested classes and methods in the strategy and UI layers. This covers completely untested subpackages (builder/, test_lab/, formation/), critical strategy systems (planet_gen, GameSession command dispatch), 16 untested panel files, and numerous UI screens with zero test coverage. This is the largest test coverage project by finding count.

## Goals
- Write unit tests for all Critical untested strategy systems (planet_gen, FleetOrderProcessor, GameSession)
- Write unit tests for all Critical untested UI subpackages (builder, test_lab, formation, BattleScreen)
- Write tests for all 16 untested panel files
- Write tests for WorkshopViewModel, WorkshopEventRouter, StrategyEventRouter
- Improve existing fragile tests (reduce heavy mocking, fix inspect.getsource patterns)
- Write proper assertions in tests that use .called instead of .assert_called()

## Scope
**In:**
- All TCG findings in STR shard (strategy layer)
- All TCG findings in UI1 shard (UI screens)
- All TCG findings in UI2 shard (UI framework)
- New test files and test cases
- Test quality improvements for existing tests

**Out:**
- Core/engine/AI/simulation test gaps (separate project)
- Code changes beyond what is needed for testability
- New feature development

## Key Files
| Component | File Path |
|-----------|-----------|
| planet_gen (no tests) | `game/strategy/data/planet_gen.py` |
| GameSession dispatch (no tests) | `game/strategy/engine/game_session.py` |
| FleetOrderProcessor (gaps) | `game/strategy/engine/fleet_order_processor.py` |
| builder/ subpackage (zero tests) | `game/ui/screens/builder/` |
| test_lab/ subpackage (zero tests) | `game/ui/screens/test_lab/` |
| formation/ subpackage (zero tests) | `game/ui/screens/formation/` |
| BattleScreen (zero tests) | `game/ui/screens/battle_screen.py` |
| 16 untested panels | `game/ui/panels/` |
| WorkshopViewModel (no tests) | `game/ui/screens/workshop_viewmodel.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All 7 Critical findings have test coverage
- [ ] All new tests pass
- [ ] No existing tests broken
- [ ] Full test suite passes (pytest tests/ -n 12)
- [ ] Audit passed
- [ ] User verified
