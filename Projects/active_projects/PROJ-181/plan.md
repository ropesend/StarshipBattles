# PROJ-181: PROJ-174 Completion - Eradicate Deprecated Registry API

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-181` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-181 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete Deprecated API | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate Deprecated Function Callers | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Test .clear() Migration - Batch 1 | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Test .clear() Migration - Batch 2 | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Documentation Updates | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Full Verification | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 5
**Last Action:** Phase 4 complete - removed redundant .clear() calls from 15 test files
**Next Action:** Begin Phase 5 - Documentation Updates
**Blockers:** None
**Context for Next Agent:** Phase 4 complete. Removed redundant RegistryManager.instance().clear() calls from 15 additional test files: test_workshop_viewmodel.py, test_workshop_data_loader.py (2 fixtures), test_builder_warning_logic.py, test_builder_viewmodel.py, test_builder_drag_drop_real.py, test_builder_data_loader.py (2 classes), test_ability_interface.py, test_main_integration.py, test_physics.py, test_spatial.py, test_theme_discovery.py, test_screenshot_manager.py, test_regressions.py, reproduce_scaling.py, and integration/ai_strategy/conftest.py. Tests: 12373 passed, 1 skipped. Phase 5: Documentation updates.

## Overview
PROJ-174 migrated all production code to `IRegistryProvider` DI but kept `get_default_registries()` and `set_default_registries()` alive with DeprecationWarnings. Per CLAUDE.md System Migration Policy ("ERADICATE the old system completely"), this project deletes those functions, updates all callers, fixes stale documentation, and migrates 24 test files from `RegistryManager.instance().clear()` boilerplate to the existing fixture pattern.

## Goals
- Complete eradication of `get_default_registries()` and `set_default_registries()`
- Remove deprecated functions from all `__all__` exports
- Migrate 24 test files from `RegistryManager.instance().clear()` to fixture-based cleanup
- Update 3 documentation files with stale registry access examples
- Fix 1 stale TYPE_CHECKING import referencing nonexistent `game.core.registries` module

## Scope
**In:**
- Delete deprecated functions from `game/core/registry.py`
- Remove exports from `game/core/registry.py` `__all__` and `game/core/__init__.py`
- Update composition roots: `conftest.py`, `game/app.py`, `simulation_tests/conftest.py`
- Update ~10 test files using `set_default_registries`/`get_default_registries`
- Migrate 24 test files from `RegistryManager.instance().clear()` to fixture patterns
- Fix `game/simulation/services/design_loader.py:28` stale import
- Update `docs/guides/component_system.md`, `docs/architecture/PATTERNS.md`
- Delete tests that only exist to test deprecated functions

**Out:**
- RegistryManager singleton removal (deferred per PROJ-174 decision AR-005, 180+ call sites)
- Migrating `RegistryManager.instance()` usage where it's NOT `.clear()` (data access in tests)
- Changes to the `IRegistryProvider` protocol itself (already complete)

## Key Files
| Component | File Path |
|-----------|-----------|
| Deprecated functions | `game/core/registry.py:81-134` |
| Core exports | `game/core/__init__.py:74-75, 134` |
| App composition root | `game/app.py:130-133` |
| Test composition root | `conftest.py:57-67` |
| Sim test composition root | `simulation_tests/conftest.py:101-108` |
| Stale import | `game/simulation/services/design_loader.py:28` |
| Doc: component_system | `docs/guides/component_system.md:134-139` |
| Doc: PATTERNS | `docs/architecture/PATTERNS.md:63-93` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (12,338 baseline)
- [ ] Grep: zero `get_default_registries`/`set_default_registries` references outside comments
- [ ] Grep: zero `game.core.registries` references
- [ ] Audit passed
- [ ] User verified
