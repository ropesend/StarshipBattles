# Prospective Project: Architecture Layer Violations

## Overview
This project addresses all cross-layer dependency violations found throughout the codebase -- pygame imports in the core layer, tkinter in the simulation layer, UI imports in non-UI modules, circular dependency workarounds, and encapsulation breaches where higher layers directly access private internals of lower layers. These are the most architecturally damaging issues in the codebase, preventing headless operation, blocking proper testing, and creating tight coupling between layers that should be independent.

## Grouping Rationale
All findings share the common theme of layer boundary violations. They affect the same architectural concern (dependency direction), frequently touch the same files (e.g., `input_mapper.py`, `screenshot_manager.py`, `persistence.py` appear in multiple findings), and share the same fix strategy: extract framework-dependent code to the UI layer, replace direct imports with protocol/interface abstractions, and eliminate circular dependency workarounds. Fixing these together prevents merge conflicts and ensures a coherent architecture outcome.

## Source
- **Sweep:** 2026-02-11_sweep_full-codebase-sweep
- **Findings:** 52 total (9 Critical, 14 Major, 24 Minor, 5 Info)

## Suggested Execution Order
**Execute first** (Order 1). Layer violations are the most fundamental architectural issues. Fixing them unblocks headless testing, removes circular imports that cause subtle bugs, and establishes clean boundaries that other projects depend on. The god class decomposition and consistency projects will be easier to implement once layers are properly separated.

## Findings

### Critical
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-001 | Pygame imported in game/core/input_mapper.py | `game/core/input_mapper.py:26,3` | Medium |
| ADR-FND-002 | Pygame imported in game/core/screenshot_manager.py | `game/core/screenshot_manager.p` | Simple |
| ADR-FND-003 | Research scene imports from game.ui (Layer Violation) | `game/research/ui/research_scen` | Medium |
| ADR-SIM-001 | AIControllerFactory runtime imports from game.ai | `game/simulation/factories/ai_f` | Medium |
| ADR-SIM-002 | persistence.py imports tkinter UI framework | `game/simulation/systems/persis` | Simple |
| ADR-UI2-001 | Pygame in Core Layer -- ScreenshotManager | `game/core/screenshot_manager.p` | Medium |
| ADR-UI2-002 | Pygame in Core Layer -- InputMapper | `game/core/input_mapper.py:26` | Complex |
| ADR-UI1-001 | Test Lab UI Imports From test_framework packages | `game/ui/screens/test_lab/scree` | Complex |
| ADR-UI1-002 | Simulation Layer Imports tkinter GUI Framework | `game/simulation/systems/persis` | Medium |

### Major
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-004 | Core protocols.py TYPE_CHECKING import from simulation | `game/core/protocols.py:42` | Simple |
| ADR-FND-005 | AI controllable.py TYPE_CHECKING import leak | `game/ai/interfaces/controllabl` | Simple |
| ADR-FND-006 | Research UI files use pygame directly | `game/research/ui/research_cont` | Medium |
| ADR-FND-007 | AIController deep attribute chain (Law of Demeter) | `game/ai/controller.py:410` | Simple |
| ADR-SIM-003 | battle_config.py TYPE_CHECKING import from strategy | `game/simulation/battle_config.` | Simple |
| ADR-SIM-004 | battle_engine.py TYPE_CHECKING import from strategy | `game/simulation/systems/battle` | Simple |
| ADR-STR-008 | ShipDisplayFormatter in Strategy Data Layer has UI concerns | `game/strategy/data/ship_displa` | Medium |
| ADR-STR-011 | hex_to_pixel/pixel_to_hex Usage in Galaxy leaks core into strategy | `game/strategy/data/galaxy.py:5` | Simple |
| ADR-UI1-007 | Extensive Private Attribute Access Across strategy modules | `game/ui/screens/strategy_event` | Medium |
| ADR-UI1-008 | UI Layer Mutates Strategy Data Objects Without Facade | `game/ui/screens/planet_list_fi` | Medium |
| ADR-UI2-003 | Renderer Directly Accesses Simulation Domain Objects | `game/ui/renderer/game_renderer` | Medium |
| ADR-UI2-004 | ShipFactory Uses pygame.math.Vector2 Instead of core math | `game/ui/services/ship_factory.` | Simple |
| ADR-UI2-005 | DesignLoaderAdapter Has Hard Runtime Import | `game/ui/services/design_loader` | Simple |
| ADR-UI2-006 | Pygame TYPE_CHECKING Import in AI Layer | `game/ai/interfaces/controllabl` | Simple |

### Minor
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-008 | UIConfig class in game/core/config.py contains UI concerns | `game/core/config.py:132-198` | Simple |
| ADR-FND-009 | ScreenshotManager.capture_strategy_layer private access | `game/core/screenshot_manager.p` | Simple |
| ADR-FND-010 | Engine collision.py TYPE_CHECKING import | `game/engine/collision.py:55` | Simple |
| ADR-FND-011 | Constants file mixes UI concerns (colors) | `game/core/constants.py:42-49` | Simple |
| ADR-SIM-008 | UI data flow - screen dimensions in simulation | `game/simulation/services/desig` | Simple |
| ADR-SIM-009 | Visual properties embedded in simulation projectile | `game/simulation/entities/proje` | Medium |
| ADR-SIM-010 | Pervasive color_hint in ability display_ data | `game/simulation/components/abi` | Large |
| ADR-SIM-011 | Circular dependency workarounds via late imports in ship.py | `game/simulation/entities/ship.` | Large |
| ADR-SIM-012 | modifier_introspection.py contains UI-specific format code | `game/simulation/components/mod` | Simple |
| ADR-STR-001 | Pervasive Lazy Imports to Avoid Circular Dependencies | `Unknown` | Complex |
| ADR-STR-002 | Galaxy Circular Dependency with Placement strategies | `game/strategy/data/galaxy.py:3` | Medium |
| ADR-STR-007 | FleetBattleAdapter Accesses Private Methods | `game/strategy/data/fleet_battl` | Simple |
| ADR-STR-009 | Color Tuples Embedded in Strategy Game Config | `game/strategy/engine/game_conf` | Medium |
| ADR-STR-013 | EmpireEconomyCalculator Provides "Display" data in strategy | `game/strategy/engine/empire_ec` | Simple |
| ADR-UI1-013 | UIConfig and DisplayConfig in Core Layer | `game/core/config.py:132-159` | Simple |
| ADR-UI1-014 | UI Color Constants (WHITE, BLACK, BLUE, RED) in core | `game/core/constants.py:42-49` | Simple |
| ADR-UI1-015 | Circular Import Avoidance via Late Import in column_manager | `game/ui/screens/column_manager` | Simple |
| ADR-UI1-016 | Module-Level tkinter Initialization Side Effect | `game/ui/screens/formation_edit` | Simple |
| ADR-UI1-017 | Deep Attribute Chains Violating Law of Demeter in TestLab | `game/ui/screens/test_lab/scree` | Medium |
| ADR-UI1-018 | Circular Import Avoidance in new_game_setup | `game/ui/screens/new_game_setup` | Simple |
| ADR-UI1-019 | TestLabScreen Directly Accesses battle_state internals | `game/ui/screens/test_lab/scree` | Simple |
| ADR-UI2-007 | ScreenshotManager Accesses Private _renderer attributes | `game/core/screenshot_manager.p` | Medium |
| ADR-UI2-008 | ValidationService Has Eager Runtime Import from simulation | `game/ui/services/validation_se` | Simple |
| ADR-UI2-009 | game_renderer.py Uses Lazy Import Inside Method | `game/ui/renderer/game_renderer` | Simple |

### Info
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| ADR-FND-012 | Research package has clean data/systems separation | `game/research/data/` | N |
| ADR-SIM-013 | battle_state.py is a large data container (observation) | `game/simulation/battle_state.p` | N |
| ADR-SIM-014 | game.engine dependencies are architecturally appropriate | `Unknown` | N |
| ADR-STR-010 | Misleading Docstring in ShipStatsCalculator | `game/strategy/services/ship_st` | Simple |
| ADR-STR-012 | DesignMetadata Contains sprite_preview Field (UI data in strategy) | `game/strategy/data/design_meta` | Simple |

## Affected Files

**Core / Engine:**
- `game/core/config.py`
- `game/core/constants.py`
- `game/core/input_mapper.py`
- `game/core/protocols.py`
- `game/core/screenshot_manager.py`
- `game/engine/collision.py`

**AI:**
- `game/ai/controller.py`
- `game/ai/interfaces/controllable.py`

**Research:**
- `game/research/ui/research_control_panel.py`
- `game/research/ui/research_scene.py`

**Simulation:**
- `game/simulation/battle_config.py`
- `game/simulation/components/abilities/`
- `game/simulation/components/modifier_introspection.py`
- `game/simulation/entities/projectile.py`
- `game/simulation/entities/ship.py`
- `game/simulation/factories/ai_factory.py`
- `game/simulation/services/design_service.py`
- `game/simulation/systems/battle_engine.py`
- `game/simulation/systems/persistence.py`

**Strategy:**
- `game/strategy/data/design_metadata.py`
- `game/strategy/data/fleet_battle_adapter.py`
- `game/strategy/data/galaxy.py`
- `game/strategy/data/ship_display_formatter.py`
- `game/strategy/engine/empire_economy_calculator.py`
- `game/strategy/engine/game_config.py`
- `game/strategy/services/ship_stats_calculator.py`

**UI:**
- `game/ui/panels/builder_widgets/`
- `game/ui/renderer/game_renderer.py`
- `game/ui/screens/column_manager.py`
- `game/ui/screens/formation_editor_screen.py`
- `game/ui/screens/new_game_setup_screen.py`
- `game/ui/screens/planet_list_filters.py`
- `game/ui/screens/strategy_event_router.py`
- `game/ui/screens/test_lab/screen.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/ship_factory.py`
- `game/ui/services/validation_service.py`

## Effort Estimate
- **Simple tasks:** 28
- **Medium tasks:** 15
- **Complex tasks:** 5
- **Unknown/N/A:** 4
- **Overall scope:** Large

## Overlap with Existing Projects
- **PROJ-106** (Architecture Layer Violations) - Direct overlap. This project was likely created from an earlier analysis. Should be merged or superseded.
- **PROJ-90** (Untangle Circular Dependencies and Layer Violations) - Significant overlap on circular import findings.
- **PROJ-92** (Clean Up Residual Circular Dependency Artifacts) - Overlaps on circular dependency workarounds.
- **PROJ-91** (Unify Resource/State Logic Between Strategy and Simulation Layers) - Partial overlap on simulation/strategy boundary violations.
- **PROJ-93** (Update Protocol Layer Type Annotations) - Overlaps on TYPE_CHECKING import findings.

## Suggested Phases
1. **Phase 1: Core Layer Purification** - Remove pygame from `input_mapper.py` and `screenshot_manager.py`, move `UIConfig` and color constants to UI layer, fix `protocols.py` TYPE_CHECKING imports.
2. **Phase 2: Simulation Layer Isolation** - Remove tkinter from `persistence.py`, fix `ai_factory.py` cross-layer import, resolve TYPE_CHECKING imports, extract UI-specific data from simulation entities.
3. **Phase 3: Strategy Layer Boundaries** - Fix circular dependencies in Galaxy, remove UI display concerns from strategy data classes, standardize hex math usage.
4. **Phase 4: UI Encapsulation** - Fix test_lab imports from test infrastructure, eliminate private attribute access across modules, ensure UI uses facades for data mutation.
5. **Phase 5: Circular Import Cleanup** - Resolve all remaining lazy/late import workarounds by proper dependency inversion.
