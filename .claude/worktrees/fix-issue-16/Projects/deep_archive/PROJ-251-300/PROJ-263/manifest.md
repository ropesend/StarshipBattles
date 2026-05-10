# PROJ-263 File Manifest

> Generated during plan writing. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Phase 1: Builder/Workshop Duplicates

| File | Type | Action |
|------|------|--------|
| `tests/unit/builder/test_builder_data_loader.py` | Test | DELETE (192 LOC) |
| `tests/unit/builder/test_builder_viewmodel.py` | Test | DELETE after migrating ~6 unique tests (440 LOC) |
| `tests/unit/builder/test_workshop_context_di.py` | Test | DELETE after migrating 2 unique tests (106 LOC) |
| `tests/unit/builder/test_workshop_viewmodel_di.py` | Test | DELETE (105 LOC) |
| `tests/unit/ui/screens/builder/test_mandatory_modifiers.py` | Test | DELETE (40 LOC) |
| `tests/unit/workshop/test_workshop_viewmodel.py` | Test | MODIFY -- receive migrated tests from builder |
| `tests/unit/workshop/test_workshop_context.py` | Test | MODIFY -- receive migrated tests from builder |
| `tests/unit/builder/` | Directory | DELETE entirely after all files removed |

## Phase 2: Superweapon & Rendering Duplicates

| File | Type | Action |
|------|------|--------|
| `tests/unit/ui/test_superweapon_operations.py` | Test | PARTIAL DELETE -- remove init/property/error-path tests (~165 LOC); migrate TestSelfDestruct |
| `tests/unit/ui/screens/test_strategy_superweapons.py` | Test | MODIFY -- receive migrated TestSelfDestruct |
| `tests/unit/ui/screens/test_strategy_renderer_animation.py` | Test | PARTIAL DELETE -- remove 3 elapsed-time tests (~20 LOC) |
| `tests/unit/ui/test_rendering_logic.py` | Test | PARTIAL DELETE -- remove 4 duplicate tests (~50 LOC); possibly DELETE if all unique |
| `tests/unit/ui/renderer/test_game_renderer.py` | Test | MODIFY if test_component_color_coding migrated |
| `tests/unit/simulation/combat/test_battle_mode_handlers.py` | Test | PARTIAL DELETE -- remove TestModeCharacteristics (~34 LOC) |

## Phase 3: Colonization Duplicates

| File | Type | Action |
|------|------|--------|
| `tests/unit/abilities/test_colonize_planet.py` | Test | DELETE after migrating export test (195 LOC) |
| `tests/unit/simulation/components/abilities/test_colonize_harvester.py` | Test | MODIFY -- receive migrated export test |
| `tests/integration/colonization/test_validation.py` | Test | DELETE (86 LOC) |
| `tests/integration/strategy/test_colonize_logic.py` | Test | PARTIAL DELETE -- remove ~185 LOC of pod consumption + validation dups |
| `tests/unit/strategy/engine/test_process_colonize_cargo.py` | Test | PARTIAL DELETE -- remove 4 duplicate tests (~85 LOC) |
| `tests/integration/colonization/test_execution.py` | Test | PARTIAL DELETE -- remove 3 duplicate tests (~45 LOC) |
| `tests/unit/abilities/` | Directory | DELETE if empty after file removal |

## Phase 4: Transfer, Production, Research & Repro Duplicates

| File | Type | Action |
|------|------|--------|
| `tests/unit/strategy/engine/test_fleet_order_transfer.py` | Test | PARTIAL DELETE -- remove TestExecuteLoad, TestExecuteUnload, TestTransferValidation (~218 LOC) |
| `tests/unit/strategy/test_fleet_order_processor.py` | Test | PARTIAL DELETE -- remove 3 dataclass tests + TestOrderProcessorCreation (~45 LOC) |
| `tests/integration/strategy/production/test_fleet_production_e2e.py` | Test | PARTIAL DELETE -- remove 2 movement + 1 save/load tests (~82 LOC) |
| `tests/unit/strategy/engine/test_superweapon_handler_validation.py` | Test | PARTIAL DELETE -- remove 5 "rejects" tests (~100 LOC) |
| `tests/unit/research/test_research_tracker_edge_cases.py` | Test | DELETE (149 LOC) |
| `tests/unit/ai/test_ai_controller_edge_cases.py` | Test | PARTIAL DELETE -- remove EngageDistance + CapabilitiesCache (~110 LOC) |
| `tests/unit/simulation/ship_combat_engine/test_combat_ops.py` | Test | PARTIAL DELETE or DELETE -- remove facade duplicates (~210 LOC) |
| `tests/repro_issues/test_bug_01_crew_delay.py` | Test | DELETE (113 LOC) |
| `tests/repro_issues/test_bug_02_seeker.py` | Test | DELETE (37 LOC) |
| `tests/repro_issues/test_bug_03_validation.py` | Test | DELETE (104 LOC) |
| `tests/repro_issues/test_bug_05_logistics.py` | Test | DELETE (108 LOC) |
| `tests/repro_issues/test_bug_05_rejected_fix.py` | Test | DELETE (91 LOC) |
| `tests/repro_issues/test_bug_05_deep_repro.py` | Test | DELETE (157 LOC) |
| `tests/repro_issues/test_bug_06_combat_propulsion.py` | Test | DELETE (147 LOC) |
| `tests/repro_issues/test_bug_07_crash.py` | Test | DELETE (59 LOC) |
| `tests/repro_issues/test_bug_08_fuel_validation.py` | Test | DELETE (59 LOC) |
| `tests/repro_issues/test_bug_09_endurance.py` | Test | DELETE (80 LOC) |
| `tests/repro_issues/test_bug_10_logistics_update.py` | Test | DELETE (112 LOC) |
| `tests/unit/test_builder_refactor.py` | Test | DELETE (36 LOC) |
| `tests/unit/performance/reproduce_scaling.py` | Test | DELETE (41 LOC) |

## Summary

| Phase | Files Deleted | Files Partially Deleted | Files Modified | Est. LOC Removed |
|-------|--------------|------------------------|---------------|-----------------|
| 1 | 5 | 0 | 2 | ~883 |
| 2 | 0-2 | 2-4 | 1-2 | ~235 |
| 3 | 2-3 | 2-3 | 1 | ~550 |
| 4 | 14-15 | 5-6 | 0 | ~1,644 |
| **Total** | **21-25** | **9-13** | **4-5** | **~3,312** |

> Note: LOC estimates for partial deletions are approximate. Actual counts will be recorded during implementation. Some files may end up fully deleted if audit reveals all tests are duplicates.
