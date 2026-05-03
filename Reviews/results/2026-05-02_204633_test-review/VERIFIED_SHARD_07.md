# Verified Shard 07 — Test Audit Report

## Verification Metadata
- **Verifier**: Skeptical Verifier (Independent)
- **Phase 1 report**: SHARD_07.md
- **Cross-shard report**: CROSS_SHARD.md
- **Methodology**: Read every cited line range + 10 lines context; cross-checked cross-shard claims via both source files.
- **Ratings**: CONFIRMED / DISPUTED / INCONCLUSIVE. Severity: downgrade only.
- **Overall**: 19 findings, 0 DISPUTED, 1 DOWNGRADE (CRITICAL → MAJOR), 18 CONFIRMED

---

## Findings Verification

### Finding 1: CAT-1 → DOWNGRADED to MAJOR — `test_configure_logging_callable` no-op assertion

**Original claim**: `assert hasattr(app_mod, "configure_logging") or True` at `test_app_public_api.py:126` always passes — zero regression protection. CRITICAL.

**Verified code** (`test_app_public_api.py:123-128`):
```python
def test_configure_logging_callable() -> None:
    """`configure_logging` must remain accessible from the module."""
    from game import app as app_mod
    assert hasattr(app_mod, "configure_logging") or True
    # Note: configure_logging may move to app_bootstrap. We still want
    # `main()` to call it; presence on `game.app` is not strictly required.
```

**Verification**: The `or True` clause makes the assertion vacuously true — confirmed. However:
1. The comment explicitly documents why this is intentionally a no-op: `configure_logging` may move to `app_bootstrap` and the test exists as a placeholder/reminder.
2. Blast radius is 1 line in a 128-line file.
3. The test body is marked by an intentional escape hatch with rationale, not an oversight.

**Verdict**: CONFIRMED (assertion always passes). **Severity DOWNGRADED CRITICAL → MAJOR**. The test is dead weight, not a hidden regression risk.

---

### Finding 2: CAT-2 MAJOR — `test_rebuild_ui_calls_renderer_rebuild` inspects source text

**Original claim**: `test_renderer.py:54-64` uses `inspect.getsource(FleetBattleSetupScreen._rebuild_ui)` and string-search `"self.renderer.rebuild(self)" in src` — tests source text, not runtime behavior.

**Verified code** (`test_renderer.py:54-64`):
```python
def test_rebuild_ui_calls_renderer_rebuild(self):
    import inspect
    from game.ui.screens.battle_setup.screen import FleetBattleSetupScreen
    src = inspect.getsource(FleetBattleSetupScreen._rebuild_ui)
    assert "self.renderer.rebuild(self)" in src
```

**Verification**: Confirmed. The test reads the source code of `_rebuild_ui` and checks for a string. If the source has the right string but the method is broken at runtime (e.g., `rebuild` signature changed), this test still passes. Zero behavioral regression protection.

**Verdict**: **CONFIRMED** — CAT-2 MAJOR appropriate. 11 LOC affected.

---

### Finding 3: CAT-11 MINOR — `test_renderer_is_stateless_between_calls` checks `__dict__`

**Original claim**: `test_renderer.py:29-38` asserts `r.__dict__ == {}` — implementation detail, not behavioral contract.

**Verified code** (`test_renderer.py:29-38`):
```python
def test_renderer_is_stateless_between_calls(self):
    from game.ui.screens.battle_setup.renderer import BattleSetupRenderer
    r = BattleSetupRenderer()
    assert r.__dict__ == {}
```

**Verification**: Confirmed. The test checks that a freshly-constructed `BattleSetupRenderer` has zero instance attributes. A future refactor adding `__slots__` or dataclass fields would break this test even if behavior is correct. No functional behavior is verified.

**Verdict**: **CONFIRMED** — CAT-11 MINOR appropriate. 10 LOC affected.

---

### Finding 4: CAT-2 MAJOR — Multiple source-code scan tests in `test_unified_entry_guard.py`

**Original claim**: ~15 test methods exercise only regex/AST scans of production source code, never testing runtime behavior. ~500 LOC affected.

**Verified code** (full file, 741 LOC, 29 test methods, 8 runtime + 21 source-scan):

| Lines | Test | Method | Verdict |
|-------|------|--------|---------|
| 70-78 | `test_whitelist_size_locked` | Checks constant `len(WHITELIST_FILES) == 3` | Source-constant |
| 80-104 | `test_no_unwhitelisted_BattleEngine_construction` | `re.compile(r"\bBattleEngine\(")` greps prod files | Source-grep |
| 115-142 | `test_no_def_setup_in_scenario_templates` | `ast.parse()` scans scenario templates | Source-AST |
| 148-194 | `test_no_legacy_compatible_comments` | Regex scans all `game/` + `combat_lab/` | Source-regex |
| 204-227 | `test_no_scenario_setup_calls_in_production` | Grep for `scenario.setup(` | Source-grep |
| 250-280 | `test_no_direct_engine_update_or_start_teams` | Grep for `.engine.update/start/start_teams(` | Source-grep |
| 286-296 | `test_no_engine_ref_closure` | Grep for `engine_ref = {"engine"...}` | Source-grep |
| 302-311 | `test_no_run_headless_method_on_battle_controller` | Regex on `battle_controller.py` | Source-regex |
| 321-331 | `test_extract_battle_results_signature_takes_outcome` | `inspect.signature()` | Source-inspect |
| 333-347 | `test_extract_battle_results_module_does_not_import_engine` | Regex on import statements | Source-regex |
| 353-360 | `test_battle_controller_has_get_outcome` | Regex on file for `def get_outcome(` | Source-regex |
| 362-369 | `test_battle_controller_has_set_spec` | Regex on file for `def set_spec(` | Source-regex |
| 492-507 | `test_complex_entries_body_contains_no_placeholder_literal` | Regex on spec_compiler.py | Source-regex |
| 584-597 | `test_battle_screen_start_team_shim_does_not_exist` | Regex on battle_screen.py | Source-regex |
| 599-606 | `test_build_fallback_outcome_does_not_exist` | String check `"_build_fallback_outcome" not in text` | Source-string |
| 608-620 | `test_battle_screen_has_only_start_battle_entry` | `hasattr` + `callable` on class | Source-reflect |
| 630-646 | `test_battle_setup_extract_scope_uses_registry` | Regex on spec_compiler.py body | Source-regex |
| 648-655 | `test_combat_modifier_collector_uses_registry` | String search in file | Source-string |
| 665-679 | `test_no_placeholder_stat_key_anywhere_in_compiler` | Regex on spec_compiler.py (comment-stripped) | Source-regex |
| 685-700 | `test_storm_emits_real_stat_key` | Regex on spec_compiler.py body | Source-regex |
| 702-741 | `test_fleet_mults_emit_real_stat_key` | Regex on spec_compiler.py body | Source-regex |

**Runtime tests present** (these DO exercise production code):
- `test_storm_compiler_emits_shield_capacity_mult` (L382) — calls `_entries_from_sector_effects`
- `test_fleet_compiler_emits_shield_capacity_mult` (L406) — calls `_entries_from_fleet_combat_modifiers`
- `test_fleet_compiler_emits_damage_mult` (L421) — calls `_entries_from_fleet_combat_modifiers`
- `test_strategy_compiler_routes_enemy_suppressor_to_receiver_team` (L435) — calls `_entries_from_fleet_combat_modifiers`
- `test_fleet_compiler_emits_shield_bonus_add` (L461) — calls `_entries_from_fleet_combat_modifiers`
- `test_shield_projector_emits_shield_bonus_add` (L537) — calls `build_manual_battle_spec`
- `test_shield_booster_emits_shield_capacity_mult_above_1` (L545) — calls `build_manual_battle_spec`
- `test_shield_suppressor_routes_to_opponent` (L551) — calls `build_manual_battle_spec`

**Verification**: The report claims ~15 source-scan tests. Actual count is 21 non-runtime tests out of 29 total. The report's specific line-range citations are accurate. However, the report understates the number — 21, not ~15. The report's characterization of these as "contract-guard tests that serve a valid policy-enforcement purpose" is accurate. The file explicitly calls itself a "unified-entry contract guard" (line 1 docstring).

**Verdict**: **CONFIRMED** — CAT-2 MAJOR appropriate. The report already self-downgraded from CRITICAL with justification. Note: actual non-runtime test count is 21 (not ~15), but this does not change the severity. ~420 LOC of non-runtime tests (not 500).

---

### Finding 5: CAT-11 MINOR — `test_whitelist_size_locked` hardcodes count

**Original claim**: `test_unified_entry_guard.py:70-78` hardcodes `assert len(self.WHITELIST_FILES) == 3`, breaks on legitimate whitelist addition.

**Verified code** (`test_unified_entry_guard.py:70-78`):
```python
def test_whitelist_size_locked(self):
    assert len(self.WHITELIST_FILES) == 3, (
        f"WHITELIST_FILES size changed from 3 to {len(self.WHITELIST_FILES)}. "
        "Adding a new whitelist entry is a load-bearing decision — update "
        "this assertion deliberately after confirming the new entry is a "
        "legitimate lifecycle path (not a new bypass)."
    )
```

**Verification**: Confirmed. The assertion message says "update this assertion deliberately" — making the test itself intentionally breakable as a gate. This is a deliberate policy gate, not an accident. Still, a legitimate new entry would break CI.

**Verdict**: **CONFIRMED** — CAT-11 MINOR appropriate. The intent is documented; the mechanical fragility is real. 9 LOC affected.

---

### Finding 6: CAT-2 MAJOR — `test_planet_selection_window.py` inspects signatures only

**Original claim**: `test_planet_selection_window.py:28-62` uses only `inspect.signature()` — zero behavioral tests.

**Verified code** (`test_planet_selection_window.py:28-62`):
```python
def test_default_parameters_backward_compatible(self, sample_planets):
    from game.ui.screens.planet_selection_window import PlanetSelectionWindow
    import inspect
    sig = inspect.signature(PlanetSelectionWindow.__init__)
    params = sig.parameters
    assert 'window_title' in params
    assert params['window_title'].default == "Select Planet to Colonize"
    assert 'list_label' in params
    assert params['list_label'].default == "Habitable bodies:"
    assert 'show_any_button' in params
    assert params['show_any_button'].default is True

def test_custom_parameters_accepted(self, sample_planets):
    from game.ui.screens.planet_selection_window import PlanetSelectionWindow
    import inspect
    sig = inspect.signature(PlanetSelectionWindow.__init__)
    params = sig.parameters
    assert 'window_title' in params
    assert 'list_label' in params
    assert 'show_any_button' in params
```

**Verification**: Confirmed. Neither test instantiates `PlanetSelectionWindow` or exercises any behavior. They only check that the constructor signature has certain parameter names and default values. Any runtime bug in the window is invisible to these tests.

**Verdict**: **CONFIRMED** — CAT-2 MAJOR appropriate. 35 LOC affected.

---

### Finding 7: CAT-8 MINOR — 6 nested `patch` blocks in strategy detail formatter test

**Original claim**: `test_strategy_detail_formatter.py:89-123` uses 6 nested `with patch(...)` blocks — setup exceeds 50% of test body.

**Verified code** (`test_strategy_detail_formatter.py:89-123`):
```python
def test_show_detail_with_star_system(self, formatter):
    system = Mock()
    # ... ~13 lines of mock attribute setup ...
    with patch('game.ui.screens.strategy_detail_formatter.is_star_system', return_value=True):
        with patch('game.ui.screens.strategy_detail_formatter.is_star', return_value=False):
            with patch('game.ui.screens.strategy_detail_formatter.is_planet', return_value=False):
                with patch('game.ui.screens.strategy_detail_formatter.is_fleet', return_value=False):
                    with patch('game.ui.screens.strategy_detail_formatter.is_warp_point', return_value=False):
                        with patch('game.ui.screens.strategy_detail_formatter.is_sector_environment', return_value=False):
                            formatter.show_detailed_report(system)
    assert formatter.current_selection is system
    formatter.graph_image.show.assert_called()
    formatter.btn_raw_data.show.assert_called()
```

**Verification**: Confirmed. The test body has ~13 lines of mock setup + 6 lines of nested context managers + 3 assertions = ~22 lines. The nested `patch` block occupies 7 lines of indent-only context management wrapping a single call. Setup genuinely exceeds 50% of the test.

**Verdict**: **CONFIRMED** — CAT-8 MINOR appropriate. 35 LOC affected.

---

### Finding 8: CAT-10 MAJOR — 5 near-identical direct-handler test classes

**Original claim**: `test_superweapon_handler_validation.py:87-192` — 5 test classes with identical structure differing only in handler class, command class, and validator method name.

**Verified**: Read all 5 classes (lines 87-192). Each class:
- Identical class-level docstring template ("Tests that XCommandHandler passes component_registry to validator.")
- Single `test_passes_component_registry_to_validator` method
- Imports the handler class and command class
- Creates the command from the command class
- Instantiates the handler
- Patches `SuperweaponValidator` 
- Calls `handler.execute(mock_session, cmd)`
- Asserts `component_registry` is in `call_args.kwargs`

Only differences: handler class name, command class name, validator method name (`validate_implode_planet` → `validate_stellerate_star` → `validate_open_warp_point` → `validate_close_warp_point` → `validate_create_dyson_sphere`).

**Verdict**: **CONFIRMED** — CAT-10 MAJOR appropriate. ~105 LOC affected. Textbook `@pytest.mark.parametrize` case.

---

### Finding 9: CAT-10 MAJOR — 5 near-identical mission-handler test classes

**Original claim**: `test_superweapon_handler_validation.py:199-393` — same pattern as above for mission handlers.

**Verified**: Read all 5 classes (lines 199-393). Each class contains:
- `test_calls_validator_with_component_registry` — patches `SuperweaponValidator` + `find_hybrid_path`, calls `handler.execute`, asserts validator called with `component_registry`
- `test_rejects_fleet_without_ability` — patches `find_ship_with_ability` returning `None`, asserts `not result.is_valid` with correct ability name in message

Only differences: handler class, command class, validator method name, ability string (`DestroyPlanet`, `DestroyStar`, `OpenWarpPoint`, `CloseWarpPoint`, `CreateDysonSphere`).

**Verdict**: **CONFIRMED** — CAT-10 MAJOR appropriate. ~195 LOC affected.

---

### Finding 10: CAT-10 MINOR — 6 round-trip attribute tests

**Original claim**: `test_ship_serialization.py:328-368` — 6 tests with identical bodies differing only in attribute name.

**Verified code** (lines 328-368): 6 methods (`test_roundtrip_preserves_name`, `test_roundtrip_preserves_ship_class`, `test_roundtrip_preserves_theme_id`, `test_roundtrip_preserves_team_id`, `test_roundtrip_preserves_color`, `test_roundtrip_preserves_movement_policy`) — each does:
```python
data = ShipSerializer.to_dict(basic_ship)
restored = ShipSerializer.from_dict(data, registries=registries)
assert restored.<attr> == basic_ship.<attr>
```

Only `test_roundtrip_preserves_color` wraps in `tuple()` and `test_roundtrip_preserves_movement_policy` uses `equipped_ship` fixture. Otherwise identical.

**Verdict**: **CONFIRMED** — CAT-10 MINOR appropriate. ~40 LOC affected.

---

### Finding 11: CAT-10 MINOR — Mode-setting and click-routing test clusters

**Original claim**: `test_superweapon_input_modes.py:49-102` (5 mode-setting tests) and lines 159-212 (5 click-routing tests) with identical bodies.

**Verified code** (lines 49-102, 159-212):

Mode-setting tests (5): Each creates `MockInputMapper(InputAction.FLEET_IMPLODE_PLANET)` / etc., sets `handler_with_mapper._mapper = mapper`, `handler_with_mapper.scene.selected_fleet = MagicMock()`, creates `event = MagicMock()`, calls `handler_with_mapper._handle_keydown_mapped(event)`, asserts `handler_with_mapper.input_mode == 'IMPLODE_PLANET_TARGET'` / etc.

Click-routing tests (5): Each sets `handler.input_mode = 'IMPLODE_PLANET_TARGET'` / etc., assigns a mock handler method, calls `handler.handle_click(100, 200, 1)`, asserts `result is True`, `handler.input_mode == 'SELECT'`, and the mock was called once.

**Verdict**: **CONFIRMED** — CAT-10 MINOR appropriate. ~100 LOC affected.

---

### Finding 12: CAT-10 MINOR — True/False variant test pairs

**Original claim**: `test_fleet_consumable_aggregator.py:84-108` and `191-207` — True/False variant pairs.

**Verified code**:
- Lines 84-100: `test_has_resources_for_movement_true` (`return_value=100.0` → `assert result is True`) + `test_has_resources_for_movement_false` (`return_value=5.0` → `assert result is False`)
- Lines 118-134: `test_consume_returns_true_on_success` (`return_value=100.0` → `assert result is True`) + `test_consume_returns_false_when_insufficient` (`return_value=5.0` → `assert result is False`)
- Lines 191-207: `test_has_resources_for_warp_true` (`return_value=100.0` → `assert result is True`) + `test_has_resources_for_warp_false` (`return_value=30.0` → `assert result is False`)

**Verification**: Confirmed. Each pair differs only in mock return value and expected boolean.

**Verdict**: **CONFIRMED** — CAT-10 MINOR appropriate. ~60 LOC affected.

---

### Finding 13: CAT-10 MINOR — 19 field comparisons in round-trip test

**Original claim**: `test_battle_state_serialization.py:306-328` — 19 individual field comparisons in `test_round_trip_minimal`.

**Verified code** (lines 306-328): 19 `assert restored.<field> == minimal_ship_state.<field>` assertions in a single test method. Fields include: `ship_id`, `name`, `ship_class`, `theme_id`, `team_id`, `color`, `movement_policy`, `position`, `velocity`, `angle`, `current_hp`, `max_hp`, `current_shields`, `max_shields`, `is_alive`, `is_derelict`, `retreat_status`, `current_target_id`, and `.id` on components list.

**Verification**: Confirmed. 19 consecutive assertions of identical structure. While each is individually valid, the pattern is amenable to extraction into a helper.

**Verdict**: **CONFIRMED** — CAT-10 MINOR appropriate. 23 LOC affected.

---

### Finding 14: CAT-5 MINOR — Heavy bypass-init fixture in race_setup_screen tests

**Original claim**: `test_race_setup_screen.py:31-148` — `_make_race_setup_screen` helper builds ~50 mock objects per test.

**Verified code** (lines 31-148): The `_make_race_setup_screen()` function:
- Uses `patch.object(RaceSetupScreen, '__init__', lambda self, *a, **kw: None)` — bypass-init pattern
- Creates `RaceSetupScreen.__new__(RaceSetupScreen)`
- Manually wires: `ui_manager`, 3 callbacks, `race_config`, `is_editing`, `race_library`, `race_registry`, `_asset_loader`, 8 panel mocks, 14 tab/button/label/input mocks, `_view_model`, `_renderer` (with 9 sub-attributes), `_controller` (with 9 sub-attributes), `_input_handler`, `_llm_service`
- Total: ~50 mock objects constructed per invocation

**Verification**: Confirmed. The fixture bypasses `__init__` entirely, manually wiring all internal state. Any bug in `RaceSetupScreen.__init__` is invisible to every test in this file. Total helper function is 118 lines of mock construction. Already graded MINOR with justification (mocks are lightweight `MagicMock` instances). Note: this is also cross-referenced as APC-001 in the cross-shard report — the `__new__` bypass-init anti-pattern.

**Verdict**: **CONFIRMED** — CAT-5 MINOR appropriate (already at lowest severity). ~118 LOC affected.

---

## Cross-Shard Claims Verification

### DUP-001: Superweapon handler test structural duplication (Shard 03 ↔ Shard 07)

**Cross-shard claim**: SHARD_03 (`test_superweapon_command_handlers.py`) and SHARD_07 (`test_superweapon_handler_validation.py`) share near-identical structural template — one test class per superweapon handler class, same mock_session/mock_fleet/mock_planet fixture chain, same `with patch('...SuperweaponValidator')` pattern. SHARD_03 tests execution path; SHARD_07 tests DI validation path.

**Verified** (both files, full content):

| Aspect | Shard 03 (test_superweapon_command_handlers.py) | Shard 07 (test_superweapon_handler_validation.py) |
|--------|-------|-------|
| Fixture pattern | `mock_fleet`, `mock_planet`, `mock_galaxy`, `mock_session` | Identical + `mock_component_registry` |
| Handler classes | 6 (ImplodePlanet, StellerateStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct) | 5 direct + 5 mission (same 5 types, no SelfDestruct) |
| Test per class | 3 (validation passes, correct order type, fleet not found) | 1 direct, 2 mission |
| Patch pattern | `patch('...SuperweaponValidator')` | Identical `patch('...SuperweaponValidator')` |
| Tests exercise | Execution path (handler.execute → validators, order creation) | DI validation path (component_registry pass-through, ability check) |

**Verification**: CONFIRMED. The structural template is identical — same fixture chain, same handler-class iteration, same mock/patch patterns. Only assertions differ (execution vs. DI validation). The recommendation to merge into Shard 03 is sound; the DI tests can be added as parametrized test methods per handler class.

**Verdict**: **CONFIRMED**. ~200 LOC estimated savings.

---

### APC-001: `__new__` bypass-init pattern — Shard 07 file confirmed

**Cross-shard claim**: `test_race_setup_screen.py` (Shard 07) uses the `__new__` bypass-init anti-pattern with 118 LOC helper.

**Verified**: See Finding 14 above. Lines 49-50 explicitly use:
```python
with patch.object(RaceSetupScreen, '__init__', lambda self, *a, **kw: None):
    screen = RaceSetupScreen.__new__(RaceSetupScreen)
```

**Verdict**: **CONFIRMED**. Present in APC-001 cluster. 118 LOC affected in this file.

---

### APC-002: `inspect.getsource()`/`inspect.signature()` pattern — Shard 07 files confirmed

**Cross-shard claim**: Two Shard 07 files use source-inspection tests:
- `test_renderer.py:54-64` — `inspect.getsource()`
- `test_planet_selection_window.py:28-62` — `inspect.signature()`

**Verified**: See Findings 2 and 6 above. Both confirmed as source-inspection-only tests with zero behavioral regression protection.

**Verdict**: **CONFIRMED**. Present in APC-002 cluster. ~46 LOC affected total (11 + 35).

---

## Summary

| # | File | Category | Severity | Verdict |
|---|------|----------|----------|---------|
| 1 | test_app_public_api.py:126 | CAT-1 | **MAJOR** (downgraded from CRITICAL) | CONFIRMED — `or True` no-op |
| 2 | test_renderer.py:54-64 | CAT-2 | MAJOR | CONFIRMED — `inspect.getsource` |
| 3 | test_renderer.py:29-38 | CAT-11 | MINOR | CONFIRMED — `__dict__` check |
| 4 | test_unified_entry_guard.py | CAT-2 | MAJOR | CONFIRMED — 21 source-scan tests |
| 5 | test_unified_entry_guard.py:70-78 | CAT-11 | MINOR | CONFIRMED — hardcoded count |
| 6 | test_planet_selection_window.py:28-62 | CAT-2 | MAJOR | CONFIRMED — `inspect.signature` only |
| 7 | test_strategy_detail_formatter.py:89-123 | CAT-8 | MINOR | CONFIRMED — 6 nested patches |
| 8 | test_superweapon_handler_validation.py:87-192 | CAT-10 | MAJOR | CONFIRMED — 5 duplicate classes |
| 9 | test_superweapon_handler_validation.py:199-393 | CAT-10 | MAJOR | CONFIRMED — 5 duplicate classes |
| 10 | test_ship_serialization.py:328-368 | CAT-10 | MINOR | CONFIRMED — 6 duplicate tests |
| 11 | test_superweapon_input_modes.py:49-102,159-212 | CAT-10 | MINOR | CONFIRMED — 10 duplicate tests |
| 12 | test_fleet_consumable_aggregator.py:84-108,191-207 | CAT-10 | MINOR | CONFIRMED — 5 True/False pairs |
| 13 | test_battle_state_serialization.py:306-328 | CAT-10 | MINOR | CONFIRMED — 19 field assertions |
| 14 | test_race_setup_screen.py:31-148 | CAT-5 | MINOR | CONFIRMED — bypass-init fixture |

| Cross-Shard Ref | Claim | Verdict |
|-----------------|-------|---------|
| DUP-001 | Shard 03 ↔ 07 superweapon test duplication | CONFIRMED |
| APC-001 | Race setup screen uses `__new__` bypass-init | CONFIRMED |
| APC-002 | Two files use `inspect.getsource`/`inspect.signature` | CONFIRMED |

### Disputes: 0

No claims were found to be inaccurate, misleading, or unfounded. One severity downgrade applied (Finding 1: CRITICAL → MAJOR) because the `or True` no-op is intentionally documented and affects only 1 LOC.

### Refinements

- Finding 4: Actual non-runtime test count is 21 (not ~15). The report's line ranges are correct; the estimate undercounts. ~420 LOC affected (not 500). Severity unchanged.
- Finding 1: The `or True` assertion carries a documented rationale (line 127-128: "configure_logging may move to app_bootstrap") making this an intentional placeholder, not an oversight. Downgraded CRITICAL → MAJOR.
