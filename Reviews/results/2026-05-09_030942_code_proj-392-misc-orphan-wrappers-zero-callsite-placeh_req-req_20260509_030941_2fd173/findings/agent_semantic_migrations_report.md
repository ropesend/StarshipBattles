# PROJ-392 Audit-Correction Semantics Verification Report

**Generated**: 2026-05-09  
**Reviewer**: OpenCode (semantic migration verification agent)  
**Scope**: 7 audit-correction migrations from PROJ-392 (orphan wrappers + zero-callsite placeholders)

---

## Correction #1: LEG-03-025 `expanded_ships` alias

**Status**: PASS

| Item | Detail |
|------|--------|
| Source file | `game/ui/panels/battle_panels.py:92` (deleted in `21ab2bdc0`) |
| Test files checked | `tests/unit/ui/test_battle_panels.py`, `tests/unit/ui/test_battle_panels_extended.py`, `tests/unit/ui/test_battle_panels_characterization.py` |
| Commit | `21ab2bdc0` (phase 1) |

**What was done**: Deleted `self.expanded_ships = self._expanded_ids` backward-compat alias on `ShipStatsPanel`. Migrated 14 test reads from `panel.expanded_ships` → `panel._expanded_ids`.

**Verification**:
- `_expanded_ids` is the canonical inherited attribute from `ExpandableIdPanel`, set in `battle_panels.py:71` (`self._expanded_ids = set()`).
- All 14 test references (across 3 test files) use `panel._expanded_ids` — confirmed via grep + git diff.
- All assertions are semantically identical: `assert "X" in panel._expanded_ids`, `assert "X" not in panel._expanded_ids`, `panel._expanded_ids.clear()`, `panel._expanded_ids.add("test_id")`.
- The `battle_screen.py:163` `self.ui.expanded_ships = set()` is a SEPARATE attribute on a different class (BattleUI), not the deleted alias — no conflict.
- PROJ-43 comments in test_battle_panels.py still reference "expanded_ships" in prose but the code references are all `_expanded_ids`.

**Dropped**: Nothing. All semantics preserved.

---

## Correction #2: LEG-02-007 `name_input` placeholder

**Status**: PASS

| Item | Detail |
|------|--------|
| Source file | `game/ui/screens/race_setup/screen.py:261` (deleted in `21ab2bdc0`) |
| Fixture files checked | `tests/fixtures/race_setup_ui_builders.py`, `tests/fixtures/test_race_setup_ui_builders.py` |
| Commit | `21ab2bdc0` (phase 1) |

**What was done**: Deleted `self.name_input = None` legacy placeholder on `RaceSetupScreen`. Removed `screen.name_input = MagicMock(...)` from `MockRaceSetupUiBuilder` and `assert screen.name_input is not None` from its test.

**Verification**:
- No `name_input` references remain in `game/ui/screens/race_setup/` (confirmed by grep).
- No `name_input` references remain in `tests/fixtures/race_setup_ui_builders.py` or `tests/fixtures/test_race_setup_ui_builders.py`.
- The `MockRaceSetupUiBuilder.build()` still populates all expected widget slots — 44 assertions in `test_mock_builder_populates_widget_slots()` pass cleanly without the `name_input` line.
- All other `*_name_input` references in unrelated files (e.g. `race_name_input`, `faction_name_input`, `save_name_input`, `leader_name_input`) are separate attributes, unaffected.

**Dropped**: Nothing. The `name_input` attribute was a zero-usage legacy placeholder. No tests or production code depended on it.

---

## Correction #3: LEG-01-007 quickstart dir wrappers

**Status**: PASS

| Item | Detail |
|------|--------|
| Source file | `game/strategy/quickstart_builder.py` (deleted in `51b216bf9`) |
| Test files checked | `tests/unit/strategy/test_quickstart_builder.py`, `tests/unit/quickstart/test_quickstart_builder.py`, `tests/unit/quickstart/conftest.py` |
| Commit | `51b216bf9` (phase 2.1-2.3) |

**What was done**: Deleted module-level `get_quickstart_races_dir()` and `get_quickstart_designs_dir()` wrappers from `quickstart_builder.py`. Inlined the 2 internal call sites to `Paths.get_starter_races_dir()` and `Paths.get_starter_designs_dir()`. Migrated 4 `mock.patch` targets in `tests/unit/strategy/test_quickstart_builder.py`.

**Verification**:
- Production wrappers confirmed deleted: grep returns no matches in `game/strategy/quickstart_builder.py`.
- Internal call sites correctly inlined:
  - `quickstart_builder.py:53`: `race_path = Paths.get_starter_races_dir() / race_filename`
  - `quickstart_builder.py:218`: `designs_source = Paths.get_starter_designs_dir()`
- 4 mock.patch targets migrated from `"game.strategy.quickstart_builder.get_quickstart_designs_dir"` → `"game.strategy.quickstart_builder.Paths.get_starter_designs_dir"` (lines 127, 144, 164, 184).
- `tests/unit/quickstart/conftest.py` retains local helper functions `get_quickstart_races_dir()` / `get_quickstart_designs_dir()` that delegate to `Paths.get_starter_*_dir()` — these are test-fixture-local utilities, NOT production wrappers. The commit explicitly kept them intact. Semantics unchanged (both delegate to the same `Paths.get_starter_*_dir()`).
- Two trivial wrapper-returns-Path tests (`TestStarterDataPathFunctions`) were dropped — these were testing the deleted wrappers themselves, not business logic.

**Dropped**: Two test cases for the deleted wrapper functions themselves. No business logic or coverage loss.

---

## Correction #4: LEG-01-009 `find_path_deep_space`

**Status**: PASS

| Item | Detail |
|------|--------|
| Source file | `game/strategy/services/galaxy_pathfinding_service.py` (deleted in `51b216bf9`) |
| Key test | `tests/integration/strategy/test_save_round_trip_phase4.py:42` |
| Commit | `51b216bf9` (phase 2.1-2.3) |

**What was done**: Deleted `GalaxyPathfindingService.find_path_deep_space` static method (4-line passthrough to `hex_linedraw`). Migrated all 7 internal callers to `hex_linedraw(...)` directly. Updated the `pathfinding.py:40-44` module-level shim to call `hex_linedraw` instead of `GalaxyPathfindingService.find_path_deep_space`.

**Verification**:
- `find_path_deep_space` confirmed absent from `galaxy_pathfinding_service.py` (grep returns no matches).
- Line 42 of `test_save_round_trip_phase4.py`:
  ```python
  path = galaxy._pathfinder.find_hybrid_path(HexCoord(0, 0), HexCoord(2, 0))
  ```
  - `find_hybrid_path` is semantically correct for this test: for a pure deep-space path (no warp lanes, start/end same system or can_warp=False), `find_hybrid_path` delegates to `hex_linedraw` — same result as the old `find_path_deep_space`.
  - Added assertion `assert path is not None` (safety).
- Test `test_find_path_deep_space_via_hex_linedraw` now exercises `hex_linedraw` directly.
- Test `test_pathfinding_shim_forwards_to_hex_linedraw` renamed and updated to compare shim output against `hex_linedraw` directly (rather than `GalaxyPathfindingService.find_path_deep_space`).

**Dropped**: Nothing. Semantics perfectly preserved — `hex_linedraw` is the canonical implementation; `find_path_deep_space` was always a 4-line passthrough to it. `find_hybrid_path` produces identical results for deep-space-only paths.

---

## Correction #5: LEG-04-006 new_game_setup static wrappers

**Status**: PARTIAL

| Item | Detail |
|------|--------|
| Source file | `game/ui/screens/new_game_setup_screen.py` (deleted in `19d929385`) |
| Test files checked | `tests/unit/ui/test_new_game_setup.py`, `tests/unit/ui/screens/test_new_game_setup_extended.py`, `tests/unit/ui/screens/test_new_game_setup_controller.py` |
| Commit | `19d929385` (phase 2.4-2.9) |

**What was done**: Deleted `validate_save_name` and `generate_default_save_name` static shims from `NewGameSetupScreen`. Migrated 9 test calls to `NewGameSetupController.validate_save_name(...)` / `NewGameSetupController.generate_default_save_name(...)`. Simplified the controller's `type(self._screen).validate_save_name` indirection. Migrated 2 patch targets.

**Verification (PASSING)**:
- Static shims confirmed deleted from `NewGameSetupScreen` (grep returns only comments referencing the deletion at lines 703-706).
- 9 test calls in `tests/unit/ui/test_new_game_setup.py` now use `NewGameSetupController.validate_save_name(...)` and `NewGameSetupController.generate_default_save_name()` directly — confirmed by grep.
- Controller at `new_game_setup_controller.py` now calls `NewGameSetupController.validate_save_name(...)` directly instead of `type(self._screen).validate_save_name(...)`.
- 2 patch targets in `tests/unit/ui/screens/test_new_game_setup_extended.py:233,246` migrated from `"new_game_setup_screen.validate_save_name"` to `"new_game_setup_controller.NewGameSetupController.validate_save_name"` — confirmed.
- All test assertions use the same method signatures and return value shapes ((bool, str) tuple).

**CONCERN — Potential Runtime Bug**:
- `new_game_setup_screen.py:348` still calls `self.generate_default_save_name()`:
  ```python
  self.save_name_input.set_text(self.generate_default_save_name())
  ```
- This is inside the production `Stage2_init_ui()` path — it runs when the screen is constructed normally (not `bypass_init`).
- Since the `generate_default_save_name` static method was deleted from `NewGameSetupScreen`, and the class does not inherit it from `pygame_gui.elements.UIWindow`, this will raise `AttributeError` at runtime.
- The fix is: `self.save_name_input.set_text(NewGameSetupController.generate_default_save_name())`
- This was not caught by tests because tests use `bypass_init` which skips `Stage2_init_ui()`.

**Dropped**: Nothing intentionally dropped. But the uncorrected `self.generate_default_save_name()` invocation is a drop — the production init path is broken.

**Severity**: The production UI init path will crash. This is a **MAJOR** issue, though bounded to the New Game Setup screen.

---

## Correction #6: LEG-01-006 strategy_renderer image wrappers

**Status**: PASS

| Item | Detail |
|------|--------|
| Source file | `game/ui/screens/strategy_renderer.py` (deleted in `51b216bf9`) |
| Commit | `51b216bf9` (phase 2.1-2.3) |

**What was done**: Deleted 3 `_load_*_image` instance wrappers on `StrategyRenderer`:
- `_load_star_image(self, star)` → delegated to `_layer_load_star_image(self, star)`
- `_load_planet_v3_image(self, image_id)` → delegated to `_layer_load_planet_v3_image(self, image_id)`
- `_load_dyson_sphere_image(self)` → delegated to `_layer_load_dyson_sphere_image(self)`

Also dropped the 3 now-unused `_layer_load_*_image` imports from the submodule imports.

**Verification**:
- The 3 wrapper methods confirmed deleted (grep returns no matches).
- The 3 corresponding import lines removed from strategy_renderer.py (confirmed via git diff).
- These were **zero-caller** wrappers — the `_layer_load_*_image` functions were already being used directly inside the `strategy_render/` submodules. The wrappers on `StrategyRenderer` were never called.
- No test references existed for these 3 wrapper methods (grep of entire test tree finds only `test_load_star_image_*` in `test_asset_manager_resolutions.py` which tests the asset manager's image loading, not the StrategyRenderer wrappers).
- No imports of `_layer_load_*_image` from strategy_render submodules needed fixing — callers within those submodules import from their own files, not from strategy_renderer.py.

**Dropped**: Nothing. The wrappers had zero callers — they were dead code with no semantic effect.

---

## Correction #7: LEG-03-014 `_get_sector_text` instance wrapper

**Status**: PASS

| Item | Detail |
|------|--------|
| Source file | `game/ui/screens/empire_build_queue_window.py` (deleted in `19d929385`) |
| Commit | `19d929385` (phase 2.4-2.9) |

**What was done**: Deleted `_get_sector_text` instance method wrapper on `EmpireBuildQueueWindow`:
```python
@staticmethod
def _get_sector_text(source: BuildQueueSource) -> str:
    return get_sector_text(source)
```

**Verification**:
- Wrapper confirmed deleted from `empire_build_queue_window.py` (grep returns no matches for `_get_sector_text`).
- The sole internal call site was already using `get_sector_text(source)` directly — line 527 in `_get_column_value`:
  ```python
  if col_id == 'sector':
      return get_sector_text(source)
  ```
- `get_sector_text` is imported at line 43 from `empire_build_queue_formatter` and the canonical implementation is at `empire_build_queue_formatter.py:95`.
- The wrapper was truly zero-caller — the call site was already bypassing it and calling the formatter function directly.
- No test references to `_get_sector_text` existed (the method was never tested independently).

**Dropped**: Nothing. The deleted code was a zero-caller 2-line passthrough. The call site was already using the real function directly.

---

## Summary

| # | Correction | Status | Concern |
|---|-----------|--------|---------|
| 1 | LEG-03-025 `expanded_ships` | PASS | — |
| 2 | LEG-02-007 `name_input` | PASS | — |
| 3 | LEG-01-007 quickstart dir wrappers | PASS | — |
| 4 | LEG-01-009 `find_path_deep_space` | PASS | — |
| 5 | LEG-04-006 new_game_setup static wrappers | **PARTIAL** | `self.generate_default_save_name()` at `new_game_setup_screen.py:348` calls deleted static method — will crash at runtime |
| 6 | LEG-01-006 strategy_renderer image wrappers | PASS | — |
| 7 | LEG-03-014 `_get_sector_text` | PASS | — |

**Total**: 6 PASS / 1 PARTIAL / 0 FAIL

### Required Remediation

**Correction #5**: Fix `game/ui/screens/new_game_setup_screen.py:348`:
```python
# Before (broken):
self.save_name_input.set_text(self.generate_default_save_name())

# After (correct):
self.save_name_input.set_text(NewGameSetupController.generate_default_save_name())
```

Add import if not already present:
```python
from game.ui.screens.new_game_setup_controller import NewGameSetupController
```
