# PROJ-117: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-11_sweep_full-codebase-sweep](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/)
- **Type:** Sweep Review (automated parallel analysis)
- **Date:** 2026-02-11
- **Report:** [View Full Report](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 396 total findings identified.
- **Critical:** 6
- **Major:** 24
- **Selected for remediation:** 65

## Selected Findings Summary

### LEG-FND-001: Backward Compatibility Wrapper `load_res
- **Severity:** Critical
- **Location:** `game/core/resources.py:101-143`
- **Effort:** Medium

### LEG-SIM-001: Empty ABILITY_CLASS_MAP dict still impor
- **Severity:** Critical
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### LEG-SIM-007: resource_manager.py re-exports ability c
- **Severity:** Critical
- **Location:** `game/simulation/systems/resour`
- **Effort:** Medium

### LEG-SIM-008: component.py uses get_default_registry_p
- **Severity:** Critical
- **Location:** `game/simulation/components/com`
- **Effort:** Medium

### LEG-UI2-001: Legacy widgets.py Module - Entire File i
- **Severity:** Critical
- **Location:** `game/ui/widgets.py:1-102`
- **Effort:** Simple

### LEG-UI1-001: Legacy BuilderScreen (builder/main.py) -
- **Severity:** Critical
- **Location:** `game/ui/screens/builder/main.p`
- **Effort:** Medium

### LEG-FND-002: StrategyMetadataService Uses Hand-Rolled
- **Severity:** Major
- **Location:** `game/core/strategy_metadata.py`
- **Effort:** Simple

### LEG-FND-003: Dead Instance Attributes `attack_state`
- **Severity:** Major
- **Location:** `game/ai/controller.py:90-91`
- **Effort:** Simple

### LEG-FND-004: Duplicate Path Resolution Logic in resou
- **Severity:** Major
- **Location:** `game/core/resources.py:31-52`
- **Effort:** Simple

### LEG-FND-005: Unused Protocol Classes and TypeGuard Fu
- **Severity:** Major
- **Location:** `game/core/protocols.py:85-110,`
- **Effort:** Simple

### LEG-SIM-002: ability_aggregator dict-format branch is
- **Severity:** Major
- **Location:** `game/simulation/entities/abili`
- **Effort:** Simple

### LEG-SIM-003: persistence.py ShipIO calls Ship.from_di
- **Severity:** Major
- **Location:** `game/simulation/systems/persis`
- **Effort:** Medium

### LEG-SIM-004: persistence.py imports tkinter (UI depen
- **Severity:** Major
- **Location:** `game/simulation/systems/persis`
- **Effort:** Medium

### LEG-SIM-005: designs.py hardcoded ship factories only
- **Severity:** Major
- **Location:** `game/simulation/designs.py:11-`
- **Effort:** Medium

### LEG-SIM-009: String-based missile type checking is a
- **Severity:** Major
- **Location:** `game/simulation/entities/proje`
- **Effort:** Simple

### LEG-SIM-010: Multiple hasattr/getattr checks for alwa
- **Severity:** Major
- **Location:** `Unknown`
- **Effort:** Simple

### LEG-SIM-013: ResourceDependencyRule has dual-path val
- **Severity:** Major
- **Location:** `game/simulation/validation/shi`
- **Effort:** Simple

### LEG-SIM-014: WeaponAbility.recalculate() uses hasattr
- **Severity:** Major
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### LEG-SIM-019: _apply_results_to_fleet is a complete st
- **Severity:** Major
- **Location:** `game/simulation/battle_control`
- **Effort:** Complex

### LEG-SIM-020: is_v2_format() implies V1 format still e
- **Severity:** Major
- **Location:** `game/simulation/components/mod`
- **Effort:** Simple

### LEG-UI2-002: SpriteManager Atlas Fallback - Dead Code
- **Severity:** Major
- **Location:** `game/ui/renderer/sprites.py:40`
- **Effort:** Simple

### LEG-UI2-003: draw_hud() and draw_bar() in game_render
- **Severity:** Major
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### LEG-UI2-004: BattleOrchestrator Never Used in Product
- **Severity:** Major
- **Location:** `game/ui/orchestration/battle_o`
- **Effort:** Medium

### LEG-UI2-005: show_overlay Hack - State Passed via Dyn
- **Severity:** Major
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### LEG-UI2-006: draw_ship() Uses Singleton ShipThemeMana
- **Severity:** Major
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Medium

### LEG-UI1-002: Backward Compatibility Aliases in Race G
- **Severity:** Major
- **Location:** `game/ui/panels/race_flag_galle`
- **Effort:** Simple

### LEG-UI1-003: Deprecated Methods on BattleScreen (hand
- **Severity:** Major
- **Location:** `game/ui/screens/battle_screen.`
- **Effort:** Simple

### LEG-UI1-004: Legacy Tuple Format Support in detail_pa
- **Severity:** Major
- **Location:** `game/ui/screens/builder/detail`
- **Effort:** Medium

### LEG-UI1-005: Backwards Compatibility Fallbacks in wor
- **Severity:** Major
- **Location:** `game/ui/screens/workshop_event`
- **Effort:** Simple

### LEG-UI1-006: Legacy Shim Skip List in detail_panel.py
- **Severity:** Major
- **Location:** `game/ui/screens/builder/detail`
- **Effort:** Simple

### LEG-FND-006: `LayerType.from_string()` Static Method
- **Severity:** Minor
- **Location:** `game/core/constants.py:117-119`
- **Effort:** Simple

### LEG-FND-007: `ScreenshotManager.capture_step()` Never
- **Severity:** Minor
- **Location:** `game/core/screenshot_manager.p`
- **Effort:** Simple

### LEG-FND-008: Python 3.9 Compatibility Shim for TypeGu
- **Severity:** Minor
- **Location:** `game/core/protocols.py:32-36`
- **Effort:** Simple

### LEG-FND-009: Color Constants (WHITE, BLACK, BLUE, RED
- **Severity:** Minor
- **Location:** `game/core/constants.py:42-46`
- **Effort:** Simple

### LEG-FND-010: `json` Import in resources.py Only Neede
- **Severity:** Minor
- **Location:** `game/core/resources.py:13`
- **Effort:** Simple

### LEG-FND-011: `_get_hp_percent` and `_is_in_pdc_arc` W
- **Severity:** Minor
- **Location:** `game/ai/controller.py:269-273`
- **Effort:** Simple

### LEG-FND-012: `FONT_MAIN` Constant Defined but Unused
- **Severity:** Minor
- **Location:** `game/core/constants.py:49`
- **Effort:** Simple

### LEG-SIM-006: FORMULA_* string constants are documenta
- **Severity:** Minor
- **Location:** `game/simulation/physics_consta`
- **Effort:** Simple

### LEG-SIM-011: shots_hit attribute dynamically added in
- **Severity:** Minor
- **Location:** `game/simulation/projectile_man`
- **Effort:** Simple

### LEG-SIM-012: combat_endurance.py legacy fallback for
- **Severity:** Minor
- **Location:** `game/simulation/entities/comba`
- **Effort:** Simple

### LEG-SIM-015: CargoStorage uses string layer instead o
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### LEG-SIM-016: ability_manager.py has [KNOWN_ISSUE] wor
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Complex

### LEG-SIM-017: Ship.base_mass is always 0.0 - vestigial
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Simple

### LEG-SIM-018: Duplicate shield_regen_cost initializati
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### LEG-UI2-007: Unnecessary hasattr Guard on LayerType.v
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Simple

### LEG-UI2-008: getattr(ship, 'id', id(ship)) - Ship.id
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Simple

### LEG-UI2-009: Excessive getattr Usage in _convert_proj
- **Severity:** Minor
- **Location:** `game/ui/services/battle_ui_ser`
- **Effort:** Medium

### LEG-UI2-010: interfaces/__init__.py Re-exports Never
- **Severity:** Minor
- **Location:** `game/ui/interfaces/__init__.py`
- **Effort:** Simple

### LEG-UI1-007: Duplicate show_overlay Toggle Keybinding
- **Severity:** Minor
- **Location:** `game/ui/screens/battle_screen.`
- **Effort:** Simple

### LEG-UI1-008: Stale Comment about Removed Duplicate Me
- **Severity:** Minor
- **Location:** `game/ui/screens/battle_screen.`
- **Effort:** Simple

### LEG-UI1-009: Hardcoded 1920x1080 Fallback Resolution
- **Severity:** Minor
- **Location:** `game/ui/screens/new_game_setup`
- **Effort:** Simple

### LEG-UI1-010: Duplicate Assignment on Consecutive Line
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/left_p`
- **Effort:** Simple

### LEG-UI1-011: Unnecessary hasattr Guard for _facade
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_windo`
- **Effort:** Simple

### LEG-UI1-012: Dead hasattr Check for print_headless_su
- **Severity:** Minor
- **Location:** `game/ui/screens/battle_screen.`
- **Effort:** Simple

### LEG-UI1-013: Monkey-Patching Domain Objects with Temp
- **Severity:** Minor
- **Location:** `game/ui/screens/strategy_rende`
- **Effort:** Medium

### LEG-UI1-014: Unused Module-Level Constants
- **Severity:** Minor
- **Location:** `game/ui/screens/builder/stats_`
- **Effort:** Simple

### LEG-FND-013: `DEBUG_SCREENSHOTS = True` Always Enable
- **Severity:** Info
- **Location:** `game/core/constants.py:53`
- **Effort:** Simple

### LEG-FND-014: `profiling.py` Comment References "backw
- **Severity:** Info
- **Location:** `game/core/profiling.py:104`
- **Effort:** Simple

### LEG-SIM-021: ShipStatsCalculator._check_mass_limits h
- **Severity:** Info
- **Location:** `game/simulation/entities/ship_`
- **Effort:** Simple

### LEG-SIM-022: TechPresetLoader has no production calle
- **Severity:** Info
- **Location:** `game/simulation/systems/tech_p`
- **Effort:** Medium

### LEG-SIM-023: EmpireStorageAbility uses non-standard s
- **Severity:** Info
- **Location:** `game/simulation/components/abi`
- **Effort:** Simple

### LEG-UI2-011: SpriteManager and ShipThemeManager Use S
- **Severity:** Info
- **Location:** `game/ui/renderer/sprites.py:7`
- **Effort:** Complex

### LEG-UI2-012: game/ui/__init__.py Purpose is xdist Rac
- **Severity:** Info
- **Location:** `game/ui/__init__.py:1-27`
- **Effort:** Simple

### LEG-UI1-015: Deprecated Properties on StrategyScreen
- **Severity:** Info
- **Location:** `game/ui/screens/strategy_scree`
- **Effort:** Simple

### LEG-UI1-016: test_lab/screen.py Accepts Game Object "
- **Severity:** Info
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Medium


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
