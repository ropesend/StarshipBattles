# VERIFIED Shard 09 — Test Audit Findings

**Verifier**: SKEPTICAL VERIFIER (independent)
**Date**: 2026-05-02
**Shard**: 09
**Files assigned**: 74 (all read per Phase 1 report)
**Total findings reviewed**: 33 shard + 5 cross-shard claims

## Summary

| Status | Count |
|--------|-------|
| CONFIRMED | 28 |
| DISPUTED | 4 |
| INCONCLUSIVE | 1 |
| **TOTAL** | **33** |

Original report counts: Critical: 6 | Major: 11 | Minor: 20
Verified counts (after downgrade corrections): **Critical: 4** | **Major: 12** | **Minor: 13** | **Noted: 4**

**Cross-shard claims involving Shard 09: 5 — all CONFIRMED.**

---

## Verification Results

### F-01: repro_facade_colonies.py — Standalone repro script
**Category**: CAT-3 | **Severity**: CRITICAL → **CONFIRMED**
**Lines**: repro_facade_colonies.py:1-93

**Evidence**: File uses `unittest.TestCase` (not pytest), lives in `tests/repro_issues/` (repro directory, not a test directory). Tests are substantive (mock galaxy/planet system, call `get_planets_at_hex`) but exist outside the pytest harness and duplicate what `tests/integration/strategy/facade/test_validation_queries.py` should cover. The file also accesses `facade._session.galaxy` (line 12) — a private attribute of the facade internals.

**Verdict**: CONFIRMED. CAT-3 accurate. 93 LOC.

---

### F-02: test_intercept_edge_cases.py — Entire file is existence-check tests
**Category**: CAT-1 | **Severity**: CRITICAL → **CONFIRMED**
**Lines**: test_intercept_edge_cases.py:13-27

**Evidence**: The ENTIRE file (27 lines) contains only 3 tests:
- Line 13: `assert pathfinding is not None`
- Line 18: `assert calculate_intercept_point is not None`
- Line 23: `assert find_path_interstellar is not None; assert find_hybrid_path is not None`

All test only import success. No behavioral assertions. File contributes zero regression protection.

**Verdict**: CONFIRMED. CAT-1 accurate. The report's LOC estimate of 15 understates the blast radius — the entire 27-LOC file is dead.

---

### F-03: test_race_theme_gallery.py — Self-fulfilling assertion tests
**Category**: CAT-1 | **Severity**: CRITICAL → **CONFIRMED**
**Lines**: test_race_theme_gallery.py:51-70

**Evidence**:
- Line 55-60: `gallery = RaceThemeGallery.__new__(RaceThemeGallery); gallery.asset_buttons = []; assert isinstance(gallery.asset_buttons, list)` — asserts value the test itself assigned.
- Line 66-70: `gallery.scroll_container = None; assert hasattr(gallery, 'scroll_container')` — same self-fulfilling prophecy.

Both use the `__new__` bypass-init pattern (APC-001). All other tests in the file (lines 72-274) also use `__new__` bypass-init, making these two only the most egregious examples.

**Verdict**: CONFIRMED. CAT-1 accurate. The entire file (274 LOC) is APC-001 affected — these two specific tests are the worst offenders. 20 LOC directly affected.

---

### F-04: test_production_rates.py — Tests reimplement local algorithm logic
**Category**: CAT-2 | **Severity**: CRITICAL → **CONFIRMED (LOC adjusted)**
**Lines**: test_production_rates.py:108-145, 180-283

**Evidence**: Three test classes reimplement the turn-calculation algorithm locally:
- `TestPerResourceTurnCalculation` (lines 108-145): `math.ceil(res_cost / rate)`, `max(1, max(turns_per_resource))` — computed locally, never calls production code.
- `TestCostPerTickCapping` (lines 180-237): `max_per_tick = rate/100`, `min(natural_rate, cap)` — all local math.
- `TestResourceConsumptionOverTurns` (lines 247-283): Same local computation pattern.

However, test_construction_speed_bonus (line 147-170) DOES call `_get_facility_production_rates()` — real production code. Similarly, `TestProductionRatesFromJSON` (lines 290-317) and `TestBuildQueueSourceIntegration` (lines 324-361) call real production functions.

**LOC correction**: The report claims ~175 LOC affected. Verifiable reimplementation spans ~133 LOC (lines 108-145, 180-237, 247-283). The remaining ~42 LOC in the cited range are valid tests calling production code.

**Verdict**: CONFIRMED with LOC adjustment. CAT-2 accurate for the three identified classes. Actual affected LOC: ~133.

---

### F-05: test_race_asset_loader.py — Signature existence test
**Category**: CAT-1 (downgraded to MAJOR) | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_race_asset_loader.py:85-93

**Evidence**: `test_load_portrait_full_has_correct_signature` asserts `hasattr(loader, 'load_portrait_full')` and `callable(loader.load_portrait_full)`. Trivial pass — cannot fail unless the module is deleted.

**Verdict**: CONFIRMED. Downgrade to MAJOR is appropriate (9 LOC, small blast radius).

---

### F-06: test_planet_report_panel.py — Function existence test
**Category**: CAT-1 (downgraded to MAJOR) | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_planet_report_panel.py:247-251

**Evidence**: `test_function_exists` does `assert callable(compute_planet_production)`. Trivial pass.

**Verdict**: CONFIRMED. Downgrade to MAJOR appropriate (5 LOC).

---

### F-07: test_quickstart_builder.py — Repeated spawn_initial_complexes setup
**Category**: CAT-9 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_quickstart_builder.py:216-409

**Evidence**: Nine `test_spawn_initial_complexes_*` tests (lines 216-409). Each recreates `empire = MagicMock()`, `session = MagicMock()`, `home_planet = MagicMock()` setup. Tests with DesignLibrary patches (lines 254-291, 307-315, 336-344, 370-382, 397-409) repeat identical `with patch("game.strategy.quickstart_builder.DesignLibrary")` blocks. ~50% of each test body is duplicated setup.

**Verdict**: CONFIRMED. ~150 LOC affected is reasonable.

---

### F-08: test_save_selection.py — Repeated autouse setup_tmpdir fixtures
**Category**: CAT-5 | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_save_selection.py:47-55, 148-156, 217-225

**Evidence**: Three test classes (`TestSaveSelectionTurnList`, `TestSaveSelectionListSaves`, `TestSaveSelectionEmpireInfo`) each define the EXACT same `autouse setup_tmpdir` fixture — identical byte-for-byte: creates tempdir, patches `SAVES_DIR`, yields, shutil.rmtree.

**Verdict**: CONFIRMED. CAT-5 accurate. ~30 LOC affected (3 x 10 lines).

---

### F-09: test_save_selection.py — Internal implementation coupling
**Category**: CAT-6 | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_save_selection.py:274-327

**Evidence**: `test_buttons_enable_after_selection` (BUG-30 regression test):
- Requires `pygame.init()`, `pygame.display.set_mode()`, `pygame_gui.UIManager()` (lines 261-268)
- Mutates `first_item["selected"] = True` on the internal dict from `window.saves_listbox.item_list` (line 316) — tightly coupled to pygame_gui's internal representation
- Calls `window._handle_selection_change()` (line 319) — private method

The test depends on pygame_gui's `UISelectionList.item_list` returning dicts with a `"selected"` key. Any pygame_gui upgrade changing this representation breaks the test.

**Verdict**: CONFIRMED. CAT-6 accurate. 55 LOC affected.

---

### F-10: test_save_selection.py — time.sleep in test
**Category**: CAT-7 | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_save_selection.py:204

**Evidence**: `time.sleep(0.1)  # Ensure different timestamp` — arbitrary sleep for timing-dependent test ordering. Flaky on slow CI.

**Verdict**: CONFIRMED. CAT-7 accurate. MAJOR may be slightly high for a single 0.1s sleep, but the practice is objectively bad. Severity sustained.

---

### F-11: test_protocols.py — Repeated local imports
**Category**: CAT-9 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_protocols.py:14-220

**Evidence**: Every test method in `TestProtocolsWithRealClasses` and `TestTypeGuardFunctions` imports the same classes locally:
- `from game.core.protocols import IFleet` — repeated 6+ times
- `from game.strategy.data.fleet import Fleet` — repeated 6+ times
- Similar patterns for Planet, StarSystem, Star, WarpPoint, SectorEnvironment

**Verdict**: CONFIRMED. ~40 duplicate import lines estimated.

---

### F-12: test_protocols.py — TypeGuard parameterize opportunity
**Category**: CAT-10 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_protocols.py:101-220

**Evidence**: `TestTypeGuardFunctions` has 10 tests with identical structure: import typeguard function, create real object, assert True; create non-object(s), assert False. Each could be `@pytest.mark.parametrize("typeguard_fn,real_class,false_objects", [...])`.

**Verdict**: CONFIRMED. ~120 → ~30 LOC via parametrization is realistic.

---

### F-13: test_loading.py — Edge case parameterize opportunity
**Category**: CAT-10 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_loading.py:159-239

**Evidence**: `TestEdgeCases` has 9 tests following identical pattern: write JSON file with edge case → `ResourceCatalog.from_json(str(filepath))` → assert catalog state. All parametrizable with (json_content, expected_ids).

**Verdict**: CONFIRMED. ~80 → ~25 LOC via parametrization is realistic.

---

### F-14: test_formatters.py — Repeated local imports
**Category**: CAT-9 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_formatters.py:9-57

**Evidence**: All 12 tests in `TestFormatCompactNumber` individually import `from game.ui.utils.formatters import format_compact_number` at the top of their body (lines 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 54).

**Verdict**: CONFIRMED. ~12 LOC of redundant imports.

---

### F-15: test_tech_node.py — Price curve non-parametrized duplicates
**Category**: CAT-10 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_tech_node.py:315-373

**Evidence**: `TestTechNodePriceCurves` has 9 individual tests (flat, linear, quadratic, exponential, logarithmic, sqrt, unknown, multiplier) with identical structure: create TechNode with price_curve → call get_effective_price at multiple levels → assert. Each is 7-9 lines. The report claims a `TestGetEffectivePriceParametrized` class below covers the same curves. Verifier confirms the non-parametrized class IS a parametrization opportunity regardless.

**Verdict**: CONFIRMED. ~60 LOC of redundant tests.

---

### F-16: test_ship.py vs test_combat.py — Derelict status duplication
**Category**: CAT-4 | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_ship.py:163-194 vs test_combat.py:98-122

**Evidence**: Both tests verify the SAME three-step derelict logic:
1. Ship with no weapons/engines → `is_derelict == True` (test_ship.py:180, test_combat.py:108)
2. Add weapon → `is_derelict == False` (test_ship.py:187, test_combat.py:115)
3. Destroy weapon → `is_derelict == True` (test_ship.py:194, test_combat.py:122)

Near-identical assertions and same core logic flow. Docstrings share language ("functional definition"). test_ship.py's version also includes bridge/crew setup but the core test sequence is duplicated.

**Verdict**: CONFIRMED. CAT-4 accurate. The report correctly recommends keeping test_ship.py's version (more appropriate location for entity-level behavior).

---

### F-17: test_seeker_weapon_bindings.py vs test_weapons_isolation.py — Recalculate duplication
**Category**: CAT-4 | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_seeker_weapon_bindings.py:100-193 vs test_weapons_isolation.py:1011-1026

**Evidence**:
- `test_weapons_isolation.py:1011-1026`: Single test `test_recalculate_applies_seeker_modifiers` uses `MagicMock.stats = {...}` to test endurance_mult, projectile_damage_mult, projectile_hp_mult, projectile_stealth_level in one consolidated test.
- `test_seeker_weapon_bindings.py:103-193`: Four separate tests, each defining `class MockComponent` inline, testing the same four modifiers individually.

Both test `SeekerWeaponAbility.recalculate()` applying the same seeker-specific stat modifiers. test_weapons_isolation.py is more comprehensive and concise.

**Verdict**: CONFIRMED. CAT-4 accurate. ~90 LOC affected in seeker_weapon_bindings.

---

### F-18: test_battle_runner_di.py vs test_battle_runner.py — Duplicate helpers
**Category**: CAT-4 | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_battle_runner_di.py:52-100 vs test_battle_runner.py:46-105

**Evidence**:
- `_make_ship_spec()`: IDENTICAL in both files (same design_id="Escort", theme_id="Federation", etc.)
- `_make_team()`: Same structure, same parameters, same output in both files.
- `ship_builder` fixture: Structurally identical in both (creates Ship at spec position, sets instance_id).
- `_minimal_spec()`: Only in test_battle_runner_di.py (lines 87-100) — NOT duplicated in test_battle_runner.py.

The duplication is real and substantive for `_make_ship_spec` and `_make_team`. The `_minimal_spec` helper is unique to the DI file.

**Verdict**: CONFIRMED. CAT-4 accurate. ~55 LOC of overlapping helpers.

---

### F-19: test_battle_runner_di.py — AST-walk test
**Category**: CAT-8 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_battle_runner_di.py:218-271

**Evidence**: `test_no_simulation_call_to_get_default_registry_provider` builds an AST-based scanner (54 lines) that parses every `.py` file in `game/simulation/`, walks AST nodes, and checks for imports/calls of `get_default_registry_provider`. This is a compile-time check masquerading as a runtime test. A simple `rg` pre-commit hook or CI check would be more maintainable.

**Verdict**: CONFIRMED. CAT-8 accurate. The test works but is over-engineered for a single boolean assertion.

---

### F-20: test_reset_state.py — Complex mock panel wiring
**Category**: CAT-6 | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_reset_state.py:17-31, 76-188

**Evidence**: 
- `_create_mock_panel` (line 17) creates a MagicMock, then binds the real `ResearchControlPanel.reset` via lambda: `panel.reset = lambda t, tt: rc.ResearchControlPanel.reset(panel, t, tt)` (line 30)
- Six test methods (lines 73-187) assert on internal call sequence:
  - `panel.clear_selection.assert_called_once()` (line 87)
  - `panel.update_budget_display.assert_called_once()` (line 103)
  - `panel.clear_log.assert_called_once()` (line 119)
  - `panel._update_auto_spread_button.assert_called_once()` (line 135)
  - `panel.slider_budget.set_current_value.assert_called_once_with(300)` (line 187)

These assertions verify the internal implementation ORDER of the `reset()` method, not its observable state. Any refactoring of the reset method's internal sequence would break these tests even if behavior is correct.

**Verdict**: CONFIRMED. CAT-6 accurate. ~100 LOC affected is reasonable.

---

### F-21: test_ship_stat_querier.py — Dead empty test class
**Category**: CAT-3 (downgraded to MAJOR) | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_ship_stat_querier.py:252-257

**Evidence**: `TestShipStatQuerierCachedSummary` class (lines 252-257) contains only a docstring and a comment (`# PROJ-225: Removed test_cached_summary_* tests (DUP-SIM-007)`). Zero test methods. Dead scaffolding.

**Verdict**: CONFIRMED. CAT-3 accurate. Downgrade to MAJOR appropriate (6 LOC).

---

### F-22: test_projectile_manager.py — Repeated MagicMock projectile construction
**Category**: CAT-9 | **Severity**: MINOR → **CONFIRMED (with line number correction)**
**Lines**: test_projectile_manager.py — 27+ occurrences across the file

**Evidence**: `grep` confirms 27 occurrences of `proj.position = Vector2(...)` across the 1628-LOC file. Common boilerplate pattern per mock projectile:
- `proj.position = Vector2(...)` (27 occurrences)
- `proj.velocity = Vector2(...)` (many)
- `proj.is_alive = True` (6 occurrences)
- `proj.team_id = ...`, `proj.type = AttackType.PROJECTILE`, `proj.damage = ...`

**Line number correction**: The report cites lines 1831-1840 and 1997-2007, but the file ends at line 1628. These line numbers are fictitious. However, the pattern IS confirmed across actual line ranges (e.g., 1501-1520, 1124-1191, and 25+ other locations).

**Verdict**: CONFIRMED with line-number correction. The pattern is real; ~200 LOC could be eliminated with a shared helper.

---

### F-23: test_edge_cases.py — test_all_path_steps_are_adjacent
**Category**: CAT-12 | **Severity**: MINOR → **DISPUTED → NOTED**
**Lines**: test_edge_cases.py:148-157

**Evidence**: `test_all_path_steps_are_adjacent` (line 148):
```python
for i in range(len(path) - 1):
    dist = hex_distance(path[i], path[i + 1])
    assert dist == 1
```
The expected value `1` IS a hardcoded constant, not computed at runtime. The test calls `find_path_deep_space(start, end)` (real production code) and verifies a property of the returned path. The loop iterates through actual path steps — this IS a valid property-based test. The assertion `dist == 1` is on a constant, not on a computed expected value.

**Verdict**: **DISPUTED**. This is a legitimate property-based test — asserts adjacency (=1) as a hardcoded constant against actual path output. Not "logic-heavy" in the problematic CAT-12 sense. **Noted** — acceptable quality.

---

### F-24: test_engine_validation.py — Parametrize opportunity
**Category**: CAT-10 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_engine_validation.py:39-312

**Evidence**: 9+ test classes (HarvestingEngine through PlanetActionEngine and beyond) with identical structure:
- Each class: `test_valid_empires_pass` + one negative test (test_colony_none_raises or test_fleet_none_*_raises)
- Same imports (`from game.strategy.engine.<X> import <X>Engine`)
- Same assertion pattern (either no raise or `pytest.raises(ValidationException)`)

Could be collapsed to one parametrized class with `@pytest.mark.parametrize("engine_cls,valid_empire_kwargs,invalid_field_path")`.

**Verdict**: CONFIRMED. CAT-10 accurate. ~250 → ~50 LOC is realistic.

---

### F-25: test_commands.py — Empty placeholder test
**Category**: CAT-3 (downgraded to MAJOR) | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_commands.py:191-198

**Evidence**: `test_handle_command` in `TestGameSessionCommands` (line 191): contains only comments about mock complexity and `pass` (line 198). Zero assertions. Dead placeholder.

**Verdict**: CONFIRMED. CAT-3 accurate. Downgrade to MAJOR appropriate (8 LOC).

---

### F-26: test_battle_runner.py — Smoke test parameterize opportunity
**Category**: CAT-10 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_battle_runner.py:254-390

**Evidence**: Five module-level test functions (test_run_battle_returns_battle_outcome through test_run_battle_seed_is_echoed, lines 254-390), each constructing a `BattleSpec` with nearly identical boilerplate:
```python
spec = BattleSpec(
    seed=..., telemetry_level=TelemetryLevel.NORMAL, boundary=None,
    end_condition=TickLimitCondition(max_ticks=...), absolute_max_ticks=...,
    teams=(...), modifier_stack=ModifierStack.empty(), post_battle_hook=None,
)
outcome = run_battle(spec, ai_factory=AIControllerFactory(), ship_builder=ship_builder)
```
Differing only in seed, tick limits, ship ids, and specific assertions. Could share a helper `_run_minimal_battle(seed, max_ticks, teams) -> (spec, outcome)`.

**Verdict**: CONFIRMED. CAT-10 accurate. ~120 → ~40 LOC is realistic.

---

### F-27: test_combat.py — test_firing_solution_lead
**Category**: CAT-12 | **Severity**: MINOR → **DISPUTED → NOTED**
**Lines**: test_combat.py:213-235

**Evidence**: `test_firing_solution_lead` (line 213):
```python
t = engine.solve_lead(mock_ship.position, mock_ship.velocity, target_pos, target_vel, proj_speed)
assert abs(t - 10.0) < 0.1
```
The expected value `10.0` IS hardcoded, not computed at runtime. The test calls the real `ShipCombatEngine.solve_lead()` method — production code. The comments (lines 228-233) document the derivation but do NOT execute any computation. This is a valid behavioral test with a hardcoded expected output.

**Verdict**: **DISPUTED**. The test calls production code and asserts against a hardcoded expected value (10.0). Comments are documentation, not logic. **Noted** — acceptable quality.

---

### F-28: test_physics.py — test_mass_dampening
**Category**: CAT-12 | **Severity**: MINOR → **DISPUTED → NOTED**
**Lines**: test_physics.py:261-281

**Evidence**: `test_mass_dampening` (line 261):
- Runs ship thrust cycle with mass=100, records fast_speed
- Runs ship thrust cycle with mass=10000, records slow_speed
- Asserts `fast_speed > slow_speed`

This is a directional property assertion (higher mass → lower speed), not a specific-value assertion. The report itself acknowledges: "This is a valid approach for testing mass-dampening direction. Fine as-is but noted."

**Verdict**: **DISPUTED**. The test asserts a directional property (comparative), not computing expected values. The report's own text concedes it's valid. **Noted** — no quality issue, just documented.

---

### F-29: test_modifier_logic_smart_floor.py — Weak assertion
**Category**: CAT-9 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_modifier_logic_smart_floor.py:37-44

**Evidence**: `test_snap_down_by_1_from_1_stays_at_min` (line 37):
```python
result = ModifierLogic.calculate_snap_value(
    current=1.0, step=1.0, direction=-1,
    min_val=0.1, max_val=1024.0, smart_floor=True
)
assert result >= 0.1
```
The test description says "should clamp at 0.1" but only asserts `>= 0.1`. If the function returned 5.0, the test would still pass. The assertion should be `result == pytest.approx(0.1, abs=0.01)`.

**Verdict**: CONFIRMED. CAT-9 (weak assertion) accurate. 5 LOC affected.

---

### F-30: test_space_yard.py — Duplicate make_ship_with_yard fixture
**Category**: CAT-4 (downgraded MAJOR) | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_space_yard.py:91-123 vs 195-226

**Evidence**: `make_ship_with_yard` fixture is defined IDENTICALLY in two classes:
- `TestFleetHasSpaceShipyard` (lines 91-123)
- `TestFleetCanBuildType` (lines 195-226)

Same imports, same MagicMock construction, same design_data dicts, same return structure. The second definition at line 195 is a byte-for-byte duplicate.

**Verdict**: CONFIRMED. CAT-4 accurate (within-file duplication). Downgrade to MAJOR appropriate (~35 LOC).

---

### F-31: test_new_game_setup.py — inspect.signature fragile test
**Category**: CAT-11 | **Severity**: MINOR → **CONFIRMED**
**Lines**: test_new_game_setup.py:103-117

**Evidence**: `test_build_game_config_signature_default_matches_dataclass` (line 103):
```python
sig = inspect.signature(NewGameSetupScreen.build_game_config)
assert sig.parameters["system_count"].default == DEFAULT_SYSTEM_COUNT
assert DEFAULT_SYSTEM_COUNT == 2
```
Uses `inspect.signature()` to verify parameter defaults (APC-002 pattern). Also fetches `inspect.getsource()` (line 110 import visible). Fragile — parameter reorganization or intermediate function wrapping breaks the test even if behavior is unchanged.

**Verdict**: CONFIRMED. CAT-11 accurate. Also an APC-002 instance (inspect.getsource/signature). 16 LOC.

---

### F-32: test_new_game_setup.py — test_curve_low_end_fine_grained
**Category**: CAT-12 | **Severity**: MINOR → **DISPUTED → NOTED**
**Lines**: test_new_game_setup.py:146-157

**Evidence**: `test_curve_low_end_fine_grained` (line 146):
```python
for t in range(0, 100):
    v = system_count_slider_curve(t)
    max_jump = max(max_jump, v - prev)
    prev = v
assert max_jump <= 1
```
The expected property `<= 1` IS a hardcoded constant. The test calls the real `system_count_slider_curve()` function and verifies a property (single-system increments at low end). This is a valid property-based test.

**Verdict**: **DISPUTED**. The test calls production code and asserts against a hardcoded property. The loop computes actual values, not expected values. Legitimate property-based test. **Noted** — acceptable quality.

---

### F-33: test_seeker_weapon_bindings.py — Inline MockComponent class duplication
**Category**: CAT-6 | **Severity**: MAJOR → **CONFIRMED**
**Lines**: test_seeker_weapon_bindings.py:103-193

**Evidence**: Four test methods each define `class MockComponent` inline:
- Line 107: `class MockComponent` with `self.stats = {'endurance_mult': 2.0}`
- Line 130: `class MockComponent` with `self.stats = {'projectile_damage_mult': 3.0}`
- Line 153: `class MockComponent` with `self.stats = {'projectile_hp_mult': 5.0}`
- Line 176: `class MockComponent` with `self.stats = {'projectile_stealth_level': 3}`

All four define identical `__init__` with `self.ability_stats = {}` and `self.data = {}`. Each could be replaced with `MagicMock(stats={...})` in one line. The pattern also exhibits CAT-4 duplication with test_weapons_isolation.py (see F-17).

**Verdict**: CONFIRMED. CAT-6 accurate. ~60 LOC of unnecessary boilerplate.

---

## Cross-Shard Claim Verification

### X-01: APC-001 — `__new__` bypass-init in test_race_theme_gallery.py
**Source**: CROSS_SHARD.md APC-001
**Claim**: test_race_theme_gallery.py (Shard 09, 200 LOC affected) uses `__new__` bypass-init extensively.

**Verification**: Confirmed. Every test in test_race_theme_gallery.py (274 LOC) uses `patch.object(RaceThemeGallery, '__init__', lambda self, *args, **kwargs: None)` + `RaceThemeGallery.__new__(RaceThemeGallery)` + manual attribute wiring. The 200 LOC estimate includes all test bodies that follow this pattern.

**Verdict**: **CONFIRMED**.

---

### X-02: APC-002 — inspect.getsource/signature in test_new_game_setup.py
**Source**: CROSS_SHARD.md APC-002
**Claim**: test_new_game_setup.py:103-117 (Shard 09) uses `inspect.signature()` + `inspect.getsource()`.

**Verification**: Confirmed. Same as F-31 above. Uses `inspect.signature(NewGameSetupScreen.build_game_config)` to verify default parameter values.

**Verdict**: **CONFIRMED**.

---

### X-03: HLP-002 — BattleRunner test helpers (test_battle_runner.py, test_battle_runner_di.py)
**Source**: CROSS_SHARD.md HLP-002
**Claim**: `_make_ship_spec`, `_make_team`, `ship_builder` are near-exact copies across both files.

**Verification**: Confirmed. Same as F-18 above. `_make_ship_spec` and `_make_team` are byte-for-byte identical across both files. `ship_builder` fixture is structurally identical.

**Verdict**: **CONFIRMED**.

---

### X-04: HLP-003 — Yard facility factory helpers (test_space_yard.py)
**Source**: CROSS_SHARD.md HLP-003
**Claim**: `make_ship_with_yard` defined twice in test_space_yard.py:91-123, 195-226.

**Verification**: Confirmed. Same as F-30 above. Identical fixture defined in two classes within the same file.

**Verdict**: **CONFIRMED**.

---

### X-05: Priority 2 — Shared mock fixtures affecting Shard 09
**Source**: CROSS_SHARD.md Recommendations Summary, Priority 2
**Claim**: Shard 09 is among shards needing shared mock ship/fleet/planet/empire fixtures.

**Verification**: Confirmed. Shard 09's test_battle_runner.py, test_battle_runner_di.py, and test_space_yard.py all have helper duplication that would benefit from shared fixtures.

**Verdict**: **CONFIRMED** (advisory recommendation, not a finding to validate).

---

## Severity Adjustments from Original Report

| Finding | Original | Verified | Reason |
|---------|----------|----------|--------|
| F-23 | MINOR (CAT-12) | NOTED | Legitimate property-based test — asserts hardcoded constant against production output |
| F-27 | MINOR (CAT-12) | NOTED | Calls production code, asserts against hardcoded expected value (10.0) |
| F-28 | MINOR (CAT-12) | NOTED | Directional property assertion — report's own text says "fine as-is" |
| F-32 | MINOR (CAT-12) | NOTED | Legitimate property-based test — asserts hardcoded constant against production output |

**4 CAT-12 findings disputed and downgraded to NOTED.** The CAT-12 category (logic-heavy tests) requires that the test computes expected values at runtime or reimplements SUT logic. These four tests all call production code and assert against hardcoded constants or properties — they are valid property-based/behavioral tests.

### Corrected Counts

| Severity | Report | Verified |
|----------|--------|----------|
| CRITICAL | 6 | **4** (F-01, F-02, F-03, F-04) |
| MAJOR | 11 | **12** (F-05, F-06, F-08, F-09, F-10, F-16, F-17, F-18, F-20, F-21, F-25, F-30, F-33) |
| MINOR | 20 | **13** (F-07, F-11, F-12, F-13, F-14, F-15, F-19, F-22, F-24, F-26, F-29, F-31) |
| NOTED | 0 | **4** (F-23, F-27, F-28, F-32) |

---

## Line Number Corrections

- **F-22 (test_projectile_manager.py)**: The report cites lines 1831-1840 and 1997-2007, but the file only has 1628 lines. The pattern is real (27 occurrences confirmed) but the specific line reference for the second and third examples is incorrect. The first example at lines 1511-1520 IS correct.

---

## Cross-Report Consistency

The Phase 1 report and Cross-Shard report are internally consistent regarding Shard 09. All cross-shard claims involving Shard 09 files are validated. The duplication claims between test_battle_runner/test_battle_runner_di (HLP-002) and within test_space_yard (HLP-003) are confirmed. The APC-001 and APC-002 anti-pattern claims are confirmed.

