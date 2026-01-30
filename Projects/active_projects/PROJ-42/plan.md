# PROJ-42: Backward Compatibility and Legacy Pattern Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-42` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-42 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quick Wins & Deprecated Module Removal | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Complete PROJ-38 Registry Migration | In Progress | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Eliminate Dual Static/Instance Patterns | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Clean Up Serialization & Format Support | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. BattleEngine & Scattered Compat Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Test Updates & Final Verification | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-29
**Active Phase:** Phase 2 - Task 2.1 Complete
**Last Action:** Completed Task 2.1 - Updated ShipStatsService with _get_registries_fallback() pattern
**Next Action:** Task 2.2 - Update ModifierService to GameRegistries
**Blockers:** None

## Overview
This project addresses all 44 backward compatibility and legacy pattern issues identified in `findings_03_backward_compatibility_legacy.md`. It completes stalled migrations (PROJ-12, PROJ-27, PROJ-35, PROJ-38, PROJ-41), removes deprecated code, eliminates 28,000+ deprecation warnings, and centralizes scattered compatibility code.

## Goals
- Complete PROJ-38 GameRegistries DI migration across all services
- Remove FleetMovementSimulator deprecated module (331 LOC)
- Eliminate dual static/instance method patterns in services
- Remove dead code paths for unsupported formats
- Centralize scattered backward compatibility code
- Reduce deprecation warnings from 28,319 to 0
- Maintain all 5199 tests passing throughout

## Scope
**In:**
- All issues from `findings_03_backward_compatibility_legacy.md` (BCD-001 through BCD-010, LPH-001 through LPH-023, STR-001, STR-002, STR-005, SIM-007)
- Complete PROJ-35, PROJ-38 migrations
- Test updates for deprecated pattern removal

**Out:**
- New feature development
- Performance optimization (unless directly related to cleanup)
- Changes to save format version support (player data protection)
- Removal of WIDTH/HEIGHT re-exports (too many dependents)
- Removal of ValidationResult dual patterns (legitimate cross-layer bridge)

## Key Files
| Component | File Path |
|-----------|-----------|
| Registry System | `game/core/registry.py` |
| Deprecated Fleet Module | `game/strategy/engine/fleet_movement.py` |
| Ship Stats Service | `game/strategy/services/ship_stats_service.py` |
| Modifier Service | `game/simulation/services/modifier_service.py` |
| Ship Entity | `game/simulation/entities/ship.py` |
| Component | `game/simulation/components/component.py` |
| Battle Engine | `game/simulation/systems/battle_engine.py` |
| Ship Serialization | `game/simulation/entities/ship_serialization.py` |
| App Entry Point | `game/app.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Source: `findings_03_backward_compatibility_legacy.md`

---

## Phase 1: Quick Wins & Deprecated Module Removal [Simple]
**Objective:** Remove obviously dead code and simple compatibility shims with no dependencies
**Status:** Not Started
**Estimated Tasks:** 5 tasks

### Summary of Changes
- Delete FleetMovementSimulator (LPH-002, STR-001)
- Remove GameState aliases in app.py (BCD-007)
- Remove V1 modifier format detection code (LPH-005)
- Clean up commented migration code in save_game_service.py (BCD-005 partial)
- Remove unused ship string format parser defense code

---

## Phase 2: Complete PROJ-38 Registry Migration [Complex]
**Objective:** Migrate all deprecated registry access to GameRegistries DI pattern
**Status:** Not Started
**Estimated Tasks:** 8 tasks

### Summary of Changes
- Update ShipStatsService to use GameRegistries exclusively (BCD-001)
- Update ModifierService to use GameRegistries exclusively (LPH-001)
- Update Ship entity to use GameRegistries exclusively
- Update Component to use GameRegistries exclusively
- Update VehicleDesignService to remove dual constructor support
- Fix ship.py:467 bug (missing registries parameter)
- Update UI layer files (workshop_screen, workshop_event_router, etc.)
- Remove deprecated utility functions after all callers migrated (BCD-002)

---

## Phase 3: Eliminate Dual Static/Instance Patterns [Medium]
**Objective:** Standardize service APIs to instance-only methods
**Status:** Not Started
**Estimated Tasks:** 4 tasks

### Summary of Changes
- Refactor ShipStatsService.calculate_stats() to instance method (LPH-003)
- Refactor ModifierService dual methods to instance-only (BCD-003)
- Update all callers to use instance pattern
- Remove parameter introspection logic

---

## Phase 4: Clean Up Serialization & Format Support [Medium]
**Objective:** Remove dead format support code, standardize serialization
**Status:** Not Started
**Estimated Tasks:** 5 tasks

### Summary of Changes
- Remove ship string format parser (BCD-010)
- Standardize component serialization to dict-only (BCD-010)
- Clean up formation editor dual format support (LPH-007)
- Remove stats mismatch warning fallback (BCD-006)
- Add explicit format version to serialization

---

## Phase 5: BattleEngine & Scattered Compat Cleanup [Medium]
**Objective:** Remove legacy controller creation paths, centralize compat code
**Status:** Not Started
**Estimated Tasks:** 6 tasks

### Summary of Changes
- Remove BattleEngine legacy controller creation path (LPH-009)
- Remove reinforcement legacy path
- Centralize PathSegment 'hex' field compatibility
- Remove _ChaserProxy, use proper adapter pattern (STR-005)
- Centralize fleet order format deserializer (STR-005)
- Clean up legacy crew requirement pattern (BCD-008)

---

## Phase 6: Test Updates & Final Verification [Medium]
**Objective:** Update tests for new patterns, verify all deprecation warnings eliminated
**Status:** Not Started
**Estimated Tasks:** 5 tasks

### Summary of Changes
- Update 34 test files using deprecated functions
- Update tests for instance-only service methods
- Add verification tests for deprecated code removal
- Run full test suite, verify 0 deprecation warnings
- Final manual verification of game functionality

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - all tests pass (5199 passed)
- [x] Document baseline deprecation warning count: 28,319

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Verify deprecation warning count decreased
- [ ] Manual smoke test of affected functionality

### Final Verification
- [ ] Run full test suite: `pytest tests/` - all tests pass
- [ ] Verify 0 deprecation warnings
- [ ] Manual test: Load save game, start battle, use ship builder
- [ ] Verify FleetMovementSimulator import fails (removed)
- [ ] Verify no IRegistryProvider usage in production code

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All Phase 6 tasks checked off
- [ ] All tests passing (5199+)
- [ ] 0 deprecation warnings
- [ ] Audit passed
- [ ] User verified
