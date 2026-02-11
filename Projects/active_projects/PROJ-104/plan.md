# PROJ-104: Cyclomatic Complexity Reduction - Critical Functions

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-104` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-104 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. BuilderScreen.handle_event (CC 111→13) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. ShipStatsCalculator.calculate (CC 62→10) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. StrategyInputHandler._handle_keydown_mapped (CC 50→8) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. TargetEvaluator.evaluate (CC 49→10) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. TestRunDetailsPanel.draw (CC 47→~8) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. FormationEditorScreen.handle_event (CC 45→~10) | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Phase 4 Complete
**Last Action:** Extracted 8 rule handler methods from evaluate(), CC reduced from 49 to 10
**Next Action:** Begin Phase 5 — TestRunDetailsPanel.draw (CC 47 → ≤8)
**Blockers:** None
**Context for Next Agent:** Phase 4 complete. Start with `phase_5_checklist.md`. Run `pytest tests/unit/ui/test_lab_scene/ -x -q` after each task.
**Baseline:** 8167 tests passing, 0 failures

## Overview
Reduce cyclomatic complexity in the 6 worst functions in the codebase (all CC ≥ 40) by extracting sub-methods within the same class. No new files, no API changes, no architectural restructuring — just mechanical decomposition of monolithic methods into focused private helpers.

## Goals
- Reduce all 6 functions to CC ≤ 15 (per-method, not per-class)
- Zero test breakage — all 8167 tests pass after each phase
- No public API changes — all call sites remain untouched
- Follow existing codebase patterns (WorkshopEventRouter sub-method style)

## Scope
**In:** Extract sub-methods within each class to reduce CC of the 6 target functions
**Out:**
- Creating new files or classes (no EventRouter extraction)
- Refactoring callers or tests
- Adding new tests (unless needed to cover extracted methods)
- Touching any functions not in the 6 targets

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Sub-method extraction only, no new classes | User preference: simpler, less file churn |
| 2026-02-10 | Extract sub-methods not dispatch tables | User preference: readable, debuggable |
| 2026-02-10 | Order by CC score (highest first) | User preference: biggest wins first |
| 2026-02-10 | Keep ShipStatsCalculator main loop intact | Strict phase ordering — only extract inner logic |

## Key Files
| Component | File Path | CC Before | Target CC |
|-----------|-----------|-----------|-----------|
| BuilderScreen.handle_event | `game/ui/screens/builder/main.py:403` | 111 | ≤15 |
| ShipStatsCalculator.calculate | `game/simulation/entities/ship_stats.py:68` | 62 | ≤15 |
| StrategyInputHandler._handle_keydown_mapped | `game/ui/screens/strategy_input_handler.py:109` | 50 | ≤8 |
| TargetEvaluator.evaluate | `game/ai/target_evaluator.py:139` | 49 | ≤10 |
| TestRunDetailsPanel.draw | `game/ui/screens/test_lab/test_run_details.py:111` | 47 | ≤8 |
| FormationEditorScreen.handle_event | `game/ui/screens/formation_editor.py:522` | 45 | ≤10 |

## Swarm Findings Summary

### Architecture
- All 6 classes are leaf nodes (no subclasses override these methods)
- No circular import risks — all sub-method extraction stays within existing class
- No dynamic attribute access (`getattr`/`hasattr`) targeting internal methods
- Zero new imports needed for any extraction

### Key Patterns to Reuse
- **WorkshopEventRouter** (`game/ui/screens/workshop_event_router.py`): Already uses `_handle_panel_action()`, `_handle_button_pressed()`, `_handle_dropdown_changed()` pattern — identical to what we'll do in BuilderScreen and FormationEditor
- **Existing sub-methods**: StrategyInputHandler already has `_take_screenshot_full()`, `_take_screenshot_viewport()` extracted; FormationEditor already has `_handle_left_down()`, `_handle_left_up()`, `_handle_mouse_motion()`

### Risks Identified
1. **ShipStatsCalculator phase ordering** — Phases 1-5 must execute sequentially. Mitigation: keep main loop intact, only extract inner body logic per-phase
2. **TargetEvaluator early termination** — `required` rules return `-inf` mid-loop. Mitigation: extracted rule handlers return `(val, match)` tuple; loop still handles early exit
3. **Test patches on `_take_screenshot_*`** — Tests mock these methods. Mitigation: no rename needed, these stay as-is

### Test Coverage
| Function | Test Files | Refactor Risk |
|----------|-----------|---------------|
| BuilderScreen.handle_event | 8 files, 71 tests (integration-level) | LOW |
| ShipStatsCalculator.calculate | 3+ files, 6+ tests (direct calls) | MODERATE |
| StrategyInputHandler._handle_keydown_mapped | 2 files, 39+ tests (via handle_event) | MODERATE |
| TargetEvaluator.evaluate | 3 files, 48 tests (direct static calls) | MODERATE |
| TestRunDetailsPanel.draw | 2 files, 79 tests (logic only, not draw) | LOW |
| FormationEditorScreen.handle_event | 2 files, 60+ tests (via InputHandler) | LOW |

---

## Phases

### Phase 1: BuilderScreen.handle_event (CC 111 → ≤15) [Complex]
**Objective:** Decompose the 319-line monolithic event handler into focused sub-methods
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/ -x -q`
**Status:** Not Started

#### Task 1.1: Extract `_handle_panel_action(self, action)` [Medium]
**File:** `game/ui/screens/builder/main.py`
- [ ] Create `_handle_panel_action(self, act_type, data)` method
- [ ] Move the entire `if act_type == 'refresh_ui': ... elif act_type == 'toggle_layer': pass` block (lines 422-620) into it
- [ ] In `handle_event`, replace block with `self._handle_panel_action(act_type, data); return`
- [ ] Verify: `pytest tests/unit/builder/ -x -q`

#### Task 1.2: Extract action handlers from `_handle_panel_action` [Medium]
**File:** `game/ui/screens/builder/main.py`
- [ ] Extract `_handle_select_component_type(self, data)` — lines 427-446 (component type selection with template modifiers)
- [ ] Extract `_handle_select_group(self, data)` — lines 449-468 (group selection with multi-select)
- [ ] Extract `_handle_select_individual(self, data)` — lines 471-490 (individual selection with shift/ctrl)
- [ ] Extract `_handle_remove_group(self, data)` — lines 493-528 (remove one component from group)
- [ ] Extract `_handle_remove_individual(self, data)` — lines 531-554 (remove specific component)
- [ ] Extract `_handle_add_component(self, act_type, data)` — lines 557-606 (clone + add with validation)
- [ ] `_handle_panel_action` now just dispatches: `if act_type == 'select_component_type': self._handle_select_component_type(data)` etc.
- [ ] Verify: `pytest tests/unit/builder/ -x -q`

#### Task 1.3: Extract `_handle_button_pressed(self, event)` [Simple]
**File:** `game/ui/screens/builder/main.py`
- [ ] Create `_handle_button_pressed(self, event)` method
- [ ] Move button if/elif chain (lines 628-651) into it
- [ ] In `handle_event`, replace with `self._handle_button_pressed(event)`
- [ ] Verify: `pytest tests/unit/builder/ -x -q`

#### Task 1.4: Extract `_handle_dropdown_changed(self, event)` [Medium]
**File:** `game/ui/screens/builder/main.py`
- [ ] Create `_handle_dropdown_changed(self, event)` method
- [ ] Move dropdown if/elif chain (lines 653-708) into it
- [ ] Extract `_handle_class_dropdown(self, event)` — lines 654-670
- [ ] Extract `_handle_vehicle_type_dropdown(self, event)` — lines 672-694
- [ ] Extract `_handle_ai_dropdown(self, event)` — lines 700-708
- [ ] In `handle_event`, replace with `self._handle_dropdown_changed(event)`
- [ ] Verify: `pytest tests/unit/builder/ -x -q`

#### Task 1.5: Verify CC reduction [Simple]
- [ ] Run `radon cc game/ui/screens/builder/main.py -s -n C` — `handle_event` should be ≤15
- [ ] Run full suite: `pytest tests/ -n 12 -q`
**Notes:**

---

### Phase 2: ShipStatsCalculator.calculate (CC 62 → ≤15) [Complex]
**Objective:** Split 5-phase stat calculation into per-phase methods, preserving strict execution order
**File:** `game/simulation/entities/ship_stats.py`
**Tests:** `pytest tests/unit/entities/test_ship_stats.py tests/unit/simulation/systems/ tests/unit/strategy/ship_stats/ -x -q`
**Status:** Not Started

#### Task 2.1: Extract Phase 1 — `_phase_damage_check_and_supply(self, ship)` [Medium]
**File:** `game/simulation/entities/ship_stats.py`
- [ ] Create method returning `(component_pool, available_crew, available_life_support)`
- [ ] Move lines 132-170 (damage threshold check, crew/life support gathering) into it
- [ ] In `calculate()`, call: `component_pool, available_crew, available_life_support = self._phase_damage_check_and_supply(ship)`
- [ ] Verify: `pytest tests/unit/entities/test_ship_stats.py tests/unit/strategy/ship_stats/ -x -q`

#### Task 2.2: Extract Phase 2 — `_phase_resource_allocation(self, ship, component_pool, available_crew, available_life_support)` [Simple]
**File:** `game/simulation/entities/ship_stats.py`
- [ ] Move lines 172-203 (crew allocation, priority sort, deactivation) into it
- [ ] In `calculate()`, call the new method
- [ ] Verify tests

#### Task 2.3: Extract Phase 3 — `_phase_stats_aggregation(self, ship, component_pool)` [Complex]
**File:** `game/simulation/entities/ship_stats.py`
- [ ] Create method that returns or mutates the local accumulators
- [ ] Move lines 205-326 (ability iteration, resource/thrust/shield aggregation) into it
- [ ] Option A: Method directly sets ship properties (simplest, matches current pattern)
- [ ] Also move the warp stat accumulation into this method
- [ ] Verify: `pytest tests/unit/entities/test_ship_stats.py tests/unit/strategy/ship_stats/ -x -q`

#### Task 2.4: Extract Phase 4 — `_phase_physics_and_limits(self, ship)` [Simple]
**File:** `game/simulation/entities/ship_stats.py`
- [ ] Move lines 328-353 (inverse mass scaling, radius calculation) into it
- [ ] Include `_check_mass_limits` call
- [ ] Verify tests

#### Task 2.5: Extract Phase 5 — `_phase_sensor_defense_scores(self, ship, component_pool)` [Simple]
**File:** `game/simulation/entities/ship_stats.py`
- [ ] Move lines 355-420 (defense score, attack mods, emissive/crystalline armor, repair, resource init) into it
- [ ] Include combat endurance call
- [ ] Verify tests

#### Task 2.6: Verify CC reduction [Simple]
- [ ] Run `radon cc game/simulation/entities/ship_stats.py -s -n C` — `calculate` should be ≤15
- [ ] Run full suite: `pytest tests/ -n 12 -q`
**Notes:** The `calculate()` method becomes a ~30-line orchestrator calling 5 phase methods in order. The local import of `ResourceStorage, ResourceGeneration` stays in `calculate()`.

---

### Phase 3: StrategyInputHandler._handle_keydown_mapped (CC 50 → ≤8) [Medium]
**Objective:** Group the 30+ elif branches into category handlers
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py -x -q`
**Status:** Not Started

#### Task 3.1: Extract `_handle_fleet_mode_action(self, action)` [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
- [ ] Create method handling FLEET_MOVE, FLEET_JOIN, FLEET_COLONIZE, FLEET_TRANSFER, FLEET_DROP_CARGO, FLEET_LOAD_CARGO, FLEET_CANCEL_MODE (lines 121-168)
- [ ] Pattern: each sets `self.input_mode` if fleet selected
- [ ] Return `True` if action was handled, `False` otherwise
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py -x -q`

#### Task 3.2: Extract `_handle_superweapon_action(self, action)` [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
- [ ] Create method handling FLEET_IMPLODE_PLANET through FLEET_SELF_DESTRUCT (lines 170-198)
- [ ] Return `True` if action was handled
- [ ] Verify tests

#### Task 3.3: Extract `_handle_ui_action(self, action)` [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
- [ ] Create method handling zoom, screenshot, button-triggered actions, and cycle selection (lines 200-232)
- [ ] Return `True` if action was handled
- [ ] Verify tests

#### Task 3.4: Extract `_handle_detail_panel_action(self, action)` [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
- [ ] Create method handling DETAIL_PANEL_ORDERS, DETAIL_PANEL_FLEET_REPORT, DETAIL_PANEL_BUILD (lines 234-243)
- [ ] Return `True` if action was handled
- [ ] Verify tests

#### Task 3.5: Refactor `_handle_keydown_mapped` as dispatcher [Simple]
**File:** `game/ui/screens/strategy_input_handler.py`
- [ ] `_handle_keydown_mapped` becomes: resolve action → try each category handler in order
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py tests/unit/ui/screens/test_strategy_input_handler_transfer.py -x -q`

#### Task 3.6: Verify CC reduction [Simple]
- [ ] Run `radon cc game/ui/screens/strategy_input_handler.py -s -n C` — `_handle_keydown_mapped` should be ≤8
- [ ] Run full suite: `pytest tests/ -n 12 -q`
**Notes:**

---

### Phase 4: TargetEvaluator.evaluate (CC 49 → ≤10) [Medium]
**Objective:** Extract per-rule-type evaluation into static helper methods
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/target_evaluator/ -x -q`
**Status:** Not Started

#### Task 4.1: Extract distance rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
- [ ] Create `_eval_distance_rule(ship, candidate, rule, distance_cache)` → `(val, match)` static method
- [ ] Handles `nearest`, `farthest`, `distance` rule types (lines 176-209)
- [ ] Verify: `pytest tests/unit/ai/target_evaluator/ -x -q`

#### Task 4.2: Extract mass/size rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
- [ ] Create `_eval_mass_rule(candidate, rule)` → `(val, match)` static method
- [ ] Handles `mass`, `largest`, `smallest`, `strongest`, `weakest` (lines 211-259)
- [ ] Verify tests

#### Task 4.3: Extract speed rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
- [ ] Create `_eval_speed_rule(candidate, rule)` → `(val, match)` static method
- [ ] Handles `fastest`, `slowest` (lines 226-232)
- [ ] Verify tests

#### Task 4.4: Extract damage rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
- [ ] Create `_eval_damage_rule(candidate, rule, stat_helpers)` → `(val, match)` static method
- [ ] Handles `most_damaged`, `least_damaged` (lines 234-249)
- [ ] Verify tests

#### Task 4.5: Extract capability rule handlers [Simple]
**File:** `game/ai/target_evaluator.py`
- [ ] Create `_eval_capability_rule(ship, candidate, rule, stat_helpers, ship_capabilities_cache)` → `(val, match)` static method
- [ ] Handles `has_weapons`, `least_armor`, `pdc_arc`/`missiles_in_pdc_arc` (lines 261-300)
- [ ] Verify tests

#### Task 4.6: Refactor `evaluate` as dispatcher loop [Simple]
**File:** `game/ai/target_evaluator.py`
- [ ] `evaluate` loop becomes: get rule type → dispatch to `_eval_*` helper → check required → accumulate score
- [ ] Use a simple dict mapping rule type categories to handler methods
- [ ] Preserve `required` early termination in the loop (not in handlers)
- [ ] Verify: `pytest tests/unit/ai/target_evaluator/ -x -q`

#### Task 4.7: Verify CC reduction [Simple]
- [ ] Run `radon cc game/ai/target_evaluator.py -s -n C` — `evaluate` should be ≤10
- [ ] Run full suite: `pytest tests/ -n 12 -q`
**Notes:** All extracted methods are `@staticmethod` to match existing class pattern.

---

### Phase 5: TestRunDetailsPanel.draw (CC 47 → ≤8) [Medium]
**Objective:** Extract drawing sections into focused sub-methods
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/unit/ui/test_lab_scene/ -x -q`
**Status:** Not Started

#### Task 5.1: Extract `_draw_header_and_status(self, surface, run_record, y_offset)` → y_offset [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
- [ ] Move lines 133-145 (run info header, status PASSED/FAILED) into it
- [ ] Returns updated y_offset
- [ ] Verify: `pytest tests/unit/ui/test_lab_scene/ -x -q`

#### Task 5.2: Extract `_draw_metadata(self, surface, run_record, y_offset)` → y_offset [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
- [ ] Move lines 147-161 (seed display, ticks display) into it
- [ ] Returns updated y_offset
- [ ] Verify tests

#### Task 5.3: Extract `_draw_action_buttons(self, surface, run_record, y_offset)` → y_offset [Medium]
**File:** `game/ui/screens/test_lab/test_run_details.py`
- [ ] Move lines 163-244 (View States, Use Seed, Copy Results buttons) into it
- [ ] All 3 buttons share the same pattern: conditional display + hover + render
- [ ] Returns updated y_offset
- [ ] Verify tests

#### Task 5.4: Extract `_draw_metrics(self, surface, run_record, y_offset)` → y_offset [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
- [ ] Move lines 256-273 (metrics title + loop) into it
- [ ] Returns updated y_offset
- [ ] Verify tests

#### Task 5.5: Extract `_draw_validation_results(self, surface, run_record, y_offset)` → y_offset [Medium]
**File:** `game/ui/screens/test_lab/test_run_details.py`
- [ ] Move lines 275-389 (validation section) into it
- [ ] Further extract `_draw_single_validation(self, surface, vr, y_offset)` → y_offset for per-item rendering
- [ ] Further extract `_draw_numeric_difference(self, surface, expected, actual, status, y_offset, indent, label_width)` → y_offset for difference/percentage logic (lines 338-369)
- [ ] Returns updated y_offset
- [ ] Verify tests

#### Task 5.6: Refactor `draw` as orchestrator [Simple]
**File:** `game/ui/screens/test_lab/test_run_details.py`
- [ ] `draw()` becomes: background → title → guard → clip → call each `_draw_*` section → scrollbar
- [ ] Should be ~25-30 lines
- [ ] Verify: `pytest tests/unit/ui/test_lab_scene/ -x -q`

#### Task 5.7: Verify CC reduction [Simple]
- [ ] Run `radon cc game/ui/screens/test_lab/test_run_details.py -s -n C` — `draw` should be ≤8
- [ ] Run full suite: `pytest tests/ -n 12 -q`
**Notes:**

---

### Phase 6: FormationEditorScreen.handle_event (CC 45 → ≤10) [Medium]
**Objective:** Extract per-event-type handlers from the monolithic method
**File:** `game/ui/screens/formation_editor.py`
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py tests/unit/ui/test_formation_input_handler.py -x -q`
**Status:** Not Started

#### Task 6.1: Extract `_handle_button_pressed(self, event)` [Simple]
**File:** `game/ui/screens/formation_editor.py`
- [ ] Move button if/elif chain (lines 526-556) into it
- [ ] 14 button branches → single method
- [ ] Verify: `pytest tests/unit/builder/test_formation_editor_logic.py tests/unit/ui/test_formation_input_handler.py -x -q`

#### Task 6.2: Extract `_handle_slider_moved(self, event)` [Simple]
**File:** `game/ui/screens/formation_editor.py`
- [ ] Move slider handling (lines 558-567) into it
- [ ] Verify tests

#### Task 6.3: Extract `_handle_text_entry(self, event)` [Simple]
**File:** `game/ui/screens/formation_editor.py`
- [ ] Move text entry handling (lines 569-586) into it
- [ ] Verify tests

#### Task 6.4: Extract `_handle_mouse_button_down(self, event)` [Simple]
**File:** `game/ui/screens/formation_editor.py`
- [ ] Move MOUSEBUTTONDOWN handling (lines 602-619) into it
- [ ] Includes canvas check, renumber arrow check, right-click pan, left-click delegation
- [ ] Verify tests

#### Task 6.5: Refactor `handle_event` as dispatcher [Simple]
**File:** `game/ui/screens/formation_editor.py`
- [ ] `handle_event` becomes: process ui_manager → dispatch by event.type to `_handle_*` methods
- [ ] Keep MOUSEWHEEL (2 lines), KEYDOWN (4 lines), MOUSEBUTTONUP (5 lines), MOUSEMOTION (1 line) inline — too small to extract
- [ ] Should be ~25 lines
- [ ] Verify: `pytest tests/unit/builder/test_formation_editor_logic.py tests/unit/ui/test_formation_input_handler.py -x -q`

#### Task 6.6: Verify CC reduction [Simple]
- [ ] Run `radon cc game/ui/screens/formation_editor.py -s -n C` — `handle_event` should be ≤10
- [ ] Run full suite: `pytest tests/ -n 12 -q`
**Notes:**

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — 8167 passed ✓

### After Each Phase
- [ ] Run `radon cc <file> -s -n C` — target function CC ≤ 15
- [ ] Run `pytest tests/ -n 12 -q` — all 8167 tests pass
- [ ] No public API changes (handle_event/calculate/evaluate signatures unchanged)

### Final Verification
- [ ] Run `radon cc game/ -s -n F` — confirm all 6 targets below CC 15
- [ ] Run full test suite: `pytest tests/ -n 12` — all tests pass
- [ ] Verify no new imports added to any file
- [ ] Verify no new files created

---

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 complete — BuilderScreen CC ≤ 15
- [ ] Phase 2 complete — ShipStatsCalculator CC ≤ 15
- [ ] Phase 3 complete — StrategyInputHandler CC ≤ 8
- [ ] Phase 4 complete — TargetEvaluator CC ≤ 10
- [ ] Phase 5 complete — TestRunDetailsPanel CC ≤ 8
- [ ] Phase 6 complete — FormationEditorScreen CC ≤ 10
- [ ] All 8167 tests passing
- [ ] Audit passed
- [ ] User verified
