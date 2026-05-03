# Prospective Project: Architecture Layer Violations

## Overview
This project addresses critical and major layer dependency violations and god class issues that undermine the architecture's maintainability. The codebase has layer violations where lower layers (Simulation, Research) incorrectly import from higher layers (AI, UI), and several classes have grown beyond maintainable sizes.

## Grouping Rationale
These findings all relate to structural architecture issues:
1. **Layer violations** - Lower layers importing from higher layers, breaking dependency direction
2. **God classes** - Classes exceeding 500+ lines with too many responsibilities
3. **Circular dependency workarounds** - Late imports and TYPE_CHECKING hacks indicating design issues

All findings share a common fix strategy: refactoring imports, extracting interfaces to protocols, and decomposing large classes.

## Source
- **Sweep:** 2026-02-13_092036_sweep_full-codebase-sweep
- **Findings:** 24 total (2 Critical, 15 Major, 7 Minor)

## Suggested Execution Order
**Should be done FIRST** - Architecture fixes establish a clean foundation for other projects. Layer violations and god classes affect testability and maintainability, so fixing them first benefits all subsequent work.

## Findings

### Critical (2)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-001 | Research UI layer imports from game.ui | `game/research/ui/research_scene.py:19` | Medium |
| ADR-SIM-001 | Simulation imports AI layer in factory functions | `game/simulation/battle_controller.py:718` | Medium |

### Major (15)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-002 | IControllable interface exceeds god class metrics | `game/ai/interfaces/controllable.py:1-478` | Complex |
| ADR-SIM-002 | TYPE_CHECKING import from AI layer | `game/simulation/systems/battle_engine.py:72-73` | Simple |
| ADR-STR-001 | Galaxy Class Exceeds Size Threshold (God Class) | `game/strategy/data/galaxy.py` | Medium |
| ADR-STR-002 | ProductionEngine Exceeds Size Threshold | `game/strategy/engine/production_engine.py` | Medium |
| ADR-UI2-001 | Direct Simulation Layer Import in ship_io | `game/ui/services/ship_io.py:16` | Medium |
| ADR-UI1-001 | TestLabScreen God Class | `game/ui/screens/test_lab/screen.py` | Complex |
| ADR-UI1-002 | FleetReportWindow God Class | `game/ui/screens/fleet_report_window.py` | Medium |
| ADR-UI1-003 | BuildQueueScreen Large Class | `game/ui/screens/build_queue_screen.py` | Medium |
| ADR-UI1-004 | StrategyScreen Large Class | `game/ui/screens/strategy_screen.py` | Medium |
| ADR-UI1-005 | Private Facade Access in Dialogs | `game/ui/screens/cargo_quick_dialog.py` | Simple |
| ADR-UI1-006 | Private Method Access in BattleUI | `game/ui/screens/battle_ui.py:9` | Simple |
| ADR-UI1-007 | StrategyInputHandler Excessive Scene Coupling | `game/ui/screens/strategy_input_handler.py` | Medium |
| ADR-STR-005 | ShipStatsCalculator Imports from Simulation | `game/strategy/services/ship_stats_calculator.py` | Medium |
| ADR-SIM-003 | Ship class exceeds 500 lines (God Class) | `game/simulation/entities/ship.py` | Complex |
| ADR-SIM-004 | BattleController exceeds 500 lines (God Class) | `game/simulation/battle_controller.py` | Medium |

### Minor (7)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-003 | protocols.py exceeds 500 lines | `game/core/protocols.py:1-547` | Simple |
| ADR-SIM-005 | Late import pattern for circular dependency | `game/simulation/entities/ship.py:492, 537` | Complex |
| ADR-STR-003 | Circular Import Workaround in galaxy.py | `game/strategy/data/galaxy.py:3` | Simple |
| ADR-STR-004 | ShipInstance Cross-Layer Late Imports | `game/strategy/data/ship_instance.py` | Complex |
| ADR-UI1-008 | Deep Attribute Chains (Law of Demeter) | `game/ui/screens/test_lab/screen.py` | Simple |
| ADR-UI1-009 | Panel Accessing Internal Cache | `game/ui/screens/test_lab/validation_manager.py` | Simple |
| ADR-UI1-011 | Workshop Data Reloader Private Attribute Access | `game/ui/screens/workshop_data_reloader.py` | Simple |

## Affected Files

### Core/Foundation
- `game/core/protocols.py`
- `game/ai/interfaces/controllable.py`
- `game/research/ui/research_scene.py`

### Simulation
- `game/simulation/battle_controller.py`
- `game/simulation/systems/battle_engine.py`
- `game/simulation/entities/ship.py`

### Strategy
- `game/strategy/data/galaxy.py`
- `game/strategy/data/ship_instance.py`
- `game/strategy/engine/production_engine.py`
- `game/strategy/services/ship_stats_calculator.py`

### UI
- `game/ui/services/ship_io.py`
- `game/ui/screens/test_lab/screen.py`
- `game/ui/screens/test_lab/validation_manager.py`
- `game/ui/screens/fleet_report_window.py`
- `game/ui/screens/build_queue_screen.py`
- `game/ui/screens/strategy_screen.py`
- `game/ui/screens/strategy_input_handler.py`
- `game/ui/screens/cargo_quick_dialog.py`
- `game/ui/screens/battle_ui.py`
- `game/ui/screens/workshop_data_reloader.py`

## Effort Estimate
- **Simple tasks:** 8
- **Medium tasks:** 11
- **Complex tasks:** 5
- **Overall scope:** Large

## Overlap with Existing Projects
- **PROJ-126 (architecture-layer-fixes)** - Direct overlap with Architecture Drift findings
- **PROJ-123 (PROJ-D_architecture-cleanup)** - Overlaps with god class decomposition

## Suggested Phases

### Phase 1: Critical Layer Violations (2-3 days)
Fix the two critical violations:
1. ADR-FND-001: Extract Camera protocol, inject via DI in ResearchScene
2. ADR-SIM-001: Move factory functions to higher layer, require AI factory injection

### Phase 2: Simulation/Strategy Layer Fixes (3-4 days)
3. ADR-SIM-002: Replace AIController with IAIController protocol in type hints
4. ADR-STR-005: Create abstraction for ship stats that doesn't cross layers
5. ADR-UI2-001: Fix ship_io.py simulation layer import

### Phase 3: God Class Decomposition - Priority Classes (5-7 days)
6. ADR-SIM-003: Continue Ship god class decomposition
7. ADR-SIM-004: Extract BattleController factory functions and state management
8. ADR-STR-001: Decompose Galaxy class
9. ADR-STR-002: Decompose ProductionEngine

### Phase 4: UI God Classes and Encapsulation (4-5 days)
10. ADR-UI1-001: Decompose TestLabScreen
11. ADR-UI1-002: Decompose FleetReportWindow
12. ADR-UI1-003, ADR-UI1-004: Decompose BuildQueueScreen and StrategyScreen
13. Fix private access violations (ADR-UI1-005, ADR-UI1-006, ADR-UI1-008, ADR-UI1-009, ADR-UI1-011)

### Phase 5: Protocol and Interface Cleanup (2-3 days)
14. ADR-FND-002: Split IControllable into role-specific interfaces
15. ADR-FND-003: Split protocols.py into domain-specific modules
16. Address remaining circular dependency workarounds
