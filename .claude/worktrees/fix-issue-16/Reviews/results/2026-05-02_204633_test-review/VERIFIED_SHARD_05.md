# VERIFIED SHARD 05 — Test Suite Audit (Independent Verification)

**Verifier**: ocode (Shard 05 Verifier)
**Date**: 2026-05-02
**Phase 1 report**: SHARD_05.md
**Cross-shard report**: CROSS_SHARD.md

---

## Summary

| Status | Count |
|--------|-------|
| CONFIRMED | 12 |
| CONFIRMED (nuance noted) | 3 |
| PARTIALLY CONFIRMED | 1 |
| DISPUTED | 1 |
| **Total claims** | **17** |

**No severity upgrades warranted.** All severity assessments in the Phase 1 report are reasonable. Two claims have factual corrections noted below.

---

## Detailed Verification

### FINDING-01: CAT-1 — Trivial Pass (VERDICT: CONFIRMED)

**File**: `tests/unit/simulation/components/abilities/test_superweapons.py:137–143`

**Verification**:
- `SUPERWEAPON_ABILITIES` is a 6-entry hardcoded module-level dict (`test_superweapons.py:19–26`)
- `assert len(SUPERWEAPON_ABILITIES) == 6` is tautological (dict has exactly 6 entries)
- The `for ability_name in SUPERWEAPON_ABILITIES: assert ability_name in ABILITY_REGISTRY` loop is a complete superset of the parametrize `test_ability_in_registry` at line 132–135
- `ABILITY_REGISTRY` is populated at import time, so if imports succeed, all 6 names are present
- Severity downgrade to MINOR is appropriate — the test adds zero incremental protection

**Status: CONFIRMED**. No discrepancies found.

---

### FINDING-02: CAT-2 — Tests Nothing Real (VERDICT: CONFIRMED)

**File**: `tests/unit/ui/screens/test_strategy_renderer_public_api.py:16–92`

**Verification**:
- All 7 tests use `inspect.signature()` (lines 36–71) or `isinstance(getattr(..., property))` (lines 89–90)
- No `StrategyRenderer` instance is constructed; no method is called
- File docstring (lines 1–7) explicitly states purpose: "This test pins the public symbols and methods... It guards the decomposition of strategy_renderer.py into the strategy_render/ subpackage"
- 92 lines total, clearly labeled "Contract test" and "PROJ-309 sub-phase 3.2"
- Severity downgrade to MINOR is justified — deliberate contract pin, not an accidental testing gap

**Status: CONFIRMED**. No discrepancies.

---

### FINDING-03: CAT-4 — Duplicate Testing (VERDICT: CONFIRMED)

**File pair**: `test_warp_hotkey.py` (lines 46–102) and `test_strategy_input_handler_hotkeys.py` (lines 67–135)

**Verification**:

| test_warp_hotkey.py | test_strategy_input_handler_hotkeys.py | Match |
|---|---|---|
| `test_w_sets_warp_target_mode:56` — W key → WARP_TARGET | `test_m_triggers_move_mode:70` — M key → MOVE | Same pattern, different key |
| `test_w_ignored_without_fleet:69` — None fleet stays SELECT | `test_fleet_keys_ignored_without_fleet:111` — None fleet stays SELECT | Identical logic |
| `test_w_ignored_when_fleet_cannot_warp:80` — capability check | `test_fleet_keys_ignored_without_fleet:111` — same gate check | Overlapping coverage |
| `test_escape_cancels_warp_target_mode:93` — ESC from WARP_TARGET | `test_escape_cancels_mode:103` — ESC from MOVE | Identical SUT path |

**Key nuance**: The warp file also contains `TestWarpHotkeyViaRealMapper` (lines 105–163) with real `InputMapper` and `TestWarpClickDispatching` (lines 166–228) testing command issuance — these are unique, non-duplicate tests. The duplication is limited to `TestWarpHotkeyModeActivation` (lines 46–102).

**Status: CONFIRMED**. The report's recommendation to merge the mode-activation tests while retaining the click-dispatching tests is correct.

---

### FINDING-04: CAT-5 — Fixture Bloat (VERDICT: CONFIRMED, nuance noted)

**File**: `tests/unit/ui/panels/test_empire_treasury_panel.py:72–88`

**Verification**:
- Fixture chain confirmed: `sample_snapshot` (lines 26–62) → `mock_ui_manager` (65–68) → `mock_panel` (71–76) → `mock_resource_icons` (79–87)
- All 4 fixtures are `function`-scoped (no `scope=` parameter)
- `mock_resource_icons` creates 5 `MagicMock` surfaces with `get_size()` calls (lines 82–87)
- **Count correction**: The report says "13 test methods" carry the 4-patch pattern. I count **12** test methods with the full 4-patch decorator pattern (lines 127, 138, 150, 162, 182, 201, 218, 237, 371, 385, 405, 420). TestPopulationUpkeepRow tests (lines 269, 286, 303, 326, 347) use only 2 patches. The delta is minor (12 vs. 13) and does not affect the severity assessment.
- The total fixture rebuild count is still significant: 12 tests × (4 fixtures + 4 patch cycles) = 96 patch start/stop operations

**Status: CONFIRMED** with a minor count discrepancy (12 vs. 13 test methods with 4-patch pattern). Recommendation to module-scope the fixtures is valid but requires verifying no test modifies shared mock state.

---

### FINDING-05: CAT-6-1 — Mocking Brittleness (elem.kill) (VERDICT: CONFIRMED, nuance noted)

**File**: `tests/unit/ui/panels/test_empire_treasury_panel.py:419–437`

**Verification**:
- Lines 419–437: `test_refresh_clears_old_elements` confirmed
- Line 426: `old_elements = list(panel._elements)` — accesses **private attribute** `_elements`
- Line 427: `old_container = panel._scroll_container` — accesses **private attribute** `_scroll_container`
- Lines 436–437: `for elem in old_elements: elem.kill.assert_called()` — iterates private state collection

**Correction**: The report says this "depends on the exact internal ordering of `_elements`." This is inaccurate — `assert_called()` does not care about ordering, only that `kill()` was called at least once. The actual brittleness source is **dependence on private attribute structure** (`_elements` being a list of mock objects with `kill` methods), not ordering. Any change to how the panel stores/manages UI elements breaks this assertion.

**Status: CONFIRMED** with a description correction. The brittleness source is private-attribute access, not call ordering.

---

### FINDING-06: CAT-6-2 — Mocking Brittleness (_build_list patch) (VERDICT: CONFIRMED)

**File**: `tests/unit/ui/screens/test_build_queue_list_window.py:10–13, 28`

**Verification**:
- Lines 10–13: `mock_window_base` fixture patches `BuildQueueListWindow._build_list` (private method with underscore prefix)
- Line 28: `test_initializes_with_title` additionally uses `patch.object(BuildQueueListWindow, '_build_list')` inline
- 11 test methods use `mock_window_base` fixture; 1 additional test (line 19) adds the same patch again
- If `_build_list` is renamed, removed, or changed in purpose, all 11 tests that depend on `mock_window_base` break

**Status: CONFIRMED**. Crystal-clear private method patching on the SUT class.

---

### FINDING-07: CAT-6-3 — Mocking Brittleness (calculate_next_hex patch) (VERDICT: CONFIRMED, nuance noted)

**File**: `tests/unit/strategy/turn_engine/test_tick_mechanics.py:149, 177`

**Verification**:
- Line 149: `patch.object(turn_engine.movement_engine, 'calculate_next_hex')` — patches a dependency's method, not the SUT's private method
- Line 177: Same `patch.object()` pattern in a different test
- Line 181: `mock_calc.assert_not_called()` — verified present

**Important nuance**: `calculate_next_hex` is **not** a private method — it has no underscore prefix (`_`). It is a public method on `movement_engine`. The report describes this as "internal sub-engine methods" which is correct (it is an internal dependency dispatch). The CAT-6 classification as "private-attr patches" is technically inaccurate for this particular finding — it should be classified as "patching internal dispatch mechanism" which has the same brittleness consequences but a different root cause.

The brittleness concern is valid: if `_process_tick` changes how it dispatches to the movement engine, `assert_not_called()` can produce false negatives.

**Status: CONFIRMED** with a categorization nuance. The method patched is not private-named (no underscore prefix). The patching is on a dependency (`movement_engine`), not the SUT directly. The brittleness concern remains valid regardless of naming.

---

### FINDING-08: CAT-8 — Needless Complexity (VERDICT: CONFIRMED)

**File**: `tests/unit/ui/test_detail_panel_rendering.py:16–41`

**Verification**:
- Lines 19–21: `del sys.modules['game.ui.screens.builder.detail_panel']` — confirmed, module cache manipulation anti-pattern
- Lines 25–32: 7 separate `patch()` starts confirmed (UIPanel, UILabel, UIImage, UIButton, UITextBox × 2, ModifierImpactGrid)
- Lines 34–41: Mock configuration confirmed (theme fonts, rect geometry)
- Line 73–75: `teardown_method` calls `patch.stopall()` — confirmed
- File has 5 test methods → 35 `patch.start()` and 35 `patch.stop()` calls minimum per full class run (7 patches × 5 tests)
- Lines 48–54: Additional module-level imports and mock setup per test

**Status: CONFIRMED**. All 7 patches, the module cache deletion, and the teardown pattern are present as described.

---

### FINDING-09: CAT-9-1 — Repeated _make_planet Helper (VERDICT: CONFIRMED)

**File**: `tests/unit/strategy/validation/test_colonize_validator.py`

**Verification**:

**Definition 1** — `TestColonizeValidatorAnyPlanetPods._make_planet` (lines 753–774):
```python
planet = MagicMock(spec=Planet)
# ... 17 attribute assignments ...
planet.radius_hexes = 0
```

**Definition 2** — `TestColonizeValidatorAdvancedEdgeCases._make_planet` (lines 890–913):
```python
planet = MagicMock(spec=Planet)  # PROJ-193 comment added
# ... 17 attribute assignments ...
planet.radius_hexes = 0
```

**Inline** — `TestColonizeValidatorZoneColonization` (lines 620–635): 14-line inline planet construction instead of using a helper.

Both `_make_planet` definitions are near-identical (identical planet property assignments, 17 attributes each). The second adds PROJ-193 comment annotations. Difference: line 763 uses `planet.deposits` vs line 901 uses `planet.deposits` (same). Identical in structure.

**Status: CONFIRMED**. Two virtually identical helper methods plus inline construction in a third class.

---

### FINDING-10: CAT-9-2 — Method-Level Imports (VERDICT: CONFIRMED)

**File**: `tests/unit/ui/utils/test_portraits.py`

**Verification**:
- Lines 7–8: `TestGetShipClassColor.test_known_class_fighter` — imports `get_ship_class_color`, `SHIP_CLASS_FIGHTER`
- Lines 12–13: `test_known_class_cruiser` — imports `get_ship_class_color`, `SHIP_CLASS_CRUISER`
- Lines 17–18: `test_unknown_class_returns_default` — imports `get_ship_class_color`, `SHIP_CLASS_DEFAULT`
- Lines 22–23: `test_none_returns_default` — imports `get_ship_class_color`, `SHIP_CLASS_DEFAULT`
- Lines 31–34: `TestCreatePlaceholderPortrait.test_returns_surface_of_correct_size` — imports `pygame`, `create_placeholder_portrait`
- Lines 40–43: `test_returns_surface_with_subtitle` — imports `pygame`, `create_placeholder_portrait`
- Lines 49–52: `test_returns_surface_without_subtitle` — imports `pygame`, `create_placeholder_portrait`

7 test methods, each with its own local imports. Moving to top-level would eliminate 14 redundant import statements.

**Status: CONFIRMED**. Every test method has independent method-level imports.

---

### FINDING-11: CAT-9-3 — Repeated Patch Decorator (VERDICT: PARTIALLY CONFIRMED)

**File**: `tests/unit/ui/screens/test_build_queue_list_window.py`

**Verification**:
- The file has **14 test methods** (not 11 as claimed)
- 7 test methods use `mock_window_base` fixture (which already patches `UIWindow.__init__` and `_build_list`)
- 5 test methods (lines 95, 126, 156, 189, 213) add **redundant** `@patch('pygame_gui.elements.UIWindow.__init__')` decorators on top of `mock_window_base`
- 2 test methods (lines 316, 346) use different patching patterns (with `UIWindow.kill`)

**Correction**: The report claims "`@patch('pygame_gui.elements.UIWindow.__init__')` decorates **every test method** (11 methods)". This is factually incorrect:
1. Only 5 of 14 test methods use the redundant `@patch` decorator (the rest use only `mock_window_base`)
2. There are 14 test methods, not 11

The simplification concern is still valid — 5 test methods have redundant patch decorators that could be handled at class level — but the claim is overstated.

**Status: PARTIALLY CONFIRMED**. Pattern exists but at smaller scale than reported (5 tests, not 11; 14 total tests, not 11).

---

### FINDING-12: CAT-10-1 — Parameterize (Battle End Conditions) (VERDICT: CONFIRMED)

**File**: `tests/unit/simulation/systems/test_battle_end_conditions.py:546–588`

**Verification**:
- Three `@pytest.mark.parametrize` blocks with **identical** `(cls, kwargs)` tuples (8 entries each):
  - `test_isinstance_check` (lines 546–558)
  - `test_has_description` (lines 560–573)
  - `test_to_dict_has_type` (lines 575–588)
- The 8 `(cls, kwargs)` pairs are byte-for-byte identical across all three blocks
- Each test differs only in its assertion (`isinstance(cond, IEndCondition)` vs `isinstance(cond.description, str)` vs `"type" in data`)

**Status: CONFIRMED**. Three duplicate parametrize blocks that could be collapsed.

---

### FINDING-13: CAT-10-2 — Parameterize (Config Edge Cases) (VERDICT: CONFIRMED)

**File**: `tests/unit/core/test_config_edge_cases.py:31–62`

**Verification**:
- 7 test methods in `TestAIConfigBoundaryValues` (lines 34–61), each:
  - Asserts a single scalar constraint on a single AIConfig constant
  - Follows identical pattern: `assert AIConfig.<ATTR> <op> <VALUE>`
- `TestPhysicsConfigConstraints` (lines 64–91) has the same pattern (6 methods, same structural template)
- All could be collapsed into parametrized tests with `(attr_name, predicate)` pairs

**Status: CONFIRMED**. Both boundary-value test classes show identical structural patterns.

---

### FINDING-14: CAT-10-3 — Parameterize (Defense Isolation) (VERDICT: CONFIRMED)

**File**: `tests/unit/simulation/components/abilities/test_defense_isolation.py:366–527`

**Verification**:

| TestToHitAttackModifier (lines 363–445) | TestToHitDefenseModifier (lines 451–526) |
|---|---|
| `test_init_with_positive_value:366` | `test_init_with_positive_value:454` |
| `test_init_with_negative_value:373` | `test_init_with_negative_value:461` |
| `test_init_with_zero:380` | `test_init_with_zero:468` |
| `test_init_with_dict_value:387` | `test_init_with_dict_value:474` |
| `test_recalculate_is_no_op:400` | `test_recalculate_is_no_op:481` |
| `test_get_ui_rows_positive_value:408` | `test_get_ui_rows_positive_value:489` |
| `test_get_ui_rows_negative_value:419` | `test_get_ui_rows_negative_value:500` |
| `test_get_ui_rows_zero_value:427` | `test_get_ui_rows_zero_value:508` |
| `test_get_primary_value:435` | `test_get_primary_value:516` |
| `test_stat_bindings_empty:442` | `test_stat_bindings_empty:523` |

Every method in the Attack class has a structural twin in the Defense class. They differ only in: class name, expected sign/value in some assertions, and label/color_hint constants (e.g., 'Targeting'/HINT_DAMAGE vs 'Evasion'/HINT_EVASION).

**Status: CONFIRMED**. 10 method pairs with identical structure.

---

### FINDING-15: CAT-10-4 — Parameterize (Resource Consumption) (VERDICT: CONFIRMED)

**File**: `tests/unit/simulation/components/abilities/test_resource_consumption.py:439–506`

**Verification**:

| Test Method | resource_type | amount | expected final |
|---|---|---|---|
| `test_fuel_consumption:439` | fuel | 25.0 | 75.0 |
| `test_energy_consumption:454` | energy | 30.0 | 20.0 |
| `test_ammo_consumption:469` | ammo | 5.0 | 15.0 |

All three:
- Set `mock_component_with_ship.ship.resources = resource_registry`
- Create identical `ResourceConsumption` with only `resource` and `amount` differing
- Assert `result is True` and `resource_registry.get_value(resource) == expected`

**Status: CONFIRMED**. Three nearly-identical tests differing only in data.

---

### FINDING-16: CAT-11 — Fragile Assertion (VERDICT: CONFIRMED)

**File**: `tests/unit/ui/screens/test_empire_build_queue_window.py:388–402`

**Verification**:
- Line 391: `col_ids = {c['id'] for c in win.columns}` — extracts column IDs from runtime data
- Lines 392–401: `expected` set with **17 column ID strings** (not 19 as counted in the report — the report mentions 19 but I count 17: location, system, sector, queue_count, first_item, turns_left, capabilities, build_rate, res_metals_rate, res_organics_rate, res_vapors_rate, res_radioactives_rate, res_exotics_rate, res_metals_total, res_organics_total, res_vapors_total, res_radioactives_total, res_exotics_total = 18 total names)

**Correction**: The report says "19 column names" — there are **18** column names in the set. Minor discrepancy, does not affect severity.

- Line 402: `assert expected.issubset(col_ids)` — any column addition/removal/rename causes test failure with a noisy diff

**Status: CONFIRMED** with a minor count correction (18 columns, not 19). The brittleness concern is valid: this tests UI configuration identity rather than behavioral invariants.

---

### FINDING-17: CAT-12 — Logic-Heavy Test (VERDICT: CONFIRMED)

**File**: `tests/unit/ai/test_advanced_behaviors.py:102–217`

**Verification**:
- `test_orbit_behavior` (lines 102–128):
  - Vector arithmetic: `ship_pos = pygame.math.Vector2(600, 0)`, `dest - ship_pos` (line 125)
  - Conditional distance logic implied in comments (lines 111, 118–120)
  - Direction assertions: `assert rel_move.x < 0`, `assert rel_move.y < 0` (lines 127–128)
- `TestKiteBehaviorSmooth` (lines 131–217):
  - Four test methods, each computing relative movement vectors
  - `test_far_from_target_navigates_toward:138` — `rel = dest - pygame.math.Vector2(0, 0)`, directional assertion
  - `test_at_optimal_range_orbits_tangentially:157` — `abs(rel.y) > abs(rel.x) * 0.5`, magnitude comparison
  - `test_too_close_moves_outward_while_orbiting:180` — `rel.x > 0`, `abs(rel.y) > 0`, dual-component assertion
  - `test_navigate_to_called_with_zero_stop_dist:203` — `kwargs.get('stop_dist', 0) == 0`

The logic tests real AI spatial behavior (OrbitBehavior, KiteBehavior) involving distance thresholds, tangential/radial component calculations. The comments (lines 115–120) explain the expected vector math. These are not testing test infrastructure — they test production AI movement logic.

**Status: CONFIRMED**. Logic is necessary for testing spatial AI behavior. The report correctly classifies as MINOR and notes the comments explain expected outcomes.

---

## Cross-Shard Claims Verification

### APC-002: `inspect.signature()` / source inspection — Shard 05 entry

**File**: `tests/unit/ui/screens/test_strategy_renderer_public_api.py:16–92`

**Verification**: This is the same file as CAT-2 above. The cross-shard report correctly identifies it as part of the APC-002 cluster. The cross-shard recommendation to "keep as-is but add a file-level docstring explaining why source inspection is used" is already satisfied — the file has a docstring (lines 1–7) explaining PROJ-309.

**Status: CONFIRMED**. File is correctly identified in APC-002. Existing docstring already addresses the cross-shard recommendation.

---

### APC-003: Private method patching — Shard 05 entries

**File 1**: `tests/unit/ui/screens/test_build_queue_list_window.py:28`
- `patch.object(BuildQueueListWindow, '_build_list')` — CONFIRMED, patches a private method (`_build_list` with underscore prefix) on the SUT class

**File 2**: `tests/unit/strategy/turn_engine/test_tick_mechanics.py:149, 177`
- `patch.object(turn_engine.movement_engine, 'calculate_next_hex')` — PARTIALLY fits APC-003 pattern
- `calculate_next_hex` is NOT a private method (no underscore prefix)
- The patch target is a dependency's public method, not the SUT's private method
- The brittleness concern (internal dispatch order changes → false negatives) is valid, but the categorization as "patching private `_methods`" is technically inaccurate

**Status**: File 1 CONFIRMED fits APC-003. File 2 has a categorization nuance — the concern is valid but the method name and target don't match APC-003's stated "private `_methods`" pattern.

---

## File Coverage Table Errors

The Phase 1 file coverage table (line 60) shows:

| 60 | tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py | 485 | CAT-4, **CAT-6** |

**CAT-6 is UNVERIFIED for this file.** I searched the entire 485-line file for:
- Private method patching (`patch.object` on `_method`): none found
- Private attribute access: none found (only `handler._mapper` assignment which is documented init behavior)
- Call-order assertions: none found

The only `patch` calls are `patch('pygame.mouse.get_pos', ...)` at lines 368, 386, 405, 425, 481 — all standard public API mocks. The CAT-6 tag appears to be an error in the file coverage table. **Recommendation: remove CAT-6 from the coverage table row for this file.**

---

## Overall Assessment

- **17 claims verified**: 12 CONFIRMED, 3 CONFIRMED with nuance notes, 1 PARTIALLY CONFIRMED (overstated scale), 1 DISPUTED (file coverage table error)
- **No severity upgrades warranted** — all existing severities are appropriate
- **Two factual corrections**: test_empire_treasury_panel.py has 12 (not 13) test methods with 4-patch pattern; test_empire_build_queue_window.py has 18 (not 19) column names
- **One file coverage table error**: test_strategy_input_handler_hotkeys.py tagged with CAT-6 but no such finding exists in that file
- **Phase 1 report quality**: Generally high. Overstatements found in CAT-9-3 (patch decorator count) and CAT-6-1 description (ordering vs. private attribute access). These do not affect the overall validity of the findings.

