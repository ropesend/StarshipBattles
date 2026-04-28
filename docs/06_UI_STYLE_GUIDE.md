# UI Style Guide

> **Last verified:** 2026-04-28 — Added Read-only component grouping section (PROJ-315) documenting the COMPONENT STATUS panel pattern.

Comprehensive reference for all color constants, theming systems, and usage patterns
in the Starship Battles UI. The visual identity is a dark blue-gray palette with cyan
accents -- a futuristic military starship aesthetic.

---

## 0. Window Management (PROJ-313)

**New strategy-modal windows MUST subclass `StrategyModalWindow`** rather
than `pygame_gui.elements.UIWindow` directly.

```python
from game.ui.screens.strategy_modal_window import StrategyModalWindow

class MyNewWindow(StrategyModalWindow):
    def __init__(
        self,
        rect,
        manager,
        # ... your domain args ...
        *,
        window_manager: "StrategyWindowManager | None" = None,
        # ... other kwargs ...
    ):
        super().__init__(
            rect, manager,
            window_display_title="My Window",
            resizable=False,
            window_manager=window_manager,
        )
        # ... your construction ...
```

The base class auto-registers the instance with the window manager on
construction and auto-deregisters in `kill()`. The strategy event router
walks `window_manager.iter_live_modals()` for click-blocking and modal
detection — no manual slot field, no `has_modal_open()` clause, no
`_is_blocking_ui_element_at()` clause required.

For windows opened **outside** the strategy screen (e.g., from
`BuildQueueScreen`), pass `window_manager=None`.

See `docs/02_PATTERNS.md` Pattern #31 for the full rationale and
historical context (Pattern #30 documents the superseded manual contract).

---

## 1. Core Color Palette (`COLORS` dict)

**Source:** `game/ui/colors.py` lines 12-43

The `COLORS` dict contains 23 named entries used for general-purpose pygame drawing.
Import as `from game.ui.colors import COLORS` and index by string key.

### Backgrounds (dark to light)

| Key | RGB | Usage |
|-----|-----|-------|
| `bg_deep` | (18, 21, 26) | Deepest recessed areas |
| `bg_dark` | (20, 24, 31) | Panel interiors, text entry bg |
| `bg_base` | (26, 30, 38) | Standard panel backgrounds |
| `bg_elevated` | (30, 37, 48) | Buttons, list items (normal) |
| `bg_hover` | (40, 48, 64) | Hovered elements |
| `bg_selected` | (42, 56, 85) | Selected items, active states |

### Borders

| Key | RGB | Usage |
|-----|-----|-------|
| `border_subtle` | (42, 48, 64) | Disabled borders |
| `border_normal` | (42, 53, 69) | Default panel borders |
| `border_active` | (58, 72, 96) | Button borders, prominent elements |
| `border_hover` | (85, 170, 238) | Hovered borders (cyan glow) |
| `border_selected` | (68, 153, 221) | Selected borders |

### Text

| Key | RGB | Usage |
|-----|-----|-------|
| `text_disabled` | (85, 96, 112) | Disabled/inactive labels |
| `text_muted` | (102, 119, 153) | Units, secondary info |
| `text_subtle` | (136, 153, 187) | Stat labels, tertiary |
| `text_normal` | (154, 171, 204) | Default text |
| `text_bright` | (170, 187, 221) | Button text, important labels |
| `text_highlight` | (170, 204, 255) | Stat values, emphasis |
| `text_hover` | (200, 218, 255) | Hovered item text |
| `text_selected` | (255, 255, 255) | Selected/active text |
| `text_error` | (255, 100, 100) | Error messages |

### Accents

| Key | RGB | Usage |
|-----|-----|-------|
| `accent_primary` | (68, 136, 221) | Filled bars, primary actions |
| `accent_glow` | (85, 170, 238) | Glow effects |
| `accent_bright` | (102, 187, 255) | Bright highlights |

Additionally, two standalone constants are defined at module level:
- `WHITE = (255, 255, 255)` and `BLACK = (0, 0, 0)`

---

## 2. Domain Color Constants

All defined as module-level tuples in `game/ui/colors.py`. Import by name:
`from game.ui.colors import HP_HEALTHY, TEAM_1_TEXT, ...`

### Ship Layer Rendering

| Constant | RGB | Purpose |
|----------|-----|---------|
| `LAYER_ARMOR` | (100, 100, 100) | Armor layer (gray) |
| `LAYER_OUTER` | (200, 50, 50) | Outer hull (red) |
| `LAYER_INNER` | (50, 50, 200) | Inner hull (blue) |
| `LAYER_CORE` | (220, 220, 220) | Core layer (light gray) |
| `LAYER_LABEL` | (80, 80, 80) | Schematic view layer labels |

### Projectiles

| Constant | RGB | Purpose |
|----------|-----|---------|
| `PROJECTILE_STANDARD` | (255, 200, 50) | Golden yellow |
| `PROJECTILE_MISSILE` | (255, 50, 50) | Red |
| `PROJECTILE_BEAM` | (100, 200, 255) | Light blue |
| `PROJECTILE_GLOW` | (255, 255, 100) | Endpoint glow effect |

### HP / Health Status

| Constant | RGB | Threshold |
|----------|-----|-----------|
| `HP_HEALTHY` | (0, 255, 0) | > 50% |
| `HP_DAMAGED` | (255, 200, 0) | 20-50% |
| `HP_CRITICAL` | (255, 50, 50) | < 20% |
| `HP_DESTROYED` | (100, 100, 100) | 0% |

### Damage Gradient (6-step)

`DAMAGE_GRADIENT` is a list of 6 tuples from bright green (max damage) to red (min damage):
`[(50,255,50), (100,220,50), (150,180,50), (200,140,50), (230,100,50), (255,60,50)]`

### Resources

| Constant | RGB | Purpose |
|----------|-----|---------|
| `RESOURCE_FUEL` | (255, 165, 0) | Orange |
| `RESOURCE_ENERGY` | (100, 200, 255) | Light blue |
| `RESOURCE_AMMO` | (200, 200, 100) | Yellowish |
| `RESOURCE_SHIELD` | (0, 200, 255) | Cyan |
| `RESOURCE_BIOMASS` | (100, 255, 100) | Green |
| `RESOURCE_METALS` | (192, 192, 192) | Silver |
| `RESOURCE_ORGANICS` | (80, 180, 80) | Green |
| `RESOURCE_VAPORS` | (100, 150, 220) | Blue |
| `RESOURCE_RADIOACTIVES` | (220, 180, 50) | Gold |
| `RESOURCE_EXOTICS` | (180, 80, 200) | Purple |

### Research Tree

| Constant | RGB | Purpose |
|----------|-----|---------|
| `RESEARCH_LOCKED` | (80, 80, 90) | Locked node |
| `RESEARCH_AVAILABLE` | (50, 100, 180) | Available for research |
| `RESEARCH_COMPLETED` | (50, 140, 60) | Completed |
| `RESEARCH_SELECTED` | (200, 180, 50) | Currently selected |
| `RESEARCH_LINE_UNMET` | (60, 65, 75) | Prerequisite line (unmet) |
| `RESEARCH_LINE_MET` | (80, 120, 80) | Prerequisite line (met) |
| `RESEARCH_LINE_NEGATED` | (180, 80, 80) | Negated prerequisite |
| `RESEARCH_LINE_NEGATED_MET` | (100, 60, 60) | Negated but met |
| `RESEARCH_TEXT` | (220, 220, 230) | Node text |
| `RESEARCH_CHANCE` | (255, 220, 100) | Research chance display |
| `RESEARCH_ALLOCATION` | (255, 255, 0) | Allocation indicator |

### Team Colors (Battle/Setup)

| Constant | RGB | Purpose |
|----------|-----|---------|
| `TEAM_1_TEXT` | (100, 200, 255) | Team 1 accent (blue) |
| `TEAM_1_BG` | (30, 50, 70) | Team 1 item bg |
| `TEAM_1_BANNER_BG` | (40, 60, 80) | Team 1 banner bg |
| `TEAM_1_BORDER` | (100, 150, 200) | Team 1 border |
| `TEAM_2_TEXT` | (255, 100, 100) | Team 2 accent (red) |
| `TEAM_2_BG` | (70, 30, 30) | Team 2 item bg |
| `TEAM_2_BANNER_BG` | (80, 40, 40) | Team 2 banner bg |
| `TEAM_2_BORDER` | (200, 100, 100) | Team 2 border |

### Ship Class Colors (Design Reports)

| Constant | RGB | Class |
|----------|-----|-------|
| `SHIP_CLASS_FIGHTER` | (255, 150, 50) | Orange |
| `SHIP_CLASS_CORVETTE` | (100, 200, 100) | Green |
| `SHIP_CLASS_ESCORT` | (100, 150, 255) | Light blue |
| `SHIP_CLASS_DESTROYER` | (255, 100, 100) | Red |
| `SHIP_CLASS_CRUISER` | (200, 100, 255) | Purple |
| `SHIP_CLASS_BATTLESHIP` | (255, 200, 50) | Yellow |
| `SHIP_CLASS_CARRIER` | (150, 255, 200) | Cyan-green |
| `SHIP_CLASS_DEFAULT` | (150, 150, 150) | Gray fallback |

### Vehicle Types

| Constant | RGB | Purpose |
|----------|-----|---------|
| `VEHICLE_DEFAULT` | (100, 100, 255) | Default new design |
| `VEHICLE_SHIP` | (80, 100, 180) | Ship |
| `VEHICLE_FIGHTER` | (180, 180, 80) | Fighter |
| `VEHICLE_STATION` | (180, 100, 80) | Station |
| `VEHICLE_COMPLEX` | (80, 180, 100) | Planetary complex |

### Battle Status

| Constant | RGB | Purpose |
|----------|-----|---------|
| `STATUS_ACTIVE_TEXT` | (255, 255, 100) | Active entity text |
| `STATUS_ACTIVE_BG` | (50, 50, 60) | Active entity bg |
| `STATUS_HIT_TEXT` | (50, 255, 50) | Hit confirmed |
| `STATUS_DESTROYED_TEXT` | (255, 50, 50) | Destroyed |
| `STATUS_DERELICT` | (255, 165, 0) | Derelict/orange alert |
| `SEEKER_TITLE` | (255, 200, 100) | Seeker monitor title |
| `DAMAGE_TEXT` | (255, 150, 150) | Damage amount |
| `TARGET_TEXT` | (150, 200, 150) | Target info |

### Battle HUD

| Constant | RGB | Purpose |
|----------|-----|---------|
| `SPEED_PAUSED` | (255, 100, 100) | Paused indicator (red) |
| `SPEED_SLOWMO` | (255, 200, 100) | Slow-mo indicator (gold) |
| `SPEED_FAST` | (100, 255, 100) | Fast-forward indicator (green) |
| `HUD_TEXT` | (180, 180, 180) | General HUD text |
| `HUD_ZOOM_TEXT` | (150, 200, 255) | Zoom level text |

### Battle Grid / Debug Overlay

| Constant | RGB | Purpose |
|----------|-----|---------|
| `GRID_BG_BATTLE` | (30, 30, 50) | Battle grid lines |
| `DEBUG_TARGET_LINE` | (0, 0, 255) | Target indicator (blue) |
| `DEBUG_WEAPON_RANGE` | (100, 100, 100) | Weapon range circle |
| `DEBUG_AIM_POINT` | (0, 100, 255) | Aim point |
| `DEBUG_FIRING_ARC` | (255, 165, 0) | Firing arc (orange) |
| `DEBUG_COLLISION` | (100, 255, 100) | Collision radius |
| `DEBUG_DIRECTION` | (255, 255, 0) | Direction indicator |

### Component Overlay

| Constant | RGB | Purpose |
|----------|-----|---------|
| `OVERLAY_COMPONENT` | (200, 200, 200) | Default component dot |
| `OVERLAY_WEAPON` | (255, 50, 50) | Weapon (red) |
| `OVERLAY_PROPULSION` | (50, 255, 100) | Propulsion (green) |
| `OVERLAY_ARMOR` | (100, 100, 100) | Armor (gray) |
| `OVERLAY_FALLBACK` | (100, 100, 100) | Missing image fallback |

### Component Status

| Constant | RGB | Purpose |
|----------|-----|---------|
| `COMPONENT_NO_POWER` | (255, 255, 0) | No power (yellow) |
| `COMPONENT_NO_FUEL` | (255, 100, 0) | No fuel (orange) |
| `COMPONENT_INACTIVE_BG` | (100, 50, 50) | Inactive bg (dark red) |
| `WEAPON_STATS_TEXT` | (150, 150, 255) | Weapon S:H stats |
| `WEAPON_INACTIVE` | (150, 50, 50) | Inactive weapon text |
| `WEAPON_INACTIVE_STATUS` | (255, 100, 100) | Inactive weapon status |
| `CREW_LOW` | (255, 100, 100) | Low crew warning |

### Section Headers

| Constant | RGB | Purpose |
|----------|-----|---------|
| `SECTION_HEADER_WEAPONS` | (200, 200, 150) | Weapons section |
| `SECTION_HEADER_COMPONENTS` | (200, 200, 100) | Components section |
| `AI_STRATEGY_TEXT` | (150, 200, 150) | Movement/targeting policy name |
| `METADATA_FILE_TEXT` | (150, 150, 200) | Source file path |

### Button Colors

| Prefix | Description | Keys |
|--------|-------------|------|
| `BTN_NEUTRAL_*` | Standard buttons | `_BG`, `_BORDER`, `_TEXT` |
| `BTN_DANGER_*` | Destructive actions | `_BG`, `_HOVER`, `_BORDER`, `_TEXT`, `_HOVER_BORDER` |
| `BTN_PRIMARY_*` | Primary confirm | `_BG`, `_BORDER` |
| `BTN_RETURN_*` | Return/back | `_BG`, `_HOVER` |
| `BTN_END_*` | End battle | `_BG`, `_BORDER`, `_TEXT` |
| `BTN_VICTORY_*` | Victory screen | `_BG`, `_BORDER` |
| `BTN_CLEAR_*` | Clear/reset | `_BG`, `_BORDER`, `_TEXT` |
| `BTN_QUICK_*` | Quick action | `_BG`, `_BORDER`, `_TEXT` |
| `BTN_DISABLED_BG` | Disabled state | Single constant |

### Scene Backgrounds

| Constant | RGB | Purpose |
|----------|-----|---------|
| `BG_BATTLE` | (10, 10, 20) | Battle + app bg |
| `BG_GALAXY` | (15, 20, 30) | Galaxy map bg |
| `BG_MENU` | (20, 20, 30) | Menu screen bg |

### Common UI Constants

| Constant | RGB | Purpose |
|----------|-----|---------|
| `TEXT_LIGHT` | (220, 220, 220) | Primary text |
| `TEXT_MUTED` | (150, 150, 150) | Muted/hint text |
| `TEXT_DIM` | (100, 100, 100) | Dim/disabled |
| `TEXT_ERROR` | (255, 100, 100) | Error text |
| `TEXT_SECONDARY` | (180, 180, 180) | Label/stat text |
| `TEXT_ITEM` | (200, 200, 200) | List item text |
| `PANEL_BG` | (30, 30, 35) | Popup/dialog bg |
| `BORDER_LIGHT` | (100, 100, 120) | Active borders |
| `BORDER_DARK` | (80, 80, 90) | Standard borders |
| `BORDER_PANEL` | (60, 60, 80) | Panel dividers |
| `BAR_BG` | (40, 40, 40) | Progress bar fill |
| `BAR_BORDER` | (80, 80, 80) | Progress bar outline |
| `BG_PANEL_DARK` | (20, 25, 35) | Dark panel bg |
| `BG_ROW_ALT` | (35, 35, 45) | Alternating row bg |
| `BG_ITEM` | (40, 40, 50) | List item bg |
| `GRID_LINE` | (45, 45, 55) | Grid/separator lines |
| `GRID_BG` | (30, 30, 40) | Grid/card bg |

### Table Selection

| Constant | RGB | Purpose |
|----------|-----|---------|
| `TABLE_SELECTED` | (60, 80, 120) | Selected row (blue tint) |
| `TABLE_UNSELECTED` | (35, 35, 35) | Unselected row bg |

### Planet Types

| Constant | RGB | Visual |
|----------|-----|--------|
| `PLANET_CONTINENTAL` | (70, 130, 70) | Green |
| `PLANET_ARID` | (180, 140, 80) | Tan |
| `PLANET_PELAGIC` | (50, 80, 180) | Blue |
| `PLANET_MAGMA` | (200, 50, 30) | Red |
| `PLANET_CRYO` | (180, 200, 220) | Icy blue |
| `PLANET_BARREN` | (130, 130, 130) | Gray |
| `PLANET_JOVIAN` | (200, 160, 100) | Tan-orange |
| `PLANET_ICE_GIANT` | (100, 150, 200) | Blue |
| `PLANET_CHTHONIAN` | (100, 80, 60) | Brown |
| `PLANET_ICE_DWARF` | (200, 210, 230) | Pale blue |
| `PLANET_PLANETOID` | (90, 90, 90) | Dark gray |
| `PLANET_TERRESTRIAL` | (100, 150, 200) | Blue |
| `PLANET_GAS_GIANT` | (200, 150, 100) | Orange |
| `PLANET_ICE` | (150, 200, 255) | Light blue |
| `PLANET_ROCKY` | (150, 100, 80) | Brown |
| `PLANET_OCEANIC` | (50, 100, 200) | Deep blue |

### Star Spectrum

| Constant | RGB | Band |
|----------|-----|------|
| `SPECTRUM_GAMMA` | (200, 0, 255) | Gamma |
| `SPECTRUM_XRAY` | (148, 0, 211) | X-ray |
| `SPECTRUM_UV` | (75, 0, 130) | Ultraviolet |
| `SPECTRUM_BLUE` | (0, 0, 255) | Blue |
| `SPECTRUM_GREEN` | (0, 255, 0) | Green |
| `SPECTRUM_RED` | (255, 0, 0) | Red |
| `SPECTRUM_INFRARED` | (139, 0, 0) | Infrared |
| `SPECTRUM_MICROWAVE` | (160, 82, 45) | Microwave |
| `SPECTRUM_RADIO` | (128, 128, 128) | Radio |

### Atmospheric Gases

| Constant | RGB | Gas |
|----------|-----|-----|
| `GAS_N2` | (173, 216, 230) | Nitrogen |
| `GAS_O2` | (0, 0, 255) | Oxygen |
| `GAS_CO2` | (100, 100, 100) | Carbon dioxide |
| `GAS_H2O` | (0, 0, 139) | Water vapor |
| `GAS_CH4` | (255, 165, 0) | Methane |
| `GAS_H2` | (255, 192, 203) | Hydrogen |
| `GAS_HE` | (255, 255, 255) | Helium |
| `GAS_AR` | (128, 0, 128) | Argon |
| `GAS_SO2` | (255, 255, 0) | Sulfur dioxide |
| `GAS_UNKNOWN` | (100, 150, 100) | Unknown gas |

### Storm Effects

| Constant | RGB | Storm type |
|----------|-----|------------|
| `STORM_ION` | (100, 150, 255) | Ion storm |
| `STORM_PLASMA` | (255, 100, 100) | Plasma storm |
| `STORM_GRAVITATIONAL` | (180, 100, 255) | Gravity anomaly |
| `STORM_RADIATION` | (255, 255, 100) | Radiation belt |
| `STORM_DARK_NEBULA` | (150, 150, 150) | Dark nebula |

### Strategy Map

| Constant | RGB | Purpose |
|----------|-----|---------|
| `WARP_LANE` | (50, 50, 100) | Warp lane lines |
| `STAR_LABEL` | (200, 200, 200) | Star name labels |
| `FLEET_SELECTED` | (255, 255, 0) | Selected fleet highlight |
| `PATH_MOVE` | (0, 255, 100) | Movement path |
| `PATH_WARP` | (255, 50, 50) | Warp path |
| `PATH_LABEL` | (200, 200, 255) | Path label text |
| `OVERLAY_PROCESSING` | (255, 200, 0) | Processing indicator |
| `WARPPOINT_FALLBACK` | (200, 0, 255) | Default warp point |
| `DYSON_FALLBACK` | (0, 200, 200) | Default Dyson sphere |
| `PLANET_FALLBACK` | (100, 100, 100) | Default planet |
| `ZONE_HIGHLIGHT` | (100, 255, 100) | Zone selection |
| `STAR_FALLBACK` | (255, 255, 200) | Default star |
| `STORM_FALLBACK` | (100, 100, 100) | Default storm tint |
| `HEX_OUTLINE_OCCUPIED` | (200, 60, 60) | Occupied hex (red) |
| `HEX_OUTLINE_PLAYER_OWNED` | (220, 220, 220) | Player-owned hex (white) |

### Setup Screen

Constants prefixed `SETUP_*`, `ITEM_*`, `DROPDOWN_*` for battle setup UI.
See `game/ui/colors.py` lines 192-211 for the full set.

### Weapon Renderer

| Constant | RGB | Purpose |
|----------|-----|---------|
| `WEAPON_BAR_BEAM` | (40, 80, 40) | Beam weapon bar bg |
| `WEAPON_BAR_PROJECTILE` | (80, 60, 40) | Projectile weapon bar bg |
| `WEAPON_BAR_SEEKER` | (80, 40, 80) | Seeker weapon bar bg |
| `WEAPON_ACCURACY_HIGH` | (0, 200, 0) | High accuracy (green) |
| `WEAPON_ACCURACY_MED` | (200, 100, 0) | Medium accuracy (orange) |
| `WEAPON_ACCURACY_LOW` | (200, 50, 50) | Low accuracy (red) |
| `WEAPON_LABEL` | (200, 200, 100) | Weapon name label |
| `WEAPON_RANGE_LABEL` | (150, 150, 200) | Range value label |
| `WEAPON_ARC` | (200, 150, 50) | Firing arc indicator |

### Modifier Impact Grid

| Constant | RGB | Purpose |
|----------|-----|---------|
| `MODIFIER_HEADER_BG` | (40, 40, 50) | Column header bg |
| `MODIFIER_ROW_BG` | (30, 30, 40) | Row bg |
| `MODIFIER_ROW_ALT_BG` | (35, 35, 45) | Alternating row bg |
| `MODIFIER_FOOTER_BG` | (50, 50, 60) | Footer bg |
| `MODIFIER_BUFF` | (100, 255, 100) | Positive effect (green) |
| `MODIFIER_DEBUFF` | (255, 100, 100) | Negative effect (red) |
| `MODIFIER_NEUTRAL` | (180, 180, 180) | Neutral |

### JSON Viewer / Scrollable Panel

Constants prefixed `JSON_*` for syntax-highlighted JSON display. `SCROLLBAR_TRACK`,
`SCROLLBAR_THUMB`, `SCROLLBAR_THUMB_ACTIVE` for scrollbar chrome.

### Diff Viewer

Constants prefixed `DIFF_*` for changed/added/removed highlighting, plus `VIEWER_BTN_*`
for diff viewer buttons.

### Design Thumbnail Fallbacks

| Constant | RGB | Purpose |
|----------|-----|---------|
| `THUMB_SHIP` | (60, 80, 120) | Ship thumbnail bg |
| `THUMB_FIGHTER` | (80, 100, 60) | Fighter thumbnail bg |
| `THUMB_SATELLITE` | (100, 80, 100) | Satellite thumbnail bg |
| `THUMB_COMPLEX` | (90, 70, 50) | Complex thumbnail bg |
| `THUMB_TEXT` | (200, 200, 200) | Thumbnail text |

### Miscellaneous

| Constant | RGB | Purpose |
|----------|-----|---------|
| `TEST_PASS` | (80, 255, 120) | Test passed (green) |
| `TEST_FAIL` | (255, 80, 80) | Test failed (red) |
| `TEST_COMPLETE_NEUTRAL` | (255, 200, 100) | Neutral result (yellow) |
| `TEST_COMPLETE_PASSED` | (80, 255, 120) | Test complete passed (green) |
| `TEST_COMPLETE_FAILED` | (255, 80, 80) | Test complete failed (red) |
| `PLACEHOLDER_DEFAULT` | (128, 128, 128) | Default placeholder color |
| `RESULT_WIN` | (0, 255, 0) | Win |
| `RESULT_DRAW` | (255, 255, 0) | Draw |
| `DRAG_HIGHLIGHT` | (150, 220, 255) | Drag border highlight |
| `PLACEHOLDER_BORDER` | (80, 80, 80) | Placeholder image border |
| `SWATCH_BORDER` | (100, 100, 100) | Color swatch border |
| `PROFILING_TEXT` | (255, 50, 50) | Debug profiling overlay |

---

## 3. Hex-String Colors

Some UI areas use `'#RRGGBB'` strings instead of RGB tuples, because they render
via pygame_gui's HTML text boxes (`UITextBox`) or inline HTML in labels.

### Builder Detail Panel (`game/ui/colors.py`)

| Constant | Hex | Purpose |
|----------|-----|---------|
| `DETAIL_COMPONENT_NAME` | `#FFFF64` | Component name (yellow-green) |
| `DETAIL_COMPONENT_INFO` | `#C8C8C8` | Component info (light gray) |
| `DETAIL_TEXT` | `#E0E0E0` | General detail text |

### Design Stats Panel (`game/ui/colors.py`)

| Constant | Hex | Purpose |
|----------|-----|---------|
| `DESIGN_MISSING_REQ` | `#ffaa55` | Missing requirement (orange) |
| `DESIGN_REQS_MET` | `#88ff88` | Requirements met (green) |
| `DESIGN_WARNING` | `#ffff88` | Warning (yellow) |
| `DESIGN_NO_RECS` | `#888888` | No recommendations (gray) |

### Builder Panel Layout (`game/ui/colors.py`)

| Constant | Hex | Purpose |
|----------|-----|---------|
| `BUILDER_ITEM_BG` | `#14181f` | Deep dark item bg |
| `BUILDER_GROUP_BG` | `#1a1e26` | Group bg |
| `BUILDER_TREE_LINE` | `#2a3545` | Tree connector lines |

### Ability UI Hints (`game/simulation/components/abilities/ui_colors.py`)

Hex strings returned by `ability.get_ui_rows()` for semantic colorization in the
component detail panel. 21 constants total:

**Weapons and Offense:**
`HINT_DAMAGE` (#FF6464), `HINT_RANGE` (#FFA500), `HINT_RELOAD` (#FFC864),
`HINT_PROJECTILE_SPEED` (#C8C832), `HINT_ACCURACY` (#FFFF00)

**Defense and Shields:**
`HINT_SHIELD_CAP` (#00FFFF), `HINT_SHIELD_REGEN` (#00C8FF), `HINT_EVASION` (#64FFFF)

**Propulsion:**
`HINT_THRUST` (#64FF64), `HINT_TURN_SPEED` (#64FF96),
`HINT_STRATEGIC_MOBILITY` (#6496FF), `HINT_WARP_ENERGY` (#64C8FF)

**Crew and Support:**
`HINT_CREW_CAP` (#96FF96), `HINT_LIFE_SUPPORT` (#96FFFF), `HINT_CREW_REQ` (#FF9696)

**Cargo and Resources:**
`HINT_CARGO_PASSENGER` (#98FB98), `HINT_CARGO_GENERIC` (#FFD700), `HINT_COLONIZE` (#00FF00)

**Special:**
`HINT_SUPERWEAPON` (#FF4444), `HINT_REQUIREMENT` (#FFCC66)

**Neutral:**
`HINT_NEUTRAL` (#C8C8C8), `HINT_DEFAULT` (#FFFFFF)

---

## 4. pygame_gui Theming (`data/builder_theme.json`)

The theme file configures all pygame_gui widgets used in the Ship Design Workshop
and other pygame_gui-based screens. It uses hex color strings with the British
spelling `"colours"`.

### Defaults

Applied to all widgets unless overridden:

```
Font: FiraCode-Regular, size 14
normal_bg: #1a1e24    hovered_bg: #252a32    disabled_bg: #15181d
selected_bg: #2a3545   dark_bg: #12151a       normal_text: #c8d4e8
normal_border: #3a4555  filled_bar: #4488dd    unfilled_bar: #252a35
```

### Widget-Specific Entries

| Widget | Key properties |
|--------|----------------|
| **button** | rounded_rectangle, corner_radius 4, border 2, shadow 2 |
| **panel** | rounded_rectangle, corner_radius 3, border 1 |
| **selection_list** | rectangle, item height 22 |
| **selection_list.@selection_list_item** | border 0, distinct bg/text for normal/hover/selected |
| **drop_down_menu** | rounded_rectangle, corner_radius 3 |
| **horizontal_slider** | rounded_rectangle, corner_radius 3 |
| **horizontal_slider.#sliding_button** | thumb colors: #3366aa normal, #4488cc hover |
| **text_entry_line** | rounded_rectangle, corner_radius 3 |
| **label** | center-aligned, transparent bg (`#00000000`) |
| **window** | rounded_rectangle, corner_radius 5, border 2 |
| **window.#title_bar** | slightly lighter bg (#1e2838) |

### Custom Object IDs

| ID | Purpose |
|----|---------|
| `#stat_label` | Left-aligned, muted text (#8899bb) |
| `#stat_value` | Right-aligned, highlight text (#aaccff) |
| `#stat_unit` | Left-aligned, dim text (#667799) |
| `#left_aligned_label` | Override default center alignment |
| `#header_label` | Bold 16px, accent color (#6699cc) |
| `#modifier_panel_container` | Modifier panel styling |
| `#component_list_panel` | Component browser panel |
| `#mini_arrow_btn` | Small arrow buttons (bold 11px, centered) |
| `#tree_item_label` | Tree view item labels |

---

## 5. Test Lab Theme (`game/ui/screens/test_lab/theme.py`)

The Test Lab has its own parallel theme module with ~80 color constants, organized
for the test runner UI. Import as:
`from game.ui.screens.test_lab.theme import BG_PRIMARY, TEXT, STATUS_PASS, ...`

It aliases `TEST_PASS` and `TEST_FAIL` from `game.ui.colors` as `STATUS_PASS` and `STATUS_FAIL`.

### Categories

| Category | Constants | Notes |
|----------|-----------|-------|
| Backgrounds | `BG_PRIMARY`, `BG_PANEL`, `BG_CONTENT`, `BG_CATEGORY`, `BG_ITEM_HOVER`, `BG_OVERLAY` | Dark gray series (20-40) |
| Borders | `BORDER`, `BORDER_ACTIVE` | (80,80,90) and (100,100,120) |
| Text | `TEXT`, `TEXT_HEADER`, `TEXT_SECONDARY`, `TEXT_EXPECTED`, `TEXT_WHITE`, `TEXT_MUTED`, `TEXT_DIM`, `TEXT_LABEL`, `TEXT_VERY_DIM`, `TEXT_DIM_BLUE` | Full text hierarchy |
| Status | `STATUS_PASS`, `STATUS_FAIL`, `STATUS_WARNING`, `STATUS_INFO`, `STATUS_HIGHLIGHT` | Test result colors |
| Tags/Filters | `TAG_ACTIVE_*`, `TAG_EXCLUDED_*`, `TAG_NORMAL_*` | 3 states x 3 props (bg/border/text) |
| Tabs | `TAB_NORMAL`, `TAB_SELECTED`, `TAB_HOVER` | Tab bar states |
| Selection | `SELECTED_BG`, `SELECTED_CARD_BG`, `SELECTED_BORDER` | Item selection |
| Buttons | `BUTTON_BLUE_*`, `BUTTON_GREEN_*`, `BUTTON_PROGRESS_*`, `BUTTON_HEADLESS_*`, `BUTTON_RUN_*` | Multiple button types |
| Scrollbar | `SCROLLBAR_TRACK`, `SCROLLBAR_THUMB` | Scrollbar chrome |
| Seed controls | `SEED_RANDOM`, `SEED_FIXED`, `SEED_CUSTOM`, `SEED_CUSTOM_PENDING`, `SEED_BUTTON_*`, `SEED_INPUT_*` | Seed management UI |
| Clear filters | `CLEAR_BUTTON_*` | Red-tinted clear button |
| JSON viewer | `JSON_TITLE_BG`, `JSON_SCROLLBAR_*` | Test Lab JSON viewer (separate from main JSON viewer) |
| Cards | `CARD_HOVER_BG`, `CARD_LATEST_BG` | Test run cards |
| Separators | `SEPARATOR_LINE`, `SEPARATOR_SUBTLE` | Section dividers |
| Section headers | `SECTION_CATEGORY`, `SECTION_SUMMARY`, `SECTION_CONDITIONS`, `SECTION_EDGE_CASES`, `SECTION_OUTCOME`, `SECTION_CRITERIA` | Info panel sections |
| Button borders | `BUTTON_VIEW_STATES_BORDER`, `BUTTON_USE_SEED_BORDER`, `BUTTON_COPY_BORDER` | Per-button-type borders |
| Dropdowns | `DROPDOWN_SELECTED_BG`, `DROPDOWN_HOVER_BG` | Component dropdown |

---

## 6. Usage Patterns

### When to use each system

| Situation | Use | Example |
|-----------|-----|---------|
| Direct pygame drawing (rects, lines, text) | `COLORS` dict or named constants from `game.ui.colors` | `pygame.draw.rect(screen, COLORS['bg_base'], rect)` |
| pygame_gui widgets (builder, panels) | `builder_theme.json` via object IDs | `UIPanel(..., object_id='#component_list_panel')` |
| HTML text in `UITextBox` | Hex-string constants | `f"<font color='{DESIGN_REQS_MET}'>OK</font>"` |
| Ability detail rows | `HINT_*` from `abilities/ui_colors.py` | `{"label": "Damage", "value": "10", "color": HINT_DAMAGE}` |
| Test Lab screens | `game.ui.screens.test_lab.theme` | `from ...theme import STATUS_PASS` |

### Import conventions

```python
# For the COLORS dict (general-purpose backgrounds, borders, text)
from game.ui.colors import COLORS

# For domain-specific named constants
from game.ui.colors import HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, TEAM_1_TEXT

# For hex-string colors in HTML rendering
from game.ui.colors import DETAIL_COMPONENT_NAME, DESIGN_MISSING_REQ

# For ability UI hints (simulation layer, hex strings)
from game.simulation.components.abilities.ui_colors import HINT_DAMAGE, HINT_SHIELD_CAP

# For test lab (self-contained theme)
from game.ui.screens.test_lab.theme import BG_PRIMARY, STATUS_PASS
```

### Actual code patterns observed

**Battle panels** import 15-20 named constants directly:
```python
from game.ui.colors import (
    HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, RESOURCE_FUEL, TEXT_MUTED,
    TEAM_1_TEXT, TEAM_1_BANNER_BG, TEAM_2_TEXT, TEAM_2_BANNER_BG, ...
)
```

**Builder detail panel** mixes named constants and hex strings:
```python
from game.ui.colors import DETAIL_COMPONENT_NAME, DETAIL_TEXT, GRID_BG, TEXT_ITEM
```

**Design stats panel** uses hex-string constants for UITextBox HTML:
```python
from game.ui.colors import DESIGN_MISSING_REQ, DESIGN_REQS_MET, DESIGN_WARNING
```

---

## 7. Read-only component grouping (PROJ-315)

**When to use:** any panel that displays per-component damage state in a
read-only context — Fleet Report's `ShipDetailPanel`, future Battle
After-Action Report, etc. The pattern is documented here so new
read-only ship-component views stay visually consistent.

### Section structure

A "COMPONENT STATUS" section always renders, independent of damage. It
lists every component grouped by layer in the canonical Workshop order:

```python
LAYER_ORDER = ('CORE', 'INNER', 'OUTER', 'ARMOR')
```

`HULL` is excluded — Fleet Report doesn't display hull layer entries.

Each layer is a collapsible block. Inside an expanded layer, identical
`component_id`s collapse into one **group row** showing
`<DisplayName> × <count>`, `<functional>/<total>`, and `<avg>%` average
damage. Expanding the group reveals one **instance row** per component,
each with its own colour and (when relevant) strikethrough overlay.

### Auto-expand semantics

Layer expand state recomputes on every `update_ship` call — there is no
per-(ship, layer) state persistence. Layers auto-expand iff they contain
at least one destroyed instance (`current_hp == 0`). All groups start
collapsed; the user must click the chevron to drill in. This is
deterministic — switching back to a previously-viewed ship always shows
the same expand pattern.

### Colour-tier rules

| State                                                       | Colour           | Strikethrough |
|-------------------------------------------------------------|------------------|---------------|
| Healthy (`current_hp == max_hp`, `is_active`)               | `HP_HEALTHY`     | No            |
| Damaged (0 < damage_pct ≤ 0.5 × threshold, `is_active`)     | `HP_DAMAGED`     | No            |
| Critical (damage_pct > 0.5 × threshold, `is_active`)        | `HP_CRITICAL`    | No            |
| Destroyed (`current_hp == 0`)                               | `HP_DESTROYED`   | Yes           |
| Damage-induced inactive (HP > 0, below threshold, !active)  | `HP_CRITICAL`    | Yes           |
| Manually disabled (HP intact, !active)                      | `MUTED_GREY`     | No            |

`MUTED_GREY = (130, 130, 150)` distinguishes "intentionally off" from
`HP_DESTROYED` grey for "broken".

### Strikethrough convention

pygame_gui has no native `<s>` rich-text. The pattern is a manual
`pygame.draw.line()` overlay rendered as a `UIImage` pinned to the
label's rect, mirroring `game/ui/screens/test_lab/dialogs.py`. The panel
encapsulates this as `_apply_strikethrough(label)` and tracks the
overlay in `ui_elements` so cleanup happens via `_clear_elements()`.

If pygame_gui adds `<s>` support in a future release, prefer that and
remove the helper.

### Module-level pure-function colocation

`group_components_by_id()`, `ComponentGroup`, and `InstanceDamage` live
at module scope **above** the panel class in `ship_detail_panel.py` —
the same pattern as `planet_report_panel.py`'s `_projection_grid_rows`,
`_qty_cell` etc. A separate `ship_component_grouping.py` module would
be premature over-modularisation for ~80 LOC of pure logic.

The damage-threshold lookup is dependency-injected into
`group_components_by_id` so unit tests can stub it without instantiating
the registry. Production wires through
`get_default_registry_provider().get_component_registry()` and falls
back to `CombatConstants.DEFAULT_DAMAGE_THRESHOLD` (0.5) if the lookup
misses.

### Read-only contract

Group rows and instance rows are `UILabel`s. The only `UIButton`
instances inside the section are the layer-header chevron buttons and
the group-header chevron buttons (toggle input only). The pre-existing
`Remove from Fleet` button below the section is unaffected.

A regression test asserts that
`len(layer_buttons) + len(group_buttons) == count(UIButton in section)`.

### When extending

- **New view in another panel** — use the same `LAYER_ORDER`, the same
  colour tier table, and the same `group_components_by_id` import. Do
  not invent a parallel rule set.
- **Repair / mutation actions** — out of scope for this pattern. Add
  them in a separate row group below the read-only block, not by
  swapping instance labels for buttons.

---

## 8. Adding New Colors

### Where to add

| Color type | Location |
|------------|----------|
| General UI (backgrounds, borders, text) | Add to `COLORS` dict in `game/ui/colors.py` |
| Domain-specific (planets, storms, weapons) | Add as module-level constant in `game/ui/colors.py` with category comment |
| HTML/UITextBox rendering | Add as hex string constant in `game/ui/colors.py` |
| Ability UI hints | Add to `game/simulation/components/abilities/ui_colors.py` and `__all__` |
| Test Lab only | Add to `game/ui/screens/test_lab/theme.py` |
| pygame_gui widget styling | Add to `data/builder_theme.json` |

### Naming conventions

- **COLORS dict keys:** `category_descriptor` -- e.g., `bg_deep`, `text_muted`, `border_hover`
- **Module-level RGB tuples:** `DOMAIN_DESCRIPTOR` -- e.g., `PLANET_MAGMA`, `TEAM_1_TEXT`, `HP_CRITICAL`
- **Hex-string constants:** `CONTEXT_PURPOSE` -- e.g., `DETAIL_COMPONENT_NAME`, `DESIGN_REQS_MET`
- **Ability hints:** `HINT_SEMANTIC_NAME` -- e.g., `HINT_DAMAGE`, `HINT_SHIELD_CAP`
- **Test Lab theme:** `CATEGORY_DESCRIPTOR` -- e.g., `TAG_ACTIVE_BG`, `SEED_FIXED`

### Design principles

1. **Depth through color:** Darker backgrounds for recessed areas, lighter for elevated.
2. **Cyan accents sparingly:** Reserve the cyan/blue glow for hover states and key highlights.
3. **Subtle borders:** Thin (1-2px), muted for normal states. Bright only on hover/selection.
4. **High contrast text:** Brighter text on darker backgrounds. Minimum contrast for readability.
5. **Consistent corner radius:** 3-5px for rounded elements.
6. **No inline RGB tuples:** Always use a named constant. Never write `(255, 100, 100)` directly in a UI file.
7. **Category grouping:** Place new constants under the matching `# === Category ===` comment block.
