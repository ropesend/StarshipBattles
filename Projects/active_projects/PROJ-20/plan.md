# PROJ-20: Standardize Data Formats

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-20` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-20 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Production Queue Standardization | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Fleet Ship Format Standardization | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Design Metadata & Tech Tree | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Legacy Stats & Test Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-01-26 21:10
**Active Phase:** Planning Complete - Ready for Approval
**Last Action:** Completed exploration, risk analysis, and detailed planning
**Next Action:** User approval of plan, then begin Phase 1
**Blockers:** None
**Context:** Baseline tests: 4542 passed, 1 flaky (test_quickstart_designs intermittent)

## Overview
Implements Phase 7 of the Legacy Code Cleanup project. Removes dual-format support for various data structures (production queues, fleet ships, design metadata, tech tree, ship stats) and standardizes on the new formats throughout the codebase. No save game migration is required.

## Goals
- Remove legacy `["name", turns]` list format from production queues
- Remove legacy string ship support from fleets (use ShipInstance only)
- Remove legacy `{"components": [...]}` wrapper from design metadata layers
- Remove legacy `{"level": N}` format from tech tree requirements
- Remove legacy ship stats field re-exports (max_fuel, max_energy, etc.)
- Update all test fixtures to use new formats

## Scope
**In:**
- Strategy layer data format standardization
- Production queue format (production_engine.py, planet.py, build_queue_screen.py)
- Fleet ship format (fleet.py and 12 callers)
- Design metadata layer format (design_metadata.py, planet.py)
- Tech tree requirement format (tech_tree.py)
- Ship stats service legacy field removal
- Test fixture updates

**Out:**
- Save game migration (explicitly not required per legacy cleanup decision)
- Simulation layer internal refactoring
- New features or capabilities

## Key Files
| Component | File Path |
|-----------|-----------|
| Fleet Ships | `game/strategy/data/fleet.py` |
| Production Engine | `game/strategy/engine/production_engine.py` |
| Planet (add_production) | `game/strategy/data/planet.py` |
| Build Queue UI | `game/ui/screens/build_queue_screen.py` |
| Ship Stats Service | `game/strategy/services/ship_stats_service.py` |
| Ship Instance | `game/strategy/data/ship_instance.py` |
| Design Metadata | `game/strategy/data/design_metadata.py` |
| Tech Tree | `game/research/data/tech_tree.py` |
| Test Fixtures | `tests/unit/strategy/conftest.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [PHASE_7_STANDARDIZE_DATA_FORMATS.md](../../legacy_cleanup/PHASE_7_STANDARDIZE_DATA_FORMATS.md) - Original phase spec

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing: `pytest tests/ -v`
- [ ] No isinstance(item, list) in production_engine.py
- [ ] No Union[str, ShipInstance] in fleet.py
- [ ] No get_ship_instances() calls remaining
- [ ] No legacy field re-exports in ship_stats_service.py
- [ ] Application launches correctly
