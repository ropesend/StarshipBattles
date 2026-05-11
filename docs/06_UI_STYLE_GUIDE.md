# UI Style Guide Compact Reference

> **Last verified:** 2026-05-11 — issue #18: Strategy Modal Windows section gained one bullet on Esc-closes-topmost (the strategy event router walks `iter_live_modals()` and kills the last-appended modal when no menu panel is open). Previous (2026-05-10): issue #12 full modality.

Audience: LLM agents working on Starship Battles UI. This is the compact current-system reference for color constants, pygame_gui theme usage, strategy modal windows, read-only component-status rendering, and UI style extension points.

## Visual Identity

Starship Battles uses a dark blue-gray military sci-fi palette with restrained cyan accents. Use darker colors for recessed surfaces, lighter colors for elevated controls, muted borders by default, and bright cyan/blue only for hover, selection, active focus, or key highlights.

Do not inline RGB tuples in UI code. Add or reuse named constants from the correct source module.

## Primary Sources

| Need | Use | Path |
|---|---|---|
| General pygame drawing | `COLORS` dict or named RGB constants | `game/ui/colors.py` |
| Domain-specific UI colors | Module-level RGB constants | `game/ui/colors.py` |
| Shared HP color thresholds | `get_damage_color()` | `game/ui/utils/formatters.py` |
| HTML/`UITextBox` text colors | Hex-string constants | `game/ui/colors.py` |
| Ability detail row hints | `HINT_*` constants | `game/simulation/components/abilities/ui_colors.py` |
| pygame_gui widget theme | Defaults, object IDs, class IDs | `data/builder_theme.json` |
| Test Lab theme | Test Lab constants | `game/ui/screens/test_lab/theme.py` |

Common imports:

```python
from game.ui.colors import COLORS
from game.ui.colors import HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, HP_DESTROYED
from game.ui.colors import DETAIL_COMPONENT_NAME, DESIGN_MISSING_REQ
from game.ui.utils.formatters import get_damage_color
from game.simulation.components.abilities.ui_colors import HINT_DAMAGE, HINT_SHIELD_CAP
from game.ui.screens.test_lab.theme import BG_PRIMARY, STATUS_PASS
```

## Strategy Modal Windows

New strategy-screen modal windows must subclass `StrategyModalWindow`, not `pygame_gui.elements.UIWindow` directly.

Paths:

- Base class: `game/ui/screens/strategy_modal_window.py`
- Manager: `game/ui/screens/strategy_window_manager.py`
- Router: `game/ui/screens/strategy_event_router.py`
- Tests: `tests/unit/ui/screens/test_strategy_modal_window.py`, `tests/unit/ui/screens/test_strategy_event_router.py`

Required strategy-only shape:

```python
from game.ui.screens.strategy_modal_window import StrategyModalWindow


class MyNewWindow(StrategyModalWindow):
    def __init__(
        self,
        rect,
        manager,
        *,
        window_manager: "StrategyWindowManager",
    ) -> None:
        super().__init__(
            rect,
            manager,
            window_display_title="My Window",
            resizable=False,
            window_manager=window_manager,
        )
```

Contracts:

- `StrategyModalWindow.__init__` auto-registers with `window_manager.register_modal(self)` when `window_manager is not None`.
- `kill()` auto-deregisters before calling `UIWindow.kill()` and is idempotent.
- `StrategyWindowManager.iter_live_modals()` yields live windows and reaps dead refs from parent-kill cascades.
- Strategy event routing uses `iter_live_modals()` for modal detection and click blocking. Do not add new manual modal slot scans, `has_modal_open()` branches, or `_is_blocking_ui_element_at()` clauses for new modal windows.
- Strategy-only modal constructors must require `window_manager` as an explicit keyword and must not default it to `None`.
- Cross-screen reusable windows may type `window_manager: "StrategyWindowManager | None"`, but callers still pass it explicitly. Use `None` only from non-strategy callers.
- The manager still exposes legacy slot attributes for registrar convenience and public API stability. New modal tracking goes through the live modal list.
- Full modality (issue #12): while any subclass instance is live, the strategy event router blocks ALL background clicks (hex grid AND top-bar buttons) regardless of click position relative to the window's rect. There is no per-window opt-out.
- Esc-closes-topmost (issue #18): when no menu panel is open, the strategy event router walks `list(window_manager.iter_live_modals())[-1].kill()` on K_ESCAPE. New `StrategyModalWindow` subclasses pick this up automatically; do not add per-window Esc handlers. The kill() chain fires the window's existing `on_close_callback` before `super().kill()`, matching the X-button close path. Per-window Esc bindings on `BuildQueueListWindow` and `TransferDialog` are retained for tooltip contract and remain safe (double-kill is idempotent).

Test-only bypass invariant:

- Tests use `tests.fixtures.ui_widget_factory.bypass_init`.
- Under bypass, `StrategyModalWindow` sets `_window_manager`, `ui_manager`, and `_window_init_bypassed = True`.
- Bypassed windows intentionally do not auto-register. Fixtures that need a live-list entry register manually.
- Production must never set `bypass_init`.

## `COLORS` Dict

Path: `game/ui/colors.py`

Use `from game.ui.colors import COLORS` and index by string key.

Background keys:

- `bg_deep` `(18, 21, 26)` - deepest recessed areas
- `bg_dark` `(20, 24, 31)` - panel interiors, text-entry backgrounds
- `bg_base` `(26, 30, 38)` - standard panel backgrounds
- `bg_elevated` `(30, 37, 48)` - buttons and normal list items
- `bg_hover` `(40, 48, 64)` - hovered elements
- `bg_selected` `(42, 56, 85)` - selected and active states

Border keys:

- `border_subtle` `(42, 48, 64)` - disabled/subtle borders
- `border_normal` `(42, 53, 69)` - default panel borders
- `border_active` `(58, 72, 96)` - prominent controls
- `border_hover` `(85, 170, 238)` - cyan hover glow
- `border_selected` `(68, 153, 221)` - selected borders

Text keys:

- `text_disabled` `(85, 96, 112)`
- `text_muted` `(102, 119, 153)`
- `text_subtle` `(136, 153, 187)`
- `text_normal` `(154, 171, 204)`
- `text_bright` `(170, 187, 221)`
- `text_highlight` `(170, 204, 255)`
- `text_hover` `(200, 218, 255)`
- `text_selected` `(255, 255, 255)`
- `text_error` `(255, 100, 100)`

Accent keys:

- `accent_primary` `(68, 136, 221)` - filled bars and primary actions
- `accent_glow` `(85, 170, 238)` - glow effects
- `accent_bright` `(102, 187, 255)` - bright highlights

Standalone constants: `WHITE = (255, 255, 255)`, `BLACK = (0, 0, 0)`.

## RGB Constant Families

All constants below live in `game/ui/colors.py` unless noted.

Health and damage:

- `HP_HEALTHY`, `HP_DAMAGED`, `HP_CRITICAL`, `HP_DESTROYED`
- `MUTED_GREY` for manually disabled but not broken components
- `DAMAGE_GRADIENT`: six green-to-red tuples
- Canonical shared thresholds live in `game/ui/utils/formatters.py::get_damage_color`: `>= 0.50` healthy, `0.25..0.49` damaged, `0.01..0.24` critical, `<= 0` or inactive destroyed. Do not rely on older 20% comments as the shared threshold contract.

Ship, projectile, and battle rendering:

- Layers: `LAYER_ARMOR`, `LAYER_OUTER`, `LAYER_INNER`, `LAYER_CORE`, `LAYER_LABEL`
- Projectiles: `PROJECTILE_STANDARD`, `PROJECTILE_MISSILE`, `PROJECTILE_BEAM`, `PROJECTILE_GLOW`
- Battle status: `STATUS_ACTIVE_TEXT`, `STATUS_ACTIVE_BG`, `STATUS_HIT_TEXT`, `STATUS_DESTROYED_TEXT`, `STATUS_DERELICT`, `SEEKER_TITLE`, `DAMAGE_TEXT`, `TARGET_TEXT`
- HUD: `SPEED_PAUSED`, `SPEED_SLOWMO`, `SPEED_FAST`, `HUD_TEXT`, `HUD_ZOOM_TEXT`
- Debug/grid: `GRID_BG_BATTLE`, `DEBUG_TARGET_LINE`, `DEBUG_WEAPON_RANGE`, `DEBUG_AIM_POINT`, `DEBUG_FIRING_ARC`, `DEBUG_COLLISION`, `DEBUG_DIRECTION`
- Component overlays/status: `OVERLAY_COMPONENT`, `OVERLAY_WEAPON`, `OVERLAY_PROPULSION`, `OVERLAY_ARMOR`, `OVERLAY_FALLBACK`, `COMPONENT_NO_POWER`, `COMPONENT_NO_FUEL`, `COMPONENT_INACTIVE_BG`

Resource and domain colors:

- Resources: `RESOURCE_FUEL`, `RESOURCE_ENERGY`, `RESOURCE_AMMO`, `RESOURCE_SHIELD`, `RESOURCE_BIOMASS`, `RESOURCE_METALS`, `RESOURCE_ORGANICS`, `RESOURCE_VAPORS`, `RESOURCE_RADIOACTIVES`, `RESOURCE_EXOTICS`
- Research: `RESEARCH_LOCKED`, `RESEARCH_AVAILABLE`, `RESEARCH_COMPLETED`, `RESEARCH_SELECTED`, `RESEARCH_LINE_UNMET`, `RESEARCH_LINE_MET`, `RESEARCH_LINE_NEGATED`, `RESEARCH_LINE_NEGATED_MET`, `RESEARCH_TEXT`, `RESEARCH_CHANCE`, `RESEARCH_ALLOCATION`
- Teams: `TEAM_1_*`, `TEAM_2_*`
- Ship classes: `SHIP_CLASS_FIGHTER`, `SHIP_CLASS_CORVETTE`, `SHIP_CLASS_ESCORT`, `SHIP_CLASS_DESTROYER`, `SHIP_CLASS_CRUISER`, `SHIP_CLASS_BATTLESHIP`, `SHIP_CLASS_CARRIER`, `SHIP_CLASS_DEFAULT`
- Vehicle types: `VEHICLE_DEFAULT`, `VEHICLE_SHIP`, `VEHICLE_FIGHTER`, `VEHICLE_STATION`, `VEHICLE_COMPLEX`

Common UI and screens:

- Text: `TEXT_LIGHT`, `TEXT_MUTED`, `TEXT_DIM`, `TEXT_ERROR`, `TEXT_SECONDARY`, `TEXT_ITEM`
- Panels/borders/bars: `PANEL_BG`, `BORDER_LIGHT`, `BORDER_DARK`, `BORDER_PANEL`, `BAR_BG`, `BAR_BORDER`
- Backgrounds/grids: `BG_PANEL_DARK`, `BG_ROW_ALT`, `BG_ITEM`, `GRID_LINE`, `GRID_BG`
- Scene backgrounds: `BG_BATTLE`, `BG_GALAXY`, `BG_MENU`
- Tables: `TABLE_SELECTED`, `TABLE_UNSELECTED`
- Buttons: `BTN_NEUTRAL_*`, `BTN_DANGER_*`, `BTN_PRIMARY_*`, `BTN_RETURN_*`, `BTN_END_*`, `BTN_VICTORY_*`, `BTN_CLEAR_*`, `BTN_QUICK_*`, `BTN_DISABLED_BG`

Map and world rendering:

- Planet types: `PLANET_CONTINENTAL`, `PLANET_ARID`, `PLANET_PELAGIC`, `PLANET_MAGMA`, `PLANET_CRYO`, `PLANET_BARREN`, `PLANET_JOVIAN`, `PLANET_ICE_GIANT`, `PLANET_CHTHONIAN`, `PLANET_ICE_DWARF`, `PLANET_PLANETOID`, `PLANET_TERRESTRIAL`, `PLANET_GAS_GIANT`, `PLANET_ICE`, `PLANET_ROCKY`, `PLANET_OCEANIC`
- Star spectrum: `SPECTRUM_GAMMA`, `SPECTRUM_XRAY`, `SPECTRUM_UV`, `SPECTRUM_BLUE`, `SPECTRUM_GREEN`, `SPECTRUM_RED`, `SPECTRUM_INFRARED`, `SPECTRUM_MICROWAVE`, `SPECTRUM_RADIO`
- Atmospheric gases: `GAS_N2`, `GAS_O2`, `GAS_CO2`, `GAS_H2O`, `GAS_CH4`, `GAS_H2`, `GAS_HE`, `GAS_AR`, `GAS_SO2`, `GAS_UNKNOWN`
- Storms: `STORM_ION`, `STORM_PLASMA`, `STORM_GRAVITATIONAL`, `STORM_RADIATION`, `STORM_DARK_NEBULA`
- Strategy map: `WARP_LANE`, `STAR_LABEL`, `FLEET_SELECTED`, `PATH_MOVE`, `PATH_WARP`, `PATH_LABEL`, `OVERLAY_PROCESSING`, `WARPPOINT_FALLBACK`, `DYSON_FALLBACK`, `PLANET_FALLBACK`, `ZONE_HIGHLIGHT`, `STAR_FALLBACK`, `STORM_FALLBACK`, `HEX_OUTLINE_OCCUPIED`, `HEX_OUTLINE_PLAYER_OWNED`

Specialized families:

- Battle setup: `SETUP_*`, `ITEM_*`, `DROPDOWN_*`
- Formation editor: `FORMATION_GRID`, `FORMATION_AXIS`, `FORMATION_ARROW`, `FORMATION_ARROW_SELECTED`, `FORMATION_FIXED`, `FORMATION_FIXED_SELECTED`
- Weapon renderer: `WEAPON_BAR_BEAM`, `WEAPON_BAR_PROJECTILE`, `WEAPON_BAR_SEEKER`, `WEAPON_ACCURACY_HIGH`, `WEAPON_ACCURACY_MED`, `WEAPON_ACCURACY_LOW`, `WEAPON_LABEL`, `WEAPON_RANGE_LABEL`, `WEAPON_ARC`
- Modifier impact grid: `MODIFIER_HEADER_BG`, `MODIFIER_ROW_BG`, `MODIFIER_ROW_ALT_BG`, `MODIFIER_FOOTER_BG`, `MODIFIER_BUFF`, `MODIFIER_DEBUFF`, `MODIFIER_NEUTRAL`
- JSON/scrollbars: `JSON_*`, `SCROLLBAR_TRACK`, `SCROLLBAR_THUMB`, `SCROLLBAR_THUMB_ACTIVE`
- Diff viewer: `DIFF_*`, `VIEWER_BTN_*`
- Design thumbnails: `THUMB_SHIP`, `THUMB_FIGHTER`, `THUMB_SATELLITE`, `THUMB_COMPLEX`, `THUMB_TEXT`
- Misc: `TEST_PASS`, `TEST_FAIL`, `TEST_COMPLETE_NEUTRAL`, `TEST_COMPLETE_PASSED`, `TEST_COMPLETE_FAILED`, `PLACEHOLDER_DEFAULT`, `PLACEHOLDER_BORDER`, `RESULT_WIN`, `RESULT_DRAW`, `DRAG_HIGHLIGHT`, `SWATCH_BORDER`, `PROFILING_TEXT`

## Hex-String Constants

Use hex strings where pygame_gui rich text or HTML text boxes require `'#RRGGBB'`.

Path: `game/ui/colors.py`

Builder/detail:

- `DETAIL_COMPONENT_NAME = "#FFFF64"`
- `DETAIL_COMPONENT_INFO = "#C8C8C8"`
- `DETAIL_TEXT = "#E0E0E0"`
- `BUILDER_ITEM_BG = "#14181f"`
- `BUILDER_GROUP_BG = "#1a1e26"`
- `BUILDER_TREE_LINE = "#2a3545"`

Design stats:

- `DESIGN_MISSING_REQ = "#ffaa55"`
- `DESIGN_REQS_MET = "#88ff88"`
- `DESIGN_WARNING = "#ffff88"`
- `DESIGN_NO_RECS = "#888888"`

Ability UI hints live in `game/simulation/components/abilities/ui_colors.py` and are exported via `__all__`.

- Weapons/offense: `HINT_DAMAGE`, `HINT_RANGE`, `HINT_RELOAD`, `HINT_PROJECTILE_SPEED`, `HINT_ACCURACY`
- Defense/shields: `HINT_SHIELD_CAP`, `HINT_SHIELD_REGEN`, `HINT_EVASION`
- Propulsion: `HINT_THRUST`, `HINT_TURN_SPEED`, `HINT_STRATEGIC_MOBILITY`, `HINT_WARP_ENERGY`
- Crew/support: `HINT_CREW_CAP`, `HINT_LIFE_SUPPORT`, `HINT_CREW_REQ`
- Cargo/resources: `HINT_CARGO_PASSENGER`, `HINT_CARGO_GENERIC`, `HINT_COLONIZE`
- Special/neutral: `HINT_SUPERWEAPON`, `HINT_REQUIREMENT`, `HINT_NEUTRAL`, `HINT_DEFAULT`

## pygame_gui Theme

Path: `data/builder_theme.json`

The theme configures pygame_gui widgets for the Ship Design Workshop and other pygame_gui screens. It uses hex strings and the pygame_gui key spelling `"colours"`.

Defaults:

- Font block: `"name": "arial"`, `"size": "14"`, with `regular_resource` pointing to `pygame_gui.data/FiraCode-Regular.ttf`.
- Colors include `normal_bg #1a1e24`, `hovered_bg #252a32`, `disabled_bg #15181d`, `selected_bg #2a3545`, `active_bg #1f2530`, `dark_bg #12151a`, `normal_text #c8d4e8`, `hovered_text #e0eaff`, `normal_border #3a4555`, `hovered_border #5588cc`, `filled_bar #4488dd`, and `unfilled_bar #252a35`.

Widget styling:

- `button`: rounded rectangle, radius `3`, border `2`, shadow `2`, tooltip delay `0.5`
- `panel`: rounded rectangle, radius `3`, border `1`
- `panel.@fast_panel`: rectangle, border `1`; used for Build Queue factory panels to avoid global rounded-panel rasterization cost
- `selection_list`: rectangle, item height `22`
- `selection_list.@selection_list_item`: borderless item states
- `drop_down_menu`, `horizontal_slider`, `text_entry_line`: rounded rectangle, radius `3`
- `horizontal_slider.#sliding_button`: thumb colors `#3366aa` normal, `#4488cc` hover, `#55aaee` selected
- `label`: centered text, transparent background
- `window`: rounded rectangle, radius `5`, border `2`
- `window.#title_bar`: background `#1e2838`
- `button.@tri_state_radio`: compact tri-state filter button class

Useful object IDs and class IDs:

- `#stat_label`, `#stat_value`, `#stat_unit`
- `#left_aligned_label`, `#header_label`
- `#modifier_panel_container`, `#component_list_panel`
- `#mini_arrow_btn`, `#tree_item_label`
- `@fast_panel` for scoped fast panels
- `@tri_state_radio` for tri-state filter buttons

Warnings:

- The file mixes JSON strings and numbers because pygame_gui expects some `misc` values as strings. Follow nearby theme entries instead of normalizing types mechanically.
- Screens that need this theme should resolve it through `Paths.DATA_DIR` or an existing helper path, not a hardcoded checkout path.

## Test Lab Theme

Path: `game/ui/screens/test_lab/theme.py`

Import Test Lab-specific colors from this module. It aliases `TEST_PASS` and `TEST_FAIL` from `game.ui.colors` as `STATUS_PASS` and `STATUS_FAIL`.

Important categories:

- Backgrounds: `BG_PRIMARY`, `BG_PANEL`, `BG_CONTENT`, `BG_CATEGORY`, `BG_ITEM_HOVER`, `BG_OVERLAY`
- Borders: `BORDER`, `BORDER_ACTIVE`
- Text: `TEXT`, `TEXT_HEADER`, `TEXT_SECONDARY`, `TEXT_EXPECTED`, `TEXT_WHITE`, `TEXT_MUTED`, `TEXT_DIM`, `TEXT_LABEL`, `TEXT_VERY_DIM`, `TEXT_DIM_BLUE`
- Status: `STATUS_PASS`, `STATUS_FAIL`, `STATUS_WARNING`, `STATUS_INFO`, `STATUS_HIGHLIGHT`
- Tags/filters: `TAG_ACTIVE_*`, `TAG_EXCLUDED_*`, `TAG_NORMAL_*`
- Tabs: `TAB_NORMAL`, `TAB_SELECTED`, `TAB_HOVER`
- Selection: `SELECTED_BG`, `SELECTED_CARD_BG`, `SELECTED_BORDER`
- Buttons: `BUTTON_BLUE_*`, `BUTTON_GREEN_*`, `BUTTON_PROGRESS_*`, `BUTTON_HEADLESS_*`, `BUTTON_BASELINE_*`, `BUTTON_RUN_*`
- Seed controls: `SEED_RANDOM`, `SEED_FIXED`, `SEED_CUSTOM`, `SEED_CUSTOM_PENDING`, `SEED_BUTTON_*`, `SEED_INPUT_*`
- JSON viewer: `JSON_TITLE_BG`, `JSON_SCROLLBAR_*`
- Validation phases: `PHASE_DATA`, `PHASE_PRECONDITION`, `PHASE_OUTCOME`
- Section headers: `SECTION_CATEGORY`, `SECTION_SUMMARY`, `SECTION_CONDITIONS`, `SECTION_EDGE_CASES`, `SECTION_OUTCOME`, `SECTION_CRITERIA`

## Read-only Component Grouping

Use this pattern for panels that display per-component damage state without mutation, such as Fleet Report `ShipDetailPanel` or future after-action reports.

Current paths:

- Implementation: `game/ui/panels/ship_detail_panel.py`
- Consuming window: `game/ui/screens/fleet_report_window.py`
- Component DTO: `game/core/component_state.py::ComponentInstanceView`
- Tests: `tests/unit/ui/panels/test_ship_detail_panel.py`

Section rules:

- Always render a `COMPONENT STATUS` section.
- Read data through `ship.iter_all_components_by_layer()`.
- Group by `LAYER_ORDER = ("CORE", "INNER", "OUTER", "ARMOR")`.
- Exclude `HULL`.
- Each layer is collapsible.
- Identical `component_id` values collapse into one group row.
- Group rows show display name, count, functional/total, and average damage percent.
- Expanding a group shows one instance row per component.

State and grouping invariants:

- `group_components_by_id(instances, damage_threshold_lookup)` is pure and lives at module scope with `ComponentGroup` and `InstanceDamage`.
- The helper preserves first-seen component ID order.
- `damage_pct = 0.0` when `max_hp <= 0`, guarding legacy or synthetic data.
- `functional` counts active instances.
- `is_damage_induced_inactive` is true when `not is_active` and `current_hp < max_hp * threshold`.
- The threshold lookup is dependency-injected for tests.
- Production threshold lookup uses `get_default_registry_provider().get_components()` and falls back to `CombatConstants.DEFAULT_DAMAGE_THRESHOLD` when the registry or component entry is unavailable.

Auto-expand semantics:

- Layer expand state recomputes on every `update_ship`.
- Layers auto-expand only when they contain at least one destroyed instance (`current_hp == 0` and `max_hp > 0`).
- Groups start collapsed.
- No per-ship/layer expansion state persists across ship reselection.

Color and strike rules:

| State | Color | Strikethrough |
|---|---|---|
| Destroyed: `damage_pct >= 1.0` | `HP_DESTROYED` | Yes |
| Damage-induced inactive: below threshold and inactive | `HP_CRITICAL` | Yes |
| Manually disabled: inactive but not damage-induced | `MUTED_GREY` | No |
| Active: any HP above zero | `get_damage_color(hp_pct)` | No |

Important correction: the component damage threshold is not the active-row color threshold. It only decides whether an inactive component is damage-induced. Active instance rows use `get_damage_color(hp_pct)` from `game/ui/utils/formatters.py`.

Strikethrough convention:

- pygame_gui has no native `<s>` support in this pattern.
- Use a manual `pygame.draw.line()` overlay rendered as a `UIImage` pinned to the label rect.
- Track overlays in `ui_elements` so `_clear_elements()` cleans them.
- If pygame_gui adds native strikethrough support, prefer that and remove the helper.

Read-only contract:

- Layer headers and group headers are `UIButton`s because they are toggles.
- Group rows and instance rows are display-only; instance rows are `UILabel`s.
- The only buttons inside the section are layer and group chevrons.
- Mutation actions belong in a separate row group below the read-only block.
- Regression tests assert button count equals `len(layer_buttons) + len(group_buttons)`.

Extension recipe:

- For a new read-only component view, import and reuse `LAYER_ORDER`, `group_components_by_id`, `ComponentGroup`, and `InstanceDamage`.
- Use the same color/strike table.
- Do not invent a parallel damage display rule set.
- Keep pure grouping logic above the panel class unless it grows into a real shared module.

## Adding Colors Or Theme Entries

Choose the correct location:

| Color type | Location |
|---|---|
| General backgrounds, borders, text | `COLORS` dict in `game/ui/colors.py` |
| Domain-specific RGB colors | Module-level constants in `game/ui/colors.py` |
| HTML/`UITextBox` text colors | Hex string constants in `game/ui/colors.py` |
| Ability UI hints | `game/simulation/components/abilities/ui_colors.py` and `__all__` |
| Test Lab only | `game/ui/screens/test_lab/theme.py` |
| pygame_gui widget styling | `data/builder_theme.json` |

Naming:

- `COLORS` keys: `category_descriptor`, for example `bg_deep`, `text_muted`, `border_hover`
- RGB tuple constants: `DOMAIN_DESCRIPTOR`, for example `PLANET_MAGMA`, `TEAM_1_TEXT`, `HP_CRITICAL`
- Hex constants: `CONTEXT_PURPOSE`, for example `DETAIL_COMPONENT_NAME`, `DESIGN_REQS_MET`
- Ability hints: `HINT_SEMANTIC_NAME`, for example `HINT_DAMAGE`, `HINT_SHIELD_CAP`
- Test Lab constants: `CATEGORY_DESCRIPTOR`, for example `TAG_ACTIVE_BG`, `PHASE_DATA`
- pygame_gui object IDs: `#specific_object`
- pygame_gui class IDs: `@shared_class`, producing selectors such as `panel.@fast_panel`

Design rules:

- Use named constants; never inline UI RGB tuples.
- Keep normal borders thin and muted, usually `1-2px`.
- Use `3-5px` corner radius for rounded pygame_gui controls unless the existing selector says otherwise.
- Use rectangular scoped class IDs when performance matters, as with `panel.@fast_panel`.
- Reserve cyan/blue glow for hover, selection, active focus, and important highlights.
- Group new constants under the matching category comment block.
- Update or add tests when a new color family carries behavior, not just presentation.

## Verification Commands

Focused checks for changes in this area:

```bash
pytest tests/unit/ui/test_colors.py
pytest tests/unit/ui/utils/test_formatters.py
pytest tests/unit/ui/panels/test_ship_detail_panel.py
pytest tests/unit/ui/screens/test_strategy_modal_window.py
pytest tests/unit/ui/screens/test_strategy_event_router.py
pytest tests/unit/ui/screens/test_build_queue_panel_factory.py
pytest tests/unit/ui/components/filters/test_tri_state_widget.py
pytest tests/integration/ui/test_editor_click_blocking.py
pytest tests/integration/ui/test_race_setup_ships_smoke.py
```

Full suite:

```bash
python Tools/test_sharded/test_sharded.py
```

## Quick Decision Table

| Situation | Use |
|---|---|
| Direct pygame rect/line/text drawing | `COLORS` or named constants from `game.ui.colors` |
| Shared HP/damage display | `get_damage_color()` from `game.ui.utils.formatters` |
| pygame_gui widgets | `data/builder_theme.json` selectors |
| `UITextBox` inline HTML | Hex-string constants |
| Ability detail rows | `HINT_*` constants |
| Test Lab UI | `game.ui.screens.test_lab.theme` |
| Strategy modal window | `StrategyModalWindow` with explicit `window_manager` |
| Read-only component damage panel | `game.ui.panels.ship_detail_panel` grouping pattern |

## Concrete RGB Values (Frequently Guessed)

Names alone are insufficient when an LLM extends the palette without grepping the source. The values below are load-bearing - inline guessing produces visibly off-palette output. Source of truth remains `game/ui/colors.py`; the table here is a guard-rail.

Health and damage:

- `HP_HEALTHY = (0, 255, 0)` - above ~50% HP
- `HP_DAMAGED = (255, 200, 0)` - middle band
- `HP_CRITICAL = (255, 50, 50)` - low band
- `HP_DESTROYED = (100, 100, 100)` - 0% HP
- `MUTED_GREY = (130, 130, 150)` - manually disabled, not broken
- `DAMAGE_GRADIENT = [(50,255,50), (100,220,50), (150,180,50), (200,140,50), (230,100,50), (255,60,50)]`

Ship layers (schematic and overlay):

- `LAYER_ARMOR (100,100,100)`, `LAYER_OUTER (200,50,50)`, `LAYER_INNER (50,50,200)`, `LAYER_CORE (220,220,220)`, `LAYER_LABEL (80,80,80)`

Projectiles:

- `PROJECTILE_STANDARD (255,200,50)`, `PROJECTILE_MISSILE (255,50,50)`, `PROJECTILE_BEAM (100,200,255)`, `PROJECTILE_GLOW (255,255,100)`

Resources (visible in HUD bars and panels):

- `RESOURCE_FUEL (255,165,0)`, `RESOURCE_ENERGY (100,200,255)`, `RESOURCE_AMMO (200,200,100)`, `RESOURCE_SHIELD (0,200,255)`, `RESOURCE_BIOMASS (100,255,100)`, `RESOURCE_METALS (192,192,192)`, `RESOURCE_ORGANICS (80,180,80)`, `RESOURCE_VAPORS (100,150,220)`, `RESOURCE_RADIOACTIVES (220,180,50)`, `RESOURCE_EXOTICS (180,80,200)`

Teams (battle/setup):

- Team 1: `TEAM_1_TEXT (100,200,255)`, `TEAM_1_BG (30,50,70)`, `TEAM_1_BANNER_BG (40,60,80)`, `TEAM_1_BORDER (100,150,200)`
- Team 2: `TEAM_2_TEXT (255,100,100)`, `TEAM_2_BG (70,30,30)`, `TEAM_2_BANNER_BG (80,40,40)`, `TEAM_2_BORDER (200,100,100)`

Ship classes (design report swatches):

- `SHIP_CLASS_FIGHTER (255,150,50)`, `SHIP_CLASS_CORVETTE (100,200,100)`, `SHIP_CLASS_ESCORT (100,150,255)`, `SHIP_CLASS_DESTROYER (255,100,100)`, `SHIP_CLASS_CRUISER (200,100,255)`, `SHIP_CLASS_BATTLESHIP (255,200,50)`, `SHIP_CLASS_CARRIER (150,255,200)`, `SHIP_CLASS_DEFAULT (150,150,150)`

Scene backgrounds:

- `BG_BATTLE (10,10,20)`, `BG_GALAXY (15,20,30)`, `BG_MENU (20,20,30)`

Common UI text (frequently misused):

- `TEXT_LIGHT (220,220,220)`, `TEXT_MUTED (150,150,150)`, `TEXT_DIM (100,100,100)`, `TEXT_ERROR (255,100,100)`, `TEXT_SECONDARY (180,180,180)`, `TEXT_ITEM (200,200,200)`

HUD speed indicators:

- `SPEED_PAUSED (255,100,100)`, `SPEED_SLOWMO (255,200,100)`, `SPEED_FAST (100,255,100)`

Strategy map outlines:

- `HEX_OUTLINE_OCCUPIED (200,60,60)` - red occupied tiles
- `HEX_OUTLINE_PLAYER_OWNED (220,220,220)` - white player-owned tiles
- `FLEET_SELECTED (255,255,0)`, `PATH_MOVE (0,255,100)`, `PATH_WARP (255,50,50)`

Planet types (map dots, fallbacks):

- `PLANET_CONTINENTAL (70,130,70)`, `PLANET_ARID (180,140,80)`, `PLANET_PELAGIC (50,80,180)`, `PLANET_MAGMA (200,50,30)`, `PLANET_CRYO (180,200,220)`, `PLANET_BARREN (130,130,130)`, `PLANET_JOVIAN (200,160,100)`, `PLANET_ICE_GIANT (100,150,200)`, `PLANET_TERRESTRIAL (100,150,200)`, `PLANET_GAS_GIANT (200,150,100)`, `PLANET_OCEANIC (50,100,200)`

Star spectrum (visible-band logical colors, not literal physics colors):

- `SPECTRUM_GAMMA (200,0,255)`, `SPECTRUM_XRAY (148,0,211)`, `SPECTRUM_UV (75,0,130)`, `SPECTRUM_BLUE (0,0,255)`, `SPECTRUM_GREEN (0,255,0)`, `SPECTRUM_RED (255,0,0)`, `SPECTRUM_INFRARED (139,0,0)`, `SPECTRUM_MICROWAVE (160,82,45)`, `SPECTRUM_RADIO (128,128,128)`

Modifier impact grid:

- `MODIFIER_BUFF (100,255,100)`, `MODIFIER_DEBUFF (255,100,100)`, `MODIFIER_NEUTRAL (180,180,180)`

Test results:

- `TEST_PASS (80,255,120)`, `TEST_FAIL (255,80,80)`, `TEST_COMPLETE_NEUTRAL (255,200,100)`

## Builder Theme Defaults (Concrete)

`data/builder_theme.json` defaults that production widgets inherit unless overridden:

- `normal_bg #1a1e24`, `hovered_bg #252a32`, `selected_bg #2a3545`, `dark_bg #12151a`, `disabled_bg #15181d`
- `normal_text #c8d4e8`, `normal_border #3a4555`
- `filled_bar #4488dd`, `unfilled_bar #252a35`
- `window.#title_bar` background `#1e2838`
- `horizontal_slider.#sliding_button` thumb: `#3366aa` normal, `#4488cc` hover

Custom object IDs commonly used in panels:

- `#stat_label` left-aligned muted (`#8899bb`)
- `#stat_value` right-aligned highlight (`#aaccff`)
- `#stat_unit` left-aligned dim (`#667799`)
- `#header_label` bold 16px accent (`#6699cc`)

## Design Principles

1. Depth through value: darker for recessed, lighter for elevated.
2. Cyan/blue accents are reserved for hover, selection, active focus, and key highlights. Avoid using them for default state.
3. Borders are thin (1-2px) and muted by default; bright cyan only on hover or selection.
4. Text contrast: brighter text on darker backgrounds. Reuse existing `TEXT_*` constants instead of inventing new shades.
5. Corner radius is 3-5px for rounded pygame_gui controls. Match the surrounding selector instead of normalizing globally.
6. Never inline RGB tuples in UI code; always reference a named constant.
7. Place new constants under the matching `# === Category ===` comment block in `game/ui/colors.py`.

## Stale References Fixed Here

- `ShipDetailPanel` is under `game/ui/panels/ship_detail_panel.py`, not `game/ui/screens/ship_detail_panel.py`.
- Component threshold lookup uses `get_default_registry_provider().get_components()`, not `get_component_registry()`.
- Active component-status colors use `get_damage_color(hp_pct)`; component damage thresholds only classify inactive rows.
- Shared HP color thresholds are `>= 50%`, `25-49%`, `1-24%`, and `<= 0%` or inactive.
- `data/builder_theme.json` currently uses button radius `3`, includes `panel.@fast_panel`, and includes `button.@tri_state_radio`.
- Test Lab theme currently includes `BUTTON_BASELINE_*` and validation `PHASE_*` constants.
