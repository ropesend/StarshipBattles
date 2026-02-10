# Phase 5: StrategyUI Detail Formatter [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-86 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract detail report logic from StrategyUI into a new `strategy_detail_formatter.py` class that works alongside the existing `strategy_detail_fmt.py` module-level functions. Removes ~170 lines of report formatting logic from StrategyUI.

**File:** `game/ui/screens/strategy_ui.py`
**New File:** `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_*.py tests/integration/ui/test_strategy_buttons.py -x`

---

## Tasks

### Task 5.1: Create strategy_detail_formatter.py [Medium]
**File:** `game/ui/screens/strategy_detail_formatter.py` (new)

- [ ] Create new file `game/ui/screens/strategy_detail_formatter.py`
- [ ] Create `class StrategyDetailFormatter` with constructor accepting:
  - `scene` - reference to StrategyScreen (for `current_empire`, `galaxy`, `turn_engine` access)
  - `manager` - pygame_gui.UIManager
  - `detail_panel` - UIPanel reference (container for planet report panel)
  - `widgets` - dict of UI widget references: `portrait_image`, `detail_text`, `graph_image`, `btn_raw_data`, `btn_colonize`, `btn_build_yard`, `btn_orders`, `btn_fleet_report`, `btn_build_fleet`
  - `graphs` - dict with `spectrum_graph` and `atmosphere_graph` references
  - `graph_rect` - pygame.Rect for graph positioning
- [ ] Move `show_detailed_report(self, obj, portrait_surface=None)` logic (lines 584-744) into `StrategyDetailFormatter.show_detailed_report(self, obj, portrait_surface=None)`
  - This method accesses `self.scene`, widget references, and calls formatting functions from `strategy_detail_fmt.py`
  - Store `self.current_selection` and `self.current_raw_data` on the formatter instance
  - Store `self.planet_report_panel` on the formatter instance
- [ ] Move `_compute_planet_production(self, planet)` logic (lines 539-570) into `StrategyDetailFormatter.compute_planet_production(self, planet)`
- [ ] Move `show_raw_data_popup(self)` logic (lines 572-582) into `StrategyDetailFormatter.show_raw_data_popup(self)`
- [ ] Move thin wrappers `_get_label_for_obj`, `_format_spectrum`, `_format_atmosphere_raw` (lines 527-537, 746-747) into the formatter
- [ ] Ensure imports: `pygame`, `pygame_gui`, protocol checks from `game.core.protocols`, `PlanetReportPanel`, `SpectrumGraph`, `AtmosphereGraph`, all functions from `strategy_detail_fmt`
- [ ] Add docstrings to module and class

**Notes:** `show_detailed_report` is 163 lines with a large if/elif chain for different object types. It reads `self.scene.current_empire` for ownership checks and creates `PlanetReportPanel` instances. The `planet_report_panel` lifecycle (create/kill) must be tracked on the formatter.

---

### Task 5.2: Update strategy_ui.py to delegate to detail formatter [Medium]
**File:** `game/ui/screens/strategy_ui.py`

- [ ] Add import: `from game.ui.screens.strategy_detail_formatter import StrategyDetailFormatter`
- [ ] In `StrategyUI.__init__`, after all widgets are created, instantiate the formatter:
  ```python
  self._detail_formatter = StrategyDetailFormatter(
      scene=self.scene,
      manager=self.manager,
      detail_panel=self.detail_panel,
      widgets={
          'portrait_image': self.portrait_image,
          'detail_text': self.detail_text,
          'graph_image': self.graph_image,
          'btn_raw_data': self.btn_raw_data,
          'btn_colonize': self.btn_colonize,
          'btn_build_yard': self.btn_build_yard,
          'btn_orders': self.btn_orders,
          'btn_fleet_report': self.btn_fleet_report,
          'btn_build_fleet': self.btn_build_fleet,
      },
      graphs={
          'spectrum_graph': self.spectrum_graph,
          'atmosphere_graph': self.atmosphere_graph,
      },
      graph_rect=self.graph_rect,
  )
  ```
- [ ] Replace `show_detailed_report` body with delegation:
  ```python
  self._detail_formatter.show_detailed_report(obj, portrait_surface)
  self.planet_report_panel = self._detail_formatter.planet_report_panel
  self.current_selection = self._detail_formatter.current_selection
  self.current_raw_data = self._detail_formatter.current_raw_data
  ```
- [ ] Replace `_compute_planet_production` body with delegation: `return self._detail_formatter.compute_planet_production(planet)`
- [ ] Replace `show_raw_data_popup` body with delegation: `self._detail_formatter.show_raw_data_popup()`
- [ ] Replace `_get_label_for_obj` body with delegation: `return self._detail_formatter._get_label_for_obj(obj)`
- [ ] Replace `_format_spectrum` body with delegation: `return self._detail_formatter._format_spectrum(star)`
- [ ] Replace `_format_atmosphere_raw` body with delegation: `return self._detail_formatter._format_atmosphere_raw(planet)`
- [ ] Remove now-unused imports from strategy_ui.py: `PlanetReportPanel`, `SpectrumGraph`, `AtmosphereGraph` (if only used in extracted methods), `is_star_system`, `is_star`, `is_planet`, `is_fleet`, `is_warp_point`, `is_sector_environment` (if only used in extracted methods -- check `handle_event` still uses `is_fleet`)
- [ ] Update `handle_resize` to re-initialize the formatter's graph references if needed

**Notes:** Some state (`current_selection`, `current_raw_data`, `planet_report_panel`) is read by event handlers in StrategyUI. Either sync it back after each call to `show_detailed_report` or have the event handler access it through `self._detail_formatter`.

---

### Task 5.3: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_strategy_ui_*.py tests/integration/ui/test_strategy_buttons.py -x`

- [ ] Run targeted tests for StrategyUI
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify no import errors or circular imports
- [ ] Verify line count of `strategy_ui.py` decreased by ~130+ lines
- [ ] Fix any failures discovered

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to Complete
- [ ] Update plan.md phase table row to Complete
- [ ] Update plan.md Current State to point to next phase
