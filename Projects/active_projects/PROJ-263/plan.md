# PROJ-263: Delete Duplicate Test Files

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-263` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-263 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete Builder/Workshop Duplicates | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Delete Superweapon & Rendering Duplicates | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Delete Colonization Duplicates | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Delete Transfer, Production, Research & Repro Duplicates | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-09
**Active Phase:** 1
**Last Action:** Plan written with 4 phases
**Next Action:** Begin Phase 1 -- delete builder/workshop duplicate test files
**Blockers:** None

## Overview
The test suite review (see `Reviews/results/2026-04-08_test-review/final_report.md`) identified ~3,300 LOC of duplicate test files across the codebase (including repro issue files now fully covered by proper unit tests). These files duplicate coverage already provided by other, better-structured test files. Keeping them inflates test counts, slows CI, and creates maintenance burden when production code changes require updating tests in multiple places.

This project systematically removes these duplicates across 4 phases, migrating any unique tests before deletion, and running the full test suite after each phase to confirm no coverage loss.

## Goals
- Remove ~3,300 LOC of duplicate test code across ~40 files (including repro issues)
- Migrate any unique tests found in duplicate files to the canonical test file before deletion
- Maintain 100% test pass rate after each phase (zero regressions)
- Eliminate the `tests/unit/builder/` directory entirely (all content is post-rename duplicates of `tests/unit/workshop/`)

## Scope
**In:**
- Deletion of duplicate test files identified by the test suite review (validators V1-V4)
- Migration of unique tests from duplicate files to their canonical counterparts
- Partial deletion of test classes/methods within files that contain both duplicate and unique tests
- Deletion of repro issue files whose coverage is fully subsumed by proper unit tests

**Out:**
- Deletion of TESTS_NOTHING_REAL files (zero game imports) -- that is PROJ-262
- Deletion of SCAFFOLD_ONLY files (hasattr/import tests) -- that is PROJ-265
- Deletion of TRIVIAL_CONSTANT tests -- that is PROJ-266
- Writing new tests to fill coverage gaps -- that is PROJ-264
- Consolidating shared test helpers (MockGalaxy, make_colony_ship) -- separate effort
- Fixing production bugs found during review (BUG-1 through BUG-5) -- that is PROJ-261

## Deletion Principles

1. **Read before delete.** Every file must be read and its duplicate claim verified before deletion. Never trust the review report blindly.
2. **Migrate first.** If a duplicate file contains ANY unique test that is not covered elsewhere, migrate that test to the canonical file and confirm it passes before deleting the source file.
3. **Run tests after each file.** Run the targeted test directory after each deletion. Run the full suite after each phase.
4. **Delete whole files when possible.** If all tests in a file are duplicates, delete the entire file. If only some tests are duplicates, delete only the duplicate classes/methods.
5. **Clean up empty directories.** If deleting files leaves a directory empty (or containing only `__init__.py` / `__pycache__`), delete the directory too.

## Key Files

### Phase 1: Builder/Workshop Duplicates (~883 LOC in files)
| Duplicate File | Canonical File |
|---------------|---------------|
| `tests/unit/builder/test_builder_data_loader.py` (192 LOC) | `tests/unit/workshop/test_workshop_data_loader.py` |
| `tests/unit/builder/test_builder_viewmodel.py` (440 LOC) | `tests/unit/workshop/test_workshop_viewmodel.py` |
| `tests/unit/builder/test_workshop_context_di.py` (106 LOC) | `tests/unit/workshop/test_workshop_context.py` |
| `tests/unit/builder/test_workshop_viewmodel_di.py` (105 LOC) | `tests/unit/workshop/test_workshop_viewmodel.py` |
| `tests/unit/ui/screens/builder/test_mandatory_modifiers.py` (40 LOC) | `tests/unit/ui/screens/builder/test_mandatory_modifiers_ownership.py` |

### Phase 2: Superweapon & Rendering Duplicates (~235 LOC removed)
| Duplicate File | Canonical File |
|---------------|---------------|
| `tests/unit/ui/test_superweapon_operations.py` (393 LOC total, ~165 LOC dup) | `tests/unit/ui/screens/test_strategy_superweapons.py` |
| `tests/unit/ui/screens/test_strategy_renderer_animation.py` (98 LOC total, ~20 LOC dup) | `tests/unit/ui/screens/test_strategy_renderer.py` |
| `tests/unit/ui/test_rendering_logic.py` (249 LOC total, ~50 LOC dup) | `tests/unit/ui/renderer/test_game_renderer.py` |
| `tests/unit/simulation/combat/test_battle_mode_handlers.py` (293 LOC total, ~34 LOC dup) | Per-handler test files |

### Phase 3: Colonization Duplicates (~550 LOC removed)
| Duplicate File | Canonical File |
|---------------|---------------|
| `tests/unit/abilities/test_colonize_planet.py` (195 LOC) | `tests/unit/simulation/components/abilities/test_colonize_harvester.py` |
| `tests/integration/colonization/test_validation.py` (86 LOC) | `tests/unit/strategy/validation/test_colonize_validator.py` |
| `tests/integration/strategy/test_colonize_logic.py` (321 LOC, ~185 LOC dup) | `tests/unit/strategy/engine/test_process_colonize_validation.py` + `tests/integration/gameplay_loop/test_commands_colonization.py` |
| `tests/unit/strategy/engine/test_process_colonize_cargo.py` (219 LOC, ~85 LOC dup) | `tests/integration/colonization/test_planet_specific_colonization.py` |
| `tests/integration/colonization/test_execution.py` (170 LOC, ~45 LOC dup) | `tests/integration/gameplay_loop/test_commands_colonization.py` |

### Phase 4: Transfer, Production, Research & Repro Duplicates (~1,644 LOC removed)
| Duplicate File | Canonical File |
|---------------|---------------|
| `tests/unit/strategy/engine/test_fleet_order_transfer.py` (389 LOC, ~218 LOC dup) | `tests/unit/strategy/engine/test_transfer_order.py` |
| `tests/unit/strategy/test_fleet_order_processor.py` (615 LOC, ~45 LOC dup) | Various strategy engine tests |
| `tests/integration/strategy/production/test_fleet_production_e2e.py` (440 LOC, ~82 LOC dup) | Other production tests |
| `tests/unit/strategy/engine/test_superweapon_handler_validation.py` (459 LOC, ~100 LOC dup) | Keep 10 "passes_component_registry" tests |
| `tests/unit/research/test_research_tracker_edge_cases.py` (149 LOC) | `tests/unit/research/test_research_tracker.py` |
| `tests/unit/ai/test_ai_controller_edge_cases.py` (413 LOC, ~110 LOC dup) | Other AI controller tests |
| `tests/unit/simulation/ship_combat_engine/test_combat_ops.py` (257 LOC, ~210 LOC dup) | `tests/unit/simulation/combat/test_damage_calculator.py` + `test_weapon_firing_system.py` |
| `tests/repro_issues/test_bug_01_crew_delay.py` (113 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_02_seeker.py` (37 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_03_validation.py` (104 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_05_logistics.py` (108 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_05_rejected_fix.py` (91 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_05_deep_repro.py` (157 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_06_combat_propulsion.py` (147 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_07_crash.py` (59 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_08_fuel_validation.py` (59 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_09_endurance.py` (80 LOC) | Covered by proper unit tests |
| `tests/repro_issues/test_bug_10_logistics_update.py` (112 LOC) | Covered by proper unit tests |
| `tests/unit/test_builder_refactor.py` (36 LOC) | Covered by workshop tests |
| `tests/unit/performance/reproduce_scaling.py` (41 LOC) | Covered by proper unit tests |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for conflict detection
- `Reviews/results/2026-04-08_test-review/final_report.md` - Source review that identified all duplicates

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (full suite via `python Tools/test_sharded/test_sharded.py`)
- [ ] No test directories left with only `__init__.py` / `__pycache__`
- [ ] Audit passed
- [ ] User verified
