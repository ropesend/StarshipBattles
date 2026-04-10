# PROJ-265: Simulation Domain Test Coverage

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-265` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-265 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. component_loader.py Unit Tests | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. DamageCalculator Event Emissions | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. FleetAuraManager Extended Coverage | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-09
**Active Phase:** Complete
**Last Action:** All 3 phases complete. 37 new tests across 3 test files. Full suite: 14,128 passed, 0 failures.
**Next Action:** Archive project
**Blockers:** None
**Context:** Phase 1: 15 tests (component_loader error paths + factory functions). Phase 2: 9 tests (DamageCalculator event emissions for all 5 event types). Phase 3: 13 tests (FleetAuraManager get_active_bonuses, external modifiers, fingerprint, operational check).

## Overview
This project closes the three highest-priority simulation-domain test coverage gaps identified in the 2026-04-08 test review. Phase 1 creates the first dedicated test file for `component_loader.py` (64.2% coverage, lowest in the simulation domain -- 54 missing statements, no dedicated tests). Phase 2 adds event emission tests for `DamageCalculator.apply_damage()` (no existing test passes an `event_bus`). Phase 3 extends `FleetAuraManager` coverage for untested paths including `get_active_bonuses()`, external modifier loading, and provider operational checks.

All three phases are test-only -- no production code changes. Every test targets existing production code paths that currently lack coverage.

## Goals
- Raise `component_loader.py` coverage from 64.2% toward 95%+ by testing all error/edge paths
- Achieve coverage of all 5 combat event emission paths in `DamageCalculator`
- Close the 31 missing-line gap in `FleetAuraManager` (79.3% -> 95%+)
- All tests written TDD-style: write test, verify it exercises the intended code path, confirm green

## Scope
**In:**
- New test file: `tests/unit/simulation/components/test_component_loader.py` (Phase 1)
- New test file: `tests/unit/simulation/combat/test_damage_calculator_events.py` (Phase 2)
- New test file: `tests/unit/simulation/combat/test_fleet_aura_extended.py` (Phase 3)

**Out:**
- No production code changes (all phases are test-only)
- No changes to existing test files
- Coverage gaps outside the simulation domain (UI, strategy, AI)
- Combat Lab (simulation_tests/) scenarios -- this project is pytest only

## Key Files
| Component | File Path | Coverage Before | Missing Lines |
|-----------|-----------|----------------|---------------|
| Component loader | `game/simulation/components/component_loader.py` | 64.2% (151 stmts) | 54 missing |
| Damage calculator | `game/simulation/combat/damage_calculator.py` | ~85% | Lines 94, 112, 131, 212-213, 222 |
| Fleet aura manager | `game/simulation/combat/fleet_aura_manager.py` | 79.3% (150 stmts) | 31 missing |
| Combat events | `game/simulation/combat/combat_events.py` | -- | Supporting types |
| Combat types | `game/core/combat_types.py` | -- | DamageContext |
| Existing DC tests | `tests/unit/simulation/combat/test_damage_calculator.py` | -- | No event_bus usage |
| Existing FA cache tests | `tests/unit/simulation/combat/test_fleet_aura_cache.py` | -- | Cache/aggregation |
| Existing FA register tests | `tests/unit/simulation/combat/test_fleet_aura_register.py` | -- | register_ship() |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-09 | Separate test files per phase (not extending existing) | Keeps phase work isolated; avoids merge conflicts with existing test files; each new file targets a distinct coverage gap |
| 2026-04-09 | Test-only project -- no production changes | All coverage gaps are in existing code that works correctly but lacks test verification of specific paths |
| 2026-04-09 | Use mock event_bus for Phase 2 | Real CombatEventBus has detail-level gating; a mock with `.emit()` lets us verify call arguments directly without needing to manage subscriber wiring |
| 2026-04-09 | Phase ordering: loader -> events -> auras | Loader has lowest coverage (highest impact). Events are isolated (no cross-file dependencies). Auras are most complex (last). |

---

## Phases

### Phase 1: component_loader.py Unit Tests [Medium]
**Objective:** Create the first dedicated test file for `component_loader.py`, covering all error paths, cache behavior, and factory functions.
**Status:** Not Started

**Coverage targets (lines from coverage report):**
- `load_components_data` with nonexistent file (lines 93-99)
- `load_components_data` with malformed JSON (lines 126-128)
- `load_components_data` with invalid component data (lines 111-116)
- `load_components` with `registry_provider=None` raising ValueError (line 146)
- `load_modifiers_data` with nonexistent file (lines 194-201)
- `load_modifiers_data` with malformed JSON (lines 227-228)
- `load_modifiers` with `registry_provider=None` raising ValueError (line 244)
- `create_component` with `registries=None` raising ValidationException (lines 285-290)
- `get_all_components` with `registries=None` raising ValidationException (lines 312-317)
- Cache hit paths in `load_components` (lines 154-157) and `load_modifiers` (lines 253-256)

See [phase_1_checklist.md](phase_1_checklist.md) for detailed task breakdown.

---

### Phase 2: DamageCalculator Event Emissions [Medium]
**Objective:** Test all 5 combat event emission paths in `DamageCalculator.apply_damage()` by passing a mock event_bus.
**Status:** Not Started

**Coverage targets (lines from coverage report):**
- SHIELD_HIT event when shields absorb damage (line 94)
- ARMOR_ABSORBED event when emissive armor reduces damage (line 112)
- ARMOR_ABSORBED event when SRA absorbs damage (line 131)
- COMPONENT_HIT event on hull hit where component survives (line 222)
- COMPONENT_DESTROYED event when component HP reaches 0 (lines 212-213)
- SHIP_DERELICT event when ship becomes non-functional (line 165)

See [phase_2_checklist.md](phase_2_checklist.md) for detailed task breakdown.

---

### Phase 3: FleetAuraManager Extended Coverage [Medium]
**Objective:** Test `get_active_bonuses()`, external modifier loading, provider operational checks, and fingerprint edge cases.
**Status:** Not Started

**Coverage targets (lines from coverage report):**
- `get_active_bonuses()` for ship providers (lines 256-272)
- `get_active_bonuses()` for external modifiers (lines 275-284)
- External modifier loading from BattleConfig -- team modifiers (lines 77-85)
- External modifier loading from BattleConfig -- global modifiers (lines 86-92)
- Provider operational check in `_recalculate()` -- component destruction removes aura (lines 192-205)
- `_get_provider_fingerprint()` dead ship branch (lines 161-166)
- `_get_provider_fingerprint()` derelict ship branch (line 166)

See [phase_3_checklist.md](phase_3_checklist.md) for detailed task breakdown.

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` -- establish baseline

### After Each Phase
- [ ] Run targeted tests for new test file
- [ ] Run `pytest tests/unit/simulation/ -v` -- existing tests still pass
- [ ] Verify coverage improvement with `pytest tests/ --cov=game/simulation/components/component_loader --cov=game/simulation/combat/damage_calculator --cov=game/simulation/combat/fleet_aura_manager -n 12`

### Final Verification
- [ ] `pytest tests/unit/simulation/ -v` -- all pass
- [ ] `python Tools/test_sharded/test_sharded.py` -- full suite green
- [ ] Coverage of component_loader.py improved from 64.2%
- [ ] All DamageCalculator event emission lines covered
- [ ] FleetAuraManager coverage improved from 79.3%
- [ ] No production code was modified

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing
- [ ] No regressions in existing simulation tests
- [ ] Audit passed
- [ ] User verified

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for conflict detection
- `Reviews/results/2026-04-08_test-review/final_report.md` - Source review that identified these gaps
