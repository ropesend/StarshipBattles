# Prospective Project: Test Coverage - Strategy Engine

## Overview
This project addresses critical test coverage gaps in the Strategy layer's engine and service components. The Strategy layer handles core game mechanics (fleet navigation, production, combat resolution, save/load) and several critical paths lack adequate test coverage, risking undetected bugs in game state management.

## Grouping Rationale
These findings all relate to test coverage gaps in the Strategy layer:
1. **Critical game mechanics** - Fleet navigation, command handling, production, superweapons
2. **Shared fix strategy** - Writing comprehensive unit and integration tests
3. **Same layer** - All findings affect game/strategy/ components
4. **Natural dependencies** - Some tests require proper infrastructure before others

## Source
- **Sweep:** 2026-02-13_092036_sweep_full-codebase-sweep
- **Findings:** 20 total (2 Critical, 13 Major, 5 Minor)

## Suggested Execution Order
**Should be done SECOND** - After architecture fixes establish a clean foundation. Test coverage work benefits from stable APIs and can validate architecture fixes.

## Findings

### Critical (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-001 | FleetNavigationService Missing Comprehensive Unit Tests | `game/strategy/services/fleet_navigation_service.py` | Medium |
| TCG-STR-003 | Superweapon Order Processor Missing Error Path Tests | `game/strategy/engine/superweapon_order_processor.py` | Medium |

### Major (13)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-004 | Production Engine Tick Consumption Edge Cases | `game/strategy/engine/production_engine.py` | Complex |
| TCG-STR-005 | No Unit Tests for services/ship_stats_calculator.py | `game/strategy/services/ship_stats_calculator.py` | Simple |
| TCG-STR-006 | FleetCapabilityCalculator.can_build_type() Galaxy Interaction | `game/strategy/data/fleet_capability_calculator.py` | Simple |
| TCG-STR-007 | EmpireEconomyCalculator Missing Integration Tests | `game/strategy/engine/empire_economy_calculator.py` | Medium |
| TCG-STR-008 | ConflictResolutionEngine Battle Resolution Paths | `game/strategy/engine/conflict_resolution_engine.py` | Medium |
| TCG-STR-009 | GameSession Missing Order Queueing Tests | `game/strategy/engine/game_session.py` | Simple |
| TCG-STR-010 | Pathfinding Edge Cases Not Covered | `game/strategy/data/pathfinding.py` | Medium |
| TCG-STR-011 | GameInitializer._setup_initial_scenario Edge Cases | `game/strategy/engine/game_initializer.py` | Medium |
| TCG-STR-012 | SaveGameService Round-Trip Edge Cases | `game/strategy/systems/save_game_service.py` | Medium |
| TCG-STR-013 | Fleet.merge_with() Tests Incomplete | `game/strategy/data/fleet.py` | Simple |
| TCG-FND-003 | CollisionSystem Missing Integration Tests | `game/engine/collision.py` | Medium |
| TCG-FND-004 | TechTree.detect_cycles() Has Limited Cycle Tests | `game/research/data/tech_tree.py` | Simple |
| TCG-FND-005 | AI FleeBehavior Has No Direct Tests | `game/ai/behaviors.py` | Simple |

### Minor (5)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| TCG-STR-014 | ResupplyEngine Partial Resupply Tests | `game/strategy/engine/resupply_engine.py` | Simple |
| TCG-STR-015 | RegionClassifier._classify_spiral Boundary Tests | `game/strategy/generation/region_classifier.py` | Simple |
| TCG-STR-016 | QuickstartBuilder.spawn_initial_complexes Failure Path | `game/strategy/quickstart_builder.py` | Simple |
| TCG-STR-017 | DesignMetadata.from_design_file with Missing Fields | `game/strategy/data/design_metadata.py` | Simple |
| TCG-STR-018 | ShipResourceManager Edge Cases | `game/strategy/data/ship_resource_manager.py` | Simple |

## Affected Files

### Strategy Services
- `game/strategy/services/fleet_navigation_service.py`
- `game/strategy/services/ship_stats_calculator.py`

### Strategy Engines
- `game/strategy/engine/production_engine.py`
- `game/strategy/engine/superweapon_order_processor.py`
- `game/strategy/engine/empire_economy_calculator.py`
- `game/strategy/engine/conflict_resolution_engine.py`
- `game/strategy/engine/game_session.py`
- `game/strategy/engine/game_initializer.py`
- `game/strategy/engine/resupply_engine.py`

### Strategy Data
- `game/strategy/data/fleet_capability_calculator.py`
- `game/strategy/data/pathfinding.py`
- `game/strategy/data/fleet.py`
- `game/strategy/data/design_metadata.py`
- `game/strategy/data/ship_resource_manager.py`
- `game/strategy/quickstart_builder.py`
- `game/strategy/generation/region_classifier.py`
- `game/strategy/systems/save_game_service.py`

### Foundation (related)
- `game/engine/collision.py`
- `game/research/data/tech_tree.py`
- `game/ai/behaviors.py`

## Effort Estimate
- **Simple tasks:** 10
- **Medium tasks:** 8
- **Complex tasks:** 2
- **Overall scope:** Medium

## Overlap with Existing Projects
- **PROJ-131 (test-coverage-strategy-ui)** - Overlaps with Strategy test coverage
- **PROJ-130 (test-coverage-core-systems)** - Overlaps with Foundation test coverage
- **PROJ-119 (Test Coverage -- Strategy and UI)** - Direct overlap
- **PROJ-118 (Test Coverage -- Core and Simulation)** - Foundation findings overlap

## Suggested Phases

### Phase 1: Critical Navigation and Commands (3-4 days)
1. TCG-STR-001: Create comprehensive FleetNavigationService unit tests
2. TCG-STR-003: Add error path tests for superweapon validation

### Phase 2: Production and Economy (3-4 days)
3. TCG-STR-004: Add production engine tick edge case tests
4. TCG-STR-007: Create integration tests for EmpireEconomyCalculator
5. TCG-STR-014: Add partial resupply tests

### Phase 3: Combat and Conflict (2-3 days)
6. TCG-STR-008: Add multi-party conflict resolution tests
7. TCG-FND-003: Add collision system integration tests

### Phase 4: Save/Load and Initialization (2-3 days)
8. TCG-STR-012: Add save/load round-trip edge case tests
9. TCG-STR-011: Add game initializer edge case tests
10. TCG-STR-009: Add order queueing tests

### Phase 5: Data Classes and Utilities (2-3 days)
11. TCG-STR-005, TCG-STR-006: Add ship stats and fleet capability tests
12. TCG-STR-010: Add pathfinding edge case tests
13. TCG-STR-013: Complete fleet merge tests
14. Remaining minor findings
