# Dead Code Hunter Report: Unused Imports Sweeper

### Summary
- Total files with unused imports: 73 (17.5% of 418 files)
- Total unused import statements: 103
- Estimated removable lines: ~124

### Top 10 Worst Offenders

| Rank | File | Unused Count | Unused Imports |
|------|------|-------------|----------------|
| 1 | `game/ui/screens/builder/__init__.py` | 7 | BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, ComponentListItem, LayerPanel, ComponentDetailPanel, ModifierLogic |
| 2 | `game/ui/screens/strategy_panel_manager.py` | 4 | Paths, StrategyMenuPanel, PANEL_WIDTH, PANEL_HEIGHT |
| 3 | `game/simulation/battle_controller.py` | 3 | Any, BattleEndCondition, BattleEndMode |
| 4 | `game/strategy/data/galaxy.py` | 3 | Enum, auto, PlanetType |
| 5 | `game/ui/screens/empire_panel_window.py` | 3 | Dict, PLANET_RESOURCES, Paths |
| 6 | `game/ui/screens/builder/panel_layout_config.py` | 3 | field, Optional, pygame |
| 7 | `game/simulation/components/abilities/stat_keys.py` | 2 | field, List |
| 8 | `game/simulation/entities/ship_serialization.py` | 2 | Optional, create_component |
| 9 | `game/simulation/managers/retreat_manager.py` | 2 | field, Any |
| 10 | `game/simulation/systems/resource_manager.py` | 2 | Any, Union |

### Distribution by Severity
- **1 unused import:** 54 files (74% of affected files)
- **2-3 unused imports:** 17 files (23%)
- **4+ unused imports:** 2 files (3%)

### Findings by Module

#### game/ai/ (4 files, 4 unused)
| File | Count | Unused Imports |
|------|-------|----------------|
| `ai/controller.py` | 1 | `is_in_pdc_arc` |
| `ai/strategy_manager.py` | 1 | `Optional` |
| `ai/target_evaluator.py` | 1 | `Vector2` |
| `ai/interfaces/controllable.py` | 1 | `CombatConstants` |

#### game/app.py (1 file, 1 unused)
| File | Count | Unused Imports |
|------|-------|----------------|
| `app.py` | 1 | `UIButton` |

#### game/core/ (3 files, 3 unused)
| File | Count | Unused Imports |
|------|-------|----------------|
| `core/math.py` | 1 | `Union` |
| `core/registry.py` | 1 | `StateException` |
| `core/validation.py` | 1 | `Enum` |

#### game/research/ (1 file, 1 unused)
| File | Count | Unused Imports |
|------|-------|----------------|
| `research/data/research_tracker.py` | 1 | `field` |

#### game/simulation/ (15 files, 21 unused)
| File | Count | Unused Imports |
|------|-------|----------------|
| `simulation/battle_controller.py` | 3 | Any, BattleEndCondition, BattleEndMode |
| `simulation/components/abilities/stat_keys.py` | 2 | field, List |
| `simulation/entities/ship_serialization.py` | 2 | Optional, create_component |
| `simulation/managers/retreat_manager.py` | 2 | field, Any |
| `simulation/systems/resource_manager.py` | 2 | Any, Union |
| `simulation/battle_config.py` | 1 | field |
| `simulation/formula_system.py` | 1 | Optional |
| `simulation/projectile_manager.py` | 1 | Set |
| `simulation/components/component.py` | 1 | safe_evaluate_math_formula |
| `simulation/components/abilities/defense.py` | 1 | PhysicsConfig |
| `simulation/entities/ability_aggregator.py` | 1 | is_ability |
| `simulation/entities/ship_stat_querier.py` | 1 | Any |
| `simulation/services/design_loader.py` | 1 | PersistenceException |
| `simulation/services/vehicle_design_service.py` | 1 | Any |
| `simulation/systems/battle_engine.py` | 1 | Tuple |

#### game/strategy/ (19 files, 27 unused)
| File | Count | Unused Imports |
|------|-------|----------------|
| `strategy/data/galaxy.py` | 3 | Enum, auto, PlanetType |
| `strategy/data/design_metadata.py` | 2 | warnings, save_json |
| `strategy/engine/maintenance_engine.py` | 2 | PlanetaryFacility, ShipInstance |
| `strategy/engine/production_engine.py` | 2 | Any, OrderType |
| `strategy/engine/resource_management_engine.py` | 2 | Optional, TYPE_CHECKING |
| `strategy/facade/dto/system_dto.py` | 2 | field, List |
| `strategy/services/fleet_cargo_projector.py` | 2 | Dict, Any |
| `strategy/adapters/simulation_adapter.py` | 1 | BattleService |
| `strategy/data/galaxy_entity_registry.py` | 1 | HexCoord |
| `strategy/data/pathfinding.py` | 1 | OrderType |
| `strategy/engine/environmental_hazard_engine.py` | 1 | Fleet |
| `strategy/engine/fleet_order_processor.py` | 1 | HexCoord |
| `strategy/engine/superweapon_order_processor.py` | 1 | StarSystem |
| `strategy/facade/dto/fleet_dto.py` | 1 | FleetType |
| `strategy/generation/region_classifier.py` | 1 | Optional |
| `strategy/generation/loaders/galaxy_layouts_loader.py` | 1 | Optional |
| `strategy/services/ship_stats_calculator.py` | 1 | IRegistryProvider |
| `strategy/systems/save_game_service.py` | 1 | PersistenceException |
| `strategy/validation/transfer_validator.py` | 1 | Dict |

#### game/ui/ (30 files, 46 unused)
| File | Count | Unused Imports |
|------|-------|----------------|
| `ui/screens/builder/__init__.py` | 7 | BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, ComponentListItem, LayerPanel, ComponentDetailPanel, ModifierLogic |
| `ui/screens/strategy_panel_manager.py` | 4 | Paths, StrategyMenuPanel, PANEL_WIDTH, PANEL_HEIGHT |
| `ui/screens/empire_panel_window.py` | 3 | Dict, PLANET_RESOURCES, Paths |
| `ui/screens/builder/panel_layout_config.py` | 3 | field, Optional, pygame |
| `ui/screens/build_queue_renderer.py` | 2 | Dict, Set |
| `ui/screens/race_setup_screen.py` | 2 | List, Paths |
| `ui/screens/builder/right_panel.py` | 2 | UITextBox, UIElement |
| `ui/components/table/header.py` | 1 | Optional |
| `ui/panels/race_environment_panel.py` | 1 | List |
| `ui/panels/system_tree_panel.py` | 1 | UIPanel |
| `ui/screens/battle_screen.py` | 1 | BattleConfig |
| `ui/screens/cargo_quick_dialog.py` | 1 | IssueTransferCommand |
| `ui/screens/design_selector_window.py` | 1 | List |
| `ui/screens/empire_build_queue_viewmodel.py` | 1 | Any |
| `ui/screens/fleet_report_view_model.py` | 1 | Any |
| `ui/screens/keybindings_scene.py` | 1 | UIPanel |
| `ui/screens/planet_list_window.py` | 1 | pygame_gui.windows |
| `ui/screens/strategy_camera_nav.py` | 1 | pygame |
| `ui/screens/strategy_detail_formatter.py` | 1 | pygame_gui.elements |
| `ui/screens/strategy_event_router.py` | 1 | hex_distance |
| `ui/screens/strategy_menu_panel.py` | 1 | Optional |
| `ui/screens/strategy_screen.py` | 1 | StarSystem |
| `ui/screens/strategy_ui.py` | 1 | Optional |
| `ui/screens/workshop_event_router.py` | 1 | UIDropDownMenu |
| `ui/screens/builder/schematic_view.py` | 1 | LayerType |
| `ui/screens/builder/structure_list_items.py` | 1 | StructurePanelLayoutConfig |
| `ui/screens/galaxy_test/system_mode.py` | 1 | STAR_FALLBACK |
| `ui/screens/test_lab/screen.py` | 1 | ConfirmationDialog |
| `ui/screens/test_lab/screen_input_handler.py` | 1 | Optional |
| `ui/services/ship_io_adapter.py` | 1 | ShipIOType |
