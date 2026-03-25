# UI Components & Widgets Duplication Report

**Scope:** `game/ui/components/`, `game/ui/widgets/`, `game/ui/panels/`, `game/ui/utils/`, `game/ui/colors.py`, `game/ui/fonts.py`, `game/ui/config.py`, `game/ui/interfaces/`
**Date:** 2026-03-24
**Files reviewed:** 40+ Python files

## Summary

The UI layer is relatively well-organized with several prior consolidation efforts (BaseGallery, DesignStatsPanel, PanelFactory, UIElementRegistry, ship_stats_renderer extraction). However, I found **11 duplication findings** across the codebase, including 5 MAJOR and 6 MINOR issues. The most significant duplication clusters around:

1. **Portrait loading and placeholder generation** -- near-identical logic in 3 files
2. **Resource icon loading** -- duplicated across 3 files
3. **HP/damage color threshold functions** -- duplicated in 2 files
4. **Section header patterns** -- two competing conventions
5. **Slider-label panel boilerplate** -- massive structural repetition in race config panels

---

## Findings

#### MAJOR: Duplicated Portrait Loading and Ship Class Parsing Logic
**ID:** DUP-UIW-001
**Location:** `game/ui/panels/design_report_panel.py:170-269` and `game/ui/panels/build_queue_portraits.py:80-128`
**Issue:** Both `DesignReportPanel._update_portrait()` and `BuildQueuePortraitLoader.load_design_portrait()` contain nearly identical logic for:
- Parsing ship class names with regex (`re.match(r"(.*)\s+\((.*)\)", ship_class)`)
- Building portrait file paths (same 3 fallback paths: ShipThemes, resources/Portraits, Default_Ship_Portrait)
- Loading and scaling images with the same error handling
- Creating colored placeholder surfaces when images not found (with same vehicle type color mapping)

The regex pattern, path construction, and fallback logic are duplicated verbatim between the two files (~50 lines each).

**Impact:** Bug fixes to portrait lookup must be applied in two places. The path list already differs slightly (DesignReportPanel has 4 paths vs BuildQueuePortraitLoader's 3), suggesting drift has already occurred.
**Recommendation:** Extract a shared `PortraitResolver` class or utility function in `game/ui/utils/` that handles ship class parsing, path resolution, image loading, and placeholder generation. Both consumers delegate to it.
**Effort:** Medium

---

#### MAJOR: Duplicated Resource Icon Loading
**ID:** DUP-UIW-002
**Location:** `game/ui/panels/build_queue_portraits.py:195-224` (`BuildQueuePortraitLoader.load_resource_icons`), `game/ui/panels/planet_report_panel.py:401-431` (`PlanetReportPanel._load_resource_icons`), and `game/ui/panels/empire_treasury_panel.py:300-322` (`load_resource_icons`)
**Issue:** Three separate implementations of resource icon loading that all:
1. Iterate over `PLANET_RESOURCES`
2. Build a path to `assets/Images/Resource Portraits/`
3. Load and `smoothscale` to a target size
4. Create fallback colored squares on failure using `RESOURCE_FALLBACK_COLORS`

The implementations are nearly identical, differing only in icon size defaults (20 vs 24) and minor error handling.

**Impact:** Three places to update if icon paths change or fallback behavior needs adjustment. The `RESOURCE_PORTRAIT_FILES` and `RESOURCE_FALLBACK_COLORS` dicts are defined in `build_queue_portraits.py` and imported by `planet_report_panel.py`, but `empire_treasury_panel.py` uses a completely different path pattern (`resource_{name.lower()}_icon.png` vs `resource_{name}_portrait.png`), suggesting a latent bug or inconsistency.
**Recommendation:** Create a single `load_resource_icons(icon_size: int) -> Dict[str, pygame.Surface]` function in a shared location (e.g., `game/ui/utils/resource_icons.py`) that all three consumers call.
**Effort:** Simple

---

#### MAJOR: Duplicated HP/Damage Color Threshold Functions
**ID:** DUP-UIW-003
**Location:** `game/ui/panels/ship_stats_renderer.py:90-106` (`get_hp_bar_color`) and `game/ui/panels/ship_detail_panel.py:29-50` (`get_damage_color`)
**Issue:** Both functions map an HP percentage to a color using the same semantic thresholds (green/yellow/red/gray), but with slightly different cutoff values:
- `get_hp_bar_color`: >0.5 green, >0.2 yellow, else red (+ inactive gray check)
- `get_damage_color`: >0.75 green, >=0.5 yellow, <0.5 red, <=0 gray

The different thresholds mean the same ship component shows different damage colors depending on which panel is viewing it, which is a UX inconsistency.

**Impact:** Inconsistent damage visualization across battle and strategy views. Maintenance burden of two similar-but-different functions.
**Recommendation:** Consolidate into a single `get_damage_color(hp_pct: float, is_active: bool = True) -> Tuple[int,int,int]` function in `ship_stats_renderer.py` (or `game/ui/utils/`) with agreed-upon thresholds. Update `ship_detail_panel.py` to import it.
**Effort:** Simple

---

#### MAJOR: Slider+Label Boilerplate in Race Config Panels
**ID:** DUP-UIW-004
**Location:** `game/ui/panels/race_environment_panel.py` (lines 165-400) and `game/ui/panels/race_aptitudes_panel.py` (lines 125-176)
**Issue:** The environment panel has 7 slider controls (gravity ideal, gravity tolerance, temp ideal, temp tolerance, radiation, water ideal, water tolerance) and 6 atmosphere sliders, each following the exact same ~15-line pattern:
1. Create UILabel for name
2. Create UIHorizontalSlider
3. Create UILabel for value display
4. Store references in instance dicts

The aptitudes panel repeats the same pattern for 9 sliders. Total: ~22 slider instances across 2 files, each with identical boilerplate structure. The `update_labels()` and `set_from_config()` methods also follow identical patterns of `if slider and label: label.set_text(format(slider.get_current_value()))`.

**Impact:** ~400 lines of structural repetition. Adding a new slider row requires copying 15 lines and updating 3 methods.
**Recommendation:** Create a `SliderRow` widget class (similar to the existing `StatRow` in `design_stats_panel.py`) that encapsulates the label+slider+value pattern. Panels would declare slider rows declaratively and let the widget handle creation, update, and config sync.
**Effort:** Complex

---

#### MAJOR: Duplicate Placeholder Portrait Generation (Gradient Fill + Text)
**ID:** DUP-UIW-005
**Location:** `game/ui/panels/design_report_panel.py:221-266` and `game/ui/panels/planet_report_panel.py:210-244`
**Issue:** Both panels create placeholder portraits when no image is found, using the same approach:
1. Create a Surface
2. Map type to base color from a dict
3. Draw gradient fill with a for-loop over height
4. Render entity name with shadow text (offset by 1px)
5. Draw border rectangle

The code structure is almost line-for-line identical, just with different type->color mappings (ship classes vs planet types) and different sizes.

**Impact:** Visual inconsistency if gradient/shadow style is updated in one place but not the other.
**Recommendation:** Extract a `create_placeholder_portrait(size, base_color, name_text, subtitle=None) -> pygame.Surface` utility function in `game/ui/utils/pygame_utils.py`.
**Effort:** Simple

---

#### MINOR: Duplicate Image Scaling/Centering Logic
**ID:** DUP-UIW-006
**Location:** `game/ui/utils/pygame_utils.py:223-260` (`scale_image_to_fit`), `game/ui/panels/ship_detail_panel.py:129-164` (`_get_scaled_image`), and `game/ui/panels/race_summary_panel.py:616-638` (inline in `_refresh_ship_preview`)
**Issue:** Three implementations of "scale image to fit within target bounds, center on background surface":
- `scale_image_to_fit` in pygame_utils (the canonical utility)
- `ShipDetailPanel._get_scaled_image` (adds 90% margin and placeholder drawing)
- `RaceSummaryPanel._refresh_ship_preview` (inline: `scale = min(ship_size / w, ship_size / h)`)

The race summary panel duplicates the core logic inline instead of using the existing utility. The ship detail panel adds extra features but shares the fundamental algorithm.

**Impact:** The utility already exists but is not being used by the other two consumers.
**Recommendation:** Refactor `ShipDetailPanel._get_scaled_image` and `RaceSummaryPanel._refresh_ship_preview` to use `scale_image_to_fit()` from `game.ui.utils`, optionally with a margin parameter.
**Effort:** Simple

---

#### MINOR: Two Competing Section Header Patterns
**ID:** DUP-UIW-007
**Location:** `game/ui/utils/pygame_utils.py:186-220` (`create_section_header`) vs `game/ui/panels/ship_detail_panel.py:333-342` (`_add_section_header`) and `game/ui/panels/design_stats_panel.py:307` (inline `f"-- {title} --"`)
**Issue:** Three different section header creation patterns:
1. `create_section_header()` utility: creates a `pygame_gui.UILabel` with `object_id="#section_header"`
2. `ShipDetailPanel._add_section_header()`: creates a `UILabel` with `f"-- {title} --"` formatting
3. `DesignStatsPanel._build_section()`: creates `UILabel` with `f"-- {title} --"` formatting

The utility function exists but panels 2 and 3 use their own inline pattern with dash-decorated titles. The visual style differs (plain text vs dash-decorated).

**Impact:** Inconsistent section header appearance. Developers may not know about the utility function.
**Recommendation:** Standardize on one pattern. If dash-decoration is desired, update `create_section_header()` to support it via a parameter, then migrate all callers.
**Effort:** Simple

---

#### MINOR: Duplicate Element Cleanup Patterns
**ID:** DUP-UIW-008
**Location:** Throughout panels: `ship_detail_panel.py:122-127`, `planet_report_panel.py:264-268`, `empire_treasury_panel.py:287-293`, `modifier_impact_grid.py:502-506`, `component_modifier_grid_panel.py:146-149`
**Issue:** Multiple panels implement the same `_clear_elements` pattern:
```python
for element in self.some_list:
    element.kill()
self.some_list = []  # or .clear()
```
This pattern appears in at least 8 different places. The `UIElementRegistry` widget (`game/ui/widgets/ui_element_registry.py`) was created to solve this exact problem but is not used by any of these panels.

**Impact:** Boilerplate code and risk of forgetting to clear lists after killing elements.
**Recommendation:** Adopt `UIElementRegistry` in panels that manage dynamic UI element lists. This was apparently created (PROJ-204) but never propagated to existing panels.
**Effort:** Medium (many files to touch, but each change is small)

---

#### MINOR: Duplicate Vehicle Type Color Maps
**ID:** DUP-UIW-009
**Location:** `game/ui/panels/build_queue_portraits.py:49-56` (`VEHICLE_TYPE_COLORS`) and `game/ui/panels/build_queue_drag_handler.py:336-341` (inline `color_map`)
**Issue:** The drag handler has an inline copy of the vehicle type -> color mapping that already exists in `build_queue_portraits.py`. The inline version is a subset but uses the same color constants.

**Impact:** Minor; the inline version is smaller and could drift from the canonical mapping.
**Recommendation:** Import `VEHICLE_TYPE_COLORS` from `build_queue_portraits.py` in the drag handler instead of duplicating the dict.
**Effort:** Simple

---

#### MINOR: Duplicate update_config/set_from_config Pattern in Race Panels
**ID:** DUP-UIW-010
**Location:** `race_environment_panel.py:450-528`, `race_aptitudes_panel.py:234-247`, `race_identity_panel.py:353-419`, `race_description_panel.py:115-135`
**Issue:** All four race configuration panels implement the same three-method interface pattern: `update_config()`, `set_from_config()`, and `update_labels()`. While the implementations differ in detail (each panel has different fields), the structural pattern is identical and could benefit from a base class or protocol that documents and enforces this contract.

**Impact:** No formal protocol means a new panel could omit one of the three methods without warning.
**Recommendation:** Define a `RaceConfigPanel` protocol (or ABC) with `update_config()`, `set_from_config()`, and `update_labels()` methods. Each panel implements it. This is more about formalization than deduplication.
**Effort:** Simple

---

#### MINOR: Colors Module Has Both Module-Level and Dict-Based Color Definitions
**ID:** DUP-UIW-011
**Location:** `game/ui/colors.py:8-9` (module-level `WHITE`, `BLACK`) vs `game/ui/colors.py:12-43` (`COLORS` dict with `'text_selected': (255, 255, 255)`)
**Issue:** The colors module defines colors in two ways:
1. Module-level constants (e.g., `WHITE = (255, 255, 255)`, `TEXT_MUTED = (150, 150, 150)`)
2. A `COLORS` dict with themed keys (e.g., `'text_muted': (102, 119, 153)`, `'text_selected': (255, 255, 255)`)

The `COLORS` dict values are different from the module-level constants with similar names (e.g., `TEXT_MUTED` = `(150, 150, 150)` vs `COLORS['text_muted']` = `(102, 119, 153)`). This creates confusion about which color to use.

**Impact:** Developers may pick the wrong color definition. The `COLORS` dict appears to be from a newer style guide that was never fully adopted, creating two parallel color systems.
**Recommendation:** Audit `COLORS` dict usage across the codebase. If it is unused, remove it. If it represents the intended style guide, migrate module-level constants to match and deprecate the dict, or vice versa.
**Effort:** Medium (requires usage analysis across full UI layer)

---

## Top 5 Priority List

| Priority | ID | Severity | Title | Effort | Rationale |
|----------|-----|----------|-------|--------|-----------|
| 1 | DUP-UIW-002 | MAJOR | Resource Icon Loading x3 | Simple | Three copies of identical loading code; one has divergent path pattern suggesting latent bug |
| 2 | DUP-UIW-001 | MAJOR | Portrait Loading + Ship Class Parsing x2 | Medium | ~100 lines of near-identical code with evidence of drift between copies |
| 3 | DUP-UIW-003 | MAJOR | HP/Damage Color Thresholds x2 | Simple | UX inconsistency where same HP shows different colors in different views |
| 4 | DUP-UIW-005 | MAJOR | Placeholder Portrait Generation x2 | Simple | Easy extraction to utility function; identical gradient+shadow+border pattern |
| 5 | DUP-UIW-008 | MINOR | Element Cleanup Pattern (8+ occurrences) | Medium | UIElementRegistry exists but is unused; propagating it would remove boilerplate from many files |
