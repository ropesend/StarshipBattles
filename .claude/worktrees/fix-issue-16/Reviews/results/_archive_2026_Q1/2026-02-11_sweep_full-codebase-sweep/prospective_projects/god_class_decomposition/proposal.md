# Prospective Project: God Class Decomposition

## Overview
This project addresses the 15 god classes and 4 oversized file observations identified across simulation, strategy, and UI layers. These classes range from 353 to 1877 lines with 25-75 methods each, violating single-responsibility principles and making the code difficult to test, maintain, and extend. The fix strategy is consistent: extract cohesive responsibility groups into delegate classes while keeping the original class as a thin facade.

## Grouping Rationale
All findings share the same structural problem (classes that are too large and do too much) and the same fix strategy (facade/delegate extraction pattern). Many of these classes interact with each other (e.g., BattleController uses Ship which uses Component), so decomposing them in a coordinated project avoids creating inconsistent intermediate states. The existing God Class Decomposition projects (PROJ-86 through PROJ-89) already cover most of these findings.

## Source
- **Sweep:** 2026-02-11_sweep_full-codebase-sweep
- **Findings:** 19 total (0 Critical, 15 Major, 0 Minor, 4 Info)

## Suggested Execution Order
**Execute second** (Order 2), after architecture layer violations. God class decomposition is easier once layer boundaries are clean, because the extraction targets are clearer when dependencies flow in the correct direction. However, this project overlaps heavily with existing PROJ-86 through PROJ-89 and may already be fully covered.

## Findings

### Critical
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| - | (none) | - | - |

### Major
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-SIM-005 | God class - battle_controller.py (848 lines) | `game/simulation/battle_control` | Large |
| ADR-SIM-006 | God class - ship.py (809 lines) | `game/simulation/entities/ship.` | Large |
| ADR-SIM-007 | God class - component.py (719 lines) | `game/simulation/components/com` | Medium |
| ADR-STR-003 | ProductionEngine God Class (701 lines, 18 methods) | `game/strategy/engine/productio` | Complex |
| ADR-STR-004 | Galaxy God Class (698 lines, 26 methods) | `game/strategy/data/galaxy.py:9` | Complex |
| ADR-STR-005 | ShipInstance God Class (658 lines, 44 methods) | `game/strategy/data/ship_instan` | Medium |
| ADR-STR-006 | Fleet God Class (353 lines, 41 methods) | `game/strategy/data/fleet.py:69` | Medium |
| ADR-UI1-003 | TestLabScreen God Class (1877 lines, 75 methods) | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-004 | BuilderScreen God Class (1042 lines, 44 methods) | `game/ui/screens/builder/main.p` | Medium |
| ADR-UI1-005 | FormationEditorScreen God Class (701 lines) | `game/ui/screens/formation_edit` | Medium |
| ADR-UI1-006 | StrategyScreen God Class (768 lines, 45 methods) | `game/ui/screens/strategy_scree` | Complex |
| ADR-UI1-009 | BattleScreen God Class (621 lines, 32 methods) | `game/ui/screens/battle_screen.` | Medium |
| ADR-UI1-010 | FleetReportWindow God Class (1075 lines) | `game/ui/screens/fleet_report_w` | Medium |
| ADR-UI1-011 | BuildQueueScreen God Class (1057 lines) | `game/ui/screens/build_queue_sc` | Medium |
| ADR-UI1-012 | EmpireBuildQueueWindow God Class (791 lines) | `game/ui/screens/empire_build_q` | Medium |

### Minor
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| - | (none) | - | - |

### Info
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-UI1-020 | WeaponsReportPanel File Size (1037 lines) | `game/ui/screens/builder/weapon` | Medium |
| ADR-UI1-021 | RaceSummaryPanel (671 lines, 25 methods) | `game/ui/panels/race_summary_pa` | Simple |
| ADR-UI1-022 | WorkshopViewModel (551 lines, 36 methods) | `game/ui/screens/workshop_viewm` | Simple |
| ADR-UI1-023 | StrategyUI Thin Facade (357 lines, 38 methods) - observation | `game/ui/screens/strategy_ui.py` | N |

## Affected Files

**Simulation:**
- `game/simulation/battle_controller.py`
- `game/simulation/components/component.py`
- `game/simulation/entities/ship.py`

**Strategy:**
- `game/strategy/data/fleet.py`
- `game/strategy/data/galaxy.py`
- `game/strategy/data/ship_instance.py`
- `game/strategy/engine/production_engine.py`

**UI:**
- `game/ui/panels/race_summary_panel.py`
- `game/ui/screens/battle_screen.py`
- `game/ui/screens/build_queue_screen.py`
- `game/ui/screens/builder/main.py`
- `game/ui/screens/builder/weapons_report_panel.py`
- `game/ui/screens/empire_build_queue_window.py`
- `game/ui/screens/fleet_report_window.py`
- `game/ui/screens/formation_editor_screen.py`
- `game/ui/screens/strategy_screen.py`
- `game/ui/screens/strategy_ui.py`
- `game/ui/screens/test_lab/screen.py`
- `game/ui/screens/workshop_viewmodel.py`

## Effort Estimate
- **Simple tasks:** 2
- **Medium tasks:** 10
- **Complex tasks:** 6
- **Unknown/N/A:** 1
- **Overall scope:** Medium (but each individual extraction is a significant effort)

## Overlap with Existing Projects
- **PROJ-87** (Strategy Data Tier) - Covers Galaxy, Fleet, ShipInstance god classes. **Direct overlap.**
- **PROJ-86** (Critical UI Tier) - Covers StrategyScreen, TestLabScreen, BuilderScreen god classes. **Direct overlap.**
- **PROJ-88** (Simulation Core Tier) - Covers Ship, BattleController, Component god classes. **Direct overlap.**
- **PROJ-89** (Remaining UI Tier) - Covers remaining UI god classes. **Direct overlap.**

**Note:** This project is almost entirely covered by the existing PROJ-86 through PROJ-89 decomposition projects. It may be best treated as a tracking/validation project rather than creating duplicate work.

## Suggested Phases
1. **Phase 1: Simulation God Classes** - Decompose BattleController, Ship, and Component using facade/delegate pattern (aligns with PROJ-88).
2. **Phase 2: Strategy God Classes** - Decompose ProductionEngine, Galaxy, ShipInstance, and Fleet (aligns with PROJ-87).
3. **Phase 3: UI Screen God Classes** - Decompose TestLabScreen, StrategyScreen, BuilderScreen, BattleScreen, and remaining UI god classes (aligns with PROJ-86, PROJ-89).
