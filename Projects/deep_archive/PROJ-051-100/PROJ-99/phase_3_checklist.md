# Phase 3: Empire Panel Window

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-99 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the main EmpirePanelWindow with tab infrastructure, Treasury tab wired to the calculator/panel, Population tab with species card rendering, and a placeholder tab.

---

## Tasks

### Task 3.1: Create EmpirePanelWindow with tab infrastructure [Medium]
**File:** `game/ui/screens/empire_panel_window.py` (NEW)
**Tests:** Manual visual test after Phase 4 integration

- [x] Create new file `game/ui/screens/empire_panel_window.py`
- [x] Import `pygame`, `pygame_gui`, `UIWindow`, `UIPanel`, `UIButton`, `UILabel`, `UIImage`, `UITextBox`, `UIScrollingContainer`
- [x] Import `EmpireEconomyCalculator` from `game.strategy.engine.empire_economy_calculator`
- [x] Import `EmpireTreasuryPanel` from `game.ui.panels.empire_treasury_panel`
- [x] Import `RaceAssetLoader` from `game.ui.screens.race_asset_loader`
- [x] Import `PLANET_RESOURCES` from `game.core.constants`
- [x] Import `Paths` from `game.core.paths`
- [x] Define constants:
  - `TAB_TREASURY = 0`, `TAB_POPULATION = 1`, `TAB_MORE = 2`
  - `TAB_NAMES = ["Treasury", "Population", "More To Follow"]`
- [x] Define `EmpirePanelWindow(UIWindow)`:
  - `__init__(self, rect, manager, empire, on_close_callback=None)`:
    - Call `super().__init__(rect, manager, window_display_title="Empire Overview", resizable=False)`
    - Store `empire`, `on_close_callback`
    - Init `tab_buttons = []`, `step_panels = []`
    - Create `_asset_loader = RaceAssetLoader()`
    - Call `_load_resource_icons()` → `_resource_icons` dict
    - Call `_create_ui()`
    - Call `_show_tab(TAB_TREASURY)` (default tab)
- [x] Implement `_load_resource_icons(self) -> Dict[str, pygame.Surface]`:
  - Uses `load_resource_icons()` from empire_treasury_panel module (DRY)
- [x] Implement `_create_ui(self)`:
  - Get container and dimensions
  - Call `_create_tab_buttons(container, width)`
  - Call `_create_tab_panels(container, width, panel_top, panel_height)`
  - Reference: `race_setup_screen.py` tab creation pattern
- [x] Implement `_create_tab_buttons(self, container, width)`:
  - Calculate button width = `(width - 10) // len(TAB_NAMES)`
  - For each tab name, create UIButton at x = 10 + i * btn_width, y = 5
  - Set `btn.tab_index = i`
  - Append to `self.tab_buttons`
- [x] Implement `_create_tab_panels(self, container, width, top, height)`:
  - For each tab index, create a UIPanel with same rect
  - Append to `self.step_panels`
  - Call `_build_treasury_tab(self.step_panels[TAB_TREASURY])`
  - Call `_build_population_tab(self.step_panels[TAB_POPULATION])`
  - Call `_build_placeholder_tab(self.step_panels[TAB_MORE])`
- [x] Implement `_show_tab(self, tab_index)`:
  - Clamp to valid range
  - Hide all panels, show target panel
  - Update tab button highlighting: `btn.select()` / `btn.unselect()`
  - Store `self.current_tab = tab_index`
- [x] Implement `process_event(self, event)`:
  - Call `super().process_event(event)`
  - On `UI_BUTTON_PRESSED`: check each tab button, call `_show_tab(btn.tab_index)`
  - Return handled
- [x] Implement `kill(self)`:
  - Fire `on_close_callback()` if set
  - Call `super().kill()`

**Notes:** Reused load_resource_icons() from empire_treasury_panel for DRY.

### Task 3.2: Build Treasury tab content [Simple]
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** Manual visual test

- [x] Implement `_build_treasury_tab(self, panel)`:
  - Create `EmpireEconomyCalculator()`
  - Call `calculator.calculate(self.empire)` → snapshot
  - Create `EmpireTreasuryPanel(panel, self.ui_manager, snapshot, self._resource_icons)`
  - Store reference as `self._treasury_panel`

**Notes:**

### Task 3.3: Build Population tab content [Medium]
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** Manual visual test

- [x] Implement `_build_population_tab(self, panel)`:
  - Create UIScrollingContainer inside panel (full size minus margins)
  - Get `race_config = self.empire.race_config`
  - If race_config is None, show "No species data available" label and return
  - Call `_render_species_card(scroll_container, race_config, y_offset=10)`
- [x] Implement `_render_species_card(self, container, race_config, y_offset) -> int`:
  - **Portrait + Flag row** (y_offset):
    - Load portrait: `self._asset_loader.load_portrait_full(self.empire.portrait_id)`
    - Scale to 128x128, render as UIImage at (10, y_offset)
    - Load flag: `self._asset_loader.load_flag_full(self.empire.flag_id)`
    - Take `shapes[0]` (rectangle), scale to 96x64, render as UIImage at (150, y_offset)
    - y_offset += 140
  - **Identity section** (y_offset):
    - Header: "Identity" UILabel (bold)
    - Rows as UILabels: Faction Name, Race Name, Government Type, Government Organization, Leader (title + name), Physical Type, Society Type
    - Skip empty/missing fields
    - y_offset += row_count * ROW_HEIGHT + gap
  - **Aptitudes section** (y_offset):
    - Header: "Aptitudes" UILabel
    - Render 9 aptitudes as "Name: value" labels
    - Layout: 3 columns (3 aptitudes per row, 3 rows)
    - Aptitude names: Strength, Intelligence, Constitution, Dexterity, Species Tolerance, Cooperation, Happiness, Pop Growth, Conflict Tolerance
    - y_offset += rows * ROW_HEIGHT + gap
  - **Environment section** (y_offset):
    - Header: "Environmental Preferences" UILabel
    - Gravity: "{ideal}g (+/- {tolerance}g)"
    - Temperature: "{ideal}K (+/- {tolerance}K)"
    - Water: "{ideal*100}% (+/- {tolerance*100}%)"
    - Radiation Tolerance: "{value}"
    - y_offset += rows * ROW_HEIGHT + gap
  - **Descriptions section** (y_offset):
    - If bio_description: "Biology" header + UITextBox (read-only, ~100px height)
    - If socio_description: "Society" header + UITextBox (read-only, ~100px height)
    - y_offset += description heights + gap
  - Return final y_offset
  - Set scroll container scrollable_height to final y_offset

**Notes:** Implemented with helper methods for each section.

### Task 3.4: Build placeholder tab [Simple]
**File:** `game/ui/screens/empire_panel_window.py`
**Tests:** Manual visual test

- [x] Implement `_build_placeholder_tab(self, panel)`:
  - Create single UILabel centered in panel: "More panels coming soon..."
  - Use subdued text color

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] File `game/ui/screens/empire_panel_window.py` exists with no syntax errors
- [x] File `game/ui/panels/empire_treasury_panel.py` exists with no syntax errors
- [x] Import chain resolves correctly (no circular imports)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
