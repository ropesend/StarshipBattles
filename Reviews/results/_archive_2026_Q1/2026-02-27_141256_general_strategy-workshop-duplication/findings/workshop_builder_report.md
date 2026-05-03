# Workshop/Builder DRY Analysis

### Summary
- Total issues found: 17
- Critical: 3, Major: 7, Minor: 7, Info: 0

### Findings

#### CRITICAL: Identical Filter Button Creation Pattern in Multiple Panels
**ID:** CQ-60
**Location:** `game/ui/screens/builder/weapons_panel.py:86-111` and `game/ui/screens/builder/left_panel.py:63-79`
**Issue:** Both panels create button arrays with nearly identical pixel layout calculations and state prefix updates (`"[x] "` / `"[ ] "`).
**Impact:** Changes to button sizing, spacing, or styling require updates in multiple locations.
**Recommendation:** Extract common `ButtonGridLayout` helper that takes button specs and returns positioned buttons.
**Effort:** Medium

#### CRITICAL: Duplicated Modifier Range/Slider Logic in ModifierControlRow
**ID:** CQ-61
**Location:** `game/ui/screens/builder/modifier_row.py:236-246` and `modifier_row.py:315-323`
**Issue:** Slider enable/disable and range update appears in both `update()` and `handle_event()`. Min/max calculation and clamping logic duplicated.
**Impact:** If min/max constraints change, logic must be updated in 3+ places.
**Recommendation:** Extract `_get_local_bounds()` method for consistent min/max handling.
**Effort:** Simple

#### CRITICAL: Tooltip Detection Logic Duplicated in WeaponsPanel
**ID:** CQ-62
**Location:** `game/ui/screens/builder/weapons_panel.py:301-311` and `game/ui/screens/builder/weapons_input_handler.py:36-102`
**Issue:** Weapon bar hit detection exists in both WeaponsReportPanel.draw() and WeaponsInputHandler. Hit rect geometry calculated twice.
**Impact:** If hit detection geometry changes, must update in both places.
**Recommendation:** Centralize hit detection in WeaponsInputHandler. Have panel call single method.
**Effort:** Medium

#### MAJOR: Repeated UI Panel Bootstrap Pattern
**ID:** CQ-63
**Location:** `game/ui/screens/builder/right_panel.py:41-48`, `layer_panel.py:60-71`, `left_panel.py:23-35`
**Issue:** All three panels follow identical setup pattern: create UIPanel, add UILabel title, configure anchors.
**Impact:** Boilerplate ~10 lines per panel. Style changes require updates in 3 places.
**Recommendation:** Create `PanelFactory.create_titled_panel()` helper.
**Effort:** Simple

#### MAJOR: Button Creation for Modifier State Display
**ID:** CQ-64
**Location:** `game/ui/screens/builder/modifier_row.py:93-100` and `weapons_panel.py:115-125`
**Issue:** Both create buttons displaying checkbox-style state with identical `set_text()` update logic.
**Impact:** State display format hardcoded in multiple places.
**Recommendation:** Extract `StateButton` wrapper class with `set_checked(bool)` method.
**Effort:** Simple

#### MAJOR: Scrollable Container Setup in Three Panels
**ID:** CQ-65
**Location:** `layer_panel.py:81-88`, `left_panel.py:41-46`, `builder_widgets.py:127-133`
**Issue:** All three panels create UIScrollingContainer with nearly identical parameters and anchor configuration.
**Impact:** Bug in one scroll setup would need fixes in 3 places.
**Recommendation:** Create `ScrollContainerFactory.create_full_width_scrolling_container()`.
**Effort:** Simple

#### MAJOR: Text Entry + Slider + Button Control Pattern
**ID:** CQ-66
**Location:** `modifier_row.py:124-182` and `left_panel.py:50-85`
**Issue:** Both implement entry + step buttons + slider layout with manual pixel math using identical layout algorithm.
**Impact:** Adjusting entry width or adding/removing buttons requires updates in 2+ places.
**Recommendation:** Extract `LinearControlBuilder` class with `add_entry()`, `add_step_buttons()`, `add_slider()` methods.
**Effort:** Medium

#### MAJOR: Enable/Disable Control Groups in Modifier Row
**ID:** CQ-67
**Location:** `modifier_row.py:236-257`
**Issue:** Same enable/disable logic for entry, slider, and buttons appears in both active and inactive code paths.
**Impact:** Adding new controls requires adding enable/disable in both blocks.
**Recommendation:** Extract `_set_controls_enabled(self, enabled: bool)` method.
**Effort:** Simple

#### MAJOR: Stat Row Display Pattern Duplicated in Multiple Panels
**ID:** CQ-68
**Location:** `design_stats_panel.py:33-100` vs `detail_panel.py` vs `components.py:99-120`
**Issue:** Three different approaches to displaying component/ship statistics: StatRow (UILabels), DetailPanel (HTML), ComponentsList (string building).
**Impact:** Code reuse impossible. Three approaches for same visual task.
**Recommendation:** Standardize on StatRow approach or create unified StatDisplay class.
**Effort:** Medium

#### MAJOR: Clear/Cleanup Pattern in Multiple Panels
**ID:** CQ-69
**Location:** `modifier_row.py:184-195`, `preset_ui.py:78-84`, and 5+ other panels
**Issue:** Each panel implements its own cleanup with ad-hoc element destruction.
**Impact:** Easy to miss destroying an element. No consistent pattern.
**Recommendation:** Create `UIElementRegistry` helper with `kill_all()` method.
**Effort:** Simple

#### Minor: Offset/Position Constants Scattered Across Files
**ID:** CQ-70
**Location:** WeaponsRenderer, ModifierRow, StructureListItems, ComponentListItem
**Issue:** Layout constants defined per-class instead of centralized.
**Impact:** Hard to maintain visual consistency.
**Recommendation:** Create `BuilderConstants.py` with organized UI geometry constants.
**Effort:** Simple

#### Minor: Emoji/Unicode in Button/Label Text
**ID:** CQ-71
**Location:** `preset_ui.py:34,57,67`, `detail_panel.py:55`, `modifier_row.py:95`
**Issue:** Unicode characters used inconsistently for buttons.
**Impact:** Inconsistent UI appearance.
**Recommendation:** Create TextStyle constants.
**Effort:** Simple

#### Minor: Color Reference Pattern
**ID:** CQ-72
**Location:** WeaponsRenderer, StatRow, DetailPanel, ComponentsList
**Issue:** Different files import different subsets of colors with no central registry.
**Impact:** Hard to audit color usage.
**Recommendation:** Create `ColorTheme` class.
**Effort:** Medium

#### Minor: Layout Configuration Initialization Pattern
**ID:** CQ-73
**Location:** `panel_layout_config.py:26-30`, `detail_panel.py:24-48`, `right_panel.py:45-80`
**Issue:** Each panel calculates and caches layout rectangles differently.
**Impact:** Hard to understand panel geometry.
**Recommendation:** Standardize on DataClass configuration + __post_init__ pattern.
**Effort:** Medium

#### Minor: Event Bus Event Type Constants
**ID:** CQ-74
**Location:** `builder_utils.py:115-123` (BuilderEvents) and `weapons_panel.py:18` (WeaponsEvents)
**Issue:** Event constants scattered across multiple files.
**Impact:** Hard to audit all events.
**Recommendation:** Consolidate into unified `UIEvents` class.
**Effort:** Simple

#### Minor: Service Injection Pattern Inconsistency
**ID:** CQ-75
**Location:** `detail_panel.py`, `modifier_logic.py`, `layer_panel.py`, `right_panel.py`
**Issue:** Three different DI patterns: no DI, class-level service, constructor injection.
**Impact:** Inconsistent service access. Testing difficult.
**Recommendation:** Standardize on constructor injection.
**Effort:** Medium

#### Minor: Error Handling Pattern Duplication
**ID:** CQ-76
**Location:** `stats_config.py:368-379, 385-394, 448-470`
**Issue:** Same try-except pattern for mock object handling repeated 3+ times.
**Impact:** Duplication.
**Recommendation:** Create `safe_getattr_ship()` helper.
**Effort:** Simple

### Top 5 Priority Issues
1. **CQ-60**: Button Grid Layout Helper (CRITICAL)
2. **CQ-66**: Linear Control Builder (MAJOR)
3. **CQ-61**: Modifier Range Logic Extraction (CRITICAL)
4. **CQ-63**: Panel Bootstrap Factory (MAJOR)
5. **CQ-68**: Unified Stat Display System (MAJOR)
