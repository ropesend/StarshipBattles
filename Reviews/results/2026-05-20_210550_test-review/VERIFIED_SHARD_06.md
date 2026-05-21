# VERIFIED_SHARD_06.md — Shard 06 Test Audit Verification

## Summary

- **Claims verified**: 19 (from SHARD_06.md) + 4 (cross-shard claims involving shard 06 files)
- **CONFIRMED**: 14
- **DISPUTED**: 4
- **INCONCLUSIVE**: 0
- **Severity changes**: 4 MAJOR (2 downgraded to MINOR, 2 disputed as incorrect); 1 MINOR disputed

---

## SHARD_06.md Claim Verifications

### Claim 1 — CAT-5: test_weapons_report_layout.py:16-35 [MAJOR → DOWNGRADED TO MINOR]

**Original claim**: Function-scoped autouse fixture creates real pygame display for every test; should be class-scoped.

**Verification**: `tests/unit/ui/test_weapons_report_layout.py:14-36`

The fixture is function-scoped autouse. However:
- There is exactly **one** test method in the class (`test_button_creation_widths` at line 38). Changing scope from function to class has zero practical effect.
- The fixture sets instance attributes via `self.surface` / `self.manager`, which is idiomatic for function-scoped (class-scoped fixtures normally use `request.cls` or return values).
- `conftest.py` already force-sets `SDL_VIDEODRIVER=dummy` before imports — line 21 is redundant.
- The fixture `yield`s without cleanup (no `pygame.quit()` / `manager.clear_and_reset()`).

**Verdict**: **CONFIRMED (downgraded to MINOR)**. The fixture does unnecessary pygame init (already handled by conftest) but with only one test, the scope concern is negligible. The real issue is the missing teardown, not the scope.

---

### Claim 2 — CAT-8: test_design_selector_window.py:489-498 [MINOR]

**Original claim**: 5 nested `with patch()` blocks repeat identically in 3 tests.

**Verification**: `tests/unit/ui/screens/test_design_selector_window.py:489-498, 509-517, 534-543`

The 6-deep nested patch stack appears verbatim at:
- Line 490-496 (`test_design_row_layout`)
- Line 509-515 (`test_design_row_with_spaces_in_design_id`)
- Line 534-540 (`test_design_row_with_fullstops_in_design_id`)

All three tests are in `TestDesignSelectorUICreation` class. The patch names and return values are identical across all three.

**Verdict**: **CONFIRMED**. The duplicate is exact and mechanically verifiable. Extracting a shared context-manager helper would eliminate ~40 lines of duplication.

---

### Claim 3 — CAT-10: test_design_selector_window.py:447-546 [MINOR]

**Original claim**: `test_rebuild_design_list_clears_existing` and `test_rebuild_design_list_creates_rows` share nearly identical setup; three design-ID tests differ only in `design_id` and expected assertion.

**Verification**: `tests/unit/ui/screens/test_design_selector_window.py:450-546`

Analysis of the 5 tests:
- `test_rebuild_design_list_clears_existing` (450-463): Tests `kill()` behavior — asserts rows are killed.
- `test_rebuild_design_list_creates_rows` (465-480): Tests row creation count — asserts `call_count == 2`.
- These two test **different behaviors** (killing vs creating). Parametrizing them would obscure intent.
- Three design-ID sanitization tests (482-498, 500-523, 525-546): These DO share substantial boilerplate and differ only in `design_id` and which sanitization character is asserted. The first (`test_design_row_layout`) differs slightly — it only asserts `row is not None` without checking `object_id`. The latter two check for absence of `' '` and `'.'` respectively.

**Verdict**: **CONFIRMED (qualified)**. The three design-ID sanitization tests are good candidates for extraction of a shared `_assert_design_row_with_id(design_id, forbidden_chars)` helper. The rebuild tests (clear/create) are functionally distinct and should NOT be parametrized together.

---

### Claim 4 — CAT-11: test_design_selector_window.py:803-814 [MINOR]

**Original claim**: `call_args[1]["filters"]["vehicle_type"]` uses positional indexing; fragile to signature changes. Same pattern at lines 189, 201, 215.

**Verification**: `tests/unit/ui/screens/test_design_selector_window.py:813-814`

```python
call_args = library.search_designs.call_args
assert call_args[1]["filters"]["vehicle_type"] == "Mine"
```

The same `call_args[1]` pattern appears at lines 189, 202, 215. `call_args` is a `tuple(args, kwargs)` — `[1]` accesses kwargs by position in the tuple, not by argument position in the function call. The real risk: if `search_designs` is ever called with positional args instead of keyword args, `call_args[1]` (the kwargs dict) would be missing those values. `.kwargs` is the idiomatic accessor and self-documents intent.

**Verdict**: **CONFIRMED**. Using `call_args.kwargs` is more robust and idiomatic. The claim's stated rationale ("third argument breaks it") is slightly inaccurate (it's about positional vs keyword args, not arg count), but the conclusion is correct. Affects ~130 LOC across the file.

---

### Claim 5 — CAT-10: test_superweapon_order_pop_matrix.py:119-509 [MINOR]

**Original claim**: 5 test classes × 3 tests each = 15 near-identical tests; parametrize across superweapon type.

**Verification**: `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py:119-510`

Examining each class:
- **TestImplodePlanetOrderPop** (119-193): Requires planet location, `galaxy._planet_to_system` mapping.
- **TestStellerateStarOrderPop** (202-257): Only **2** tests (not 3 — no `failure_no_ship` test). Success asserts `fleet_consumed is True` and `fleet.pop_order.assert_not_called()` — fundamentally different assertion (negation). Uses `SystemDestroyer`-patched path.
- **TestOpenWarpPointOrderPop** (264-338): Requires two systems (source + target), `galaxy.name_map`, warp point setup.
- **TestCloseWarpPointOrderPop** (345-427): Requires `WarpPoint` objects, `destination_id` + `target_hex` in order target.
- **TestCreateDysonSphereOrderPop** (434-510): No planet/warp-point setup; `no_target` variant tests "fleet not at a system" rather than "target is None".

The setup code for each weapon type is **substantially different**:
- Different process methods (`process_implode_planet`, `process_open_warp_point`, etc.)
- Different galaxy/system/planet/warp-point scaffolding
- Different `Order` target structures (planet object vs `{'target_system_name': ...}` vs `{'destination_id': ..., 'target_hex': ...}`)
- Stellerate success path asserts fleet consumption instead of pop_order

Parametrizing would require a large tuple with conditional branching for each type's unique setup and assertions, making the tests harder to read and debug individually.

**Verdict**: **DISPUTED**. While the tests follow a common three-outcome pattern (success / no-target / no-ship), the per-weapon setup and assertion code differ too significantly for productive parametrization. The claim's characterization of "near-identical bodies" is inaccurate. The current per-weapon-class structure is deliberate and appropriate for characterization tests that pin behavior across fundamentally different code paths.

---

### Claim 6 — CAT-10: test_strategy_input_handler_hotkeys.py:70-175 [MINOR]

**Original claim**: 7 fleet mode-activation hotkey tests share identical structure; parametrize.

**Verification**: `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py:70-175`

Tests verified:
- M/J/C/T mode-activation tests (70-101): 4 tests, identical structure (key → mode)
- Escape cancels mode (103-109): starts from non-default mode
- Ignore-without-fleet tests (111-134): 3 tests, identical structure (key → SELECT when no fleet)
- W-triggered tests (144-175): 4 tests with capability checking (`can_use_warp`)

The M/J/C/T tests are genuinely near-identical and are good candidates for parametrization. The W tests add capability-check complexity. The ignore-without-fleet tests form a second cluster.

**Verdict**: **CONFIRMED**. The M/J/C/T cluster and the ignore-without-fleet cluster are strong parametrization candidates. The claim's scope of 7 tests is reasonable for the base mode-activation cluster.

---

### Claim 7 — CAT-10: test_strategy_input_handler_hotkeys.py:178-208 [MINOR]

**Original claim**: 4 zoom tests identical structure; parametrize.

**Verification**: `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py:181-208`

All 4 tests follow the exact same pattern:
1. Create handler
2. Call `handle_event(_keydown(key, modifiers))`
3. Assert `.assert_called_once()` on a camera-nav method
4. Assert `.assert_called()` on `ui.handle_event`

Differ only in `(key, modifiers, camera_method_name)`.

**Verdict**: **CONFIRMED**. Ideal parametrization target. No caveats.

---

### Claim 8 — CAT-10: test_strategy_input_handler_hotkeys.py:211-317 [MINOR]

**Original claim**: 11 button-hotkey tests + 3 ignore variants; parametrize.

**Verification**: `tests/unit/ui/screens/test_strategy_input_handler_hotkeys.py:214-317`

The 14 tests span simple key→action mappings. However, the action targets differ:
- Some call methods on `mock_scene` directly (e.g., `advance_turn`)
- Some call methods on `mock_scene.ui` (e.g., `open_planet_list`)
- Some call methods with arguments (`cycle_selection("colony", -1)`)
- The O/F tests include additional assertion on the fleet argument passed
- Ignore variants assert `assert_not_called()` instead of `assert_called_once()`

These could be parametrized into 2 groups (simple trigger + complex trigger) but the assertion target diversity (different mock sub-objects, different verification patterns) adds meaningful parametrize-tuple complexity.

**Verdict**: **CONFIRMED (qualified)**. Parametrization is feasible but would require grouping into at least 2 distinct parametrize sets (simple-action vs fleet-dependent). The claim's estimate of 2-3 parametrized tests collapsing from ~13 is reasonable.

---

### Claim 9 — CAT-7: test_race_description_llm_controller.py:325 [MAJOR]

**Original claim**: `time.sleep(0.02)` introduces latency and flaky timing; replace with `_wait_until` polling loop.

**Verification**: `tests/unit/strategy/services/test_race_description_llm_controller.py:313-374`

- Line 133: `_wait_until(predicate, timeout=2.0)` polling helper exists in the file.
- Line 325: `time.sleep(0.02)` before cancel — used as a blind wait for the worker thread to enter blocking state.
- Line 343: Same pattern in `test_cancel_all`.
- Line 364: Same pattern in `test_cancel_socio_while_running`.
- After the sleep, `_wait_until` IS already used to verify the final CANCELLED state.

The `time.sleep(0.02)` is a race-prone blind wait. The replacement pattern would be:
```python
controller.generate_bio()
_wait_until(lambda: controller.bio_status == FieldStatus.RUNNING)
controller.cancel_bio()
_wait_until(lambda: (controller.update(), controller.bio_status == FieldStatus.CANCELLED)[1])
```

This eliminates the timing race and reduces the worst-case wait from fixed 20ms to polling-based transition detection.

**Verdict**: **CONFIRMED**. Legitimate CAT-7 (flaky timing) issue. Three identical blind-sleep-then-cancel patterns exist. The `_wait_until` helper at line 133 is already imported and available.

---

### Claim 10 — CAT-9: test_empire_build_queue_formatter.py:235-270 [MINOR]

**Original claim**: `get_resource_rate_text` and `get_resource_total_text` imported inside each test method body (8 times).

**Verification**: `tests/unit/ui/screens/test_empire_build_queue_formatter.py:235-270`

Lines 235, 241, 250, 258, 266 each contain:
```python
from game.ui.screens.empire_build_queue_formatter import get_resource_rate_text
```
This is inside `TestGetResourceRateText` (5 methods). The pattern repeats in `TestGetResourceTotalText` (additional methods at lines 278+).

**Verdict**: **CONFIRMED**. The same import appears in each test method body. These are pure functions with no side effects — imports belong at module level.

---

### Claim 11 — CAT-5: conftest.py:12-35 (conflict_resolution) [MAJOR → DISPUTED]

**Original claim**: `mock_fleet` and `mock_empire` return stateless MagicMock objects; should be session-scoped.

**Verification**: `tests/unit/strategy/conflict_resolution/conftest.py:12-35`

```python
@pytest.fixture
def mock_fleet():
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    ...

@pytest.fixture
def mock_empire():
    empire = MagicMock()
    empire.id = 0
    ...
```

**Dispute**: The claim's premise that these are "stateless" is incorrect. `MagicMock` objects inherently accumulate call state (`.call_args_list`, `.call_count`, `.called`, etc.). If a test asserts `mock_fleet.append_orders.assert_called_once()` and a previous test also called `append_orders`, the mock's call count would be 2, causing the second test to fail. Even if current tests don't test call counts, future additions could, creating non-deterministic failures. Session scope for mocks is a well-known anti-pattern for this reason. The function scope is correct and safe.

**Verdict**: **DISPUTED**. MagicMock objects are NOT stateless — they accumulate call history that would leak across tests under session scope. Function scope is the correct default for all mock fixtures. The claim's severity should be **NONE** (current code is correct).

---

### Claim 12 — CAT-5: conftest.py:6-35 (armor_mechanics) [MAJOR → DISPUTED]

**Original claim**: `mock_ship_with_emissive` and `mock_ship_base` return stateless MagicMock fixtures; should be session-scoped.

**Verification**: `tests/unit/simulation/armor_mechanics/conftest.py:6-35`

```python
@pytest.fixture
def mock_ship_with_emissive():
    ship = MagicMock()
    ship.is_alive = True
    ship.emissive_armor = 15
    ship.recalculate_stats = MagicMock()
    ship.update_derelict_status = MagicMock()
    ...
```

**Dispute**: Same issue as Claim 11. These are MagicMock objects with attribute-level MagicMock instances (`recalculate_stats`, `update_derelict_status`). All accumulate call state. The `hp`, `shields`, etc. attributes are mutable integer values — if any armor test modifies `ship.hp` or `ship.current_shields` (as armor tests commonly do), that mutation persists across tests under session scope.

**Verdict**: **DISPUTED**. Same rationale as Claim 11. Function scope is correct. Severity should be **NONE**.

---

### Claim 13 — CAT-6: test_hex_outlines.py:101-106 [MAJOR]

**Original claim**: Asserts on `renderer._draw_inner_hex.call_args_list` matching exact float positions; fragile to hex math changes.

**Verification**: `tests/unit/ui/screens/strategy_render/test_hex_outlines.py:36-37, 101-106`

The renderer context (line 36) sets `_draw_inner_hex=MagicMock()`. At lines 101-106:
```python
assert renderer._draw_inner_hex.call_args_list == [
    call(screen, 0.0, 0.0, 0.88, HEX_OUTLINE_PLAYER_OWNED),
    call(screen, 15.0, 8.660254037844386, 0.88, HEX_OUTLINE_OCCUPIED),
    call(screen, 30.0, 17.32050807568877, 0.90, HEX_OUTLINE_PLAYER_OWNED),
    call(screen, 30.0, 17.32050807568877, 0.80, HEX_OUTLINE_OCCUPIED),
]
```

Issues confirmed:
1. `_draw_inner_hex` is a private method — testing private API surface.
2. Exact float values `8.660254037844386` and `17.32050807568877` are derived from hex geometry (`10 * √3/2 ≈ 8.660254`). Any change to hex math precision (e.g., using `math.sqrt(3)` vs `numpy.sqrt(3)`, float32 vs float64, or hex_size change) breaks these assertions without any behavioral defect.
3. The assertion pattern is a full-list equality check rather than individual `assert_any_call()` — a single pixel shift breaks the entire test.

**Verdict**: **CONFIRMED**. Strong CAT-6 violation. Testing private methods with exact float literals is doubly fragile.

---

### Claim 14 — CAT-6: test_fleet_report_sidebar.py:38-58 [MAJOR]

**Original claim**: `_create_sidebar` patches internal modules (UILabel, UIButton) from two different module paths.

**Verification**: `tests/unit/ui/screens/test_fleet_report_sidebar.py:38-48`

```python
with patch('game.ui.screens.fleet_report_sidebar.UILabel'), \
     patch('game.ui.widgets.column_toggle_section.UILabel'):
    with patch('game.ui.screens.fleet_report_sidebar.UIButton') as mock_btn_cls, \
         patch('game.ui.widgets.column_toggle_section.UIButton') as _shared_btn_cls:
```

The comment at lines 35-37 documents the PROJ-319 reason: column toggles moved to `game.ui.widgets.column_toggle_section`, requiring dual-module patching. This is a 4-patch × 3-depth nested stack (counting `TriStateFilterWidget` at line 49). The code itself acknowledges this is suboptimal with `DUP-X-08` reference.

**Verdict**: **CONFIRMED**. The nested patch-stack mocks internal implementation modules and is inherently brittle. The documented reason doesn't justify the pattern — it confirms the fragility is known. The suggestion to use `make_ui_widget` factory pattern would be a cleaner abstraction.

---

### Claim 15 — CAT-5: conftest.py:17-89 (density) [MAJOR → DISPUTED]

**Original claim**: All 8 primitive fixtures are function-scoped; should be session-scoped.

**Verification**: `tests/unit/strategy/generation/density/conftest.py:17-93`

Examining each fixture:
- `radial_primitive` (17-20): Returns `RadialPrimitive(...)` — could be session-scoped if truly immutable.
- `ring_primitive` (23-26): Returns `RingPrimitive(...)` — same.
- `spiral_arm_primitive` (29-35): Returns `SpiralArmPrimitive(...)` — same.
- `linear_primitive` (38-44): Returns `LinearPrimitive(...)` — same.
- `noise_primitive` (47-50): Returns `NoisePrimitive(...)` — same.
- `geometric_primitive` (53-59): Returns `GeometricPrimitive(...)` — same.
- **`seeded_rng`** (62-65): Returns `random.Random(12345)` — **mutable**. `random.Random` is a stateful PRNG. Tests that consume random bytes would see a different sequence depending on which tests ran before them. Session scope would be **incorrect**.
- **`simple_density_map`** (74-79): Returns `DensityMap(radius=1000)` with `dm.add_primitive(radial_primitive, weight=1.0)`. `DensityMap` is **mutable** (has `.add_primitive()`). Session scope would allow test A's additions to persist into test B.
- **`all_primitive_types`** (82-93): Returns `(name, cls(**kwargs))` tuple — the tuples are immutable but the primitive objects depend on the class implementations.

**Dispute**: At minimum, `seeded_rng` and `simple_density_map` (and anything depending on `simple_density_map`) MUST stay function-scoped. For the plain primitive fixtures, the safety depends on whether `RadialPrimitive` etc. are truly immutable value objects — which cannot be confirmed without reading their implementations. The blanket recommendation to session-scope all 8 is incorrect.

**Verdict**: **DISPUTED (downgraded to MINOR)**. The 6 primitive fixtures *might* be safe to session-scope, but `seeded_rng` and `simple_density_map` definitely cannot be. The claim's blanket recommendation is unsafe.

---

### Claim 16 — CAT-6: test_characterization.py:92 [MAJOR]

**Original claim**: Tests patches `engine._auto_disable_components_for_resource`, a private method of the SUT.

**Verification**: `tests/unit/strategy/consumable_management_engine/test_characterization.py:83-101`

```python
def test_failed_consume_resource_triggers_auto_disable_and_returns_depletion(
    mock_registries, mock_empire, mock_fleet, mock_ship,
):
    mock_ship.consume_resource.return_value = False
    engine = ConsumableManagementEngine(registries=mock_registries)
    with patch.object(engine, "_auto_disable_components_for_resource",
                      return_value=["engine_1"]) as mock_dis:
        result = engine.process_per_turn_consumption(1, [mock_empire])
    mock_dis.assert_called_once_with(mock_ship, "fuel")
    assert result[0].components_disabled == ["engine_1"]
```

Issues confirmed:
1. `_auto_disable_components_for_resource` is a **private** method on the **SUT** (line 92: `patch.object(engine, ...)`) — the code under test.
2. Mocking it replaces the real implementation, so the test cannot detect regressions in `_auto_disable_components_for_resource` itself.
3. The test verifies `mock_dis.assert_called_once_with(mock_ship, "fuel")` — testing that the private method was called, not that it produced the correct result.
4. The `components_disabled` check (line 101) is tautological: the mock returns `["engine_1"]`, and the test asserts the result contains `["engine_1"]`. It verifies passthrough, not correctness.

**Verdict**: **CONFIRMED**. Strong CAT-6 violation. Mocking a private method of the SUT makes the test fragile and masks implementation changes.

---

### Claim 17 — CAT-12: test_colony_output.py:436-452 [MINOR]

**Original claim**: Test is logic-heavy — computes `rate * 2.0` and asserts ratio with fragile `rel=1e-9` tolerance.

**Verification**: `tests/unit/strategy/formulas/test_colony_output.py:436-451`

```python
def test_high_happiness_scales_logistic_term(self):
    rate_normal = projected_growth_rate(planet, pop_normal, race, cfg)
    rate_giddy  = projected_growth_rate(planet, pop_giddy, race, cfg)
    assert rate_giddy == pytest.approx(rate_normal * 2.0, rel=1e-9)
```

The test re-derives the expected relationship internally (happiness 2.0 → 2× rate). There is no pre-computed expected value. The `rel=1e-9` tolerance is appropriate for the computation being tested but combined with re-derivation, this is moderately logic-heavy.

**Verdict**: **CONFIRMED**. CAT-12 applies — the test is moderately logic-heavy. MINOR severity is appropriate. The ratio approach (2× scaling) is conceptually sound (testing the linear happiness term) but would be stronger with a pre-computed expected value.

---

### Claim 18 — CAT-11: test_design_report_panel.py:267-273 [MINOR]

**Original claim**: `assert width == 750` — hardcoded constant.

**Verification**: `tests/unit/ui/panels/test_design_report_panel.py:267-273`

```python
def test_width_returns_750(self):
    panel = _bypass_init_panel()
    width = panel.get_width_required()
    assert width == 750
```

The value 750 is a magic number. If the panel width constant changes in the source, this test fails spuriously.

**Verdict**: **CONFIRMED**. Classic fragile-assertion. Should assert against the named constant or use property-based assertions (`width > 0`).

---

### Claim 19 — CAT-11: test_workshop_event_router_select_component.py:79-91 [MINOR]

**Original claim**: Test reimplements bridge mass formula locally; fragile to formula changes.

**Verification**: `tests/unit/ui/screens/test_workshop_event_router_select_component.py:79-91`

```python
expected = 50.0 * (2000.0 / 1000.0) ** 0.5
assert gui.controller.dragged_item.mass == pytest.approx(expected, abs=0.1)
```

The formula `50 * sqrt(2000/1000)` is duplicated from production code. Changing the formula in production would cause test failure with a wrong expected value while production code is correct.

**Verdict**: **CONFIRMED**. Formula duplication is an anti-pattern. Should assert on properties (`mass > 0`, `ship is gui.ship`) and rely on dedicated formula tests for regression.

---

## Cross-Shard Claim Verifications (Shard 06 files)

### DUP-005: `_make_empire(colonies=None)` — Shard 06 reference

**Claim**: `tests/unit/strategy/engine/test_component_activation_engine.py:41` is attributed to Shard 06 in CROSS_SHARD.md DUP-005.

**Verification**: This file is actually in **Shard 09** (confirmed by `SHARD_CONFIG.json` line matching). CROSS_SHARD.md DUP-005 incorrectly attributes it to Shard 06. The same file is correctly attributed to Shard 09 in HLP-006.

Regardless of shard attribution, the code at `test_component_activation_engine.py:41-46` does contain the `_make_empire(colonies=None)` pattern as described — this is independently verified.

**Verdict**: **CONFIRMED (with cross-shard attribution errata)**. The `_make_empire` pattern duplication claim is valid. CROSS_SHARD.md DUP-005 has an attribution error — this file belongs to Shard 09, not Shard 06.

---

### HLP-002: `MockPlanetType(Enum)` — Shard 06 reference

**Claim**: `tests/unit/strategy/validation/test_colonize_validator.py:21` defines `MockPlanetType` with `CONTINENTAL`, `ICE_DWARF`, `DYSON_SPHERE`.

**Verification**: `tests/unit/strategy/validation/test_colonize_validator.py:21-25`
```python
class MockPlanetType(Enum):
    CONTINENTAL = "CONTINENTAL"
    ICE_DWARF = "ICE_DWARF"
    DYSON_SPHERE = "DYSON_SPHERE"
```
Matches the cross-shard claim. This variant has 3 values (some others have 2).

**Verdict**: **CONFIRMED**.

---

### HLP-004: `_make_fleet` — Shard 06 references (×2)

**Claim A**: `tests/integration/strategy/test_three_empire_battle.py:63`
```python
def _make_fleet(fleet_id, owner_id, location, speed=5):
    fleet = MagicMock()
    fleet.id = fleet_id
    fleet.owner_id = owner_id
    fleet.location = location
    fleet.speed = speed
    fleet.ships = [MagicMock()]
    fleet.task_forces = []
    return fleet
```
Matches the cross-shard pattern description (MagicMock with id, owner_id, location, speed).

**Claim B**: `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py:66`
```python
def _make_fleet(loc=HexCoord(10, 10)) -> MagicMock:
    fleet = MagicMock(spec=Fleet)
    fleet.id = 1
    fleet.owner_id = 0
    fleet.location = loc
    fleet.ships = []
    fleet.orders = []
    return fleet
```
Uses `spec=Fleet` and a different parameter name (`loc` vs `location`), plus has `orders` field. Similar pattern but with significant signature differences.

**Verdict**: **CONFIRMED** for both. Both follow the `_make_fleet` pattern but with different fields and signatures — consistent with the cross-shard report's finding that the 43+ definitions "differ in appropriate ways."

---

## Severity Adjustment Summary

| Original Claim | Original Severity | Final Severity | Change |
|---|---|---|---|
| Claim 1 (weapons_report_layout fixture scope) | MAJOR | MINOR | Downgraded — single test in class; confirmed but severity reduced |
| Claim 5 (superweapon parametrization) | MINOR | NONE (DISPUTED) | Disputed — per-weapon setup differs too significantly |
| Claim 11 (conflict_resolution fixture scope) | MAJOR | NONE (DISPUTED) | Disputed — MagicMock MUST remain function-scoped |
| Claim 12 (armor_mechanics fixture scope) | MAJOR | NONE (DISPUTED) | Disputed — same rationale |
| Claim 15 (density fixture scope) | MAJOR | MINOR | Downgraded — 2 of 8 fixtures are mutable, blanket session-scope unsafe |

## Final Tally

- **CONFIRMED (no change)**: 15 — Claims 1, 2, 3, 4, 6, 7, 8, 9, 10, 13, 14, 16, 17, 18, 19
- **CROSS-SHARD CONFIRMED**: 4 — DUP-005, HLP-002, HLP-004 (×2 files)
- **DISPUTED**: 4 — Claims 5, 11, 12, 15
- **INCONCLUSIVE**: 0
- **Total items**: 19 (PHASE 1) + 4 (CROSS-SHARD) = 23. **19 actionable** (15 PHASE 1 + 4 CROSS-SHARD).
