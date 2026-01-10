# Test Shielding Manifest

| Batch | Scope | Status | Agent | Last Updated |
| :--- | :--- | :--- | :--- | :--- |
| **S01** | AI & Behaviors | [x] Complete | Antigravity | 2026-01-09 |
| **S02** | Builder - Core | [x] Complete | Antigravity | 2026-01-09 |
| **S03** | Builder - Sync & Selection | [x] Complete | Antigravity | 2026-01-09 |
| **S04** | Ships & Entities | [x] Complete | Antigravity | 2026-01-09 |
| **S05** | Ship Stats & Physics | [x] Complete | Antigravity | 2026-01-09 |
| **S06** | Regressions & Bugs I | [x] Complete | Antigravity | 2026-01-09 |
| **S07** | Regressions & Bugs II | [x] Complete | Antigravity | 2026-01-09 |
| **S08** | Simulation & Systems | [x] Complete | Antigravity | 2026-01-09 |
| S09 | Scripts & Utils | [x] Complete | Antigravity | remediated utility and performance scripts with cleanup |
| **S10** | Broken/Repro Cleanup | [x] Complete | Antigravity | 2026-01-09 |

---

## Shielding Log
| File | Remediation Applied | Isolation Pass | Suite Pass | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `test_advanced_behaviors.py` | Pygame quit in tearDown | Pass | Pass | - |
| `test_ai.py` | Registry & Strategy clear in tearDown | Pass | Pass | - |
| `test_ai_behaviors.py` | Pygame quit in tearDown | Pass | Pass | - |
| `test_movement_and_ai.py` | Pygame, Registry, Strategy clear in tearDown | Pass | Pass | - |
| `test_strategy_system.py` | Pygame quit in tearDown | Pass | Pass | - |
| `test_targeting_rules.py` | Pygame quit in tearDown | Pass | Pass | - |
| `test_builder_drag_drop_real.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_builder_improvements.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_builder_interaction.py` | Pygame quit in tearDown | Pass | Pass | - |
| `test_builder_logic.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_builder_structure_features.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_builder_ui_sync.py` | Pygame/Registry/Strategy reset in tearDown | Pass | Pass | - |
| `test_builder_validation.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_builder_warning_logic.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_designs.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_multi_selection_logic.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_selection_refinements.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_detail_panel_rendering.py` | Pygame/Registry reset in tearDown | Pass | Pass | [KNOWN_ISSUE] fixed |
| `test_ship.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_ship_core.py` | Registry reset in fixture finalizer | Pass | Pass | - |
| `test_ship_classes.py` | Pygame/Registry/Theme reset in tearDown | Pass | Pass | - |
| `test_ship_loading.py` | Registry reset in tearDown | Pass | Pass | Located in `tests/unit/builder/` |
| `test_ship_physics_mixin.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_ship_resources.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_scaling_logic.py` | Registry reset in tearDown | Pass | Pass | - |
| `test_planetary_complex.py` | Registry reset in tearDown | Pass | Pass | - |
| `test_ship_stats.py` | mock.patch.dict(sys.modules), Registry clear in tearDown | Pass | Pass | CRITICAL: Fixed module poisoning |
| `test_physics.py` | Pygame quit/Registry clear in tearDown | Pass | Pass | - |
| `test_spatial.py` | Pygame quit/Registry clear in tearDown | Pass | Pass | - |
| `test_spatial_extended.py` | Pygame quit/Registry clear in tearDown | Pass | Pass | - |
| `test_ability_driven_thrust.py` | N/A | - | - | File not found (likely merged or deleted) |
| `test_regressions.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_warnings.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_bug_03_validation.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_bug_05_rejected_fix.py` | Registry reset in fixture | Pass | Pass | - |
| `test_bug_10_repro.py` | Registry reset in fixture | Pass | Pass | - |
| `test_bug_11_hull_update.py` | Registry reset in fixture finalizer | Pass | Pass | - |
| `test_bug_13_weapons_report.py` | Pygame quit in tearDown | Pass | Pass | - |
| `test_sequence_hazard.py` | Registry reset in autouse fixture | Pass | Pass | Located in `tests/repro_issues/` |
| `test_main_integration.py` | Pygame/Registry reset in tearDown | Pass | Pass | Located in `tests/unit/systems/` |
| `test_crash_regressions.py` | Pygame/Registry reset in tearDown | Pass | Pass | Located in `tests/unit/regressions/` |
| `test_battle_scene.py` | Pygame/Registry reset in tearDown | Pass | Pass | - |
| `test_battle_scene_extended.py` | Pygame/Registry/Strategy reset in tearDown | Pass | Pass | - |
| `test_battle_panels.py` | module reload + sys.path/patcher restore | Pass | Pass | CRITICAL: Fixed sticky pygame module ref |
| `test_allowed_layers_removal.py` | Registry reset in tearDown | Pass | Pass | - |
| `test_dynamic_layers.py` | Registry reset in tearDown | Pass | Pass | - |
| `test_layer_refinements.py` | Registry reset in tearDown | Pass | Pass | - |
| `test_arcade_movement.py` | Pygame/Registry reset in tearDown | Pass | Pass | Additional file found during S08 scan |
| `repro_energy_stats.py` | Fixed imports and Pattern I cleanup | Pass | Pass | Located in `tests/unit/performance/` |
| `repro_shield.py` | Fixed imports, Pattern I cleanup, and ability access | Pass | Pass | Located in `tests/unit/performance/` |
| `reproduce_scaling.py` | Fixed ability access and Registry cleanup | Pass | Pass | Located in `tests/unit/performance/` |
| `verify_determinism_current.py` | Fixed imports and Pattern I isolation | Pass | Pass | Located in `tests/unit/performance/` |
| `repro_bug_05_deep.py` | Fixed layer access and Pattern I isolation | Pass | Pass | Located in `tests/repro_issues/` |
| `test_slider_increment.py` | Pattern I isolation (mock.patch.dict) | Pass | Pass | Located in `tests/unit/repro_issues/` |
