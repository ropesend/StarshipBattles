# PROJ-XX: Consistency Standardization

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
| 1. Convention Decisions | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Type Hints and Docstrings | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Naming Standardization | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Pattern Standardization | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Planning
**Last Action:** Project created from sweep findings
**Next Action:** Begin Phase 1 -- document convention decisions
**Blockers:** None

## Overview
Standardize naming conventions, type hints, error handling patterns, DI patterns, logging approaches, and documentation across the entire codebase. Phase 1 establishes the conventions; subsequent phases apply them systematically. This project ensures that developers encounter consistent patterns regardless of which module they are working in.

## Goals
- Resolve all duplicate class names (ModifierEditorPanel, ColumnManager)
- Standardize event handler naming (`handle_event` everywhere, not `on_event`)
- Standardize draw/update parameter naming (`surface`/`dt` consistently)
- Add type hints to all public methods lacking them
- Add docstrings to all public modules and classes
- Standardize DI pattern across UI services (constructor injection, no singletons)
- Standardize error handling (specific exceptions, consistent "not found" returns)
- Standardize logging (one approach per module, no parallel systems)

## Scope
**In:**
- All CON-type findings across all layers
- Convention decision documentation
- Mechanical standardization across affected files

**Out:**
- Architecture layer violations (separate project)
- Legacy dead code removal (separate project)
- Duplication elimination (separate project, though some overlap on naming)
- New feature development

## Key Files
| Component | File Path |
|-----------|-----------|
| Duplicate class names | `game/ui/panels/builder_widgets/`, `game/ui/screens/column_manager.py` |
| Missing type hints (core) | `game/core/hex_math.py`, `game/engine/spatial.py` |
| Missing type hints (strategy) | `game/strategy/data/fleet.py`, `game/strategy/data/physics.py` |
| Missing type hints (UI) | `game/ui/renderer/camera.py`, `game/ui/widgets.py` |
| DI inconsistency | `game/ui/services/vehicle_class_service.py`, `game/ui/renderer/sprites.py` |
| Logging inconsistency | `game/ai/combat_utils.py`, `game/ui/screens/builder/main.py` |
| Naming inconsistency | `game/strategy/facade/strategy_facade.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log (especially important for convention decisions)

## Verification
- [ ] All phase checklists complete
- [ ] Convention decisions documented for each category
- [ ] No duplicate class names remain
- [ ] All public methods have type hints
- [ ] All public modules have docstrings
- [ ] Consistent DI pattern across UI services
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
