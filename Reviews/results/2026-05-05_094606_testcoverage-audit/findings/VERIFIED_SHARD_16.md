# Shard 16 — Verified Findings (Skeptical Verifier)

**Verified by:** OpenCode (Skeptical Verifier)  
**Verification date:** 2026-05-05  
**Source:** Phase 2 report `SHARD_16.md`  
**Methodology:** Read every cited production file; searched for and read corresponding test files; grepped for indirect import references across the full test suite.

---

## Verification Summary

| Claim | Original Tier | Phase 2 Severity | Verdict | Revised Tier |
|-------|--------------|------------------|---------|--------------|
| `replay_outcome.py` | Tier 0 | CRITICAL | CONFIRMED (with nuance) | Tier 2 (1/5 indirect) |
| `economy_slice.py` | Tier 0 | CRITICAL | CONFIRMED | Tier 0 |
| `storm.py` | Tier 0 | CRITICAL | **DISPUTED** | Tier 3 (fully covered) |
| `gravity_target_editor.py` | Tier 0 | MAJOR | CONFIRMED | Tier 0 |
| `strategy_screen_lifecycle.py` | Tier 0 | MAJOR | **DISPUTED** | Tier 3 (fully covered) |
| `galaxy_test/screen.py` | Tier 2 | MAJOR | CONFIRMED | Tier 2 (3/16 tested) |
| `race_setup/controller.py` | Tier 2 | MAJOR | DISPUTED (overstated) | Tier 2 (~16/26 tested) |

---

## CRITICAL Claims — Detailed Verification

### 1. `game/simulation/replay/replay_outcome.py` — **CONFIRMED (with nuance)**

**Phase 2 Claim:** 5 callables untested (Tier 0), CRITICAL.

**Evidence gathered:**
- `glob("**/test*replay_outcome*")` → **No dedicated unit test file exists.**
- `grep("replay_outcome", test_*.py)` → 10 matches across 3 files:
  - `test_replay_verifier.py` — tests `verify_replay_outcome` (different module, not ReplayOutcome).
  - `test_capture_pipeline.py:177` — **indirectly exercises `ReplayOutcome.to_battle_outcome()`** via capture sink integration test: `rebuilt = replay_outcome.to_battle_outcome()`.
  - `test_replay_playback.py:128` — variable name `replay_outcome` but this is a `BattleOutcome`, not `ReplayOutcome`. No coverage.

**Verdict: CONFIRMED (CRITICAL)**

The Phase 2 claim of "Tier 0 — no tests at all" is **slightly overstated** — `to_battle_outcome()` is exercised once in an integration test. However, the 4 other callables (`from_battle_outcome`, `to_dict`, `from_dict`, constructor) have **zero coverage**. The core roundtrip contract (`from_battle_outcome` → `to_dict` → `from_dict` → `to_battle_outcome`) that the Phase 2 report correctly identifies as the "PROJ-312 replay persistence contract" is **completely untested**.

**Revised tier:** Tier 2 (1/5 indirect via integration test; no unit tests). CRITICAL classification stands.

---

### 2. `game/strategy/facade/slices/economy_slice.py` — **CONFIRMED**

**Phase 2 Claim:** 5 callables untested (Tier 0), CRITICAL — the heaviest facade slice.

**Evidence gathered:**
- `glob("**/test*economy_slice*")` → **No file found.**
- `grep("economy_slice", test_*.py)` → **No matches.**
- `grep("EconomySlice", test_*.py)` → **No matches.**
- Searched for any indirect import chain through facade tests → None found.

**Verdict: CONFIRMED (CRITICAL)**

188 LOC of completely untested production code. `get_colony_demographic_view` (~104 LOC) contains habitability calculations, species iteration, food surplus bonus logic with cap enforcement, and per-resource upkeep aggregation — all zero coverage. This DTO feeds strategy UI demographic panels at runtime and is the single heaviest untested gap in Shard 16.

**Revised tier:** Tier 0. CRITICAL classification confirmed.

---

### 3. `game/strategy/services/ability_sources/storm.py` — **DISPUTED**

**Phase 2 Claim:** 9 callables untested (Tier 0), CRITICAL. "Global-frame hex math path completely untested."

**Evidence gathered:**
- `glob("**/test*storm*")` → Found `tests/unit/strategy/services/ability_sources/test_storm.py` — **106 lines, 11 test functions.**
- Read the test file in full. It covers **every callable** in `StormAbilitySource`:
  - `source_kind` → `test_source_kind_is_storm` (line 20)
  - `source_label` → `test_source_label_is_storm_name` (line 25)
  - `source_id` → `test_source_id_stable_and_prefixed` (line 30)
  - `owner_id` → `test_owner_id_is_none` (line 38)
  - `get_abilities` (dict path) → `test_get_abilities_returns_storm_abilities_dict` (line 43)
  - `get_abilities` (empty path) → `test_get_abilities_empty_when_storm_has_no_abilities` (line 49)
  - `affects_hex` (unparented, in-bounds) → `test_affects_hex_true_for_occupied_unparented_storm` (line 54)
  - `affects_hex` (unparented, out-of-bounds) → `test_affects_hex_false_outside_unparented_storm` (line 67)
  - **`affects_hex` (GLOBAL-FRAME with system)** → `test_affects_hex_translates_local_to_global_when_system_provided` (line 72) — explicitly tests `sys_loc + storm_loc + offset` arithmetic with `_MockSystem(global_location=HexCoord(1969, 817))`. Confirms local coords are NOT matched (line 93: `assert src.affects_hex(HexCoord(3, 3)) is False`).
  - `get_activation_state` → `test_get_activation_state_is_none` (line 98)
  - `IAbilitySource` protocol conformance → `test_satisfies_iability_source_protocol` (line 103)
- **`affects_system` (always returns True) not explicitly tested** — trivially a one-liner return, but technically a gap.

**Verdict: DISPUTED**

The Phase 2 report claims Tier 0 ("No Tests At All") and asserts "Global-frame hex math path completely untested." Both claims are **factually incorrect**. The test file exists at the expected location (`tests/unit/strategy/services/ability_sources/test_storm.py`), and `test_affects_hex_translates_local_to_global_when_system_provided` directly covers the global-frame arithmetic with `system.global_location`, `storm.location`, and `hex_offsets`. This is the exact code path the Phase 2 report flagged as uncovered.

**Revised tier:** Tier 3 (fully covered). Remove from CRITICAL list. The only minor gap is `affects_system` (one-liner `return True`), classified as ADVISORY.

---

## MAJOR Claims — Detailed Verification

### 4. `game/ui/screens/gravity_target_editor.py` — **CONFIRMED**

**Phase 2 Claim:** 9 callables untested (Tier 0), MAJOR.

**Evidence gathered:**
- `glob("**/test*gravity_target*")` → **No file found.**
- `grep("gravity_target_editor", test_*.py)` → 3 matches:
  - `test_strategy_modal_window.py:376` — only mentions the module name in a modal-blocking test (does not import/instantiate `GravityTargetEditor`)
  - `test_editor_click_blocking.py:18` — imports `GravityTargetEditor` but tests modal-window blocking behavior, **not** the editor's own methods
- No unit test for slider clamping, `G_TO_MS2` conversion math, species ideal lookup, button handlers, or `_build_ui` widget construction.

**Verdict: CONFIRMED (MAJOR)**

Zero dedicated tests. The `G_TO_MS2 = 9.81` conversion, slider range clamping (`MIN_GRAVITY_G=0.1` to `MAX_GRAVITY_G=3.0`), species `rc.preferences["gravity"].setpoint` lookup, and the three preset buttons each deserve explicit test coverage. Integration tests only exercise modal-window mechanics, not the editor's domain logic.

**Revised tier:** Tier 0. MAJOR classification confirmed.

---

### 5. `game/ui/screens/strategy_screen_lifecycle.py` — **DISPUTED**

**Phase 2 Claim:** 8 lifecycle functions untested (Tier 0), MAJOR.

**Evidence gathered:**
- `glob("**/test*strategy_screen_lifecycle*")` → Found `tests/unit/ui/screens/test_strategy_screen_lifecycle.py` — **163 lines, 14 test methods in 6 test classes.**
- Read the test file in full. It covers **every function** in the production module:

| Function | Test Method | Line |
|----------|------------|------|
| `on_design_click` — callback path | `TestOnDesignClick.test_invokes_callback_with_context` | 29 |
| `on_design_click` — no-callback guard | `TestOnDesignClick.test_no_callback_no_call` | 38 |
| `on_menu_option("save_game")` | `TestOnMenuOption.test_save_game_dispatches` | 50 |
| `on_menu_option("load_game")` | `TestOnMenuOption.test_load_game_dispatches` | 55 |
| `on_menu_option("settings")` | `TestOnMenuOption.test_settings_opens_settings_window` | 60 |
| `on_menu_option("controls")` | `TestOnMenuOption.test_controls_calls_callback` | 65 |
| `on_menu_option("quit_to_menu")` | `TestOnMenuOption.test_quit_to_menu_dispatches` | 70 |
| `on_menu_option("quit_game")` | `TestOnMenuOption.test_quit_game_calls_callback` | 75 |
| `on_menu_option` — unknown/noop | `TestOnMenuOption.test_unknown_option_is_noop` | 80 |
| `show_load_game_dialog` | `TestLoadGameDialog.test_show_load_game_dialog_creates_window` | 88 |
| `on_load_selected` — success | `TestLoadGameDialog.test_on_load_selected_calls_callback` | 99 |
| `on_load_selected` — no callback | `TestLoadGameDialog.test_on_load_selected_no_callback_safe` | 106 |
| `confirm_quit_to_menu` | `TestQuitConfirmation.test_confirm_quit_creates_dialog` | 113 |
| `handle_quit_confirmed` | `TestQuitConfirmation.test_handle_quit_confirmed_clears_and_callbacks` | 121 |
| `show_coming_soon` | `TestComingSoon.test_show_coming_soon_creates_message_window` | 130 |
| `on_save_game_click` — success | `TestSaveGameClick.test_save_success_shows_success_dialog` | 141 |
| `on_save_game_click` — failure | `TestSaveGameClick.test_save_failure_shows_error_dialog` | 153 |

**Verdict: DISPUTED**

All 8 functions are tested with 14 test methods. All 6 menu-option branches are explicitly tested. Both save success and save failure paths are covered. The test uses `MagicMock` screens and patches UI window constructors — a clean unit-test approach with no pygame dependency. The Phase 2 classification as Tier 0 ("No Tests At All") is **factually incorrect**.

**Revised tier:** Tier 3 (fully covered). Remove from MAJOR list entirely. This module is a model of good unit-test coverage for UI lifecycle logic.

---

### 6. `game/ui/screens/galaxy_test/screen.py` — **CONFIRMED**

**Phase 2 Claim:** 13 of 16 callables untested (Tier 2), MAJOR gap.

**Evidence gathered:**
- `glob("**/test*galaxy_test*")` → Found `tests/unit/ui/screens/test_galaxy_test_screen.py` — **96 lines.**
- Read the test file in full. Coverage breakdown:

| Callable | Test Coverage |
|----------|--------------|
| `GalaxyTestScreen.MODE_*` constants | `TestGalaxyTestConstants` + `TestModeSwitching` (5 tests) |
| `_clear_ui` | `TestClearUI` (2 tests — kill elements, empty list) |
| `__init__` | Not directly tested (bypass_init pattern used) |
| `_create_menu_ui` | **NOT TESTED** |
| `_create_galaxy_ui` | **NOT TESTED** |
| `_create_system_ui` | **NOT TESTED** |
| `update` | **NOT TESTED** |
| `draw` | **NOT TESTED** |
| `handle_event` | **NOT TESTED** |
| `_handle_button_click` | **NOT TESTED** |
| `_go_to_menu` | **NOT TESTED** |
| `_go_to_galaxy_mode` | **NOT TESTED** |
| `_go_to_system_mode` | **NOT TESTED** |
| `_on_close` | **NOT TESTED** |
| `handle_resize` | **NOT TESTED** |
| `handle_input` | **NOT TESTED** |

**Verdict: CONFIRMED (MAJOR)**

The test file exercises only `_clear_ui` and class-level constants. The 13 remaining callables (including the entire rendering loop, event dispatch, mode-switching logic, and resize handling) are untested. The Phase 2 count of "3/16 tested" is confirmed.

**Context note:** This is a developer testing tool, not a user-facing screen. The practical impact of missing tests here is lower than for gameplay-critical modules. Still, MAJOR classification is appropriate given the large gap.

**Revised tier:** Tier 2 (3/16 tested). MAJOR classification confirmed.

---

### 7. `game/ui/screens/race_setup/controller.py` — **DISPUTED (overstated)**

**Phase 2 Claim:** 11 untested methods (Tier 2), MAJOR gap. "8 randomization methods" listed as key gap.

**Evidence gathered:**
- `glob("**/test*race_setup*")` → Found `tests/unit/ui/screens/test_race_setup_screen.py` — **1451 lines.**
- Read the test file in full. Coverage of controller methods (verified via `screen._controller.<method>` calls):

**TESTED directly by the test file (16 methods):**

| Method | Test Location | Lines |
|--------|--------------|-------|
| `on_race_selected` | `TestRaceSetupLoadSpecies` | 602–648 |
| `populate_ui_from_config` | `TestBug118SummaryRefreshOnPopulate` | 1375–1381 |
| `on_save` | `TestSaveUpdateDialog` | 663–698 |
| `validate_for_save` | Via mock in `TestSaveUpdateDialog` | 668, 686 |
| `do_save` | `TestRaceRegistryInvalidationOnSave` | 816–862 |
| `on_overwrite_save` | `TestSaveUpdateDialog` | 700–716 |
| `on_save_as_new` | `TestSaveUpdateDialog` | 718–736 |
| `on_save_dialog_cancel` | `TestSaveUpdateDialog` | 738–746 |
| `on_randomize` | `TestFeat12OnRandomizeDispatch` | 934–964 |
| `randomize_environment` | `TestFeat12RandomizeEnvironmentHandler` | 966–1036 |
| `randomize_aptitudes` | `TestFeat12RandomizeAptitudesHandler` | 1038–1097 |
| `randomize_all` | `TestFeat12RandomizeAllHandler` | 1100–1188 |
| `on_cancel` | `TestBug115CloseButtonInvokesCancel` (via `on_close_window_button_pressed`) | 1345–1357 |
| `__init__` | Tested indirectly through `_make_race_setup_screen` fixture | 37–87 |
| `description_controller` (property) | Trivial getter; tested indirectly | — |
| `attach_description_controller` | Trivial setter; tested indirectly | — |

**NOT TESTED (10 methods):**

| Method | Reason |
|--------|--------|
| `on_load_race` | Creates pygame_gui widgets; no unit test |
| `on_theme_selected` | Simple attribute set; no isolation test |
| `on_race_browser_cancelled` | Trivial logging only |
| `randomize_identity` | Only tested via `on_randomize` dispatch (test mocks it); no isolation test for attribute writes |
| `randomize_visuals` | Only tested via `on_randomize` dispatch; no isolation test |
| `randomize_ships` | Only tested via `on_randomize` dispatch; no isolation test |
| `on_description_controller_change` | PROJ-299; no test |
| `update_description_char_counts` | PROJ-299; no test |
| `update_descriptions_from_text` | PROJ-299; no test |
| `on_save_as_new` (*) | Confirmed tested (see above) |

**Verdict: DISPUTED (overstated)**

The Phase 2 report claims "11 untested methods including 8 randomization methods." The evidence shows:
- **Save flow methods** (`on_save`, `do_save`, `on_overwrite_save`, `on_save_as_new`, `on_save_dialog_cancel`) are **all tested**, contrary to the report.
- **3 of 8 randomization methods** (`randomize_environment`, `randomize_aptitudes`, `randomize_all`) are **thoroughly tested** with mock RaceRandomizer patches and assertion of config writes + panel refreshes.
- **~10 methods** are untested, not 11. Of these, 3 (PROJ-299 description controller callbacks) are thin delegation, 3 (identity/visuals/ships randomization) are per-tab handlers that the dispatch method `on_randomize` covers indirectly, and 4 are load-flow/theme-mutation methods.

**Revised tier:** Tier 2 (~16/26 tested). MAJOR classification is downgraded to **MINOR** — the randomization and save paths, which constitute the heaviest logic in the controller, are well-tested. The remaining gaps are smaller, simpler methods.

---

## Cross-Claim Verification: Tier 2 Partial Coverage Files

### `game/simulation/combat/weapon_registry.py` — PASS confirmed
`WeaponRegistry.__init__` and `reset` tested indirectly. `detect_family()` None-return path gap identified correctly. **CONFIRMED.**

### `game/simulation/components/abilities/propulsion.py` — PASS confirmed
`WarpJump._parse_attrs` integer shortcut path deserves explicit test. **CONFIRMED.**

### `game/simulation/managers/retreat_manager.py` — PASS confirmed
`__init__` and `_handle_ship_escaped` tested indirectly. **CONFIRMED.**

### `game/strategy/data/spatial_index.py` — PASS confirmed
`get_k_nearest()` expansion loop with `max_radius=None` and sparse data needs test. **CONFIRMED.**

### `game/strategy/facade/slices/system_slice.py` — PASS confirmed
`get_all_systems()`, `get_system_at_hex()`, `get_system_containing_fleet()` need explicit tests. **CONFIRMED.**

### `game/ui/screens/race_validator.py` — PASS confirmed
`__init__` trivial, tested indirectly. **CONFIRMED.**

---

## Final Verification Summary

### CRITICAL — Revised Status

| # | File | Phase 2 | Verified | Action |
|---|------|---------|----------|--------|
| 1 | `replay_outcome.py` | CRITICAL (tier 0) | **CONFIRMED** — 1 callable indirectly covered via integration; 4 truly untested | Keep CRITICAL |
| 2 | `economy_slice.py` | CRITICAL (tier 0) | **CONFIRMED** — zero test coverage found; no grep matches | Keep CRITICAL |
| 3 | `storm.py` | CRITICAL (tier 0) | **DISPUTED** — fully covered by 11 tests in `test_storm.py` | **Remove from CRITICAL** |

### MAJOR — Revised Status

| # | File | Phase 2 | Verified | Action |
|---|------|---------|----------|--------|
| 4 | `gravity_target_editor.py` | MAJOR (tier 0) | **CONFIRMED** — zero unit tests; only indirect modal-window integration | Keep MAJOR |
| 5 | `strategy_screen_lifecycle.py` | MAJOR (tier 0) | **DISPUTED** — all 8 functions covered by 14 tests | **Remove from MAJOR** |
| 6 | `galaxy_test/screen.py` | MAJOR (tier 2) | **CONFIRMED** — 3/16 tested confirmed; 13 callables untested | Keep MAJOR |
| 7 | `race_setup/controller.py` | MAJOR (tier 2) | **DISPUTED** — ~16/26 tested (not 15/26); key randomization + save paths covered | **Downgrade to MINOR** |

### Adjusted Priority Order

**CRITICAL (2 items):**
1. `economy_slice.py` — 188 LOC, completely untested. Highest-impact gap in this shard.
2. `replay_outcome.py` — 49 LOC, 4/5 callables untested. Roundtrip contract untested.

**MAJOR (2 items):**
3. `gravity_target_editor.py` — 220 LOC, completely untested. Conversion math and slider logic uncovered.
4. `galaxy_test/screen.py` — 13/16 callables untested. Developer tooling but large gap.

**MINOR (1 item — downgraded from MAJOR):**
5. `race_setup/controller.py` — ~10/26 methods untested. Key logic paths (save, randomize) already tested.

### Adjusted Total

| | Phase 2 Report | Verified |
|---|---------------|----------|
| CRITICAL files | 4 | **2** |
| MAJOR files | 3 | **2** (plus 1 downgraded to MINOR) |
| Total untested callables | ~120 | ~100 (reduced by ~20 from 2 disputed Tier-0→Tier-3 reclassifications) |
