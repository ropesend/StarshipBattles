# Prospective Project: Test Coverage -- Core and Simulation

## Overview
This project addresses all test coverage gaps in the foundation layers (core, engine, AI, research) and simulation layer. These are the most critical test gaps because core and simulation form the backbone of the entire application -- untested code here affects every dependent system. The findings range from completely untested classes (BattleService, ProjectileManager, AbilityAggregator) to missing edge case tests for critical combat calculations and physics formulas.

## Grouping Rationale
Foundation and simulation test gaps are grouped together because: (1) they share the same testing infrastructure and patterns (unit tests with minimal mocking), (2) simulation tests often require core fixtures and utilities, (3) they form the bottom two layers of the architecture, and (4) they should be stabilized before testing higher layers that depend on them. The combined count of 51 findings is appropriate for a single focused testing project.

## Source
- **Sweep:** 2026-02-11_sweep_full-codebase-sweep
- **Findings:** 51 total (8 Critical, 22 Major, 14 Minor, 7 Info)

## Suggested Execution Order
**Execute sixth** (Order 6), in parallel with or after legacy cleanup. Test coverage work is independent of most other projects and can proceed in parallel. However, if legacy dead code is removed first, some test gaps may become moot (tests for dead code are not needed). Foundation tests should be written before UI tests since they establish test patterns and infrastructure.

## Findings

### Critical
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-FND-001 | PhysicsBody.apply_force() and forward_velocity not tested | `game/engine/physics.py` | Simple |
| TCG-FND-002 | AIController.update() Integration Path Not Tested | `game/ai/controller.py` | Medium |
| TCG-FND-003 | CollisionSystem.process_beam_attack() Hit detection not tested | `game/engine/collision.py` | Medium |
| TCG-SIM-001 | BattleService has no unit tests | `game/simulation/services/battl` | Medium |
| TCG-SIM-002 | ProjectileManager has no unit tests | `game/simulation/projectile_man` | Complex |
| TCG-SIM-003 | AbilityAggregator has no unit tests | `game/simulation/entities/abili` | Medium |
| TCG-SIM-004 | ShipPhysicsMixin has no unit tests | `game/simulation/entities/ship_` | Medium |
| TCG-SIM-005 | ShipFormation has no unit tests | `game/simulation/entities/ship_` | Simple |

### Major
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-FND-004 | SpatialGrid.query_radius() Boundary and Edge Case Tests | `game/engine/spatial.py` | Simple |
| TCG-FND-005 | AIController._handle_formation_master() Missing Tests | `game/ai/controller.py` | Medium |
| TCG-FND-006 | AIController._check_formation_integrity() Missing Tests | `game/ai/controller.py` | Simple |
| TCG-FND-007 | AIController.check_avoidance() Collision Tests Missing | `game/ai/controller.py` | Medium |
| TCG-FND-008 | AIController.navigate_to() Core Navigation Not Tested | `game/ai/controller.py` | Simple |
| TCG-FND-009 | ResearchService.process_turn() Leaky Bucket Tests Missing | `game/research/systems/research` | Simple |
| TCG-FND-010 | TechNode.get_effective_price() Only Partially Tested | `game/research/data/tech_node.p` | Simple |
| TCG-FND-011 | ResearchRenderer Test Coverage is Minimal | `game/research/ui/research_rend` | Simple |
| TCG-FND-012 | ResearchControlPanel.handle_event() Lacks Event Tests | `game/research/ui/research_cont` | Medium |
| TCG-FND-024 | No Integration Test for AI Controller + Strategy Manager | `tests/integration/ai_strategy/` | Medium |
| TCG-SIM-006 | ShipSerializer has no dedicated unit tests | `game/simulation/entities/ship_` | Medium |
| TCG-SIM-007 | VehicleDesignService has no unit tests | `game/simulation/services/vehic` | Medium |
| TCG-SIM-008 | ModifierService has no unit tests | `game/simulation/services/modif` | Medium |
| TCG-SIM-009 | CombatEndurance calculations have no unit tests | `game/simulation/entities/comba` | Simple |
| TCG-SIM-010 | ShipStatQuerier has no unit tests | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-011 | ShipLoader functions have no dedicated unit tests | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-012 | DamageCalculator _damage_layer weighted selection not tested | `game/simulation/combat/damage_` | Simple |
| TCG-SIM-013 | BattleState serialization round-trip not tested | `game/simulation/battle_state.p` | Medium |
| TCG-SIM-024 | No tests for BattleEngine.update tick processing | `game/simulation/systems/battle` | Complex |
| TCG-SIM-025 | No boundary tests for physics formula calculations | `game/simulation/entities/ship_` | Simple |
| TCG-SIM-026 | No tests for resource consumption during combat abilities | `game/simulation/components/abi` | Medium |
| TCG-SIM-027 | ShipCombatEngine combat cooldowns only partially tested | `game/simulation/entities/ship_` | Simple |

### Minor
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-FND-013 | StrategyManager.resolve_strategy() Default Fallback Not Tested | `game/ai/strategy_manager.py` | Simple |
| TCG-FND-014 | HexCoord Arithmetic with Non-HexCoord Types Not Tested | `game/core/hex_math.py` | Simple |
| TCG-FND-015 | pixel_to_hex() Rounding Edge Cases at Cell Boundaries | `game/core/hex_math.py` | Simple |
| TCG-FND-016 | RegistryManager.hydrate() Partial Resource Loading Not Tested | `game/core/registry.py` | Simple |
| TCG-FND-017 | combat_utils.is_in_pdc_arc() Missing Test Coverage | `game/ai/combat_utils.py` | Simple |
| TCG-FND-018 | TargetEvaluator._eval_speed_rule() Slower Target Preference Not Tested | `game/ai/target_evaluator.py` | Simple |
| TCG-FND-019 | ResearchTracker.spread_rp_evenly() Does Not Test Zero RP Case | `game/research/data/research_tr` | Simple |
| TCG-SIM-014 | Abilities base class (Ability) has no isolated tests | `game/simulation/components/abi` | Simple |
| TCG-SIM-015 | ColonizeAbility and HarvesterAbility have no unit tests | `game/simulation/components/abi` | Simple |
| TCG-SIM-016 | ModifierIntrospection has no unit tests | `game/simulation/components/mod` | Simple |
| TCG-SIM-017 | ComponentHealthManager has no unit tests | `game/simulation/components/com` | Simple |
| TCG-SIM-018 | ComponentResourceManager has no unit tests | `game/simulation/components/com` | Simple |
| TCG-SIM-019 | TechPresetLoader has no unit tests | `game/simulation/systems/tech_p` | Simple |
| TCG-SIM-020 | LayerData has no unit tests | `game/simulation/entities/layer` | Simple |

### Info
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-FND-020 | Collision Edge Case Tests Use Heavy Mocking (fragile) | `tests/unit/engine/collision_ed` | Complex |
| TCG-FND-021 | ScreenshotManager Tests Are Fragile Due to Singleton | `tests/unit/core/test_screensho` | Simple |
| TCG-FND-022 | StrategyMetadataService Uses Legacy Singleton in tests | `game/core/strategy_metadata.py` | Simple |
| TCG-FND-023 | ErraticBehavior Uses `import random` Instead of injectable RNG | `game/ai/behaviors.py` | Simple |
| TCG-SIM-021 | Weapon ability classes tested primarily through integration | `game/simulation/components/abi` | Medium |
| TCG-SIM-022 | Defense ability classes tested primarily through integration | `game/simulation/components/abi` | Simple |
| TCG-SIM-023 | ShipIO (persistence.py) inherently difficult to test | `game/simulation/systems/persis` | N |

## Affected Files

**Core / Engine:**
- `game/core/hex_math.py`
- `game/core/registry.py`
- `game/core/screenshot_manager.py`
- `game/core/strategy_metadata.py`
- `game/engine/collision.py`
- `game/engine/physics.py`
- `game/engine/spatial.py`

**AI:**
- `game/ai/behaviors.py`
- `game/ai/combat_utils.py`
- `game/ai/controller.py`
- `game/ai/strategy_manager.py`
- `game/ai/target_evaluator.py`

**Research:**
- `game/research/data/research_tracker.py`
- `game/research/data/tech_node.py`
- `game/research/systems/research_service.py`
- `game/research/ui/research_control_panel.py`
- `game/research/ui/research_renderer.py`

**Simulation:**
- `game/simulation/battle_state.py`
- `game/simulation/combat/damage_calculator.py`
- `game/simulation/components/abilities/`
- `game/simulation/components/component_health_manager.py`
- `game/simulation/components/component_resource_manager.py`
- `game/simulation/components/modifier_introspection.py`
- `game/simulation/entities/ability_aggregator.py`
- `game/simulation/entities/combat_endurance.py`
- `game/simulation/entities/layer_data.py`
- `game/simulation/entities/ship_combat_engine.py`
- `game/simulation/entities/ship_formation.py`
- `game/simulation/entities/ship_loader.py`
- `game/simulation/entities/ship_physics_mixin.py`
- `game/simulation/entities/ship_serializer.py`
- `game/simulation/entities/ship_stat_querier.py`
- `game/simulation/projectile_manager.py`
- `game/simulation/services/battle_service.py`
- `game/simulation/services/modifier_service.py`
- `game/simulation/services/vehicle_design_service.py`
- `game/simulation/systems/battle_engine.py`
- `game/simulation/systems/persistence.py`
- `game/simulation/systems/tech_preset_loader.py`

**Tests:**
- `tests/unit/core/`
- `tests/unit/engine/`
- `tests/unit/simulation/`
- `tests/integration/ai_strategy/`

## Effort Estimate
- **Simple tasks:** 32
- **Medium tasks:** 15
- **Complex tasks:** 3
- **Unknown/N/A:** 1
- **Overall scope:** Medium

## Overlap with Existing Projects
- **PROJ-110** (Test Coverage - Core Systems) - Direct overlap for FND findings. Should be merged or superseded.
- **PROJ-111** (Test Coverage - UI and Framework) - No overlap (that project covers UI, this one covers core and simulation).

## Suggested Phases
1. **Phase 1: Engine and Core Tests** - Write tests for PhysicsBody, CollisionSystem, SpatialGrid, HexCoord edge cases, RegistryManager.hydrate().
2. **Phase 2: AI Controller Tests** - Write integration and unit tests for AIController.update(), formation handling, avoidance, navigation.
3. **Phase 3: Simulation Entity Tests** - Write tests for ShipPhysicsMixin, ShipFormation, AbilityAggregator, ShipSerializer, CombatEndurance, ShipStatQuerier, LayerData.
4. **Phase 4: Simulation Service Tests** - Write tests for BattleService, ProjectileManager, VehicleDesignService, ModifierService, BattleEngine tick processing.
5. **Phase 5: Simulation Component Tests** - Write tests for Ability base class, ColonizeAbility, HarvesterAbility, ComponentHealthManager, ComponentResourceManager, resource consumption during combat.
