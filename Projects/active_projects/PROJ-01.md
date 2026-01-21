# PROJ-01: Design Workshop UI Enhancement

## Overview
Refactor the Design Workshop's component modifier panel and component report to improve usability, information density, and add new features including detailed tooltips, a modifier impact grid, and JSON inspection capability.

## Goals
- Streamline modifier panel UX (modifiers only editable after component selection)
- Increase modifier visibility by compacting rows (2x more visible)
- Add detailed tooltips showing all affected values
- Add JSON inspection popup for modifiers
- Create modifier impact grid showing all effects in tabular format
- Enable scrolling for modifier panel overflow

## Scope
**In Scope:**
- ModifierEditorPanel layout and height changes
- ModifierControlRow compact redesign
- Tooltip system enhancement
- JSON popup button for modifiers
- Modifier impact grid in Component Report
- Scrollable modifier panel
- Removal of template/preset system

**Out of Scope:**
- Weapons Report changes (reference only for height)
- Component addition workflow changes (already works correctly)
- Other Design Workshop panels

## Current State
**Last Updated:** 2026-01-21 12:00
**Current Phase:** Planning - Awaiting Approval
**Last Agent Action:** Created detailed implementation plan with swarm analysis
**Next Action:** User approval, then begin Phase 1
**Blockers:** None
**Context for Next Agent:** Plan complete. Start with Phase 1, Task 1.1. All files identified, patterns documented.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-21 | Project started | User request for Design Workshop UI improvements |
| 2026-01-21 | Remove template/preset system entirely | User decision - components should always add with defaults |
| 2026-01-21 | Grid shows only affected stats | User decision - cleaner display, not all possible stats |
| 2026-01-21 | Row layout: Name + Value + Slider + JSON | User decision - compact but retain full controls |
| 2026-01-21 | Exact height match with Weapons Report | User decision - visual consistency |

## Key Files Reference

| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Workshop Screen | `game/ui/screens/workshop_screen.py` | `DesignWorkshopGUI` |
| Modifier Panel | `game/ui/panels/builder_widgets.py` | `ModifierEditorPanel` |
| Modifier Row | `ui/builder/modifier_row.py` | `ModifierControlRow` |
| Component Detail | `ui/builder/detail_panel.py` | `ComponentDetailPanel` |
| Weapons Panel | `ui/builder/weapons_panel.py` | `WeaponsReportPanel` |
| Layout Constants | `game/ui/screens/builder_utils.py` | `PANEL_HEIGHTS`, `PANEL_WIDTHS` |
| Preset UI (DELETE) | `ui/builder/preset_ui.py` | `PresetManagerUI` |
| Preset Manager (DELETE) | `game/simulation/preset_manager.py` | `PresetManager` |
| Modifier Effects | `game/simulation/components/modifier_effects.py` | `ModifierEffectEvaluator` |
| Modifier Introspection | `game/simulation/components/modifier_introspection.py` | `ModifierIntrospection` |

## Swarm Findings Summary

### Architecture
- MVVM pattern: DesignWorkshopGUI → WorkshopViewModel → EventBus → Panels
- ModifierEditorPanel tightly coupled to GUI via direct callbacks (not ideal but acceptable)
- ComponentDetailPanel loosely coupled via EventBus (good pattern to follow)
- Current modifier row height: 52px (28px controls + 20px preview + 4px spacing)

### Key Patterns to Reuse
- **JSON Popup**: `detail_panel.py:280-314` - UIWindow + UITextBox with monospace font
- **Scrollable Container**: `UIScrollingContainer` + `set_scrollable_area_dimensions()`
- **Tooltips**: `ModifierIntrospection.generate_modifier_tooltip()` already exists
- **Rotated Text**: `pygame.transform.rotate(surface, 45)` for grid headers

### Risks Identified
1. **Slider/Scroll conflict** - Must disable scroll during slider drag
2. **Row height usability** - 28px is minimum for desktop, test carefully
3. **Effect preview loss** - Moving to tooltip must preserve all info

---

## Phases

### Phase 1: Remove Template/Preset System [Medium]
**Objective:** Clean removal of preset functionality - components always add with defaults
**Status:** Not Started

#### Task 1.1: Remove PresetManagerUI from ModifierEditorPanel [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** Run `pytest tests/unit/builder/` after changes
- [ ] Remove import: `from ui.builder.preset_ui import PresetManagerUI` (line 10)
- [ ] Remove `self.preset_ui = PresetManagerUI(...)` in `__init__` (line 29)
- [ ] Remove `self.preset_ui.layout(y)` call in `layout()` method (lines 107-108)
- [ ] Remove `self.preset_ui.clear()` call (line 110)
- [ ] Remove `self.preset_ui.handle_event()` delegation in `handle_event()` (lines 171-173)
- [ ] Remove `preset_manager` parameter from `__init__` signature
**Notes:**

#### Task 1.2: Simplify ModifierEditorPanel for edit-only mode [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** Manual test - open workshop, verify panel shows message when no component selected
- [ ] Remove `self.template_modifiers = {}` instance variable usage
- [ ] Update `rebuild()` method - when `editing_component` is None, show "Select a component to edit modifiers"
- [ ] Remove "New Component Settings" header text (line 52-53)
- [ ] Change "Clear Settings" button to only show when component selected
- [ ] Update `_on_row_change()` to remove template_modifiers handling (lines 140-146)
**Notes:**

#### Task 1.3: Update Workshop Screen [Medium]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** Run `pytest tests/unit/workshop/` after changes
- [ ] Remove `self.template_modifiers = {}` (search for all occurrences)
- [ ] Remove `self.preset_manager` instantiation
- [ ] Update `ModifierEditorPanel()` constructor call - remove preset_manager param (around line 197-201)
- [ ] Update `rebuild_modifier_ui()` calls - remove template_modifiers argument
- [ ] Search for any other `template_modifiers` references and remove
**Notes:**

#### Task 1.4: Update WorkshopEventRouter [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** Run full workshop test suite
- [ ] Remove preset-related event handling (search for "preset" or "template")
- [ ] Remove `gui.template_modifiers` references (around lines 107-109)
- [ ] Remove template modifier application during drag (lines 139-150 area)
**Notes:**

#### Task 1.5: Delete preset files [Simple]
**Tests:** Run full test suite to ensure no import errors
- [ ] Delete file: `ui/builder/preset_ui.py`
- [ ] Delete file: `game/simulation/preset_manager.py`
- [ ] Delete test file: `tests/unit/builder/test_preset_manager.py` (if exists)
- [ ] Search codebase for any remaining imports of deleted files
- [ ] Run `pytest` to verify no import errors
**Notes:**

---

### Phase 2: Compact Modifier Row Layout [Complex]
**Objective:** Reduce row height from 52px to ~28px, move effect preview to tooltip, add JSON button
**Status:** Not Started

#### Task 2.1: Update ModifierControlRow height and remove effect preview [Medium]
**File:** `ui/builder/modifier_row.py`
**Tests:** `pytest tests/unit/entities/test_modifier_row.py`
- [ ] Change `self.height = 52` to `self.height = 28` (line 31)
- [ ] Remove `self.effect_preview_label` creation in `_build_linear_controls()` (lines 186-194)
- [ ] Remove `effect_preview_label` from `self.ui_elements` list
- [ ] Remove `effect_preview_label` update in `update()` method (lines 284-287)
- [ ] Remove `_generate_effect_preview()` method (lines 59-97) - moving to tooltip
**Notes:**

#### Task 2.2: Remove toggle button prefix, simplify to just name [Simple]
**File:** `ui/builder/modifier_row.py`
**Tests:** Manual visual test
- [ ] Change toggle button text from `f"[{check_char}] {self.mod_def.name}"` to just `f"{self.mod_def.name}"` (line 109, 243)
- [ ] Consider renaming `toggle_btn` to `name_btn` or `label_btn` for clarity
- [ ] Remove toggle handling in `handle_event()` - modifiers are always active (lines 301-310)
- [ ] Remove `is_active` state tracking if no longer needed
**Notes:** All visible modifiers are always applied to selected component

#### Task 2.3: Update row layout for compact design [Medium]
**File:** `ui/builder/modifier_row.py`
**Tests:** Manual visual test - verify all controls fit and align
- [ ] Adjust control positions in `build_ui()` and `_build_linear_controls()`:
  - Name label: 150px width (was 170px toggle button)
  - Value entry: 50px width (was 60px)
  - Slider: dynamic width (remaining space minus JSON button)
  - JSON button: 28px at end (NEW)
- [ ] Remove or reduce step buttons if space constrained (optional per user feedback)
- [ ] Ensure vertical centering of all controls in 28px height
**Notes:**

#### Task 2.4: Enhance tooltip with full effect details [Medium]
**File:** `ui/builder/modifier_row.py`
**Tests:** Manual test - hover over modifier, verify tooltip shows all effects
- [ ] Update `_generate_tooltip()` method to include:
  - Modifier name and description
  - Current parameter value
  - ALL affected stats with calculated values (not just first 3)
  - Formula for each effect
  - Target ability if applicable
- [ ] Format tooltip for readability:
  ```
  === Hardened Mount ===
  HP increases as square of mass multiplier

  Current Value: 2.00

  Effects:
    mass_mult: x2.00 (formula: param)
    hp_mult: x4.00 (formula: param^2)
    cost_mult: x2.00 (formula: param)
  ```
- [ ] Use `ModifierIntrospection.generate_modifier_tooltip()` as base, enhance if needed
**Notes:**

#### Task 2.5: Add JSON popup button [Medium]
**File:** `ui/builder/modifier_row.py`
**Tests:** Manual test - click JSON button, verify popup shows modifier definition
- [ ] Add `self.json_btn` UIButton in `_build_linear_controls()`:
  - Position: right edge of row
  - Size: 28x28
  - Text: `"{ }"` or info icon
- [ ] Add to `self.ui_elements` list
- [ ] Add to `self.buttons` dict with action `'show_json'`
- [ ] Create `show_modifier_json_popup()` method:
  - Get modifier definition dict from `self.mod_def`
  - Use `json.dumps(mod_def.__dict__, indent=4)` or similar
  - Create UIWindow with UITextBox (copy pattern from `detail_panel.py:280-314`)
  - Use monospace font for JSON display
- [ ] Handle button click in `handle_event()` to call popup method
**Notes:**

#### Task 2.6: Update ModifierEditorPanel for new row heights [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** Manual test - verify rows don't overlap, spacing is correct
- [ ] Verify `layout()` method uses `row.height` correctly (line 96)
- [ ] Adjust any hardcoded spacing values if needed
- [ ] Test with component that has many modifiers
**Notes:**

---

### Phase 3: Scrollable Modifier Panel [Medium]
**Objective:** Add scrolling when modifiers exceed panel height
**Status:** Not Started

#### Task 3.1: Wrap modifier rows in UIScrollingContainer [Medium]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** Manual test - add component with many modifiers, verify scroll appears
- [ ] Create `self.scroll_container = UIScrollingContainer(...)` in appropriate location
- [ ] Set scroll container as parent for ModifierControlRow instances
- [ ] Update `_ensure_row()` to use scroll_container as container parameter
- [ ] Calculate and set scrollable area dimensions after all rows added:
  ```python
  total_height = sum(row.height for row in self.modifier_rows.values())
  self.scroll_container.set_scrollable_area_dimensions((width, total_height))
  ```
**Notes:**

#### Task 3.2: Handle scroll/slider conflict [Medium]
**File:** `ui/builder/modifier_row.py` and `game/ui/panels/builder_widgets.py`
**Tests:** Manual test - drag slider while scrolling, verify no conflict
- [ ] Add `self.slider_dragging = False` flag to ModifierControlRow
- [ ] Set flag True on `UI_HORIZONTAL_SLIDER_MOVED` event start
- [ ] Set flag False on slider release (may need to track mouseup)
- [ ] In ModifierEditorPanel, check if any row has slider_dragging before allowing scroll
- [ ] Alternative: Disable scroll container during any slider interaction
**Notes:** This is a known pygame_gui issue - sliders in scroll containers can conflict

#### Task 3.3: Preserve scroll position on rebuild [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** Manual test - scroll down, change modifier, verify position maintained
- [ ] Before rebuild, cache: `saved_scroll = self.scroll_container.vert_scroll_bar.scroll_position` (if exists)
- [ ] After layout complete, restore: `self.scroll_container.vert_scroll_bar.set_scroll_from_start_percentage(saved_scroll)`
- [ ] Handle case where scroll container doesn't exist yet
**Notes:**

---

### Phase 4: Height Synchronization with Weapons Report [Medium]
**Objective:** Match modifier panel height exactly to Weapons Report
**Status:** Not Started

#### Task 4.1: Create shared height calculation function [Medium]
**File:** `game/ui/screens/builder_utils.py`
**Tests:** Unit test the calculation function
- [ ] Add function `calculate_bottom_panel_height(screen_height, num_weapons=None)`:
  ```python
  def calculate_bottom_panel_height(screen_height: int) -> int:
      """Calculate height for bottom panels (weapons report, modifier panel)."""
      # Base calculation - both panels should be same height
      available = screen_height - PANEL_HEIGHTS.bottom_bar
      # Return reasonable height, perhaps 40% of available or fixed max
      return min(400, int(available * 0.4))
  ```
- [ ] Update `PANEL_HEIGHTS` dataclass if needed
- [ ] Export function for use by workshop_screen
**Notes:**

#### Task 4.2: Update workshop_screen to use shared height [Medium]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** Manual test - verify both panels are same height
- [ ] Import `calculate_bottom_panel_height` from builder_utils
- [ ] Remove hardcoded `360` for modifier panel height (around line 152)
- [ ] Use shared calculation for both modifier panel and weapons report positioning
- [ ] Verify horizontal alignment of both panels
**Notes:**

#### Task 4.3: Handle dynamic height changes (optional) [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** Manual test - toggle weapon filters, verify layout stable
- [ ] If weapons report changes height due to filters, recalculate modifier panel
- [ ] Add debounce (100ms) to prevent layout thrashing
- [ ] Or: Use fixed height regardless of weapons shown (simpler)
**Notes:** May be optional depending on weapons panel behavior

---

### Phase 5: Modifier Impact Grid in Component Report [Complex]
**Objective:** Add grid showing how modifiers affect component stats
**Status:** Not Started

#### Task 5.1: Add data methods to Component class [Medium]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_components.py` + new tests
- [ ] Add method `get_all_modifier_effects() -> List[ModifierEffect]`:
  ```python
  def get_all_modifier_effects(self):
      """Get all evaluated effects from all applied modifiers."""
      all_effects = []
      for app_mod in self.modifiers:
          effects = app_mod.definition.evaluate_effects(app_mod.value)
          all_effects.extend(effects)
      return all_effects
  ```
- [ ] Add method `get_modifier_stat_summary() -> Dict`:
  ```python
  def get_modifier_stat_summary(self):
      """Get summary grouped by stat with net values and contributors."""
      # Returns: {stat_key: {'net_value': float, 'effects': [...], 'operation': str}}
  ```
- [ ] Write unit tests for both methods
**Notes:**

#### Task 5.2: Create ModifierImpactGrid widget [Complex]
**File:** `game/ui/panels/modifier_impact_grid.py` (NEW FILE)
**Tests:** Unit tests for grid rendering
- [ ] Create new file with class `ModifierImpactGrid`
- [ ] Constructor takes: `manager, container, rect, component`
- [ ] Layout structure:
  - Header row with rotated stat names (45 degrees)
  - One row per modifier showing effect values
  - Bottom row showing net multiplier for each stat
- [ ] Implement `pygame.transform.rotate(text_surface, 45)` for headers
- [ ] Fixed column width (50-60px) with text truncation
- [ ] Support for horizontal scrolling if many stats
- [ ] Method `update(component)` to refresh with new component data
**Notes:** Only show columns for stats that are actually affected (user decision)

#### Task 5.3: Integrate grid into ComponentDetailPanel [Medium]
**File:** `ui/builder/detail_panel.py`
**Tests:** Manual test - select component, verify grid appears in report
- [ ] Import `ModifierImpactGrid`
- [ ] Add grid section at end of component report (after existing content)
- [ ] Add section header: "── Modifier Impact ──"
- [ ] Create grid instance in `__init__` or lazily on first use
- [ ] Update grid in `show_component()` method
- [ ] Subscribe to `SHIP_UPDATED` event to refresh grid when modifiers change
- [ ] Handle case where component has no modifiers (hide grid or show message)
**Notes:**

#### Task 5.4: Add grid scrolling if needed [Simple]
**File:** `game/ui/panels/modifier_impact_grid.py`
**Tests:** Manual test - component with many modifiers/stats
- [ ] Wrap grid content in UIScrollingContainer
- [ ] Enable both horizontal and vertical scrolling
- [ ] Consider freezing first column (modifier names) - may be complex
- [ ] Set reasonable max height before scroll activates
**Notes:**

---

## Verification Checklist

### After Each Phase
- [ ] Run `pytest tests/unit/` - all tests pass
- [ ] Manual test in Design Workshop - no crashes
- [ ] Verify no console errors/warnings

### Final Verification
- [ ] Open Design Workshop
- [ ] Select component with multiple modifiers
- [ ] Verify modifier panel height matches Weapons Report
- [ ] Verify modifier panel scrolls when full
- [ ] Verify JSON button shows modifier JSON popup
- [ ] Verify tooltip shows full effect details
- [ ] Verify Component Report shows modifier impact grid
- [ ] Verify grid shows only affected stats with rotated headers
- [ ] Load existing ship design - verify modifiers preserved
- [ ] Test drag-and-drop new component - verify defaults applied
- [ ] Run full test suite: `pytest`

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
