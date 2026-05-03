# DRY-UI: UI Layer Duplication Analysis Report

## Summary
- **Total duplication findings:** 18
- **Critical:** 3, **Major:** 7, **Minor:** 6, **Info:** 2

## Findings

### CRITICAL: Duplicated _sanitize_object_id() Method
**ID:** CQ-101
**Location:** `game/ui/panels/base_gallery.py:215`, `game/ui/panels/race_theme_gallery.py:157`
**Issue:** Identical string sanitization utility in two panel classes.
**Recommendation:** Extract to shared utility module.
**Effort:** Simple

### CRITICAL: Panel Initialization Boilerplate (4 panels)
**ID:** CQ-102
**Location:** `race_identity_panel.py`, `race_environment_panel.py`, `race_aptitudes_panel.py`, `race_description_panel.py` (all ~lines 42-66)
**Issue:** All 4 race panels implement identical 25-line initialization pattern.
**Recommendation:** Create abstract `BaseRacePanel` with shared `__init__` and abstract `_create_content()`.
**Effort:** Medium

### CRITICAL: Section Header Creation Pattern (19 occurrences)
**ID:** CQ-103
**Location:** 19 occurrences across 6 files (environment, identity, aptitudes, description, summary, treasury panels)
**Issue:** Identical UILabel creation pattern for section headers repeated 19 times.
**Recommendation:** Create `_create_section_header(text, y, width)` utility.
**Effort:** Medium

### MAJOR: Slider Creation and Label Update Pattern (21 instances)
**ID:** CQ-104
**Location:** `race_environment_panel.py:67-225`, `race_aptitudes_panel.py:84-186`, formation_editor, new_game_setup
**Issue:** 21 instances of duplicated slider creation with value-label synchronization.
**Recommendation:** Create `SliderRow` widget wrapping UIHorizontalSlider with auto label sync.
**Effort:** Medium

### MAJOR: Text Input with Label Pattern (15+ fields)
**ID:** CQ-105
**Location:** `race_identity_panel.py:110-243`, `race_description_panel.py:65-111`
**Issue:** 15+ form fields repeat 8-line label + text input pattern.
**Recommendation:** Create `LabeledTextInput` widget wrapper.
**Effort:** Medium

### MAJOR: Dropdown Creation with Config Sync (10+ instances)
**ID:** CQ-106
**Location:** `race_identity_panel.py:150-261`, `race_environment_panel.py:144-169`
**Issue:** Duplicate dropdown setup with EMPTY_OPTION handling repeated 10+ times.
**Recommendation:** Create `ConfigDropdown` widget with built-in empty option handling.
**Effort:** Medium

### MAJOR: Gallery Button Highlight Management (3 implementations)
**ID:** CQ-107
**Location:** `base_gallery.py:219-241`, `race_theme_gallery.py:161-200`, `build_queue_selector.py:128-146`
**Issue:** Three separate button selection/highlighting implementations.
**Recommendation:** Extract `SelectableButtonGroup` widget class.
**Effort:** Medium

### MAJOR: Asset Discovery and Caching (3 galleries)
**ID:** CQ-108
**Location:** `race_flag_gallery.py:98-137`, `race_portrait_gallery.py:98-130`, `race_theme_gallery.py:127-155`
**Issue:** Three gallery classes independently implement 35-line file discovery + caching pattern.
**Recommendation:** Create `AssetDiscovery` utility with configurable path and caching.
**Effort:** Medium

### MAJOR: Format Summary Methods (12 methods)
**ID:** CQ-109
**Location:** `race_summary_panel.py:341-452`
**Issue:** 12 format methods all follow `return f"X: {self.race_config.field:.1f} {unit}"` pattern.
**Recommendation:** Create `SummaryFormatter` with configurable templates.
**Effort:** Simple

### MAJOR: Button Click Handler Pattern (3 implementations)
**ID:** CQ-110
**Location:** `base_gallery.py:249`, `race_theme_gallery.py:187`, `build_queue_selector.py:128`
**Issue:** Same button click dispatch control flow in 3 locations.
**Recommendation:** Consolidate to `SelectableItemList` base class.
**Effort:** Simple

### Minor: Text Update Boilerplate (11 occurrences)
**ID:** CQ-111
**Issue:** Repeated `set_text()` calls with f-string formatting across panels.
**Effort:** Simple

### Minor: Dropdown Value Extraction
**ID:** CQ-112
**Issue:** Custom tuple-vs-string handling for pygame_gui dropdown values.
**Recommendation:** Create `DropdownHelper` utility.
**Effort:** Simple

### Minor: Panel Update/Refresh Lifecycle
**ID:** CQ-113
**Issue:** Similar lifecycle methods (set_from_config, update_config, refresh) in multiple panels.
**Recommendation:** Create abstract lifecycle base class.
**Effort:** Minor

### Minor: Visible/Hidden Element Management
**ID:** CQ-114
**Issue:** Duplicated element cleanup/visibility logic in panel refresh methods.
**Recommendation:** Create `ElementPool` utility.
**Effort:** Simple

### Minor: Panel Width Calculation (7+ occurrences)
**ID:** CQ-115
**Issue:** `panel.get_relative_rect().width - 20` repeated in every panel's `_create_content()`.
**Recommendation:** Add property to base class.
**Effort:** Simple

### Minor: Empty Configuration Handling
**ID:** CQ-117
**Issue:** `EMPTY_OPTION = "-- Select --"` defined locally in multiple panels.
**Recommendation:** Move to shared constants module.
**Effort:** Simple

### Info: Color Definition Inconsistencies
**ID:** CQ-116
**Issue:** While `colors.py` exists, some panels still define custom colors inline.
**Recommendation:** Consolidate all UI colors into `colors.py` with semantic naming.
**Effort:** Simple

### Info: Various small patterns
**ID:** CQ-118
**Issue:** Additional minor patterns observed but individually low-impact.
**Effort:** N/A

## Top 5 Priority Consolidation Opportunities
1. **CQ-103**: Section header utility - 19 duplications across 6 files, Simple-Medium
2. **CQ-102**: BaseRacePanel class - 4 panels share identical init, Medium
3. **CQ-104**: SliderRow widget - 21 instances, Medium, Major consistency win
4. **CQ-107+CQ-110**: Gallery/selector button management - 3 implementations, Medium
5. **CQ-108**: Asset discovery utility - 3 galleries, 35-line pattern each, Medium
