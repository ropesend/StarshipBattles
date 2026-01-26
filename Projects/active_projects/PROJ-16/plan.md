# PROJ-16: Consolidate Re-exports (Phase 3)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-16` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-16 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. PLANET_RESOURCES Re-export | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Component Constants Re-exports | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. AI Re-exports | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Ship Loader Re-exports | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Wrapper Evaluation | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-25 (Session 1)
**Active Phase:** Phase 3
**Last Action:** Completed Phase 2 - Component Constants re-export removal (65+ files updated including ship.py, tests, and simulation files). Re-export block removed from component.py.
**Next Action:** Begin Phase 3 - AI Re-exports (StrategyManager, TargetEvaluator from controller.py)
**Blockers:** None

**Context for Next Agent:**
- Phase 1 and Phase 2 are fully complete
- All tests passing: 4524 passed (1 pre-existing failure in test_advanced_fleet_orders, 1 pre-existing import error in test_ui_widgets.py)
- Key lesson from Phase 2: When removing re-exports, need to check if the module uses those types internally. component.py needed to import ComponentStatus, Modifier, ApplicationModifier for its own use
- Key lesson: Combined imports like `from module import A, B, C` need special handling - grep for pattern `import.*CONSTANT` not just `import CONSTANT`
- Phase 3 scope: AI re-exports from controller.py (~40+ files). See phase_3_checklist.md for details.

## Overview

This project consolidates re-exports across the codebase by updating all callers to import from canonical module locations, then removing the backward-compatibility re-exports. This is Phase 3 of the 8-phase Legacy Cleanup initiative, following the completion of Phases 1 (Delete Dead Code) and 2 (Remove Shims & Aliases).

## Goals
- Update all callers to import from canonical module locations instead of re-export locations
- Remove backward compatibility re-exports from component.py, ship.py, controller.py, and planet.py
- Evaluate thin wrapper classes (ModifierLogic, _ProfilerProxy, ShipControllableAdapter backward compat)
- Improve architectural clarity by making import paths reflect actual code locations

## Scope

**In Scope:**
- Remove PLANET_RESOURCES re-export from `game/strategy/data/planet.py` (8 files)
- Remove component constants re-exports from `game/simulation/components/component.py` (65 files)
- Remove AI re-exports from `game/ai/controller.py` (40+ files)
- Remove ship_loader re-exports from `game/simulation/entities/ship.py` (67 files)
- Evaluate ModifierLogic wrapper for potential removal
- Evaluate _ProfilerProxy simplification
- Evaluate ShipControllableAdapter backward compat features

**Out of Scope:**
- Creating new `__init__.py` export files (deferred to future project)
- Removing ModifierLogic.calculate_snap_value (UI-specific, must stay in UI layer)
- Removing _ProfilerProxy entirely (tests depend on it)
- Changes to layer boundaries (that's Phase 4)

## Key Files

| Component | File Path | Action |
|-----------|-----------|--------|
| PLANET_RESOURCES re-export | `game/strategy/data/planet.py:6-8` | Remove re-export |
| Component re-exports | `game/simulation/components/component.py:68-74` | Remove re-exports |
| AI re-exports | `game/ai/controller.py:52-61` | Remove re-exports |
| Ship loader re-exports | `game/simulation/entities/ship.py:21-26` | Remove re-exports |
| ModifierLogic wrapper | `ui/builder/modifier_logic.py` | Evaluate, likely keep |
| PROFILER proxy | `game/core/profiling.py:133-143` | Evaluate, likely keep |
| ShipControllableAdapter | `game/ai/interfaces/controllable.py:162-319` | Remove backward compat features |

## Risk Assessment

| Re-export | Files Affected | Risk | Mitigation |
|-----------|---------------|------|------------|
| PLANET_RESOURCES | 8 | Very Low | Simple search-replace |
| Component constants | 65 | Low | Isolated, no circular imports |
| AI (strategy_manager) | 38 | Medium | Test infrastructure updates needed |
| AI (target_evaluator) | 5 | Low | Split adoption already |
| Ship loader | 67 | Medium | Critical initialization path |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log
- [Legacy Cleanup README](../../legacy_cleanup/README.md) - Overall project context
- [Phase 3 Original Spec](../../legacy_cleanup/PHASE_3_CONSOLIDATE_REEXPORTS.md) - Original requirements

## Verification

### Per-Phase Verification
- [ ] `pytest tests/ --testmon` passes after each task
- [ ] No circular import errors: `python -c "import game"`
- [ ] Application launches: `python -m game`

### Final Verification
- [ ] Full test suite: `pytest tests/` (4562 tests)
- [ ] Simulation tests: `pytest simulation_tests/`
- [ ] No re-export imports remain (grep verification)
- [ ] All phase checklists complete
- [ ] User verified
