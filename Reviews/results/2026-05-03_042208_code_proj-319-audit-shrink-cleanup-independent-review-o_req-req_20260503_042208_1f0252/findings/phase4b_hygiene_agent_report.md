# PROJ-319 Phase 4 Independent Review — Findings Report

**Reviewer:** Independent code-review agent  
**Date:** 2026-05-02  
**Scope:** Tasks 4.8-4.14 (DUP-X-10, DUP-X-06, DUP-X-04, DUP-X-05, DUP-X-02, DUP-X-14, DUP-X-03), project hygiene, pre-existing bugs, style checks  
**Base commit:** `1eb325608` on `main`

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 0 | — |
| HIGH     | 3 | Manifest gaps (9 files), LOC ceiling violation, sort-key duplication unresolved |
| MEDIUM   | 3 | Missing `from __future__ import annotations` in 3 new files, naming discrepancy, `_with_ship` placement |
| LOW      | 2 | Manifest lists `_compute_circular_position` but code uses `compute_circular_position`, pre-existing LLM flake |

All 7 Phase 4 consolidation tasks (4.8-4.14) are **correctly implemented** — behavior-preserving, no regressions. The issues found are hygiene/documentation gaps, not functional defects.

---

## Part A: Phase 4 Tasks 4.8-4.14 — Detailed Results

### Task 4.8: Workshop `_with_ship` helper (DUP-X-10) ✅ PASS

| Check | Result |
|-------|--------|
| Three return-type variants handled correctly? | **PASS.** `add_component` → `True` (bool), `remove_component` → `result.removed_component` (Optional[Component]), `move_component` → `True` (bool). All three use `_with_ship` with correctly-typed `on_success` lambdas. |
| add_component returns True (bool)? | **PASS.** `workshop_viewmodel_ship_ops.py:94-99`: `lambda _result: True`. |
| remove_component returns `result.removed_component`? | **PASS.** `workshop_viewmodel_ship_ops.py:150-155`: `lambda result: result.removed_component`, `on_failure=None`. |
| move_component returns True? | **PASS.** `workshop_viewmodel_layer_ops.py:206-213`: `lambda _result: True`. |
| Guard semantics: `_require_ship` returns False → `on_failure`, no service call, no notify | **PASS.** `workshop_viewmodel.py:151-152`: `if not self._require_ship(op_name): return on_failure` — returns immediately without calling `service_call` or `notify_ship_changed()`. |
| `_with_ship` placed on `WorkshopViewModel` | **PASS** (architecturally works) but see Finding H3 below. |

**Pre-/post-change comparison:** Pre-change, each of `add_component`, `remove_component`, `add_component_instance`, and `move_component` had identical 7-9 line guard→service→result→notify→warn skeletons. Post-change, all delegate to `_with_ship`. Seven service-call sites reduced to one-line delegations. Behavior identical.

### Task 4.9: Strategy event router `_open_planet_target_editor` (DUP-X-06) ✅ PASS

| Check | Result |
|-------|--------|
| Passes `window_manager=self.ui.window_manager`? | **PASS.** `strategy_event_router.py:242`: `window_manager=ui.window_manager` passed to each editor constructor. |
| Default `rect_size=(400, 300)` matches original? | **PASS.** Pre-change gravity editor used `create_centered_rect(400, 300, ...)`, water editor same, radiation editor same. Default matches all three. |
| `target_kwarg` correctly threaded? | **PASS.** `strategy_event_router.py:235`: `**{target_kwarg: target_value}` — gravity passes `"gravity_target"`, water passes `"water_target"`, radiation passes `"shielding_target"`. |
| Three wrappers pass correct classes? | **PASS.** Gravity → `GravityTargetEditor` + `SetGravityTargetCommand`, Water → `WaterTargetEditor` + `SetWaterTargetCommand`, Radiation → `RadiationShieldEditor` + `SetRadiationShieldTargetCommand`. |
| Atmosphere editor NOT using helper? | **PASS.** Atmosphere has its own `_open_atmosphere_editor` (lines 175-211) with different `rect_size=(700, 500)` and inline `race_config` resolution. This is correct — Task 4.9 only consolidated the three 400×300 editors. |

### Task 4.10: RaceConfigResolverMixin (DUP-X-04) ✅ PASS

| Check | Result |
|-------|--------|
| Mixin appears BEFORE parent base in MRO? | **PASS.** All four editors MRO: `EditorClass → PlanetTargetEditor → RaceConfigResolverMixin → StrategyModalWindow → ...`. Mixin is correctly positioned before `StrategyModalWindow`. |
| Old local `_get_active_race_config` fully deleted? | **PASS.** Grep across all four editors returns zero matches for `def _get_active_race_config`. |
| Instance attributes set in `__init__`? | **PASS.** Each editor sets `self._species_dropdown`, `self._default_race_id`, and `self.race_config` in `__init__`. |
| Resolution order correct? | **PASS.** `RaceConfigResolverMixin._get_active_race_config()` at `species_selector_mixin.py:147-163`: dropdown → default_race_id → self.race_config. Matches all four pre-change locals. |

### Task 4.11: PlanetTargetEditor base (DUP-X-05) ✅ PASS

| Check | Result |
|-------|--------|
| Base inherits `RaceConfigResolverMixin, StrategyModalWindow` in right order? | **PASS.** `planet_target_editor_base.py:27`: `class PlanetTargetEditor(RaceConfigResolverMixin, StrategyModalWindow)`. |
| All 4 editors inherit ONLY from PlanetTargetEditor? | **PASS.** AtmosphereTargetEditor(PlanetTargetEditor), GravityTargetEditor(PlanetTargetEditor), WaterTargetEditor(PlanetTargetEditor), RadiationShieldEditor(PlanetTargetEditor). |
| `_button_handlers()` overrides match original `process_event` dispatch? | **PASS.** Atmosphere: `btn_apply→_on_apply, btn_species_ideal→_set_species_ideal, btn_match_current→_set_match_current, btn_clear→_clear_target`. Gravity/Water same pattern. Radiation: `btn_apply→_on_apply, btn_auto→_set_auto, btn_clear→_clear_target`. All match pre-change dispatch. |
| Base `process_event` calls `super().process_event()`? | **PASS.** `planet_target_editor_base.py:47`: `handled = super().process_event(event)`. Falls through to `return handled` on line 61. |
| `event.ui_element is self` guard preserved? | **PASS.** `planet_target_editor_base.py:56`: `if event.ui_element is self:`. Pre-change was `if event.ui_element == self:` — `is` is stricter (identity check vs equality), but for pygame_gui UIWindow subclasses this is correct and more idiomatic. **Semantic change noted:** `==` → `is`, but functionally equivalent for this use case. |
| Returns True for handled events? | **PASS.** Button dispatch (line 52) and close handler (line 59) both return True. |

### Task 4.12: Superweapon pipeline (DUP-X-02) ✅ PASS

| Check | Result |
|-------|--------|
| `getattr(self.scene._superweapons, designation_method)` matches prior explicit calls? | **PASS.** Pre-change: `self.scene._superweapons.handle_implode_planet_designation(mx, my, self.scene.selected_fleet)`. New: `getattr(self.scene._superweapons, 'handle_implode_planet_designation')(mx, my, self.scene.selected_fleet)`. Same call, same args. |
| Five thin wrappers pass correct method names? | **PASS.** Implode → `'handle_implode_planet_designation'`, Stellerate → `'handle_stellerate_star_designation'`, OpenWarp → `'handle_open_warp_designation'`, CloseWarp → `'handle_close_warp_designation'`, Dyson → `'handle_dyson_sphere_designation'`. |
| Right-click (button==3) cancel behavior preserved? | **PASS.** `strategy_click_dispatcher.py:297-300`: `elif button == 3: self.input_mode = 'SELECT'; logger.debug("Input Mode: SELECT"); return True`. Matches all five pre-change handlers identically. |
| `_emit_validated_order` on BaseCommandHandler? | **PASS.** `game/strategy/engine/handlers/base.py:228-247`. Static method, called by all 6 direct command handlers. |
| Log format comparison (old vs new)? | **PASS.** Old: `logger.info(f"GameSession: Issued IMPLODE_PLANET order for Fleet {fleet.id}")`. New: `logger.info("GameSession: Issued %s order for Fleet %s", log_label, fleet.id)`. Rendered text is **identical**: `GameSession: Issued IMPLODE_PLANET order for Fleet 1`. |
| Behavior on `result.is_valid == False`? | **PASS.** `base.py:243-247`: `if result.is_valid:` guards order creation AND log line. Falls through to `return result`. No order added, no log. Identical to pre-change pattern. |
| `_resolve_superweapon_target` extraction from strategy_superweapons.py? | **PASS (deferred).** `decisions.md` line 16 explicitly documents this as scoped out. Not flagged. |
| Mission handlers NOT consolidated? | **PASS (deferred).** Mission handlers (e.g., `ImplodePlanetMissionCommandHandler`) still use inline f-string logging and direct `Order()` construction. Per decisions.md, this was scoped out. |

### Task 4.13: Data source base class (DUP-X-14) ✅ PASS

| Check | Result |
|-------|--------|
| `ListDataSource` base class structure? | **PASS.** `list_data_source_base.py:17-102`. Implements `ITableDataSource`, provides `get_row_count`, `get_columns`, `get_cell_value`, `get_cell_image`, `update_data(rows)`. |
| PlanetDataSource overrides only `_render_icon`? | **PASS.** `planet_data_source.py:61`: `def _render_icon(self, entity) → _get_planet_icon(entity)`. All other plumbing inherited. |
| StarDataSource overrides only `_render_icon`? | **PASS.** `star_data_source.py:38`: `def _render_icon(self, entity) → _get_star_icon(entity)`. All other plumbing inherited. |
| Legacy aliases: `_planets` → `_rows`, `_stars` → `_rows`? | **PASS.** `planet_data_source.py:57-59`: `_planets` property returns `self._rows`. `star_data_source.py:34-36`: `_stars` property returns `self._rows`. |
| `get_planet_at_index` / `get_star_at_index` delegate to `_entity_at`? | **PASS.** Both call `self._entity_at(row_index)`. |
| `update_data(rows)` compatible with old `update_data(planets)` / `update_data(stars)`? | **PASS.** Old callers passed a list; new `update_data(rows)` accepts the same list type. Binary-compatible. |

### Task 4.14: Data list window unification (DUP-X-03) ✅ PASS (with one finding)

| Check | Result |
|-------|--------|
| `DataListWindowMixin` shared methods? | **PASS.** Provides `_toggle_column`, `_save_preset`, `_sync_slider_text`. Both `PlanetListWindow` and `StarListWindow` inherit it via `class ...(DataListWindowMixin, StrategyModalWindow)`. |
| Planet list uses mixin correctly? | **PASS.** `planet_list_window.py:111`: `class PlanetListWindow(DataListWindowMixin, StrategyModalWindow)`. Uses `_toggle_column` and `_save_preset` from mixin; overrides `_capture_current_state` and `_apply_state` per subclass variation. |
| Star list uses mixin correctly? | **PASS.** `star_list_window.py:39`: `class StarListWindow(DataListWindowMixin, StrategyModalWindow)`. Same pattern. |
| Drift between planet/star accommodated? | **PASS.** Planet has effect filters + owner filters; star has type filters only. The mixin does NOT force column unification — subclasses define their own `columns`, `_capture_current_state`, `_apply_state`, and `process_event` bodies. |
| Sort-key utilities shared? | **FAIL — see Finding H2.** `planet_list_filters.py:221-233` and `star_list_filters.py:134-147` both contain identical `sort_key` inner functions. While the manifest claims this was shared (manifest line 38-39), the actual code still has two independent copies. |

---

## Part B: Project Hygiene

### Phase Checklists

| Checklist | Status | Notes |
|-----------|--------|-------|
| `phase_1_checklist.md` | Complete ✅ | All 14 tasks checked, validation passed. |
| `phase_2_checklist.md` | Complete ✅ | Both tasks checked, validation passed. |
| `phase_4_checklist.md` | Complete ✅ | All 14 tasks checked, LOC delta ~ -657 claimed. |

### Manifest Completeness

**Finding H1 (HIGH):** `manifest.md` is missing **9 files** that were modified or created by PROJ-319 commits:

**NEW files not listed:**
1. `game/ui/screens/planet_target_editor_base.py` — Task 4.11 (DUP-X-05)
2. `game/ui/screens/list_data_source_base.py` — Task 4.13 (DUP-X-14)
3. `game/ui/screens/data_list_window_mixin.py` — Task 4.14 (DUP-X-03)

**MODIFIED files not listed:**
4. `game/ui/screens/workshop_viewmodel.py` — Task 4.8 (got `_with_ship` + `_require_ship`)
5. `game/strategy/engine/handlers/base.py` — Task 4.12 (got `_emit_validated_order`)

**MODIFIED test files not listed:**
6. `tests/unit/ui/screens/test_event_log_sidebar.py` — Task 4.3 patch points
7. `tests/unit/ui/screens/test_fleet_report_sidebar.py` — Task 4.3 patch points
8. `tests/unit/ui/screens/test_fleet_report_window_multi_select.py` — Task 4.3 patch points
9. `tests/unit/ui/screens/test_planet_list_components.py` — Task 4.4 patch points

**Fix:** Add all 9 entries to `manifest.md` with correct Phase/Task/DUP-X associations.

### decisions.md — Notable Decisions Coverage

| Decision | Captured? |
|----------|-----------|
| Zero-rejection rate | **YES.** `decisions.md:12`: "Surface zero-rejection rate from verifier explicitly in design.md". Also documented in `verification_report.md:17-25`. |
| MASS_MOON re-export bug | **YES.** `decisions.md` (Task 4.1 notes) documents the re-export break and fix. Also documented in `verification_report.md:113-136` (Round 3). |
| LLM flaky timing test | **YES.** `decisions.md:14`: Pre-existing flake on Windows, `time.sleep()` resolution ~15.6ms, out of scope for PROJ-319. |
| BuildContext protocol pre-existing bug | **YES.** `decisions.md:15`: PROJ-210 removed `has_space_shipyard` from Fleet; test expects `isinstance(fleet, BuildContext)` to pass. Out of scope. |

### verification_report.md — Round 3

| Check | Result |
|-------|--------|
| Round 3 documents re-export gap? | **YES.** `verification_report.md:113-136`: Full documentation of the MASS_MOON re-export discovery during Phase 4 Task 4.1 execution, including lesson for audit-shrink skill. |

---

## Part C: Pre-existing Bug Verification

### Bug 1: `test_fleet_satisfies_build_context_protocol`

```
Result: FAILED
Root cause: PROJ-210 Phase 2 removed direct has_space_shipyard and can_build_type
            attributes from Fleet. Fleet now accesses these via fleet.capabilities.*
            The BuildContext Protocol requires has_space_shipyard as a direct
            property/attribute, which Fleet no longer exposes.
```

- Git log confirms PROJ-210 commit `a381784b5` on both `test_build_context.py` and `fleet.py`.
- Isolated test run: `AssertionError: assert False` at `isinstance(mock_fleet, BuildContext)`.
- Root cause: `BuildContext` protocol (`game/strategy/data/build_context.py:21`) requires `has_space_shipyard` property. Fleet's `has_space_shipyard` was removed by PROJ-210 (now accessed via `fleet.capabilities.has_space_shipyard`). The protocol check fails at runtime.

### Bug 2: `test_elapsed_seconds_is_monotonic_then_frozen`

```
Result: ALL 5 RUNS PASSED
```

This is an intermittent timing flake — it did NOT manifest in 5 consecutive isolation runs. This is consistent with what `decisions.md:14` documents: a pre-existing Windows timing-resolution issue (`time.sleep(0.01)` vs ~15.6ms default resolution). No PROJ-319 correlation.

---

## Part D: Style / Hygiene Checks

### D1: Layer Violations

**PASS.** All new modules respect the layered architecture:
- `planet_target_editor_base.py` — imports from `game.ui.screens.species_selector_mixin` (same tier) and `game.ui.screens.strategy_modal_window` (same tier). No upward import.
- `list_data_source_base.py` — imports only from `game.ui.components.table.data_source` (same tier).
- `data_list_window_mixin.py` — imports only `pygame_gui` (external). No game-layer imports.
- `_formation_utils.py` — imports only `math` and `pygame.math.Vector2`. No upward import.

### D2: 500-LOC Ceiling Violations

**Finding H2 (HIGH):** `planet_list_window.py` is **604 lines**, exceeding the 500-LOC ceiling. This appears pre-existing (the file already exceeded 500 lines before PROJ-319). PROJ-319 did refactor some duplication out of this file, but it remains over the ceiling.

All other new/modified files are within limit:
| File | Lines |
|------|-------|
| `planet_list_window.py` | **604** ← VIOLATION |
| `strategy_click_dispatcher.py` | 495 |
| `strategy_event_router.py` | 420 |
| `workshop_viewmodel.py` | 399 |
| `handlers/base.py` | 307 |
| `superweapon_command_handlers.py` | 278 |
| All others | < 300 |

### D3: Naked `except Exception`

**PASS.** All three new files (`planet_target_editor_base.py`, `list_data_source_base.py`, `data_list_window_mixin.py`) contain no `except Exception` blocks. The pre-existing files that use broad catches all carry `# Intentional broad catch:` comments.

### D4: `from __future__ import annotations` Mismatch

**Finding M1 (MEDIUM):** Three new Phase 4 files are missing `from __future__ import annotations`:

| File | Has `from __future__ import annotations`? |
|------|------------------------------------------|
| `game/ai/spatial_behaviors/_formation_utils.py` | **NO** |
| `game/ui/widgets/range_slider_builder.py` | **NO** |
| `game/ui/widgets/column_toggle_section.py` | **NO** |

All other new/modified production files follow the convention (the audit checked `species_selector_mixin.py`, `planet_target_editor_base.py`, `list_data_source_base.py`, `data_list_window_mixin.py`, `strategy_event_router.py`, `workshop_viewmodel.py`, `workshop_viewmodel_ship_ops.py`, `workshop_viewmodel_layer_ops.py`, `strategy_click_dispatcher.py`, `superweapon_command_handlers.py`, `handlers/base.py` — all have it). The convention in this codebase is PEP 604 syntax (`int | None`) with `from __future__ import annotations` for forward compatibility.

**Fix:** Add `from __future__ import annotations` to the three files above.

### D5: Naming Inconsistency — `compute_circular_position`

**Finding M2 (MEDIUM):** The audit recommended `_compute_circular_position` (with leading underscore indicating a private utility). The implementation uses `compute_circular_position` (without underscore). The manifest still lists `_compute_circular_position`. The Task 4.7 checklist explicitly documents the decision: "dropped the leading underscore to make it a proper public utility for sibling modules."

This is a **deliberate deviation** but creates a drift between the audit specification and implementation. If the intent is a public utility, the manifest should be updated to match. If it's genuinely private, the underscore should be restored.

**Fix:** Either update manifest to say `compute_circular_position`, or add the underscore back to the function name. The former is recommended since it matches the design intent already documented in the checklist.

### D6: Sort-Key Duplication Not Resolved

**Finding H3 (HIGH):** `planet_list_filters.py:221-233` and `star_list_filters.py:134-147` both contain an identical `sort_key` inner function inside their respective `sort_planets` and `sort_stars` functions:

```python
def sort_key(p) -> Any:     # planet variant
    if 'func' in col:
        return col['func'](p)
    elif 'attr' in col:
        attrs = col['attr'].split('.')
        obj = p
        for a in attrs:
            if hasattr(obj, a):
                obj = getattr(obj, a)
            else:
                return ""
        return obj
    return ""

def sort_key(s) -> Any:     # star variant — identical body, different param name
    if 'func' in col:
        return col['func'](s)
    elif 'attr' in col:
        attrs = col['attr'].split('.')
        obj = s
        for a in attrs:
            if hasattr(obj, a):
                obj = getattr(obj, a)
            else:
                return ""
        return obj
    return ""
```

The phase_4_checklist (Task 4.14) and manifest (lines 38-39) claim the sort-key utility was shared, but the actual code still has two independent, identical copies. This duplication was meant to be absorbed by the DUP-X-03 list-window refactor.

**Note:** The `ListDataSource._extract_value()` method (`list_data_source_base.py:78-93`) provides equivalent value-extraction logic. The `sort_key` inner functions in both filter files duplicate this same extraction pattern. A refactor could have `sort_planets`/`sort_stars` use the data source's column definitions and value extraction instead of maintaining their own copies.

**Fix:** Extract a shared `_make_sort_key(columns, column_id)` factory function (returning a callable) to a common location. Both `sort_planets` and `sort_stars` would use it. This addresses the remaining DUP-X-17 duplication.

---

## Architectural / Placement Observations

### Finding L1 (LOW): `_with_ship` placement on ViewModel

`_with_ship()` is defined on `WorkshopViewModel` (lines 129-159) rather than on `WorkshopShipOps`. Both `_ship_ops` and `_layer_ops` access it through `self._viewmodel._with_ship(...)`. This works because the helper modules already hold a reference to the viewmodel. However, the method only uses `_require_ship`, `_last_result`, `notify_ship_changed`, and `logger` — all accessible through the viewmodel reference. Placing it on `WorkshopShipOps` (or as a standalone module-level function) would be more cohesive, since it is exclusively used by the helper classes, not by the ViewModel's own methods. **No functional impact** — purely a code organization observation.

### Finding L2 (LOW): Manifest lists `_compute_circular_position` with underscore

`manifest.md:53` lists `_compute_circular_position(anchor_x, anchor_y, distance, slot_index, total)` but the implementation exports `compute_circular_position` (no underscore). The Decision column in the manifest should match the actual code. See Finding M2 above.

---

## Verification Summary

| Task | Verdict | Issues |
|------|---------|--------|
| 4.8  | ✅ PASS | — |
| 4.9  | ✅ PASS | — |
| 4.10 | ✅ PASS | — |
| 4.11 | ✅ PASS | `is` vs `==` in close guard (semantically equivalent) |
| 4.12 | ✅ PASS | Log format compatible; deferred items correctly scoped per decisions.md |
| 4.13 | ✅ PASS | — |
| 4.14 | ✅ PASS | Sort-key duplication still present (Finding H3) |
| Checklists | ✅ PASS | All phases marked Complete |
| Manifest | ❌ GAPS | 9 files missing (Finding H1) |
| Decisions | ✅ PASS | All 4 notable decisions captured |
| Verification Report | ✅ PASS | Round 3 documents re-export gap |
| Bug 1 | ✅ CONFIRMED | PROJ-210 pre-existing, fails in isolation |
| Bug 2 | ✅ CONFIRMED | LLM timing flake — all 5 runs passed (intermittent) |
| Layer violations | ✅ PASS | No violations |
| LOC ceiling | ❌ VIOLATION | `planet_list_window.py` at 604 lines (pre-existing) |
| `except Exception` | ✅ PASS | No new naked broad catches |
| `from __future__ import annotations` | ❌ MISSING | 3 files (Finding M1) |
| Naming consistency | ❌ DRIFT | `compute_circular_position` vs audit's `_compute_circular_position` (Finding M2) |

---

## Recommended Actions (Priority Order)

1. **Update `manifest.md`** — add the 9 missing files. (Finding H1)
2. **Resolve sort-key duplication** — extract shared `_make_sort_key` from `planet_list_filters.py` and `star_list_filters.py`. (Finding H3)
3. **Add `from __future__ import annotations`** to `_formation_utils.py`, `range_slider_builder.py`, `column_toggle_section.py`. (Finding M1)
4. **Fix manifest naming** — change `_compute_circular_position` → `compute_circular_position` in manifest. (Finding L2 / M2)
5. **Address `planet_list_window.py` LOC ceiling** — split into sub-modules (e.g., extract detail panel, process_event, or update logic). Pre-existing but exceeds 500-line standard.
6. **Consider moving `_with_ship` to `WorkshopShipOps`** — minor cohesion improvement. (Finding L1)
