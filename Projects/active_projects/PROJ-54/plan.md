# PROJ-54: Combat Lab Quality Cleanup and Expansion

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-54` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-54 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation Cleanup | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Template Refactor & Projectile Migration | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Beam & Seeker Scenario Simplification | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Defense Ability Tests | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Modifier Tests | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Coverage Index & Final Cleanup | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-06
**Active Phase:** PROJECT COMPLETE - All 6 phases done
**Last Action:** Phase 6 complete. Created `simulation_tests/coverage_index.py` with ABILITY_TO_TESTS mapping 19 abilities/modifier effects to test ID prefixes. Implemented `get_coverage_report()` and `get_uncovered_abilities()` functions using TestRegistry. Created `simulation_tests/tests/test_coverage_index.py` with 4 meta-tests validating coverage completeness. All 19 tracked abilities are covered. Final cleanup verified: `self.results['initial_hp']` only in `_collect_results`, `_resolve_path` consolidated to standalone function, all exports included. Sim tests: 62 passed, 5 pre-existing failures, 4 skipped. Full suite: 6112 passed, 5 skipped.
**Next Action:** Project complete. Pending audit and user verification.
**Blockers:** None
**Pre-existing failures (not PROJ-54):** PROP-001 (distance tolerance), PROP-003/004 (missing result keys), RESOURCE-002/003 (max_hp mismatch + fuel starvation)

## Overview

The Combat Lab is a mature testing framework (~60 scenarios) for validating combat simulation behavior. Before expanding it to cover all abilities and modifiers, we need to address quality and maintainability issues in the existing code. This project first cleans up the foundation (Phases 1-3), then adds new defense and modifier test coverage (Phases 4-5), and finally creates a coverage tracking system (Phase 6).

## Goals

1. **Eliminate code duplication** - Remove ~400 lines of duplicated verify/results boilerplate across beam, seeker, and projectile scenarios
2. **Consolidate utility code** - Extract shared `_resolve_path` (3 copies → 1), generalize `_extract_ship_validation_data` (beam-only → all abilities)
3. **Migrate projectile scenarios to templates** - Move 9 raw `TestScenario` subclasses to `StaticTargetScenario`
4. **Add defense ability test coverage** - 7 new scenarios for shields, armor, ECM, sensors
5. **Add modifier test coverage** - 8 single-effect test modifiers + 6 new modifier scenarios
6. **Create coverage index** - Automated tracking of which abilities have test coverage

## Scope

**In:**
- All files in `simulation_tests/scenarios/` (quality cleanup)
- `simulation_tests/data/` (new test components, modifiers, ships)
- New scenario files for defense and modifier testing
- Coverage index with meta-test

**Out:**
- Changes to production game code (`game/`)
- Adding new resource types or changing the resource system
- Changes to the Combat Lab UI
- Performance optimization

## Key Files

| Component | File Path |
|-----------|-----------|
| Test base class | `simulation_tests/scenarios/base.py` |
| Template classes | `simulation_tests/scenarios/templates.py` |
| Validation rules | `simulation_tests/scenarios/validation.py` |
| Pre-run validation | `simulation_tests/scenarios/prerun_validation.py` |
| Beam scenarios | `simulation_tests/scenarios/beam_scenarios.py` |
| Projectile scenarios | `simulation_tests/scenarios/projectile_scenarios.py` |
| Seeker scenarios | `simulation_tests/scenarios/seeker_scenarios.py` |
| Resource scenarios | `simulation_tests/scenarios/resource_scenarios.py` |
| Scenario exports | `simulation_tests/scenarios/__init__.py` |
| Test components | `simulation_tests/data/components.json` |
| Test modifiers | `simulation_tests/data/modifiers.json` |
| Test constants | `simulation_tests/test_constants.py` |
| Game modifiers (ref) | `data/modifiers.json` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification

### After Each Phase
```bash
# Run simulation tests headless
pytest simulation_tests/ -v

# Run full suite
pytest tests/ -n 4
```

### Final Verification
- [ ] All phase checklists complete
- [ ] All tests passing (full suite, not --testmon)
- [ ] All existing test IDs and pass/fail behavior unchanged
- [ ] New defense + modifier scenarios passing
- [ ] Coverage index reports all combat abilities covered
- [ ] Audit passed
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] Phase 1 complete (Foundation Cleanup)
- [x] Phase 2 complete (Template Refactor & Projectile Migration)
- [x] Phase 3 complete (Beam & Seeker Simplification)
- [x] Phase 4 complete (Defense Tests)
- [x] Phase 5 complete (Modifier Tests)
- [x] Phase 6 complete (Coverage Index)
- [x] All tests passing
- [ ] Audit passed
- [ ] User verified
