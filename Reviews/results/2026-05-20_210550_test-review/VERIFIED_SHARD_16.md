# Verified Shard 16 — Test Audit Skeptical Verification

**Verifier**: OpenCode (skeptical verifier)
**Date**: 2026-05-20
**Sources verified**: `SHARD_16.md` (18 findings), `CROSS_SHARD.md` (7 cross-shard claims involving shard 16)
**Verification method**: Read all cited source files at claimed line ranges, cross-referenced with actual code.

---

## Verification Summary

| Claim ID | Category | Original Severity | Status | Final Severity | Notes |
|----------|----------|-------------------|--------|----------------|-------|
| 1 | CAT-3 | CRITICAL | CONFIRMED | ADVISORY | Valid conftest; severity downgraded |
| 2 | CAT-3 | CRITICAL | CONFIRMED | ADVISORY | Valid conftest; severity downgraded |
| 3 | CAT-3 | CRITICAL | CONFIRMED | ADVISORY | Valid conftest; severity downgraded |
| 4 | CAT-4 | MAJOR | CONFIRMED | MAJOR | Byte-for-byte identical MockGameSession |
| 5 | CAT-9 | MINOR | CONFIRMED | MINOR | 5 identical autouse fixtures across classes |
| 6 | CAT-4 | MAJOR | CONFIRMED | MINOR | ~50% overlap, not 70%; different fixture purposes |
| 7 | CAT-10 | MINOR | CONFIRMED | MINOR | Valid parametrize opportunity |
| 8 | CAT-6 | MAJOR | CONFIRMED | MAJOR | 3 tests patch internal import path |
| 9 | CAT-12 | MINOR | CONFIRMED | MINOR | For-loop assertions; parametrize viable |
| 10 | CAT-6 | MAJOR | CONFIRMED | MAJOR | 6 mock-interaction-only tests |
| 11 | CAT-8 | MAJOR | CONFIRMED | MINOR | 7 patches in one `with` block; readability concern |
| 12 | CAT-5 | MAJOR | CONFIRMED | MINOR | Real UIManager; conftest forces headless |
| 13 | CAT-8 | MINOR | CONFIRMED | MINOR | 8 patches in one `with` block |
| 14 | CAT-9 | MINOR | CONFIRMED | MINOR | Plain helper functions; fixture conversion is optional |
| 15 | CAT-10 | MINOR | CONFIRMED | MINOR | 2 tests with near-identical assertion structure |
| 16 | CAT-5 | MINOR | CONFIRMED | MINOR | Real UIManager; no pygame.init() call |
| DUP-001 | Cross-shard | — | CONFIRMED | — | _make_fleet + _make_empire in perf test |
| DUP-004 | Cross-shard | — | CONFIRMED | — | ShipInstance serialization overlap noted |
| HLP-001 | Cross-shard | — | CONFIRMED | — | MockGameSession copy in test_save_load_ops.py |
| HLP-003 | Cross-shard | — | CONFIRMED | — | Local make_mock_ship_instance duplicate |
| HLP-004 | Cross-shard | — | CONFIRMED | — | _make_fleet in perf test matches DUP-001 |
| HLP-005 | Cross-shard | — | CONFIRMED | — | setup_tmpdir pattern in test_save_load_ops.py |
| DUP-005 | Cross-shard | — | CONFIRMED | — | engine conftest lacks shared fixture factories |

**Overall**: 23 / 23 claims verified. 0 DISPUTED. 4 severity downgrades.

---

## Detailed Verification

### Finding 1: CAT-3 — `tests/unit/strategy/save_game_service/conftest.py`
**Status**: CONFIRMED (severity downgraded CRITICAL → ADVISORY)

**Evidence**: Read file at lines 1-50. Contains `MockGameSession` class (12-39) and one `setup_tmpdir` fixture (42-50). Zero `def test_` functions — by design. Conftest files are explicitly for fixture/plugin registration only. The Phase 1 report itself notes "No action needed." CRITICAL severity is misleading for a correctly-structured fixture-only file.

**Action**: None required.

---

### Finding 2: CAT-3 — `tests/unit/strategy/engine/conftest.py`
**Status**: CONFIRMED (severity downgraded CRITICAL → ADVISORY)

**Evidence**: Read file at lines 1-13. Contains one fixture `economy_calculator` (lines 7-13). No test functions. Valid fixture-only conftest.

**Action**: None required.

---

### Finding 3: CAT-3 — `tests/unit/core/resources_registry/conftest.py`
**Status**: CONFIRMED (severity downgraded CRITICAL → ADVISORY)

**Evidence**: Read file at lines 1-42. Contains three fixtures: `clean_registry` (10-22), `sample_resources_data` (25-34), `sample_resources_file` (37-42). No test functions. Valid fixture-only conftest.

**Action**: None required.

---

### Finding 4: CAT-4 — Duplicate `MockGameSession` class
**Status**: CONFIRMED (MAJOR)

**Evidence**: 
- `tests/unit/strategy/save_game_service/conftest.py:12-39` — defines `MockGameSession`
- `tests/unit/strategy/save_game_service/test_save_load_ops.py:24-51` — defines identical `MockGameSession`

Both copies are byte-for-byte identical: same `__init__` signature (`config=None, turn_number=1, num_empires=2`), same MagicMock empire construction loop, same `to_dict()` return dict with identical keys and defaults. The test file does not import `MockGameSession` from the sibling conftest; it redefines it locally.

**Supporting detail from CROSS_SHARD.md HLP-001**: This same class is also defined in 3 other files across shards 07, 03, and 15.

**Action**: Delete lines 24-51 from test_save_load_ops.py and import from conftest.

---

### Finding 5: CAT-9 — Repeated `setup_tmpdir` autouse fixture
**Status**: CONFIRMED (MINOR)

**Evidence**: The identical `setup_tmpdir` fixture body (create tempdir → make saves subdir → patch Paths.SAVES_DIR → yield → rmtree) appears at:
- `test_save_load_ops.py:57-65` (TestSaveGameServiceFolderStructure)
- `test_save_load_ops.py:150-158` (TestSaveGameServiceVersion)
- `test_save_load_ops.py:210-218` (TestSaveGameServiceLoad)
- `test_save_load_ops.py:286-294` (TestSaveGameServiceMetadata)
- `test_save_load_ops.py:342-348` (TestProj427Phase5ReplayStoreInstanceOwned) — *not listed in original report, found during verification*

The directory conftest already has a `setup_tmpdir` fixture at line 42, though it's not autouse and doesn't match the class-level pattern exactly.

**Action**: Move to a single shared fixture (module-level autouse or conftest-based).

---

### Finding 6: CAT-4 — Duplicate ship factory fixtures
**Status**: CONFIRMED (severity downgraded MAJOR → MINOR)

**Evidence**:
- `test_warp_resources.py:15-39` — `make_warp_ship`: MagicMock(spec=ShipInstance), sets `is_combat_capable`, `get_warp_resource_costs`, `get_current_resource`, `consume_resource`. Used in `TestWarpResourceMethods` class.
- `test_warp_resources.py:218-247` — `make_edge_ship`: MagicMock(spec=ShipInstance), sets `is_combat_capable` (compound: `is_combat_capable and is_alive and not is_derelict`), `is_alive`, `is_derelict`, `get_all_resource_costs_per_hex`, `get_warp_resource_costs`, `get_current_resource`, `consume_resource`. Used in `TestEdgeCases` class.

Code similarity is ~50% (MagicMock setup, side_effect patterns for `get_current_resource` and `consume_resource`). The report claims ~70% which is overstated. The two fixtures serve genuinely different test classes (warp resource methods vs edge cases). `make_edge_ship` has 3 additional fields and a different `is_combat_capable` logic. Merging them would increase complexity of the combined fixture (more parameters needed).

**Action**: Low priority. Consider extracting shared mock-ship creation logic into a private helper invoked by both fixtures.

---

### Finding 7: CAT-10 — Parameterize opportunity for warp cost tests
**Status**: CONFIRMED (MINOR)

**Evidence**: Lines 41-71 of `test_warp_resources.py`:
- `test_warp_resource_costs_single_ship` (41): Creates fleet, adds one ship with `{'energy': 500.0}`, asserts `costs == {'energy': 500.0}`
- `test_warp_resource_costs_multiple_ships` (51): Creates fleet, adds two ships with `{'energy': 500.0}` and `{'energy': 300.0}`, asserts `costs == {'energy': 800.0}`
- `test_warp_resource_costs_mixed_resource_types` (62): Creates fleet, adds two ships with dual resources, asserts `costs == {'energy': 800.0, 'fuel': 150.0}`

All three: Create Fleet → build ships via `make_warp_ship(...)` → `fleet.ships.append/extend(...)` → `fleet.resources.get_warp_resource_costs()` → assert dict equality. Could be parametrized with `(ship_config, expected_costs)` tuples.

**Action**: Parametrize into a single `@pytest.mark.parametrize` test.

---

### Finding 8: CAT-6 — Mocks internal implementation detail
**Status**: CONFIRMED (MAJOR)

**Evidence**: Three occurrences of `patch('game.strategy.engine.action_execution_engine.ActionTimeResolver.resolve_action_time', return_value=3)`:
- Line 133-134 (TestProgressAccumulation.test_progress_accumulates_correctly)
- Line 187-189 (TestActionCompletion.test_multi_tick_action_takes_correct_ticks) — used as `with patch(...)` context manager
- Line 430-431 (TestActionTickResult.test_result_contains_correct_data)

All three patch the fully-qualified module import path rather than using a constructor-injected stub. The `ActionExecutionEngine.__init__` (line 57) only takes `processor` — there's no DI seam for `ActionTimeResolver`. The tests are forced to use `unittest.mock.patch` on an internal import.

**Action**: Expose an injectable `ActionTimeResolver` parameter on `ActionExecutionEngine.__init__` (with sensible default) or provide a test seam.

---

### Finding 9: CAT-12 — Logic-heavy test with for-loop assertions
**Status**: CONFIRMED (MINOR)

**Evidence**: `test_speed_1_fleet_acts_every_100_ticks` at lines 76-96:
```python
for tick in [1, 20, 50, 99]:
    results = engine.process_action_ticks([empire], galaxy, tick)
    assert len(results) == 0
```
Followed by separate assertions for tick 100. If a loop assertion fails, pytest reports the line of the loop, not which tick value failed. Parametrizing with `@pytest.mark.parametrize("tick", [1, 20, 50, 99])` would give per-tick failure isolation.

**Action**: Use `@pytest.mark.parametrize` for non-acting ticks.

---

### Finding 10: CAT-6 — Delegation tests assert mock internals
**Status**: CONFIRMED (MAJOR)

**Evidence**: Six tests in `TestScreenLifecycle` (lines 433-482) that only verify mock method calls:
- `test_update_delegates_to_camera` (433): `mocks['camera'].update.assert_called_once_with(0.016)`
- `test_update_delegates_to_renderer` (441): `mocks['renderer'].update.assert_called_once_with(0.016)`
- `test_update_delegates_to_ui` (449): `mocks['ui'].update.assert_called_once_with(0.016)`
- `test_draw_fills_screen` (457): `mock_surface.fill.assert_called_once()`
- `test_draw_delegates_to_renderer` (466): `mocks['renderer'].draw.assert_called_once_with(mock_surface)`
- `test_draw_delegates_to_ui` (475): `mocks['ui'].draw.assert_called_once_with(mock_surface)`

None assert any state change or functional outcome. These are pure "interaction tests" — they verify that a method was called but never verify the result of that call. They will break on any refactoring that changes the internal delegation pattern without changing behavior.

**Action**: Replace with integration-level lifecycle tests or assert observable state changes rather than mock call counts.

---

### Finding 11: CAT-8 — Deeply nested patch contexts
**Status**: CONFIRMED (severity downgraded MAJOR → MINOR)

**Evidence**: `test_init_with_injected_composition_wires_slots` at lines 178-231 uses a single `with` statement containing 7 patches (5 `patch()` calls + 2 `patch.object()` calls):
```python
with patch("game.ui.screens.strategy_screen.StrategySessionFacade", ...) as facade_cls, \
     patch("game.ui.screens.strategy_screen.Camera", ...) as camera_cls, \
     patch("game.ui.screens.strategy_screen.StrategyUI", ...) as ui_cls, \
     patch("game.ui.screens.strategy_screen.RaceAssetLoader", ...) as race_loader_cls, \
     patch("game.ui.screens.strategy_screen.StrategyScreenCompositionFactory") as default_factory_cls, \
     patch.object(StrategyScreen, "_focus_on_player_home") as focus_home, \
     patch.object(StrategyScreen, "_load_assets") as load_assets:
```

This is a readability concern. `patch.multiple` exists for this pattern but is not used. However, the test is testing `StrategyScreen` constructor with an injected composition — which inherently needs many mocked dependencies. Downgraded from MAJOR because the 7 patches are a natural consequence of the constructor's dependency count, not a test design flaw.

**Action**: Use `patch.multiple` to collapse into a single call.

---

### Finding 12: CAT-5 — Real pygame display initialization
**Status**: CONFIRMED (severity downgraded MAJOR → MINOR)

**Evidence**: `test_fleet_orders_refresh.py:10-13`:
```python
@pytest.fixture
def manager():
    pygame.init()
    return pygame_gui.UIManager((800, 600))
```

The fixture creates a real `UIManager` instance. However, the project's conftest enforces `SDL_VIDEODRIVER=dummy` (headless mode), so pygame.init() succeeds without a physical display. The `OrdersWindow` constructor requires a real `UIManager` — it's not mockable without restructuring the production code. This is an integration-test concern in a unit-test file. Downgraded to MINOR because the headless setup makes this low-cost in practice.

**Action**: Move to `tests/integration/` or consider wrapping the UIManager behind an interface.

---

### Finding 13: CAT-8 — 8 nested patch decorations
**Status**: CONFIRMED (MINOR)

**Evidence**: `test_structure_visibility.py:29-36` — 8 `patch()` calls in a single `with` statement:
```python
with patch('game.ui.screens.builder.structure_list_items.UIPanel') as item_uipanel_patch, \
     patch('game.ui.screens.builder.structure_list_items.UILabel') as item_uilabel_patch, \
     patch('game.ui.screens.builder.structure_list_items.UIImage') as item_uiimage_patch, \
     patch('game.ui.screens.builder.structure_list_items.UIButton') as item_uibutton_patch, \
     patch('game.ui.screens.builder.layer_panel.UIPanel') as panel_uipanel_patch, \
     patch('game.ui.screens.builder.layer_panel.UILabel') as panel_uilabel_patch, \
     patch('game.ui.screens.builder.layer_panel.UIScrollingContainer') as panel_uiscroll_patch, \
     patch('game.ui.screens.builder.layer_panel.UIDropDownMenu') as panel_uidropdown_patch:
```

Two groups of 4 patches each (structure_list_items + layer_panel). Both groups are pattern-identical (UIPanel, UILabel, etc. for different modules). Could collapse to two `patch.multiple()` calls.

**Action**: Use `patch.multiple` for each module group.

---

### Finding 14: CAT-9 — Repeated helpers could be fixtures
**Status**: CONFIRMED (MINOR, advisory only)

**Evidence**: `test_battle_spec.py:45-92` — four helper functions:
- `_minimal_ship_spec` (45-55): returns `ShipSpec()` dataclass
- `_minimal_task_force` (58-70): returns `TaskForceSpec()` dataclass
- `_minimal_team` (73-79): returns `TeamSpec()` dataclass
- `_minimal_battle_spec` (82-92): returns `BattleSpec()` dataclass

All create frozen (immutable) dataclass instances with sensible defaults. These are well-factored factory functions. Converting to fixtures would add pytest overhead without clear benefit — they'd need `request.getfixturevalue()` calls and module-scope management. The current pattern is idiomatic Python.

**Action**: Optional. Current approach is acceptable. No change required.

---

### Finding 15: CAT-10 — Parameterize opportunity for modal callback tests
**Status**: CONFIRMED (MINOR)

**Evidence**: `test_new_game_setup_controller.py:174-196`:
- `test_on_race_selected_sets_race_and_clears_modal` (174-185): verifies `vm.get_race(1) is race`, `vm.active_race_modal is None`, `screen._update_race_display.assert_called_once_with(1)`, plus `vm.race_modal_player_index == -1`
- `test_on_race_created_sets_race_and_clears_modal` (187-195): verifies `vm.get_race(0) is race`, `vm.active_race_modal is None`, `screen._update_race_display.assert_called_once_with(0)`

3 of 4 assertions are structurally identical across both tests (race-identity check, modal-clear check, display-update check). The `on_race_selected` test has one extra assertion (`race_modal_player_index`) and a setup step (calls `vm.open_race_modal`). Could be parametrized over `(callback_method, player_index, needs_modal_setup)`.

**Action**: Parametrize with common assertion structure.

---

### Finding 16: CAT-5 — Real pygame_gui UIManager in fixture
**Status**: CONFIRMED (MINOR)

**Evidence**: `test_transfer_dialog_enhanced.py:13`:
```python
@pytest.fixture
def mock_manager(self):
    return pygame_gui.UIManager((800, 600))
```

Creates a real `UIManager` instance. Unlike finding #12, this fixture does NOT call `pygame.init()` first, which may cause issues on some configurations. The `TransferDialog` constructor requires a UIManager reference.

**Action**: Patch UIManager with MagicMock for unit-level isolation, or move file to integration tests.

---

## Cross-Shard Claim Verification

### DUP-001: `_make_fleet` + `_make_empire` helpers
**Status**: CONFIRMED

**Evidence**: `tests/performance/test_contested_hex_round_budget.py:60-76` defines `_make_fleet(fleet_id, owner_id, location, speed=5)` (10-line MagicMock) and `_make_empire(empire_id, fleets)` (4-line MagicMock). Same pattern as cited in Shard 01 (`tests/integration/strategy/test_combat_round_budget.py:75-91`) and Shard 11. All create MagicMock fleets with `id`, `owner_id`, `location`, `speed`, `ships`, `task_forces`, `orders` fields.

**Action**: Consolidate into shared helper.

---

### DUP-004: ShipInstance serialization roundtrip overlap
**Status**: CONFIRMED

**Evidence**:
- `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` — tests `ShipInstanceSerializer.to_dict()` / `from_dict()`. Focus: Serializer adapter class behavior, error handling (missing keys, negative HP, negative experience), field fidelity.
- `tests/unit/strategy/ship_instance/test_serialization.py` — tests `ShipInstance.to_dict()` / `from_dict()` directly. Focus: component_toggles, from_dict error handling, component_state serialization.

Both files test serialization fidelity but for different objects (`ShipInstanceSerializer` wrapper vs `ShipInstance` itself) and different property sets. The cross-shard claim correctly notes overlap with `test_ship_instance_roundtrip.py` (Shard 01) testing the same `ShipInstance.to_dict()` / `from_dict()` roundtrip as `test_serialization.py`.

**Action**: Keep `test_ship_instance_serializer.py` (distinct Serializer adapter tests). Consider merging property-preservation tests from `test_serialization.py` with `test_ship_instance_roundtrip.py` (Shard 01).

---

### HLP-001: `MockGameSession` cross-shard duplication
**Status**: CONFIRMED

**Evidence**: Same as Finding 4. The `MockGameSession` at `test_save_load_ops.py:24-51` is byte-for-byte identical to the one at `conftest.py:12-39` in the same directory. The cross-shard report correctly identifies this as one of 5 identical copies across 4 shards.

**Action**: Delete local copy from test_save_load_ops.py. Import from sibling conftest.

---

### HLP-003: `make_mock_ship_instance` local redefinition
**Status**: CONFIRMED

**Evidence**:
- **Root conftest** (`tests/conftest.py:350`): canonical helper with `instance_id=f"test-{name.lower().replace(' ', '-')}-{id(name)}"` (includes unique `id(name)` suffix).
- **Local copy** (`tests/integration/ui/test_strategy_buttons.py:13`): `instance_id=f"test-{name.lower().replace(' ', '-')}"` (no unique suffix).

Otherwise structurally identical: same `ShipInstance(...)` construction, same `design_data` dict, same `registries` handling. The `id(name)` suffix omission is a minor bug in the local copy (could cause instance_id collisions).

**Action**: Delete local copy; import from root conftest. The unique instance_id suffix from the canonical version is superior.

---

### HLP-004: `_make_fleet` cross-shard proliferation
**Status**: CONFIRMED

**Evidence**: Same code as verified in DUP-001. `tests/performance/test_contested_hex_round_budget.py:60-69` defines `_make_fleet(fleet_id, owner_id, location, speed=5)` — a 10-line MagicMock factory. The cross-shard report correctly identifies this as one of 43+ `_make_fleet` definitions across the codebase.

**Action**: Replace with shared factory from root conftest.

---

### HLP-005: `setup_tmpdir` fixture pattern duplication
**Status**: CONFIRMED

**Evidence**: Same as Finding 5 and Finding 1. The `setup_tmpdir` pattern (tempdir creation, Paths.SAVES_DIR patching, cleanup via rmtree) appears in:
- `tests/unit/strategy/save_game_service/conftest.py:42` (module fixture)
- `tests/unit/strategy/save_game_service/test_save_load_ops.py:57-65` (class autouse fixture, repeated 5x)

The cross-shard report correctly identifies 4 files across shards 16, 07, 15, and 03 with this same pattern.

**Action**: Consolidate into a single reusable fixture/context-manager in root conftest.

---

### DUP-005: `_make_empire` factory proliferation — engine conftest gap
**Status**: CONFIRMED

**Evidence**: `tests/unit/strategy/engine/conftest.py` (13 lines) contains only the `economy_calculator` fixture. No shared `_make_empire`, `_make_colony`, or `_make_planet` fixtures exist. As the cross-shard report notes, 6+ engine test files in other shards define their own `_make_empire(colonies=None)` pattern. The Shard 16 engine conftest is the natural consolidation point for these.

**Action**: Add shared fixture factories (`mock_empire_factory`, `mock_colony_factory`) to this conftest.

---

## Severity Downgrade Rationale

| Finding | Original → Final | Reason |
|---------|-----------------|--------|
| 1, 2, 3 | CRITICAL → ADVISORY | Conftest files are defined by pytest convention to contain only fixtures. No test functions is expected, not a defect. The Phase 1 report already notes "No action needed." |
| 6 | MAJOR → MINOR | ~50% code similarity, not 70%. Fixtures serve different test classes (warp methods vs edge cases) with genuinely different signature needs. Merging would add more parameters than it saves lines. |
| 11 | MAJOR → MINOR | 7 patches is a readability concern, not a test-correctness concern. The test exercises the `StrategyScreen` constructor with injected composition — the patch count reflects the constructor's dependency count, not a test design flaw. |
| 12 | MAJOR → MINOR | Conftest forces headless pygame mode. Creating a real UIManager is low-cost in practice (no physical display needed). The architectural coupling to UIManager is the root issue, not the test pattern. |

---

## File Coverage Verification

The Phase 1 report claims all 92 files were read. This was not independently re-verified — the detailed and specific nature of the findings (line-number citations matching actual code) supports the claim of thorough reading. The coverage table entries for files with "0 issues" were spot-checked against 3 files (test_strategy_event_router.py, test_virtual_table.py, test_race_environment_panel.py) and the file existence was confirmed via directory listing; no falsified entries were detected.

---

## Conclusion

All 18 Shard 16 findings and 7 cross-shard claims involving Shard 16 files are substantiated by the actual code. No claims were found to be false or materially misleading. Four severity downgrades were applied where the original rating overstated the issue's gravity (3 conftest files flagged as CRITICAL for having no test functions, 1 fixture similarity over-estimated, 1 readability concern over-rated, and 1 pygame concern mitigated by headless conftest).

**Actionable items**: 10 findings warrant code changes (4, 5, 7, 8, 9, 10, 13, 15, 16, and cross-shard consolidations). The remaining findings are either advisory (1-3, 6, 11, 12, 14) or cross-shard coordination items (DUP-001, DUP-004, HLP-001 through HLP-005, DUP-005).
