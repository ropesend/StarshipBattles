# Shard 12 Test Coverage Audit — Findings

**Auditor**: Discovery Agent (OpenCode)  
**Date**: 2026-05-04  
**Production files**: 41 | **Estimated LOC**: ~8708  
**Skeptical verification**: Not run (Discovery phase only)

---

## Summary

| Severity  | Count | Description |
|-----------|-------|-------------|
| CRITICAL  | 1     | Core-layer Protocol with zero tests |
| MAJOR     | 2     | Untested production classes (UI editors/registrars, >80 LOC) |
| MINOR     | 5     | Partially tested modules, matrix false-negatives, untested private helpers |
| ADVISORY  | 7     | `__init__.py` / rendering / config-only files |
| **TIER 3 Verified** | **7** | Adequate test coverage confirmed |

**Overall assessment**: One CRITICAL gap (Core `ISerializable` Protocol). Two MAJOR gaps (UI editor + registrar, both 0 tests). Seven Tier-3 files verified as well-covered. The remaining Tier-2 files mostly have good indirect coverage; untested symbols are private helpers or trivial property wrappers.

---

## Tier 0 — CRITICAL & MAJOR Gaps

### CRITICAL: `game/core/protocols/persistence.py` (27 LOC)

**Status**: Tier 0 — NO tests exist. 0/3 symbols untested.  
**Impact**: `ISerializable` Protocol defines the serialization contract (`to_dict`, `from_dict`) used by battle state dataclasses (`ComponentState`, `ShipState`, `ProjectileState`, `BattleState`, `BattleResults`). This is a foundational architecture contract in the Core layer. Zero test coverage means there is no lock against accidental Protocol signature drift — a renamed method or changed return type would silently break all implementors.  
**Recommendation**: Create `tests/unit/core/protocols/test_persistence.py` with at minimum:
- Structural Protocol conformance tests (verify a conforming class passes `isinstance(obj, ISerializable)`)
- Negative tests (a class missing `to_dict` or `from_dict` should fail `isinstance`)
- Verify the `@runtime_checkable` decorator works as expected

### MAJOR: `game/ui/screens/radiation_shield_editor.py` (231 LOC)

**Status**: Tier 0 — NO tests exist. 0/8 symbols: `RadiationShieldEditor`, `__init__`, `_build_ui`, `update`, `_button_handlers`, `_on_apply`, `_set_auto`, `_clear_target`.  
**Impact**: Full editor window with slider range logic, Auto/Clear/Apply buttons, species selector integration. The `_set_auto` method reads `race_config.preferences["radiation"].setpoint` and clamps to `[0.0, 2.0]` — if the clamp range or preference lookup changes silently, the editor would malfunction. 231 LOC of untested UI logic.  
**Recommendation**: Create `tests/unit/ui/screens/test_radiation_shield_editor.py` using the bypass-init pattern. Test: `_set_auto` clamping behavior, `_on_apply` fires callback with correct planet_id+shielding tuple, `_clear_target` fires with `None`, slider range correctness.

### MAJOR: `game/ui/screens/strategy_windows/empire_panel_ctrl.py` (82 LOC)

**Status**: Tier 0 — NO tests exist. 0/8 symbols: `EmpirePanelRegistrar`, `SettingsRegistrar`, and all their methods.  
**Impact**: Contains two registrar classes (`EmpirePanelRegistrar.open`, `SettingsRegistrar.open`) that create modal windows with DI wiring (registries, race_registry resolution). The `open` methods kill existing windows, compute layout rects, and call into `EmpirePanelWindow`/`SettingsWindow` constructors. No test for any of this.  
**Recommendation**: Create `tests/unit/ui/screens/test_empire_panel_ctrl.py`. Test: `EmpirePanelRegistrar.open` kills existing window if present, passes correct rect dimensions, calls `_on_closed` resets the composer slot.

### MINOR (Matrix False-Negative): `game/app_bootstrap.py` (281 LOC)

**Status**: Matrix says Tier 0, but 2 test files exist (`test_app_bootstrap_invariants.py` 211 lines, `test_app_bootstrap_profiling.py` 115 lines). 0/6 symbols in matrix but all functions are exercised via the integration-style `bootstrap()` call.  
**Impact**: The AST scanner could not resolve imports from `game.app_bootstrap` as tested (tests import from `game.app_bootstrap` but patch heavily). Individual helpers like `_detect_resolution`, `parse_args`, `configure_logging` are only tested through integration — no direct unit tests. This is low-risk (startup code naturally exercises them).  
**Recommendation**: No action required. Tests exist and validate the 6 initialization-order invariants + 14 profiling phases. The matrix just needs a `candidate_test_files` entry for the 2 test files.

### MINOR (Matrix False-Negative): `game/ui/screens/test_lab/renderer/_condition_logic.py` (136 LOC)

**Status**: Matrix says Tier 0, but `tests/unit/ui/screens/test_lab/test_renderer_pure_functions.py` (159 lines) exercises both `format_check_pair` and `is_condition_verified`. The test calls them via class-attribute aliases on `TestLabRenderer` (`TestLabRenderer._format_check_pair`, `TestLabRenderer._is_condition_verified`), which the AST scanner could not link back to `_condition_logic.py`.  
**Impact**: Both functions are well-tested — the matrix is a false negative.  
**Recommendation**: No test changes needed. The extracted file header correctly documents the coverage path via the orchestrator class-attribute aliases. The matrix entry needs `candidate_test_files` updated.

---

## Tier 1–2 — Partial Coverage Analysis

### `game/core/formula_evaluator.py` (413 LOC) — MINOR gap

**Matrix**: 6/7 symbols tested. Untested: `_eval_node` (private AST walker, tested indirectly via `evaluate`).  
**Test file**: `tests/unit/core/test_formula_evaluator.py` (139 lines) — covers arithmetic, variables, math functions, comparisons, power, caret substitution, ternary (ifexp), validation, security, safe_evaluate.  
**Gap**: The `ast.List` and `ast.Tuple` node handlers in `_eval_node` have no explicit test exercising list/tuple literal evaluation in formulas. The `FormalContext` dataclass is untested as an independent unit (exercised via `evaluate(..., formula_context=...)`).  
**Severity**: MINOR — the untested code paths are defensive branches for AST nodes that rarely appear in real formulas.

### `game/strategy/adapters/simulation_adapter.py` (449 LOC) — MINOR gap

**Matrix**: 4/9 symbols tested. Untested: `_run_simulated_battle`, `_resolve_seed`, `_build_spec`, `_build_capture_context`, `_instances_to_ships`.  
**Test file**: `tests/unit/strategy/adapters/test_simulation_adapter.py` (338 lines) — covers `resolve_battle` (sole-survivor, no-ships, truncated-no-capable, simulator branches), `_determine_winner` (SURVIVED win, DERELICT win, draw, all-wiped).  
**Gap**: Private helpers are exercised indirectly through the public `resolve_battle` method, but:
- `_build_capture_context` (PROJ-312 replay capture) — not tested for empire/sector extraction from fleet attributes, `ShipInstanceSerializer` fallback on exception
- `_resolve_seed` — not tested for the `hasattr` branch (creating `_seed_rng` on first call)
- `_instances_to_ships` — not tested for the list comprehension calling `inst.to_ship(...)`  
**Severity**: MINOR — the critical paths are tested; the untested paths are wiring helpers.

### `game/strategy/data/habitability_factors.py` (384 LOC) — MINOR gap

**Matrix**: 5/10 symbols tested. Untested: `_make_scalar_extractor` (closure factory), inner `extract` closure, `_make_gas_extractor`, inner `extract` closure, `_build_gas_factors`.  
**Test file**: `tests/unit/strategy/data/test_habitability_factors.py` (375 lines) — exhaustive registry shape tests (7 scalar + 10 gas), partition invariants, default bounds, extractor behavior, scorer edge cases, `get_factor`/`iter_scalar_factors`/`iter_gas_factors`.  
**Gap**: Factory closures are not independently unit-testable; they're exercised by the registry construction + extractor tests on the built `FACTOR_REGISTRY`. The `_build_gas_factors` N2 default_setpoint bug-fix (2026-04-18) is tested indirectly via `test_all_defaults_within_bounds` and `test_scalar_and_gas_partitions_are_disjoint_and_cover_registry`.  
**Severity**: MINOR — no actionable gap; the registry-level tests provide adequate coverage.

### `game/strategy/data/ship_instance.py` (787 LOC) — MINOR gap

**Matrix**: 39/55 symbols tested. Untested: mostly property wrappers (`hull_class`, `ship_name`, `serial_number`, `__post_init__`, `__hash__`, etc.) and legacy helpers (`_lookup_design_max_hp`, `get_damaged_components_by_layer`).  
**Test files**: 5 files (`test_ship_instance_damage.py`, `test_ship_instance_serializer.py`, `test_ship_instance_bridge.py`, `test_ship_instance_roundtrip.py`, `test_ship_instance_components.py`).  
**Gap**: `_lookup_design_max_hp` has unreachable fallback logic (accesses `get_default_registry_provider()` bypass) that only fires when `self._registries` is None — a state that should never occur under PROJ-211 DI. `get_damaged_components_by_layer` builds a comp_id_to_layer mapping and filters per-instance components — no direct test.  
**Severity**: MINOR — the untested methods are either trivial accessors or legacy fallbacks. The core create/repair/consume/to_ship/from_dict paths are well-covered.

### `game/strategy/engine/planet_action_engine.py` (387 LOC) — MINOR gap

**Matrix**: 3/16 symbols tested (many false-negatives; private methods tested indirectly).  
**Test file**: `tests/unit/strategy/engine/test_planet_action_engine.py` (438 lines) — exhaustive tests for activation, deactivation, cancel, phase-guard rejection, facility existence checks, event-bus emission, energy drain, deactivation time.  
**Gap**: Most untested symbols are private helpers (`_process_planet_tick`, `_execute_order`, `_initiate_activation`, `_initiate_deactivation` etc.) that are exercised via `process_planet_actions_tick`. The directly untested public surface is small: `_resolve_component_key` with the composite-key path (vs fallback lookup) and `_get_deactivation_time` with different ability data shapes.  
**Severity**: MINOR — the 438-line test file provides thorough indirect coverage.

### `game/strategy/engine/planet_modifier_effect_engine.py` (96 LOC) — MINOR gap

**Matrix**: 2/7 symbols tested (private methods tested indirectly).  
**Test file**: `tests/unit/strategy/engine/test_planet_modifier_effect_engine.py` (239 lines) — covers gravity apply/revert/no-change, radiation apply/revert, MagicMock guard, `_has_active_ability` lookup.  
**Gap**: Untested symbols are private helpers exercised via `process_modifier_effects_tick`. The `_has_active_ability` method converting dict states to `ComponentActivationState` has no direct test for the dict-branch.  
**Severity**: MINOR — indirect coverage is thorough.

### `game/ui/screens/keybindings_scene.py` (582 LOC) — MINOR gap

**Matrix**: 11/25 symbols tested.  
**Test file**: `tests/unit/ui/screens/test_keybindings_scene.py` (281 lines) — IScene protocol compliance, action list display, key capture, conflict detection, save/reset/close.  
**Gap**: Private UI construction methods (`_build_ui`, `_build_action_rows`, `_build_action_row`, `_build_footer`, `_clear_ui`) are tested indirectly via scene creation but have no targeted tests. The `_draw_capture_overlay` and `_refresh_all_rows` methods are untested.  
**Severity**: MINOR — core behaviors (capture, conflict, save, reset) are covered. Untested methods are UI layout helpers.

### `game/ui/screens/strategy_detail_formatter.py` (454 LOC) — MINOR gap

**Matrix**: 4/25 symbols tested.  
**Test file**: `tests/unit/ui/screens/test_strategy_detail_formatter.py` (400 lines) — init, `show_detailed_report` dispatch (star, planet, fleet, warp point, storm, sector environment, null), planet report panel management, planet-ability checks, `__getattr__` delegation, `show_raw_data_popup`.  
**Gap**: Many untested symbols are private formatting methods (`_format_star`, `_format_fleet`, `_format_warp_point`, `_format_storm`, `_format_sector_environment`, `_format_star_system`) that are called by `show_detailed_report` and tested indirectly. The `_layout_action_buttons` method (calculates button widths from text) is untested directly.  
**Severity**: MINOR — the 400-line test file covers the dispatch logic thoroughly.

---

## Tier 3 — Verified as Adequately Covered

These 7 files have all symbols matched to test files and verified:

| File | LOC | Symbols | Test files | Notes |
|------|-----|---------|------------|-------|
| `game/research/data/tech_node.py` | 158 | 9/9 | `test_tech_node.py` | Tech requirement resolution, status checks, price curves |
| `game/simulation/combat/boundary.py` | 221 | 21/21 | `test_boundary.py`, `test_boundary_retreat.py` | RectBoundary, CircleBoundary, UnboundedRegion, ExitPolicy |
| `game/simulation/entities/ship_design_stats.py` | 111 | 1/1 | `test_ship_design_stats.py` | `calculate_design_stats` fully covered |
| `game/simulation/entities/ship_loader.py` | 174 | 4/4 | `test_ship_loader.py` (30 test files matched) | Vehicle class loading, validator creation, ship data init |
| `game/strategy/services/fleet_speed_calculator.py` | 189 | 6/6 | `test_fleet_speed_calculator.py`, `test_fleet_speed_invariants.py` | Ship/fleet speed, tick interval, multipliers |
| `game/ui/screens/strategy_screen_composition.py` | 114 | 18/18 | `test_strategy_screen_composition.py` | All 8 `make_*` factory methods + mock fixture |
| `game/ui/screens/workshop_context.py` | 153 | 6/6 | `test_workshop_context.py` (177 lines) | Standalone/integrated modes, factory methods |

---

## File Coverage Verification

| # | Production File | LOC | Tier | Test Files Exist? | Verified |
|---|----------------|-----|------|-------------------|----------|
| 1 | `game/app_bootstrap.py` | 281 | 0* | Yes (2) | MATRIX FALSE-NEG |
| 2 | `game/core/formula_evaluator.py` | 413 | 2 | Yes (2) | OK — minor gaps |
| 3 | `game/core/protocols/__init__.py` | 151 | 1 | Indirect (18) | ADVISORY (re-export) |
| 4 | `game/core/protocols/persistence.py` | 27 | 0 | **NO** | **CRITICAL** |
| 5 | `game/research/data/tech_node.py` | 158 | 3 | Yes | VERIFIED |
| 6 | `game/services/__init__.py` | 13 | 0 | No | ADVISORY (docstring) |
| 7 | `game/simulation/combat/__init__.py` | 20 | 1 | Indirect (2) | ADVISORY (re-export) |
| 8 | `game/simulation/combat/boundary.py` | 221 | 3 | Yes (2) | VERIFIED |
| 9 | `game/simulation/entities/ship_design_stats.py` | 111 | 3 | Yes | VERIFIED |
| 10 | `game/simulation/entities/ship_loader.py` | 174 | 3 | Yes | VERIFIED |
| 11 | `game/strategy/adapters/simulation_adapter.py` | 449 | 2 | Yes | OK — minor gaps |
| 12 | `game/strategy/data/habitability_factors.py` | 384 | 2 | Yes | OK — minor gaps |
| 13 | `game/strategy/data/order_serializer.py` | 231 | 2 | Yes (408 lines) | OK — thorough |
| 14 | `game/strategy/data/ship_cargo_manager.py` | 117 | 2 | Yes (156 lines) | OK — thorough |
| 15 | `game/strategy/data/ship_instance.py` | 787 | 2 | Yes (5 files) | OK — thorough |
| 16 | `game/strategy/engine/planet_action_engine.py` | 387 | 2 | Yes (438 lines) | OK — thorough |
| 17 | `game/strategy/engine/planet_modifier_effect_engine.py` | 96 | 2 | Yes (239 lines) | OK — thorough |
| 18 | `game/strategy/services/fleet_speed_calculator.py` | 189 | 3 | Yes (2 files) | VERIFIED |
| 19 | `game/ui/effects/__init__.py` | 1 | 1 | Indirect | ADVISORY |
| 20 | `game/ui/orchestration/__init__.py` | 1 | 0 | No | ADVISORY |
| 21 | `game/ui/panels/build_queue_portraits.py` | 205 | 2 | Yes (145 lines) | OK — minor gaps |
| 22 | `game/ui/screens/battle_setup/__init__.py` | 16 | 0 | No | ADVISORY (re-export) |
| 23 | `game/ui/screens/battle_setup/renderer.py` | 85 | 2 | Yes | OK — minor gaps |
| 24 | `game/ui/screens/builder/modifier_config.py` | 99 | 1 | Indirect | ADVISORY (config dict) |
| 25 | `game/ui/screens/fleet_selection_window.py` | 152 | 2 | Yes (155 lines) | OK — minor gaps |
| 26 | `game/ui/screens/keybindings_scene.py` | 582 | 2 | Yes (281 lines) | OK — minor gaps |
| 27 | `game/ui/screens/new_game_setup_controller.py` | 364 | 2 | Yes (268 lines) | OK — thorough |
| 28 | `game/ui/screens/planet_list_controller.py` | 48 | 2 | Indirect (via window) | OK — small |
| 29 | `game/ui/screens/planet_list_filter_manager.py` | 148 | 2 | Yes (305 lines) | OK — thorough |
| 30 | `game/ui/screens/planet_list_window.py` | 760 | 2 | Yes (291 lines) | OK — thorough |
| 31 | `game/ui/screens/race_setup/__init__.py` | 26 | 0 | No | ADVISORY (re-export) |
| 32 | `game/ui/screens/race_setup_screen.py` | 31 | 1 | Indirect (4 files) | ADVISORY (shim) |
| 33 | `game/ui/screens/radiation_shield_editor.py` | 231 | 0 | **NO** | **MAJOR** |
| 34 | `game/ui/screens/star_list_filter_manager.py` | 85 | 2 | Yes | OK — thorough |
| 35 | `game/ui/screens/strategy_detail_formatter.py` | 454 | 2 | Yes (400 lines) | OK — thorough |
| 36 | `game/ui/screens/strategy_render/planets.py` | 78 | 0 | No | ADVISORY (rendering) |
| 37 | `game/ui/screens/strategy_screen_composition.py` | 114 | 3 | Yes | VERIFIED |
| 38 | `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | 82 | 0 | **NO** | **MAJOR** |
| 39 | `game/ui/screens/test_lab/renderer/_condition_logic.py` | 136 | 0* | Yes (159 lines) | MATRIX FALSE-NEG |
| 40 | `game/ui/screens/workshop_context.py` | 153 | 3 | Yes (177 lines) | VERIFIED |
| 41 | `game/ui/screens/workshop_screen.py` | 648 | 2 | Yes (9 matched) | OK — minor gaps |

\* Matrix false-negative: test files exist but AST scanner could not resolve the imports.

---

## Matrix Accuracy Notes

The pre-computed coverage matrix has 3 false-negatives in this shard:

1. **`game/app_bootstrap.py`** — 2 test files exist (`test_app_bootstrap_invariants.py`, `test_app_bootstrap_profiling.py`) but the matrix lists 0. The tests import `game.app_bootstrap` with heavy mocking, which the AST scanner could not trace.

2. **`game/ui/screens/test_lab/renderer/_condition_logic.py`** — 1 test file exists (`test_renderer_pure_functions.py`) but the matrix lists 0. The test accesses functions via `TestLabRenderer._format_check_pair` / `TestLabRenderer._is_condition_verified` class-attribute aliases, which the AST scanner could not resolve back to `_condition_logic.py`.

3. **`game/core/formula_evaluator.py`** — Matrix says `_eval_node` is untested. The function is private and tested indirectly through `FormulaEvaluator.evaluate()`, which calls it. No direct unit test exists. The scanner correctly identified the lack of direct test, but indirect coverage is strong.

---

## Context Usage Estimate

This report was produced by:
- Reading all 41 production files (~8708 LOC spread across the shard)
- Reading the docs: `01_ARCHITECTURE.md` (partial), `02_PATTERNS.md` (partial), `03_CONVENTIONS.md` (partial)
- Reading the coverage matrix and filtering to Shard 12 entries
- Reading 22 test files (partial, sampling key areas) to verify coverage claims
- Scanning file system via glob patterns for test file discovery

**Estimated token context**: ~85,000 tokens (production file reading dominated)
