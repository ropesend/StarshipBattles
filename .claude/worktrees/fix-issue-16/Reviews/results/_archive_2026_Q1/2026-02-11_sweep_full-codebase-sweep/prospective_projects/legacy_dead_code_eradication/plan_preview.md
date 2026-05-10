# PROJ-XX: Legacy Dead Code Eradication

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
| 1. Foundation Layer Cleanup | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation Layer Cleanup | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. UI Framework Cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Screens Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Planning
**Last Action:** Project created from sweep findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Eradicate all legacy dead code, backward compatibility wrappers, deprecated modules, vestigial attributes, and unused code paths across the entire codebase. This is a purely subtractive project -- every change removes code rather than adding it. Per the project's System Migration Policy, old systems must be completely removed with no fallback paths.

## Goals
- Remove all backward compatibility wrappers (load_resources, race flag aliases, tuple format support)
- Delete entirely dead modules (widgets.py, BattleOrchestrator)
- Remove deprecated classes and methods (legacy BuilderScreen, BattleScreen handle_* stubs)
- Eliminate vestigial attributes (Ship.base_mass, AIController.attack_state)
- Replace hasattr/getattr guards with direct attribute access where attrs are guaranteed
- Remove dead code branches (ability_aggregator dict format, SpriteManager atlas fallback)
- Clean up unused imports, constants, and protocol classes

## Scope
**In:**
- All LEG-type findings across all layers
- Dead code deletion, deprecated method removal, backward compat wrapper removal
- Updating references to deleted code

**Out:**
- Architecture layer violation fixes (separate project)
- Duplication elimination (separate project)
- New feature development

## Key Files
| Component | File Path |
|-----------|-----------|
| Legacy resource loading | `game/core/resources.py` |
| Dead protocols | `game/core/protocols.py` |
| Dead widgets module | `game/ui/widgets.py` |
| Legacy persistence | `game/simulation/systems/persistence.py` |
| Dead ability class map | `game/simulation/components/abilities/` |
| Dead resource manager re-exports | `game/simulation/systems/resource_manager.py` |
| Legacy builder screen | `game/ui/screens/builder/main.py` |
| Dead battle orchestrator | `game/ui/orchestration/battle_orchestrator.py` |
| Dead renderer methods | `game/ui/renderer/game_renderer.py` |
| Dead sprite fallback | `game/ui/renderer/sprites.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (no test should break from removing truly dead code)
- [ ] No backward compatibility wrappers remain
- [ ] No deprecated methods remain
- [ ] No hasattr guards for guaranteed attributes remain
- [ ] Audit passed
- [ ] User verified
