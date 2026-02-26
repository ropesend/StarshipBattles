# PROJ-199: Duck Typing Cleanup - Lazy Init and CompDef Centralization

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-199` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-199 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Lazy Init — True Missing Inits | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Lazy Init — Unnecessary Guards | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. CompDef Abilities Centralization | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. ShipStatsCalculator Dual-Format Cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-25
**Active Phase:** Planning
**Last Action:** Deep code review complete — all instances verified with line numbers
**Next Action:** User approval of plan
**Blockers:** None
**Context for Next Agent:** PROJ-198 eliminated ~110+ duck typing patterns. This project handles 2 leftover categories: (1) hasattr(self, ...) lazy init patterns, (2) getattr(comp_def, 'abilities', {}) not routed through component_inspector.

## Overview
Follow-up to PROJ-198 (UI Layer Duck Typing Elimination). Addresses two specific remaining categories that PROJ-198's audit flagged as legitimate but which have clean mechanical fixes:
1. **Lazy Init** (~25 instances): `hasattr(self, 'attr')` checks where attributes should be initialized in `__init__`
2. **CompDef Centralization** (~10 instances): `getattr(comp_def, 'abilities', {})` calls that should use the canonical `get_component_abilities()` helper

## Goals
- Initialize all conditionally-set self-attributes in `__init__` (to `None`, `False`, or `[]`)
- Remove all unnecessary `hasattr(self, ...)` guards where attribute already exists
- Route all `comp_def.abilities` access through `component_inspector.get_component_abilities()`
- Add `get_component_type()` and `get_component_threshold()` helpers for remaining dual-format patterns
- Zero test regressions (baseline: 12724 passed, 1 skipped)

## Scope
**In Scope:**
- `hasattr(self, ...)` patterns in `game/app.py`, `game/ui/` (9 true lazy inits + 16 unnecessary guards)
- `getattr(comp_def, 'abilities', {})` in 6 files (8 call sites → route through helper)
- `getattr(comp_def, 'type_str'/'damage_threshold')` in `ship_stats_calculator.py` (2 call sites → new helpers)

**Out of Scope (Exempt — decided by PROJ-190 through PROJ-198):**
- `getattr(pygame, key_name)` — idiomatic module introspection
- `stats_config.py` dynamic dispatch — JSON-driven, intentional
- `planet_data_source.py` / `planet_list_filters.py` dotted-path traversal — intentional
- `component_resource_manager.py:97` `evaluated_resource_cost` — genuinely optional dynamic attr
- `ship_stats_renderer.py` Component attribute getattr — always exist, but harmless defensive code in UI renderer (low value)
- All `hasattr(event, 'ui_element')` pygame_gui patterns — appropriate for library event handling
- Ability system internals (`abilities/base.py`, `weapons.py`) — core pattern, not duck typing

## Key Files Reference
| Component | File Path | Key Info |
|-----------|-----------|----------|
| Component Inspector | `game/strategy/services/component_inspector.py` | `get_component_abilities()` — canonical helper |
| Ship Stats Calculator | `game/strategy/services/ship_stats_calculator.py` | 4 dual-format patterns (L192, L331, L339, L358) |
| Harvesting Engine | `game/strategy/engine/harvesting_engine.py` | 2 getattr calls (L75, L213) |
| Resource Mgmt Engine | `game/strategy/engine/resource_management_engine.py` | 1 getattr call (L141) |
| Resupply Engine | `game/strategy/engine/resupply_engine.py` | 1 getattr call (L159) |
| Planet | `game/strategy/data/planet.py` | 1 getattr call (L94) |
| Planet Report Panel | `game/ui/panels/planet_report_panel.py` | 1 getattr call (L516) |
| App | `game/app.py` | 2 true lazy inits (L565, L598) |
| Builder Widgets | `game/ui/panels/builder_widgets.py` | 1 true lazy init (L273) |
| Formation Editor | `game/ui/screens/formation_editor.py` | 2 true lazy inits (L778, L797) |
| Planet List Window | `game/ui/screens/planet_list_window.py` | 1 true lazy init (L366) |
| Race Setup Screen | `game/ui/screens/race_setup_screen.py` | 3 true lazy inits (L384, L389, L889) |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-25 | Scope limited to 2 categories only | PROJ-198 audit cleared remaining 113 patterns as legitimate; only lazy-init and comp_def centralization have clean mechanical fixes |
| 2026-02-25 | Split lazy init into "true missing" vs "unnecessary guard" | Different fixes: add init vs just remove hasattr |
| 2026-02-25 | Add `get_component_type()` and `get_component_threshold()` helpers | ship_stats_calculator has 2 non-abilities dual-format patterns that follow same pattern |
| 2026-02-25 | Keep `_get_numeric_value()` as-is | General-purpose dual-format getter at L459 — too broadly used to change |

## Initial Analysis

### Category 1: True Lazy Inits (9 instances)
Attributes created conditionally or late in lifecycle, never initialized in `__init__`:

| File | Line | Attribute | Fix |
|------|------|-----------|-----|
| `game/app.py` | 565 | `showing_new_game_setup` | Init to `False` |
| `game/app.py` | 598 | `return_state` | Init to `None` |
| `game/ui/panels/builder_widgets.py` | 273 | `clear_settings_btn` | Init to `None` |
| `game/ui/screens/formation_editor.py` | 778 | `rotation_mode_btn` | Init to `None` |
| `game/ui/screens/formation_editor.py` | 797 | `renumber_slider` | Init to `None` |
| `game/ui/screens/planet_list_window.py` | 366 | `last_preset_selection` | Init to `None` |
| `game/ui/screens/race_setup_screen.py` | 384 | `_ship_preview_elements` | Init to `[]` |
| `game/ui/screens/race_setup_screen.py` | 389 | `ship_preview_scroll` | Init to `None` |
| `game/ui/screens/race_setup_screen.py` | 889 | `btn_load` | Init to `None` |

### Category 2: Unnecessary Guards (16 instances)
`hasattr(self, ...)` where attribute IS initialized in `__init__` — just remove the guard:

| File | Line | Attribute | Why unnecessary |
|------|------|-----------|----------------|
| `game/ui/panels/planet_report_panel.py` | 448 | `resource_panel` | Init at L161 |
| `game/ui/panels/planet_report_panel.py` | 452 | `panel` | Init at L82 |
| `game/ui/screens/fleet_report_window.py` | 158 | `ship_detail_panel` | Init via `_init_detail_panel()` |
| `game/ui/screens/fleet_report_window.py` | 356 | `virtual_table` | Init in `_init_layout()` |
| `game/ui/screens/fleet_report_window.py` | 360 | `ship_detail_panel` | Init via `_init_detail_panel()` |
| `game/ui/screens/planet_list_window.py` | 441 | `asset_resolver` | Init param in `__init__` L43 |
| `game/ui/screens/planet_list_window.py` | 496 | `virtual_table` | Init in `_build_ui()` from `__init__` |
| `game/ui/screens/strategy_screen.py` | 338 | `session` | Init at L76 |
| `game/ui/screens/strategy_screen.py` | 339 | `session` | Init at L76 |
| `game/ui/screens/strategy_ui.py` | 212 | `system_tree` | Init from widgets in `__init__` |
| `game/ui/screens/strategy_ui.py` | 214 | `sector_tree` | Init from widgets in `__init__` |
| `game/ui/screens/strategy_window_manager.py` | 531 | `_pending_confirmation_dialog` | Init to None in `__init__` |
| `game/ui/screens/test_lab/dialogs.py` | 61 | `close_button` | Init at L51 |
| `game/ui/screens/test_lab/dialogs.py` | 194 | `confirm_button` | Init at L162 |
| `game/ui/screens/test_lab/dialogs.py` | 196 | `cancel_button` | Init at L167 |
| `game/ui/screens/transfer_dialog.py` | 158 | `lbl_debug` | Init in `_setup_ui()` |

### Category 3: CompDef Abilities Centralization (8 call sites)
All follow identical pattern — replace 2-4 lines with single `get_component_abilities()` call:

| File | Line | Current Code |
|------|------|-------------|
| `game/strategy/engine/harvesting_engine.py` | 75 | `getattr(comp_def, 'abilities', {}) or {}` |
| `game/strategy/engine/harvesting_engine.py` | 213 | `getattr(comp_def, 'abilities', {}) or {}` |
| `game/strategy/engine/resource_management_engine.py` | 141 | `getattr(comp_def, 'abilities', {}) or {}` |
| `game/strategy/engine/resupply_engine.py` | 159 | `getattr(comp_def, 'abilities', {}) or {}` |
| `game/strategy/data/planet.py` | 94 | `getattr(comp_def, 'abilities', {}) or {}` |
| `game/ui/panels/planet_report_panel.py` | 516 | `getattr(comp_def, 'abilities', {}) or {}` |
| `game/strategy/services/ship_stats_calculator.py` | 189-192 | `isinstance` check + `getattr` fallback |
| `game/strategy/services/ship_stats_calculator.py` | 336-339 | `isinstance` check + `getattr` fallback |

### Category 4: ShipStatsCalculator Non-Abilities Dual-Format (2 call sites)
Same isinstance/getattr pattern but for `type_str` and `damage_threshold`:

| File | Line | Current Code |
|------|------|-------------|
| `game/strategy/services/ship_stats_calculator.py` | 328-331 | `isinstance` → `comp_def.get('type')` else `getattr(comp_def, 'type_str')` |
| `game/strategy/services/ship_stats_calculator.py` | 355-358 | `isinstance` → `comp_def.get('damage_threshold')` else `getattr(comp_def, 'damage_threshold')` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- PROJ-198 plan — predecessor that eliminated ~110+ patterns

---

## Phases

### Phase 1: Lazy Init — True Missing Inits [Simple]
**Objective:** Add `__init__` declarations for 9 attributes that are currently set late/conditionally, then replace `hasattr` checks with direct access.
**Status:** Not Started

#### Task 1.1: App — showing_new_game_setup [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/ui/ -k app --testmon`
- [ ] Add `self.showing_new_game_setup: bool = False` in `__init__` (near L148, with other state flags)
- [ ] L565: Replace `if hasattr(self, 'showing_new_game_setup') and self.showing_new_game_setup:` with `if self.showing_new_game_setup:`
**Notes:**

#### Task 1.2: App — return_state [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/ui/ -k app --testmon`
- [ ] Add `self.return_state: Optional[GameState] = None` in `__init__` (near L148)
- [ ] L598: Replace `if hasattr(self, 'return_state') and self.return_state == GameState.TEST_LAB:` with `if self.return_state == GameState.TEST_LAB:`
**Notes:**

#### Task 1.3: BuilderWidgets — clear_settings_btn [Simple]
**File:** `game/ui/panels/builder_widgets.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`
- [ ] Add `self.clear_settings_btn = None` in `__init__` (before conditional layout code)
- [ ] L273: Replace `if hasattr(self, 'clear_settings_btn') and event.ui_element == self.clear_settings_btn:` with `if self.clear_settings_btn and event.ui_element == self.clear_settings_btn:`
**Notes:**

#### Task 1.4: FormationEditor — rotation_mode_btn & renumber_slider [Simple]
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/ui/screens/ -k formation --testmon`
- [ ] Add `self.rotation_mode_btn = None` in `__init__` or `FormationCore.__init__`
- [ ] Add `self.renumber_slider = None` in `__init__` or `FormationCore.__init__`
- [ ] L778: Replace `if hasattr(self, 'rotation_mode_btn'):` with `if self.rotation_mode_btn:`
- [ ] L797: Replace `if hasattr(self, 'renumber_slider'):` with `if self.renumber_slider:`
**Notes:** Check class hierarchy — may need to init in base class

#### Task 1.5: PlanetListWindow — last_preset_selection [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`
- [ ] Add `self.last_preset_selection = None` in `__init__`
- [ ] L366: Replace `if not hasattr(self, 'last_preset_selection'):` with `if self.last_preset_selection is None:`
**Notes:**

#### Task 1.6: RaceSetupScreen — preview elements & btn_load [Simple]
**File:** `game/ui/screens/race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k race --testmon`
- [ ] Add `self._ship_preview_elements: list = []` in `__init__`
- [ ] Add `self.ship_preview_scroll = None` in `__init__`
- [ ] Add `self.btn_load = None` in `__init__`
- [ ] L384: Replace `if hasattr(self, '_ship_preview_elements'):` with direct loop (list is always `[]` or populated): `for elem in self._ship_preview_elements: elem.kill()`
- [ ] L389: Replace `if not hasattr(self, 'ship_preview_scroll'):` with `if self.ship_preview_scroll is None:`
- [ ] L889: Replace `elif hasattr(self, 'btn_load') and self.btn_load and event.ui_element == self.btn_load:` with `elif self.btn_load and event.ui_element == self.btn_load:`
**Notes:**

#### Task 1.7: Run targeted tests [Simple]
**Tests:** `pytest tests/ --testmon`
- [ ] All affected tests pass
**Notes:**

---

### Phase 2: Lazy Init — Unnecessary Guards [Simple]
**Objective:** Remove 16 `hasattr(self, ...)` guards where the attribute is always initialized in `__init__`. Pure deletion — no new code.
**Status:** Not Started

#### Task 2.1: PlanetReportPanel [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`
- [ ] L448: Replace `if hasattr(self, 'resource_panel') and self.resource_panel:` with `if self.resource_panel:`
- [ ] L452: Replace `if hasattr(self, 'panel'):` with `if self.panel:` (or direct `self.panel.kill()` if always non-None)
**Notes:**

#### Task 2.2: FleetReportWindow [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k fleet --testmon`
- [ ] L158: Replace `if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel.process_event(event):` with `if self.ship_detail_panel and self.ship_detail_panel.process_event(event):`
- [ ] L356: Replace `if hasattr(self, 'virtual_table') and self.virtual_table:` with `if self.virtual_table:`
- [ ] L360: Replace `if hasattr(self, 'ship_detail_panel') and self.ship_detail_panel:` with `if self.ship_detail_panel:`
**Notes:**

#### Task 2.3: PlanetListWindow [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`
- [ ] L441: Replace `if hasattr(self, 'asset_resolver') and self.asset_resolver:` with `if self.asset_resolver:`
- [ ] L496: Replace `if hasattr(self, 'virtual_table'):` with `if self.virtual_table:`
**Notes:**

#### Task 2.4: StrategyScreen [Simple]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L338: Replace `self.session.player_empire if hasattr(self, 'session') else None` with `self.session.player_empire`
- [ ] L339: Replace `self.session if hasattr(self, 'session') else None` with `self.session`
**Notes:**

#### Task 2.5: StrategyUI [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L212: Replace `if hasattr(self, 'system_tree'):` with `if self.system_tree:`
- [ ] L214: Replace `if hasattr(self, 'sector_tree'):` with `if self.sector_tree:`
**Notes:**

#### Task 2.6: StrategyWindowManager [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`
- [ ] L531: Replace `hasattr(self, "_pending_confirmation_dialog")` with `self._pending_confirmation_dialog is not None`
**Notes:**

#### Task 2.7: TestLab Dialogs [Simple]
**File:** `game/ui/screens/test_lab/dialogs.py`
**Tests:** `pytest tests/unit/ui/screens/test_lab/ --testmon`
- [ ] L61: Replace `if hasattr(self, 'close_button') and self.close_button:` with `if self.close_button:`
- [ ] L194: Replace `if hasattr(self, 'confirm_button') and self.confirm_button:` with `if self.confirm_button:`
- [ ] L196: Replace `if hasattr(self, 'cancel_button') and self.cancel_button:` with `if self.cancel_button:`
**Notes:**

#### Task 2.8: TransferDialog [Simple]
**File:** `game/ui/screens/transfer_dialog.py`
**Tests:** `pytest tests/unit/ui/screens/ --testmon`
- [ ] L158: Replace `if hasattr(self, 'lbl_debug'):` with direct call `self.lbl_debug.set_text(debug_msg)` (always initialized in `_setup_ui()`)
**Notes:**

#### Task 2.9: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12724 tests pass
**Notes:**

---

### Phase 3: CompDef Abilities Centralization [Simple]
**Objective:** Route all 8 `getattr(comp_def, 'abilities', {})` call sites through the canonical `get_component_abilities()` helper in `component_inspector.py`.
**Status:** Not Started

#### Task 3.1: Harvesting Engine [Simple]
**File:** `game/strategy/engine/harvesting_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k harvest --testmon`
- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L74-75: Replace:
  ```python
  # comp_def may be dict (JSON) or Component object
  abilities = getattr(comp_def, 'abilities', {}) or {}
  ```
  With:
  ```python
  abilities = get_component_abilities(comp_def)
  ```
- [ ] L212-213: Same replacement pattern
**Notes:** The `or {}` is handled inside `get_component_abilities()` (returns `{}` for None)

#### Task 3.2: Resource Management Engine [Simple]
**File:** `game/strategy/engine/resource_management_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k resource --testmon`
- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L140-141: Replace:
  ```python
  # comp_def may be dict (JSON) or Component object
  abilities = getattr(comp_def, 'abilities', {}) or {}
  ```
  With:
  ```python
  abilities = get_component_abilities(comp_def)
  ```
**Notes:**

#### Task 3.3: Resupply Engine [Simple]
**File:** `game/strategy/engine/resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/ -k resupply --testmon`
- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L158-159: Replace:
  ```python
  # comp_def may be dict (JSON) or Component object
  abilities = getattr(comp_def, 'abilities', {}) or {}
  ```
  With:
  ```python
  abilities = get_component_abilities(comp_def)
  ```
**Notes:**

#### Task 3.4: Planet [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/ -k planet --testmon`
- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L93-94: Replace:
  ```python
  # comp_def may be dict (JSON) or Component object
  abilities = getattr(comp_def, 'abilities', {}) or {}
  ```
  With:
  ```python
  abilities = get_component_abilities(comp_def)
  ```
**Notes:** Check for circular imports — planet.py is in strategy/data, inspector is in strategy/services

#### Task 3.5: Planet Report Panel [Simple]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`
- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L515-516: Replace:
  ```python
  abilities = getattr(comp_def, 'abilities', {}) or {}
  ```
  With:
  ```python
  abilities = get_component_abilities(comp_def)
  ```
**Notes:**

#### Task 3.6: ShipStatsCalculator — Abilities Access [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/ --testmon`
- [ ] Add import: `from game.strategy.services.component_inspector import get_component_abilities`
- [ ] L188-192: Replace 4-line isinstance/getattr block:
  ```python
  # comp_def may be a dict (JSON registry) or Component object (simulation)
  if isinstance(comp_def, dict):
      abilities = comp_def.get('abilities', {}) or {}
  else:
      abilities = getattr(comp_def, 'abilities', {}) or {}
  ```
  With:
  ```python
  abilities = get_component_abilities(comp_def)
  ```
- [ ] L336-339: Same replacement
**Notes:** Same file also has Phase 4 changes — do these first

#### Task 3.7: Run targeted tests [Simple]
**Tests:** `pytest tests/ --testmon`
- [ ] All affected tests pass
**Notes:**

---

### Phase 4: ShipStatsCalculator Dual-Format Helpers [Simple]
**Objective:** Add `get_component_type()` and `get_component_threshold()` helpers to `component_inspector.py` for the remaining 2 dual-format patterns in `ship_stats_calculator.py`.
**Status:** Not Started

#### Task 4.1: Add helpers to component_inspector.py [Simple]
**File:** `game/strategy/services/component_inspector.py`
**Tests:** `pytest tests/unit/strategy/services/ --testmon`
- [ ] Add `get_component_type(comp_def: Any) -> str` function:
  ```python
  def get_component_type(comp_def: Any) -> str:
      """Extract component type string from a component definition.
      Handles dict ('type' key) vs Component object ('type_str' attr).
      """
      if comp_def is None:
          return ''
      if isinstance(comp_def, dict):
          return comp_def.get('type', '')
      return getattr(comp_def, 'type_str', '')
  ```
- [ ] Add `get_component_threshold(comp_def: Any, default: float) -> float` function:
  ```python
  def get_component_threshold(comp_def: Any, default: float) -> float:
      """Extract damage threshold from a component definition.
      Handles both dict and Component object formats.
      """
      if comp_def is None:
          return default
      if isinstance(comp_def, dict):
          return comp_def.get('damage_threshold', default)
      return getattr(comp_def, 'damage_threshold', default)
  ```
- [ ] Add both to `__all__` list
**Notes:** Follows same pattern as `get_component_abilities()`

#### Task 4.2: Update ShipStatsCalculator [Simple]
**File:** `game/strategy/services/ship_stats_calculator.py`
**Tests:** `pytest tests/unit/strategy/services/ --testmon`
- [ ] Update import to include new helpers: `from game.strategy.services.component_inspector import get_component_abilities, get_component_type, get_component_threshold`
- [ ] L327-331: Replace 4-line isinstance/getattr block:
  ```python
  if isinstance(comp_def, dict):
      comp_type = comp_def.get('type', '')
  else:
      comp_type = getattr(comp_def, 'type_str', '')
  ```
  With:
  ```python
  comp_type = get_component_type(comp_def)
  ```
- [ ] L354-358: Replace 4-line isinstance/getattr block:
  ```python
  if isinstance(comp_def, dict):
      threshold = comp_def.get('damage_threshold', DEFAULT_DAMAGE_THRESHOLD)
  else:
      threshold = getattr(comp_def, 'damage_threshold', DEFAULT_DAMAGE_THRESHOLD)
  ```
  With:
  ```python
  threshold = get_component_threshold(comp_def, DEFAULT_DAMAGE_THRESHOLD)
  ```
**Notes:**

#### Task 4.3: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All 12724 tests pass
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — 12724 passed, 1 skipped (baseline 2026-02-25)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Run `pytest tests/ -n 12` — full suite passes (after Phase 2 and Phase 4)

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Grep audit: no remaining `hasattr(self, ...)` in modified files (except exempt patterns)
- [ ] Grep audit: no remaining `getattr(comp_def, 'abilities', {})` outside `component_inspector.py`

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 complete (true lazy inits)
- [ ] Phase 2 complete (unnecessary guards)
- [ ] Phase 3 complete (abilities centralization)
- [ ] Phase 4 complete (dual-format helpers)
- [ ] All tests passing (12724 passed, 1 skipped)
- [ ] Audit passed
- [ ] User verified
