# Test Audit Manifest

| Batch | Directory | Status | Agent | Last Updated |
| :--- | :--- | :--- | :--- | :--- |
| **B01** | `tests/unit/ai/` | [x] Complete | Antigravity | 2026-01-09 |
| **B02** | `tests/unit/builder/` | [x] Complete | Antigravity | 2026-01-09 |
| **B03** | `tests/unit/combat/` | [x] Complete | Antigravity | 2026-01-09 |
| **B04** | `tests/unit/data/` | [x] Complete | Antigravity | 2026-01-09 |
| **B05** | `tests/unit/entities/` (A-M) | [x] Complete | Antigravity | 2026-01-09 |
| **B06** | `tests/unit/entities/` (N-Z) | [x] Complete | Antigravity | 2026-01-09 |
| **B07** | `tests/unit/performance/` | [x] Complete | Antigravity | 2026-01-09 |
| **B08** | `tests/unit/regressions/` & `repro_issues/` | [x] Complete | Antigravity | 2026-01-09 |
| **B09** | `tests/unit/simulation/` | [x] Complete | Antigravity | 2026-01-09 |
| **B10** | `tests/unit/systems/` | [x] Complete | Antigravity | 2026-01-09 |
| **B11** | `tests/unit/ui/` | [x] Complete | Antigravity | 2026-01-09 |
| **B12** | `tests/unit/` (Root) | [x] Complete | Antigravity | 2026-01-09 |

## Findings Log

| `test_advanced_behaviors.py` | Pygame Leak | `pygame.init()` called in `setUp` without `pygame.quit()` | Add `pygame.quit()` to `tearDown` higher up or locally. |
| `test_ai.py` | Registry Pollution | `STRATEGY_MANAGER`, component, and vehicle registries loaded without reset | Add reset/clear calls to `tearDown`. |
| `test_movement_and_ai.py` | Pygame/Registry Leak | Both `pygame.init()` and multiple global registries polluted | Wrap in `tearDown` cleanup. |
| `test_builder_drag_drop_real.py` | Pygame/Registry Leak | `pygame.init()` without `quit()`; Ship/Builder usage implies Registry pollution | Add `pygame.quit()` and `RegistryManager` reset to `tearDown`. |
| `test_builder_improvements.py` | Pygame/Registry Leak | Explicitly skips `pygame.quit()`; directly updates `vehicle_classes` without reset | Add `pygame.quit()` and `RegistryManager` reset to `tearDown`. |
| `test_builder_interaction.py` | Pygame Leak | `pygame.init()` without `quit()` | Add `pygame.quit()` to `tearDown`. |
| `test_builder_logic.py` | Pygame/Registry Leak | `pygame.init()` without `quit()`; `initialize_ship_data` and `load_components` pollute Registry without reset | Add `pygame.quit()` and `RegistryManager` reset to `tearDown`. |
| `test_builder_structure_features.py` | Pygame Leak | `pygame.init()` and `set_mode()` without `quit()` | Add `pygame.quit()` to `tearDown`. |
| `test_builder_ui_sync.py` | Pygame/Registry Leak | `pygame.init()` without `quit()`; `initialize_ship_data`, `load_components`, and `load_combat_strategies` pollute registries without reset | Add `pygame.quit()` and Registry/Strategy manager resets to `tearDown`. |
| `test_builder_validation.py` | Pygame/Registry Leak | `pygame.init()` without `quit()`; `initialize_ship_data` pollutes Registry without reset | Add `pygame.quit()` and `RegistryManager` reset to `tearDown`. |
| `test_builder_warning_logic.py` | Pygame Leak | `pygame.init()` without `quit()` | Add `pygame.quit()` to `tearDown` or via `addCleanup`. |
| `test_designs.py` | Pygame/Registry Leak | `pygame.init()` without `quit()`; `initialize_ship_data` and `load_components` pollute Registry without reset | Add `pygame.quit()` and `RegistryManager` reset to `tearDown`. |
| `test_multi_selection_logic.py` | Pygame Leak | `pygame.init()` and `set_mode()` without `quit()` | Add `pygame.quit()` to `tearDown`. |
| `test_selection_refinements.py` | Pygame Leak | `pygame.init()` and `set_mode()` without `quit()` | Add `pygame.quit()` to `tearDown`. |
| `test_ship_loading.py` | Registry Pollution | `load_components`, `load_modifiers`, and `load_vehicle_classes` pollute Registry without reset | Add `RegistryManager` reset to `tearDown`. |
| `test_planetary_complex.py` | Registry Pollution | Loads components and modifiers in `setUp` without `tearDown` reset | Add `RegistryManager` reset to `tearDown`. |
| `test_scaling_logic.py` | Registry Pollution | Loads components and modifiers in `setUp` without `tearDown` reset | Add `RegistryManager` reset to `tearDown`. |
| `test_ship.py` | Pygame/Registry Leak | `pygame.init()` without `quit()`; Registry initialized without reset | Add `pygame.quit()` and `RegistryManager` reset to `tearDown`. |
| `test_ship_classes.py` | Pygame/Registry Leak | `pygame.init()` and Registry/Theme managers initialized without reset | Add `pygame.quit()` and Registry/Theme resets to `tearDown`. |
| `test_ship_core.py` | Registry Pollution | Fixtures update `RegistryManager` without cleanup | Add cleanup to fixtures or `RegistryManager` reset. |
| `test_ship_physics_mixin.py` | Pygame/Registry Leak | `pygame.init()` and Registry initialized without reset | Add `pygame.quit()` and `RegistryManager` reset to `tearDown`. |
| `test_ship_resources.py` | Pygame/Registry Leak | `pygame.init()` and Registry initialized without reset | Add `pygame.quit()` and `RegistryManager` reset to `tearDown`. |
| `test_ship_stats.py` | sys.modules/Registry | Poisoning `sys.modules['pygame']` and Registry pollution | Use `mock.patch.dict(sys.modules, ...)` and add Registry reset. |
| `repro_energy_stats.py` | BROKEN / Pollution | `ImportError`; Pygame/Registry pollution without cleanup | Fix imports; add `pygame.quit()` and `RegistryManager` reset. |
| `repro_shield.py` | BROKEN / Pollution | `ImportError`; Pygame/Registry pollution without cleanup | Fix imports; add `pygame.quit()` and `RegistryManager` reset. |
| `reproduce_scaling.py` | BROKEN / Pollution | `AttributeError`; Registry pollution without reset | Fix component attribute access; add Registry reset. |
| `verify_determinism_current.py` | BROKEN / Pollution | `ImportError`; Pygame/Registry pollution without cleanup | Fix imports; add `pygame.quit()` and Registry reset. |
| `profile_simulation.py` | Pollution | Script lacks Pygame/Registry cleanup; modifies `sys.path` | Add `pygame.quit()` and Registry reset; use `mock.patch.dict(sys.modules)`. |
| `strategy_tournament.py` | Pollution | Script lacks Pygame/Registry cleanup; modifies `sys.path` | Add `pygame.quit()` and Registry reset. |
| `stress_test.py` | Pollution | Script lacks Pygame/Registry cleanup; modifies `sys.path` | Add `pygame.quit()` and Registry reset. |
| `generate_test_data.py` | Pollution | Script lacks Registry cleanup; modifies `sys.path` | Add `RegistryManager` reset. |
| `test_crash_regressions.py` | Pygame Leak | `pygame.init()` without `quit()` | Add `pygame.quit()` to `tearDown`. |
| `test_regressions.py` | Pygame/Registry Leak | `pygame.init()` without `quit()`; modifies `vehicle_classes` without reset | Add `pygame.quit()` and Registry reset. |
| `test_warnings.py` | Pygame/Registry Leak | `pygame.init()` without `quit()`; modifies `vehicle_classes` without reset | Add `pygame.quit()` and Registry reset. |
| `test_bug_03_validation.py` | Pygame/Registry Leak | `pygame.init()` without `quit()`; modifies `vehicle_classes` without reset | Add `pygame.quit()` and Registry reset. |
| `test_bug_05_rejected_fix.py` | Registry Pollution | Modifies `vehicle_classes` directly in test methods | Add `RegistryManager` reset to `tearDown`. |
| `test_bug_10_repro.py` | Registry Pollution | Calls `load_vehicle_classes()` and `load_components()` in tests | Add `RegistryManager` reset to `tearDown`. |
| `test_bug_11_hull_update.py` | Registry Pollution | `clear()` and `update()` on Registry in fixture without reset | Add `RegistryManager` reset to fixture finalize. |
| `test_bug_13_weapons_report.py` | Pygame Leak | `pygame.init()` without `quit()` | Add `pygame.quit()` to `tearDown`. |
| `test_sequence_hazard.py` | Registry Pollution | Explicitly injects state into global registries | Add `RegistryManager` reset to `tearDown`. |
| `repro_bug_05_deep.py` | BROKEN / Pollution | `KeyError` on `LayerType.INNER`; modifies `sys.path` | Fix layer access; use `mock.patch.dict(sys.modules)`. |
| `run_component_tests.py` | Pygame/Registry/BROKEN | `pygame.init()` without `quit()`; Registry loads without reset; `ModuleNotFoundError` for `game` | Add `pygame.quit()` and `RegistryManager` reset; fix `sys.path`. |
| `update_test_ships.py` | Pygame/Registry | `pygame.init()` without `quit()`; Registry loads without reset | Add `pygame.quit()` and `RegistryManager` reset to `update_ships`. |
| `component_test_logger.py` | Global State | Modifies `game.core.logger` handler; global `ACTIVE_LOGGER` | Ensure cleanup in `finally` blocks; reset global state. |
| `test_allowed_layers_removal.py` | Registry Pollution | `initialize_ship_data()` and `load_components()` in `setUp` without reset | Add `RegistryManager.reset()` to `tearDown`. |
| `test_dynamic_layers.py` | Registry Pollution | `initialize_ship_data()` and `load_components()` in `setUp` without reset | Add `RegistryManager.reset()` to `tearDown`. |
| `test_layer_refinements.py` | Registry Pollution | `initialize_ship_data()` in `setUp` without reset | Add `RegistryManager.reset()` to `tearDown`. |
| `test_main_integration.py` | Pygame/Registry | `pygame.display.set_mode` and `game.app` (Registry) used without cleanup | Add `pygame.quit()` and `RegistryManager.reset()` to `tearDown`. |
| `test_physics.py` | Pygame Leak | `pygame.init()` without `quit()` | Add `pygame.quit()` to `tearDown`. |
| `test_spatial.py` | Pygame Leak | `pygame.init()` without `quit()` | Add `pygame.quit()` to `tearDown`. |
| `test_spatial_extended.py` | Pygame Leak | `pygame.init()` without `quit()` | Add `pygame.quit()` to `tearDown`. |
| `test_targeting_rules.py` | Pygame / Global State | `pygame.init()` without `quit()`; `STRATEGY_MANAGER` used without reset; `sys.path` modified | Add `pygame.quit()` and `STRATEGY_MANAGER.clear()` to `tearDown`. |
