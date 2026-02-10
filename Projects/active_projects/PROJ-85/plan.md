# PROJ-85: Eradicate Module-Level Mutable Global State

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-85` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-85 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Remove Module-Level Globals | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-02-09 21:30
**Active Phase:** Planning
**Last Action:** Plan created and awaiting approval
**Next Action:** Implement Phase 1 (single phase project)
**Blockers:** None

## Overview
Remove three dead module-level global variables (`COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, `VEHICLE_CLASSES`) that were kept for UI hot-reload compatibility during PROJ-42 but have zero importers after PROJ-43/44/50 completed the migration to services and constructor DI. This eliminates import-time side effects and removes the last contradiction to the strict DI model.

## Goals
- Remove `COMPONENT_REGISTRY` and `MODIFIER_REGISTRY` from `component.py`
- Remove `VEHICLE_CLASSES` from `ship.py`
- Clean up orphaned imports and dead `TYPE_CHECKING` block
- All 7353 tests continue to pass

## Scope
**In:**
- Delete the three module-level globals and their associated comments
- Clean up the `get_default_registry_provider` import in `ship.py` (only used by the deleted global)
- Clean up the dead `if TYPE_CHECKING: pass` block in `ship.py`

**Out:**
- `get_default_registry_provider()` and `DefaultRegistryProvider` (widely used elsewhere, stays)
- `ComponentCacheManager` and `reset_component_caches()` (actively used by conftest/loaders, stays)
- `load_components()` and `load_modifiers()` wrapper functions (still used, stays)
- Documentation/archive files referencing these globals (historical records)
- Any refactoring of the `conftest.py` test isolation pattern

## Key Files
| Component | File Path |
|-----------|-----------|
| COMPONENT_REGISTRY, MODIFIER_REGISTRY globals | `game/simulation/components/component.py:77-82` |
| VEHICLE_CLASSES global | `game/simulation/entities/ship.py:24-27` |
| Dead TYPE_CHECKING block | `game/simulation/entities/ship.py:14-15` |
| Import to clean | `game/simulation/entities/ship.py:4,11` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12` — 7353 baseline)
- [ ] Grep confirms no remaining imports of deleted globals
- [ ] Audit passed
- [ ] User verified
