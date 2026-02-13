# Prospective Project: Legacy Dead Code Eradication

## Overview
This project removes all legacy system holdovers found across the codebase: backward compatibility wrappers, dead code paths, unused modules, deprecated methods, vestigial attributes, hasattr/getattr guards for attributes that always exist, and old format support branches that are never exercised. Per the project's System Migration Policy, old systems must be eradicated completely -- no fallbacks, no compatibility layers, no commented-out code.

## Grouping Rationale
All 65 findings are LEG (Legacy System Holdovers) type, sharing the same root cause (code that once served a purpose but is no longer needed) and the same fix strategy (delete the dead code and update any remaining references). Many findings cluster in the same files (e.g., `persistence.py`, `resources.py`, `controller.py`, `battle_ui_service.py`) making it efficient to address them together. This is the safest project to execute because it is purely subtractive -- it removes code without adding new behavior.

## Source
- **Sweep:** 2026-02-11_sweep_full-codebase-sweep
- **Findings:** 65 total (6 Critical, 24 Major, 26 Minor, 9 Info)

## Suggested Execution Order
**Execute third** (Order 3), after architecture layer violations and in parallel with or after god class decomposition. Legacy removal is safe to do at any time, but it is more effective after layer violations are fixed (some legacy code exists specifically to work around layer violations). It can also run in parallel with consistency and duplication projects since the affected files rarely overlap.

## Findings

### Critical
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-FND-001 | Backward Compatibility Wrapper `load_resources` wraps `load_resources_data` | `game/core/resources.py:101-143` | Medium |
| LEG-SIM-001 | Empty ABILITY_CLASS_MAP dict still imported by 3+ modules | `game/simulation/components/abi` | Simple |
| LEG-SIM-007 | resource_manager.py re-exports ability classes (dead indirection) | `game/simulation/systems/resour` | Medium |
| LEG-SIM-008 | component.py uses get_default_registry_provider (legacy DI) | `game/simulation/components/com` | Medium |
| LEG-UI2-001 | Legacy widgets.py Module - Entire File is dead code | `game/ui/widgets.py:1-102` | Simple |
| LEG-UI1-001 | Legacy BuilderScreen (builder/main.py) - marked deprecated | `game/ui/screens/builder/main.p` | Medium |

### Major
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-FND-002 | StrategyMetadataService Uses Hand-Rolled singleton | `game/core/strategy_metadata.py` | Simple |
| LEG-FND-003 | Dead Instance Attributes `attack_state` in AIController | `game/ai/controller.py:90-91` | Simple |
| LEG-FND-004 | Duplicate Path Resolution Logic in resources.py | `game/core/resources.py:31-52` | Simple |
| LEG-FND-005 | Unused Protocol Classes and TypeGuard Functions | `game/core/protocols.py:85-110,` | Simple |
| LEG-SIM-002 | ability_aggregator dict-format branch is dead code | `game/simulation/entities/abili` | Simple |
| LEG-SIM-003 | persistence.py ShipIO calls Ship.from_dict (legacy path) | `game/simulation/systems/persis` | Medium |
| LEG-SIM-004 | persistence.py imports tkinter (UI dependency in sim) | `game/simulation/systems/persis` | Medium |
| LEG-SIM-005 | designs.py hardcoded ship factories only for test usage | `game/simulation/designs.py:11-` | Medium |
| LEG-SIM-009 | String-based missile type checking is legacy pattern | `game/simulation/entities/proje` | Simple |
| LEG-SIM-010 | Multiple hasattr/getattr checks for always-present attrs | `Unknown` | Simple |
| LEG-SIM-013 | ResourceDependencyRule has dual-path validation | `game/simulation/validation/shi` | Simple |
| LEG-SIM-014 | WeaponAbility.recalculate() uses hasattr for guaranteed attrs | `game/simulation/components/abi` | Simple |
| LEG-SIM-019 | _apply_results_to_fleet is a complete stub | `game/simulation/battle_control` | Complex |
| LEG-SIM-020 | is_v2_format() implies V1 format still exists | `game/simulation/components/mod` | Simple |
| LEG-UI2-002 | SpriteManager Atlas Fallback - Dead Code Path | `game/ui/renderer/sprites.py:40` | Simple |
| LEG-UI2-003 | draw_hud() and draw_bar() in game_renderer.py are dead | `game/ui/renderer/game_renderer` | Simple |
| LEG-UI2-004 | BattleOrchestrator Never Used in Production | `game/ui/orchestration/battle_o` | Medium |
| LEG-UI2-005 | show_overlay Hack - State Passed via Dynamic Attribute | `game/ui/renderer/game_renderer` | Simple |
| LEG-UI2-006 | draw_ship() Uses Singleton ShipThemeManager (legacy pattern) | `game/ui/renderer/game_renderer` | Medium |
| LEG-UI1-002 | Backward Compatibility Aliases in Race Flag Gallery | `game/ui/panels/race_flag_galle` | Simple |
| LEG-UI1-003 | Deprecated Methods on BattleScreen (handle_* stubs) | `game/ui/screens/battle_screen.` | Simple |
| LEG-UI1-004 | Legacy Tuple Format Support in detail_panel.py | `game/ui/screens/builder/detail` | Medium |
| LEG-UI1-005 | Backwards Compatibility Fallbacks in workshop_event_router | `game/ui/screens/workshop_event` | Simple |
| LEG-UI1-006 | Legacy Shim Skip List in detail_panel.py | `game/ui/screens/builder/detail` | Simple |

### Minor
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-FND-006 | `LayerType.from_string()` Static Method is unused | `game/core/constants.py:117-119` | Simple |
| LEG-FND-007 | `ScreenshotManager.capture_step()` Never Called | `game/core/screenshot_manager.p` | Simple |
| LEG-FND-008 | Python 3.9 Compatibility Shim for TypeGuard | `game/core/protocols.py:32-36` | Simple |
| LEG-FND-009 | Color Constants (WHITE, BLACK, BLUE, RED) in core | `game/core/constants.py:42-46` | Simple |
| LEG-FND-010 | `json` Import in resources.py Only Needed by legacy path | `game/core/resources.py:13` | Simple |
| LEG-FND-011 | `_get_hp_percent` and `_is_in_pdc_arc` wrappers are trivial | `game/ai/controller.py:269-273` | Simple |
| LEG-FND-012 | `FONT_MAIN` Constant Defined but Unused | `game/core/constants.py:49` | Simple |
| LEG-SIM-006 | FORMULA_* string constants are documentation artifacts | `game/simulation/physics_consta` | Simple |
| LEG-SIM-011 | shots_hit attribute dynamically added in projectile_manager | `game/simulation/projectile_man` | Simple |
| LEG-SIM-012 | combat_endurance.py legacy fallback for missing attributes | `game/simulation/entities/comba` | Simple |
| LEG-SIM-015 | CargoStorage uses string layer instead of LayerType enum | `game/simulation/components/abi` | Simple |
| LEG-SIM-016 | ability_manager.py has [KNOWN_ISSUE] workaround | `game/simulation/components/abi` | Complex |
| LEG-SIM-017 | Ship.base_mass is always 0.0 - vestigial attribute | `game/simulation/entities/ship.` | Simple |
| LEG-SIM-018 | Duplicate shield_regen_cost initialization | `game/simulation/entities/ship_` | Simple |
| LEG-UI2-007 | Unnecessary hasattr Guard on LayerType.value | `game/ui/services/battle_ui_ser` | Simple |
| LEG-UI2-008 | getattr(ship, 'id', id(ship)) - Ship.id always exists | `game/ui/services/battle_ui_ser` | Simple |
| LEG-UI2-009 | Excessive getattr Usage in _convert_projectile | `game/ui/services/battle_ui_ser` | Medium |
| LEG-UI2-010 | interfaces/__init__.py Re-exports Never Used | `game/ui/interfaces/__init__.py` | Simple |
| LEG-UI1-007 | Duplicate show_overlay Toggle Keybinding | `game/ui/screens/battle_screen.` | Simple |
| LEG-UI1-008 | Stale Comment about Removed Duplicate Method | `game/ui/screens/battle_screen.` | Simple |
| LEG-UI1-009 | Hardcoded 1920x1080 Fallback Resolution | `game/ui/screens/new_game_setup` | Simple |
| LEG-UI1-010 | Duplicate Assignment on Consecutive Lines | `game/ui/screens/builder/left_p` | Simple |
| LEG-UI1-011 | Unnecessary hasattr Guard for _facade | `game/ui/screens/strategy_windo` | Simple |
| LEG-UI1-012 | Dead hasattr Check for print_headless_summary | `game/ui/screens/battle_screen.` | Simple |
| LEG-UI1-013 | Monkey-Patching Domain Objects with Temp Attributes | `game/ui/screens/strategy_rende` | Medium |
| LEG-UI1-014 | Unused Module-Level Constants | `game/ui/screens/builder/stats_` | Simple |

### Info
| ID | Title | Location | Effort |
|----|-------|----------|--------|
| LEG-FND-013 | `DEBUG_SCREENSHOTS = True` Always Enabled | `game/core/constants.py:53` | Simple |
| LEG-FND-014 | `profiling.py` Comment References "backward compat" | `game/core/profiling.py:104` | Simple |
| LEG-SIM-021 | ShipStatsCalculator._check_mass_limits has dead branch | `game/simulation/entities/ship_` | Simple |
| LEG-SIM-022 | TechPresetLoader has no production callers | `game/simulation/systems/tech_p` | Medium |
| LEG-SIM-023 | EmpireStorageAbility uses non-standard string layer | `game/simulation/components/abi` | Simple |
| LEG-UI2-011 | SpriteManager and ShipThemeManager Use Singletons | `game/ui/renderer/sprites.py:7` | Complex |
| LEG-UI2-012 | game/ui/__init__.py Purpose is xdist Race Condition Workaround | `game/ui/__init__.py:1-27` | Simple |
| LEG-UI1-015 | Deprecated Properties on StrategyScreen | `game/ui/screens/strategy_scree` | Simple |
| LEG-UI1-016 | test_lab/screen.py Accepts Game Object "just in case" | `game/ui/screens/test_lab/scree` | Medium |

## Affected Files

**Core / Engine:**
- `game/core/constants.py`
- `game/core/profiling.py`
- `game/core/protocols.py`
- `game/core/resources.py`
- `game/core/screenshot_manager.py`
- `game/core/strategy_metadata.py`

**AI:**
- `game/ai/controller.py`

**Simulation:**
- `game/simulation/battle_controller.py`
- `game/simulation/components/abilities/`
- `game/simulation/components/ability_manager.py`
- `game/simulation/components/component.py`
- `game/simulation/components/modifier_format.py`
- `game/simulation/designs.py`
- `game/simulation/entities/ability_aggregator.py`
- `game/simulation/entities/combat_endurance.py`
- `game/simulation/entities/projectile.py`
- `game/simulation/entities/ship.py`
- `game/simulation/entities/ship_physics_mixin.py`
- `game/simulation/physics_constants.py`
- `game/simulation/projectile_manager.py`
- `game/simulation/systems/persistence.py`
- `game/simulation/systems/resource_manager.py`
- `game/simulation/systems/tech_preset_loader.py`
- `game/simulation/validation/ship_validator.py`

**UI:**
- `game/ui/__init__.py`
- `game/ui/interfaces/__init__.py`
- `game/ui/orchestration/battle_orchestrator.py`
- `game/ui/panels/race_flag_gallery.py`
- `game/ui/renderer/game_renderer.py`
- `game/ui/renderer/sprites.py`
- `game/ui/screens/battle_screen.py`
- `game/ui/screens/builder/detail_panel.py`
- `game/ui/screens/builder/left_panel.py`
- `game/ui/screens/builder/main.py`
- `game/ui/screens/builder/stats_panel.py`
- `game/ui/screens/new_game_setup_screen.py`
- `game/ui/screens/strategy_renderer.py`
- `game/ui/screens/strategy_screen.py`
- `game/ui/screens/strategy_window_manager.py`
- `game/ui/screens/test_lab/screen.py`
- `game/ui/screens/workshop_event_router.py`
- `game/ui/services/battle_ui_service.py`
- `game/ui/widgets.py`

## Effort Estimate
- **Simple tasks:** 48
- **Medium tasks:** 14
- **Complex tasks:** 3
- **Overall scope:** Large (but predominantly simple deletions)

## Overlap with Existing Projects
- **PROJ-109** (Legacy Cleanup) - Direct overlap. This project was likely created from an earlier analysis. Should be merged or superseded.
- **PROJ-58** (Eradicate Backward Compatibility Shims) - Partial overlap, though PROJ-58 may already be complete per MEMORY.md.
- **PROJ-94** (Resource API Cleanup and Protocol Wiring) - Some overlap on resources.py legacy wrappers.

## Suggested Phases
1. **Phase 1: Foundation Layer Cleanup** - Remove dead code from `resources.py`, `constants.py`, `protocols.py`, `strategy_metadata.py`, `screenshot_manager.py`, and `controller.py`.
2. **Phase 2: Simulation Layer Cleanup** - Remove empty ABILITY_CLASS_MAP, dead ability_aggregator branches, persistence.py legacy paths, vestigial attributes, hasattr guards.
3. **Phase 3: UI Framework Cleanup** - Delete `widgets.py` entirely, remove dead `draw_hud()`/`draw_bar()`, remove BattleOrchestrator, clean SpriteManager fallbacks.
4. **Phase 4: UI Screens Cleanup** - Remove deprecated BuilderScreen, backward compat aliases, legacy tuple format support, deprecated BattleScreen methods.
