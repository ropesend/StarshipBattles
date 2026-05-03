# Prospective Project: Legacy Code Cleanup

## Overview
This project addresses legacy code holdovers including dead code, incomplete migrations, defensive patterns from old systems, stale comments, and backward compatibility shims that should be removed. Following the project policy of "eradicating old systems completely," this cleanup will improve code clarity and reduce maintenance burden.

## Grouping Rationale
These findings all relate to legacy code that should be removed or completed:
1. **Dead code** - Empty packages, unused methods, stale comments
2. **Incomplete migrations** - Stub methods, partial implementations
3. **Defensive patterns** - getattr/hasattr checks on attributes that should always exist
4. **Backward compatibility** - Shims and fallbacks no longer needed
5. **Shared fix strategy** - Delete, complete, or simplify legacy code

## Source
- **Sweep:** 2026-02-13_092036_sweep_full-codebase-sweep
- **Findings:** 33 total (0 Critical, 10 Major, 16 Minor, 7 Info)

## Suggested Execution Order
**Should be done FIFTH** - After test coverage ensures safety net for deletions. Legacy cleanup benefits from comprehensive tests to validate that removed code was truly dead.

## Findings

### Major (10)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-SIM-001 | Empty Factory Module (Dead Package) | `game/simulation/factories/__init__.py` | Simple |
| LEG-SIM-002 | Incomplete Migration - StrategyBattleModeHandler.apply_results() | `game/simulation/combat/battle_mode_handler.py:225-240` | Medium |
| LEG-SIM-003 | Defensive getattr/hasattr Usage on Core Ship Attributes | Multiple files | Medium |
| LEG-SIM-004 | Hasattr Checks for ability_instances on Components | Multiple files | Simple |
| LEG-UI2-001 | Global Registry Fallback Pattern in ShipFactory | `game/ui/services/ship_factory.py` | Medium |
| LEG-UI2-002 | Global Registry Fallback Pattern in ComponentService | `game/ui/services/component_service.py` | Medium |
| LEG-UI1-001 | Legacy Single-Selection Fields in EmpireBuildQueue | `game/ui/screens/empire_build_queue_window.py` | Medium |
| LEG-UI1-002 | Backward Compatibility Property in TestLabScreen | `game/ui/screens/test_lab/screen.py` | Simple |
| LEG-UI1-003 | Legacy API Method in FleetReportWindow | `game/ui/screens/fleet_report_window.py` | Medium |
| LEG-FND-002 | Extensive getattr() Defensive Patterns | `game/ai/combat_utils.py:63-181` | Complex |

### Minor (16)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-FND-003 | Singleton Pattern Still Used Extensively | `game/core/singleton.py` | Complex |
| LEG-FND-004 | hasattr() Checks for Mock Detection | `game/ai/combat_utils.py:43-47` | Simple |
| LEG-FND-005 | Fallback Behavior Documented Extensively | `game/ai/__init__.py:34-52` | Medium |
| LEG-FND-006 | Commented Strategy Hints in Controller | `game/ai/controller.py:346` | Simple |
| LEG-SIM-005 | V1 Modifier Format Check Still Present | `game/simulation/components/modifier_schema.py:36,50` | Simple |
| LEG-SIM-006 | Projectile Type String Conversion Pattern | `game/simulation/entities/projectile.py:47-53` | Simple |
| LEG-SIM-007 | Legacy Comment References (PROJ-106) | `game/simulation/systems/battle_engine.py:270,322,470` | Simple |
| LEG-SIM-008 | Stale Docstring Reference to Legacy Behavior | `game/simulation/systems/battle_engine.py:177-178` | Simple |
| LEG-UI2-003 | Unused Protocol Import (IBattleUI) | `game/ui/services/battle_ui_service.py` | Simple |
| LEG-UI2-005 | Global Registry Fallback in DesignLoaderAdapter | `game/ui/services/design_loader_adapter.py` | Simple |
| LEG-UI2-006 | Defensive getattr Patterns for Missing Attributes | `game/ui/services/battle_ui_service.py` | Medium |
| LEG-UI2-007 | hasattr Checks for Potentially Missing Attributes | `game/ui/services/battle_ui_service.py` | Medium |
| LEG-UI1-004 | Comments Referencing "Legacy Dispatch" | `game/ui/screens/strategy_input_handler.py` | Simple |
| LEG-UI1-005 | Pass Statements in Stub Methods | `game/ui/screens/test_lab/ship_panels.py` | Simple |
| LEG-UI1-008 | Fallback Chains in Workshop Context | `game/ui/screens/workshop_context.py` | Simple |
| LEG-UI1-009 | PROJ-40 Migration Comments Still Present | `game/ui/screens/fleet_report_filters.py` | Simple |

### Info (7)
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-FND-007 | Potential Dead Parameters in navigate_to | `game/ai/controller.py:434` | Simple |
| LEG-UI2-004 | Unused Method get_ships_folder in ShipIOAdapter | `game/ui/services/ship_io_adapter.py` | Simple |
| LEG-UI1-006 | Extensive hasattr() Checks for Optional Features | Unknown | Complex |
| LEG-UI1-007 | Singleton Instance Access Pattern | Unknown | Complex |
| LEG-UI1-010 | getattr() Defensive Patterns | `game/ui/screens/empire_panel_window.py` | Medium |
| LEG-UI1-011 | Dual-Path Ship/DTO Support in BattlePanel | `game/ui/panels/battle_panels.py` | Deferred |
| LEG-UI1-012 | Build Queue Fallback Mode | `game/ui/panels/build_queue_controller.py` | None |

## Affected Files

### Simulation Layer
- `game/simulation/factories/__init__.py` (delete entire directory)
- `game/simulation/combat/battle_mode_handler.py`
- `game/simulation/components/modifier_schema.py`
- `game/simulation/entities/projectile.py`
- `game/simulation/systems/battle_engine.py`
- `game/simulation/battle_state.py`
- `game/simulation/combat/weapon_firing_system.py`
- `game/simulation/combat/damage_calculator.py`
- `game/simulation/combat/targeting_system.py`
- `game/simulation/entities/ability_aggregator.py`
- `game/simulation/entities/ship_stats.py`
- `game/simulation/entities/combat_endurance.py`

### UI Services
- `game/ui/services/ship_factory.py`
- `game/ui/services/component_service.py`
- `game/ui/services/design_loader_adapter.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/services/ship_io_adapter.py`

### UI Screens
- `game/ui/screens/empire_build_queue_window.py`
- `game/ui/screens/test_lab/screen.py`
- `game/ui/screens/test_lab/ship_panels.py`
- `game/ui/screens/fleet_report_window.py`
- `game/ui/screens/fleet_report_filters.py`
- `game/ui/screens/strategy_input_handler.py`
- `game/ui/screens/workshop_context.py`
- `game/ui/screens/empire_panel_window.py`

### UI Panels
- `game/ui/panels/battle_panels.py`
- `game/ui/panels/build_queue_controller.py`

### Foundation/AI
- `game/core/singleton.py`
- `game/ai/__init__.py`
- `game/ai/combat_utils.py`
- `game/ai/controller.py`

## Effort Estimate
- **Simple tasks:** 18
- **Medium tasks:** 10
- **Complex tasks:** 5
- **Overall scope:** Medium-Large

## Overlap with Existing Projects
- **PROJ-129 (legacy-system-cleanup)** - Direct overlap with legacy findings
- **PROJ-121 (PROJ-B_legacy-eradication)** - Direct overlap
- **PROJ-58 (Eradicate Backward Compatibility Shims)** - Direct overlap

## Suggested Phases

### Phase 1: Dead Code Removal (2-3 days)
Remove clearly dead code with no usage:
1. LEG-SIM-001: Delete game/simulation/factories/ directory
2. LEG-UI2-004: Remove unused get_ships_folder method
3. LEG-UI2-003: Remove unused IBattleUI import
4. LEG-UI1-005: Address stub methods with pass statements
5. Remove stale comments (LEG-SIM-007, LEG-SIM-008, LEG-UI1-004, LEG-UI1-009)

### Phase 2: Defensive Pattern Cleanup - Simulation (3-4 days)
Remove unnecessary defensive patterns:
1. LEG-SIM-003: Audit getattr usage on Ship attributes
2. LEG-SIM-004: Remove hasattr checks for ability_instances
3. LEG-SIM-005: Verify V1 modifiers don't exist, remove check
4. LEG-SIM-006: Audit Projectile callers, remove string handling if unused

### Phase 3: Defensive Pattern Cleanup - UI (3-4 days)
1. LEG-FND-002: Refactor combat_utils defensive patterns
2. LEG-UI2-006, LEG-UI2-007: Clean battle_ui_service patterns
3. LEG-UI1-010: Clean empire_panel_window patterns
4. LEG-FND-004: Remove mock detection hasattr if not needed

### Phase 4: Registry Fallback Removal (3-4 days)
Remove global registry fallback patterns:
1. LEG-UI2-001: Remove fallback in ShipFactory
2. LEG-UI2-002: Remove fallback in ComponentService
3. LEG-UI2-005: Remove fallback in DesignLoaderAdapter
4. Update all callers to always provide registry

### Phase 5: Incomplete Migrations (2-3 days)
Address incomplete migration stubs:
1. LEG-SIM-002: Complete or document apply_results() stub
2. LEG-UI1-001: Remove legacy single-selection fields
3. LEG-UI1-002: Remove backward compatibility property
4. LEG-UI1-003: Remove legacy API method
5. LEG-UI1-008: Remove fallback chains in workshop

### Phase 6: Architectural Legacy (Deferred)
These items are Complex or Deferred:
- LEG-FND-003: Singleton pattern migration (Complex - project-wide)
- LEG-UI1-006, LEG-UI1-007: hasattr checks and singleton access (Complex)
- LEG-UI1-011: Dual-path Ship/DTO (Deferred - requires PROJ-41)
- LEG-UI1-012: Build queue fallback (None - may be intentional)
