# Compiled Confirmed Gaps — Shards 13-18

**Compiled by:** Phase 4 summary compiler  
**Date:** 2026-05-05  
**Scope:** All CONFIRMED gaps from VERIFIED_SHARD_13.md through VERIFIED_SHARD_18.md  
**Excluded:** All DISPUTED and INCONCLUSIVE claims

---

## Per-Shard Statistics

| Shard | Reviewed | Confirmed | Disputed | Inconclusive | Downgrades | Upgrades |
|---|---|---|---|---|---|---|---|
| 13 | 5 (MAJ) | 1 | 4 | 0 | 5 (all MAJ→MINOR or ADVISORY) | 0 |
| 14 | 5 (1 CRI + 4 MAJ) | 1 | 4 | 0 | 4 (1 CRI→MAJ, 3 MAJ→ADVISORY) | 0 |
| 15 | 5 (2 CRI + 2 MAJ + 1 ADD) | 3 | 3 | 0 | 1 (CRI→ADVISORY: _formation_utils) | 0 |
| 16 | 7 (3 CRI + 4 MAJ) | 4 | 3 | 0 | 1 (MAJ→MINOR: race_setup/controller) | 0 |
| 17 | 5 (1 CRI + 4 MAJ) | 2 | 3 | 0 | 0 | 0 |
| 18 | 17 (7 CRI + 10 MAJ) | 9 | 8 | 0 | 7 (4 CRI→MAJ/ADV, 3 MAJ→MINOR) | 0 |
| **TOTAL** | **44** | **20** | **25** | **0** | **18** | **0** |

**Note:** "Reviewed" counts only CRITICAL/MAJOR claims explicitly verified. MINOR/ADVISORY pass-through confirmations are documented in the gap listing below but not double-counted as reviewed claims. Disputed rate across shards: 57%.

---

## All CONFIRMED Gaps

---

### Shard 13

#### [MINOR] game/ui/screens/workshop_data_loader.py — load_all error paths
- **Shard**: 13
- **Location**: workshop_data_loader.py:157-168
- **Original severity**: MAJOR, downgraded to MINOR
- **Untested**: try/except blocks in `load_all` for `FileNotFoundError`/`OSError`, `JSONDecodeError`/`KeyError`/`TypeError`, and `ValueError`. Corrupt JSON, missing `modifiers.json`, missing `components.json` — none of these error paths are exercised.
- **Note**: `find_file` method is well-tested (249 LOC of tests across 2 test files). Only exception handlers remain untested.

#### [MINOR] game/strategy/services/replay_resolver.py — replay_dir is None branch
- **Shard**: 13
- **Location**: replay_resolver.py:103-104
- **Original severity**: MAJOR, downgraded to MINOR (identified within DISPUTED claim)
- **Untested**: `replay_dir is None` branch returns `"missing"`. The store fixture in all tests always creates a save_root with a valid replay_dir.
- **Note**: 10 of 11 branches comprehensively tested in `tests/integration/replay/test_replay_resolver.py`.

#### [MINOR] game/ui/screens/strategy_render/context.py — hex_radius_to_screen guard clause
- **Shard**: 13
- **Location**: context.py:25-26
- **Original severity**: MAJOR, downgraded to MINOR
- **Untested**: `radius_hexes <= 0` branch returning `3`. The renderer test only passes positive radii. Different `hex_size` and `zoom` values are also untested (all tests use hex_size=10, zoom=1.0).
- **Note**: Core power-curve formula is tested via `StrategyRenderer._hex_radius_to_screen()` wrapper.

#### [MINOR] game/simulation/event_bus.py — empty event_type emission
- **Shard**: 13
- **Location**: event_bus.py (exact lines not specified in verified report)
- **Original severity**: MINOR (Phase 1)
- **Untested**: Empty event_type emission path.
- **Suggested test**: Test that emitting an event with an empty or None event_type is handled gracefully or ignored.

#### [MINOR] game/engine/physics.py — radiation edge cases
- **Shard**: 13
- **Location**: physics.py (exact lines not specified in verified report)
- **Original severity**: MINOR (Phase 1)
- **Untested**: Empty stars list for radiation calculation, distance=0 clamp behavior.
- **Suggested test**: Verify radiation calculation with empty input and zero-distance boundary.

#### [MINOR] game/ui/strategy_camera_nav.py — _resolve_global_hex edge branches
- **Shard**: 13
- **Location**: strategy_camera_nav.py (exact lines not specified in verified report)
- **Original severity**: MINOR (Phase 1)
- **Untested**: Edge branches in `_resolve_global_hex` method.
- **Suggested test**: Exercise `_resolve_global_hex` with boundary hex coordinates.

#### [MINOR] game/ui/orders_window.py — OrderType branches
- **Shard**: 13
- **Location**: orders_window.py (exact lines not specified in verified report)
- **Original severity**: MINOR (Phase 1)
- **Untested**: Some OrderType enum branches in order rendering/processing.
- **Suggested test**: Ensure all OrderType values are exercised in window rendering/logic.

---

### Shard 14

#### [MAJOR] game/ui/strategy_fleet_command_router.py — All 10 symbols
- **Shard**: 14
- **Location**: strategy_fleet_command_router.py (entire file)
- **Untested**: Zero coverage on all 10 symbols:
  - `FleetCommandRouter.__init__` (trivial)
  - `scene` property (delegates to handler)
  - `input_mode` getter/setter (delegates to handler)
  - `handle_fleet_action` — 9 `InputAction` branches: MOVE, JOIN, COLONIZE, TRANSFER, DROP_CARGO, LOAD_CARGO, WARP, CANCEL_MODE + unknown
  - `handle_superweapon_action` — 6 branches: IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP, CLOSE_WARP, DYSON_SPHERE, SELF_DESTRUCT
  - `handle_detail_action` — 8 branches: ORDERS, PLANET_ORDERS, SHIELD_TOGGLE, GEOLOGIC_TOGGLE, STELLAR_TOGGLE, WARP_TOGGLE, ABILITIES_WINDOW, FLEET_REPORT, BUILD
  - `_handle_ability_toggle` (L238-297, 60 lines) — facility scanning, component resolution, state determination, command dispatch
  - `finish_move_action` — shift-key check + mode reset
- **Note**: No test file exists; no indirect coverage found via grep.

---

### Shard 15

#### [MAJOR] game/simulation/components/modifier_manager.py — 5 deprecated static methods
- **Shard**: 15
- **Location**: modifier_manager.py:221-330
- **Untested**: 5 deprecated static methods have zero independent test coverage:
  - `add_modifier_static()` — lines 223-251
  - `remove_modifier_static()` — lines 253-259
  - `remove_modifier_inplace()` — lines 261-274
  - `get_modifier_static()` — lines 276-285
  - `get_all_effects_static()` — lines 287-294
  - `get_stat_summary_static()` — lines 296-330
- **Note**: Instance methods are well-tested (19 tests), and logic is nearly identical, so cleanup regression risk is LOW. The test file note claiming coverage via instance methods is inaccurate.
- **Suggested test**: Before PROJ-322 Task 1.3 cleanup, either write minimal smoke tests or verify zero callers exist in production code and delete without tests.

#### [MINOR] game/simulation/components/modifier_manager.py — _load_initial_modifiers()
- **Shard**: 15
- **Location**: modifier_manager.py:57-81
- **Original severity**: MAJOR, mitigated (CONFIRMED-MITIGATED)
- **Untested**: Not listed as a separate coverage symbol (private method called from `__init__`). Direct standalone call and re-call after construction are not tested. All 3 branches are exercised through constructor path.
- **Risk**: LOW — private method, covered through `__init__`.
- **Suggested test**: None critical; structural reporting gap only.

#### [ADVISORY] game/ai/spatial_behaviors/_formation_utils.py — compute_circular_position
- **Shard**: 15
- **Location**: _formation_utils.py (entire file, 39 LOC)
- **Original severity**: CRITICAL (in table) / ADVISORY (in narrative), resolved to ADVISORY
- **Untested**: `compute_circular_position` has 0 direct test references. Called from `escort_behavior.py` and `screen_behavior.py` (Tier 2 callers), so indirect exercise is plausible but unverified at unit level. Single branch: `total = max(int(total), 1)`.
- **Suggested test**: Unit test for `compute_circular_position` with corner-case parameters (count=0, count=1, large count, index=tied).

---

### Shard 16

#### [CRITICAL] game/simulation/replay/replay_outcome.py — Roundtrip contract
- **Shard**: 16
- **Location**: replay_outcome.py (entire file, 49 LOC)
- **Untested**: 4 of 5 callables have zero coverage:
  - `from_battle_outcome()` — factory from domain object
  - `to_dict()` — serialization
  - `from_dict()` — deserialization
  - Constructor — direct instantiation
- **Note**: Only `to_battle_outcome()` is indirectly exercised once in an integration test (`test_capture_pipeline.py:177`). The core PROJ-312 replay persistence roundtrip contract (`from_battle_outcome` → `to_dict` → `from_dict` → `to_battle_outcome`) is completely untested.
- **Suggested test**: Test full roundtrip: create BattleOutcome → ReplayOutcome.from_battle_outcome → to_dict → from_dict → to_battle_outcome, verify fidelity.

#### [CRITICAL] game/strategy/facade/slices/economy_slice.py — All 5 callables
- **Shard**: 16
- **Location**: economy_slice.py (entire file, 188 LOC)
- **Untested**: Zero coverage — no test file, no grep matches, no indirect import chain:
  - `get_colony_demographic_view` (~104 LOC) — habitability calculations, species iteration, food surplus bonus logic with cap enforcement, per-resource upkeep aggregation
  - All 4 other callables also untested
- **Note**: Heaviest untested gap in Shard 16. This DTO feeds strategy UI demographic panels at runtime.
- **Suggested test**: Dedicated test for `EconomySlice.get_colony_demographic_view` with multi-species colony fixtures covering habitability, food surplus caps, and resource upkeep.

#### [MAJOR] game/ui/screens/gravity_target_editor.py — All 9 callables
- **Shard**: 16
- **Location**: gravity_target_editor.py (entire file, 220 LOC)
- **Untested**: All 9 callables including:
  - `G_TO_MS2 = 9.81` conversion math
  - Slider range clamping (`MIN_GRAVITY_G=0.1` to `MAX_GRAVITY_G=3.0`)
  - Species `rc.preferences["gravity"].setpoint` lookup
  - Three preset button handlers
  - `_build_ui` widget construction
- **Note**: Integration tests only exercise modal-window mechanics, not editor domain logic.
- **Suggested test**: Unit tests for G↔ms² conversion at boundaries, slider clamp values, species ideal gravity lookup, and preset button behavior.

#### [MAJOR] game/ui/screens/galaxy_test/screen.py — 13/16 callables
- **Shard**: 16
- **Location**: galaxy_test/screen.py
- **Untested**: 13 of 16 callables:
  - `_create_menu_ui`, `_create_galaxy_ui`, `_create_system_ui`
  - `update`, `draw`, `handle_event`, `_handle_button_click`
  - `_go_to_menu`, `_go_to_galaxy_mode`, `_go_to_system_mode`
  - `_on_close`, `handle_resize`, `handle_input`
- **Note**: Only `_clear_ui` and MODE_* constants are tested (96 LOC test file). This is a developer testing tool, not user-facing. Practical risk is lower than gameplay-critical modules.
- **Suggested test**: Tests for mode-switching logic, event dispatch, and UI creation functions.

#### [MINOR] game/strategy/data/spatial_index.py — get_k_nearest() expansion loop
- **Shard**: 16 (Cross-Claim Verification — PASS confirmed)
- **Location**: spatial_index.py
- **Untested**: `get_k_nearest()` expansion loop with `max_radius=None` and sparse data.
- **Suggested test**: Exercise `get_k_nearest()` with None radius and sparse/empty index.

#### [MINOR] game/strategy/facade/slices/system_slice.py — Multiple methods
- **Shard**: 16 (Cross-Claim Verification — PASS confirmed)
- **Location**: system_slice.py
- **Untested**: `get_all_systems()`, `get_system_at_hex()`, `get_system_containing_fleet()` need explicit tests.
- **Suggested test**: Dedicated tests for each untested method with mock galaxy/system data.

---

### Shard 17

#### [CRITICAL] game/simulation/combat/families/seeker.py — 6 untested code paths
- **Shard**: 17
- **Location**: seeker.py:40-53, 73
- **Untested** (CONFIRMED with nuance — golden test provides baseline integration coverage):
  1. `fire()` with target outside `firing_arc` → `launch_vec` from `comp_facing` (line 42)
  2. `fire()` with `target=None` → `launch_vec` only (line 45 gate)
  3. `fire()` with `aim_vec.length() == 0` → fallback to `launch_vec` (line 50)
  4. `fire()` with non-zero `ship.velocity` → `p_vel` incorporates velocity (line 53)
  5. `WEAPON_REGISTRY` registration for `WeaponFamily.SEEKER` (line 73)
  6. `facing_angle` non-zero computation path (lines 40-42)
- **Note**: Happy path (target in arc) is covered by `test_weapon_dispatch_golden.py:346-368`. No dedicated unit test file exists.
- **Suggested test**: Write `tests/unit/simulation/combat/families/test_seeker.py` covering all 6 paths.

#### [MAJOR] game/ui/screens/strategy_windows/fleet_report_ctrl.py — 4 untested code paths
- **Shard**: 17
- **Location**: fleet_report_ctrl.py:33-49, 62-63
- **Untested**:
  1. `SplitFleetCommand` closure dispatch correctness — field construction, command routing never verified (lines 37-49)
  2. Dimension computation at 90% of screen — `w, h = c.width * 0.9, c.height * 0.9` (lines 33-34)
  3. `_on_closed` clears window reference — `self._composer.fleet_report_window = None` (lines 62-63)
  4. `facade.handle_command()` routing through CQRS pipeline (line 49)
- **Note**: Indirect coverage via `test_strategy_window_manager.py` exercises window creation happy path but does not test internal logic of `FleetReportRegistrar.open()`.
- **Suggested test**: Dedicated test for `FleetReportRegistrar.open()` verifying SplitFleetCommand construction, dimension math, and `_on_closed` cleanup.

---

### Shard 18

#### [CRITICAL] game/core/protocols/common.py — No dedicated tests
- **Shard**: 18
- **Location**: protocols/common.py (entire file, 46 LOC)
- **Untested**: All 7 symbols — `_has_attrs` helper and 3 protocols (`ILocatable`, `INamed`, `IOwnable`). No dedicated unit test file exists.
- **Note**: `_has_attrs` is a trivial one-liner (`all(hasattr(obj, attr) for attr in attrs)`). Protocols are `@runtime_checkable` and exercised pervasively through `isinstance()` checks. Risk is mitigated by simplicity but foundational nature warrants coverage.
- **Suggested test**: Direct test for `_has_attrs` with valid/invalid attribute sets.

#### [CRITICAL] game/simulation/entities/ship_resource_manager.py — All 3 symbols
- **Shard**: 18
- **Location**: ship_resource_manager.py (entire file, 53 LOC)
- **Untested**: `__init__`, `get_resource_stat`, and class-level state fields. No dedicated unit tests. `get_resource_stat` constructs `f'{resource_name}_{stat_type}'` + `getattr(self._ship, attr_name, 0.0)` — the silent-return-0.0 fallback for typos/bad inputs is untested.
- **Suggested test**: Test `get_resource_stat` with known attributes, bad attribute names (verify returns 0.0, not raises), edge cases.

#### [CRITICAL] game/simulation/entities/stat_contributors/weapons.py — aggregate_targeting_scores
- **Shard**: 18
- **Location**: weapons.py (entire file, 56 LOC)
- **Untested**: `aggregate_targeting_scores` — called by ship stats calculator pipeline. No direct unit test. `isinstance(ecm_score, bool)` defensive cast and side-effect writes (`ship.baseline_to_hit_offense = attack_mods`) are not tested in isolation.
- **Suggested test**: Test targeting score aggregation with bool ecm_score, normal values, zero values, and verify baseline_to_hit_offense side effect.

#### [MAJOR] game/simulation/combat/formation.py — Tie-detection and "other" archetype
- **Shard**: 18
- **Location**: formation.py:296-299
- **Untested**: `resolve_default_for_task_force` tie-detection branch (equal-count tied archetypes, e.g., 2 strike + 2 defender). "other" archetype fallback path (ships with `design_role=''` or unrecognized role hitting line 299).
- **Note**: Default formation composition IS tested for majority archetypes. Tie and unrecognized paths are always untested.
- **Suggested test**: Create ship lists with equal counts of different archetypes; create ship with empty/unrecognized design_role.

#### [MINOR] game/simulation/components/abilities/planetary.py — __init__ non-dict edge case
- **Shard**: 18
- **Location**: planetary.py
- **Original severity**: MAJOR, downgraded to MINOR
- **Untested**: Non-dict `data` parameter else-branch in planetary ability `__init__` methods. The 18 `__init__` methods flagged as untested are false positives from heuristic name matching — they ARE tested through `get_primary_value`/`get_ui_rows` tests.
- **Note**: The non-dict data edge case is a rare production scenario.
- **Suggested test**: Instantiate a Planetary ability with non-dict data parameter and verify fallback behavior.

#### [MINOR] game/strategy/data/fleet_pursuer_tracker.py — hasattr guard
- **Shard**: 18
- **Location**: fleet_pursuer_tracker.py:103
- **Original severity**: MAJOR, downgraded to MINOR
- **Untested**: `hasattr(new_target, '_pursuer_tracker')` guard in `redirect_pursuers`. In production, `new_target` is always a Fleet (which always has `_pursuer_tracker`), so the False path is unreachable.
- **Note**: Defensive coding pattern. Risk is MINOR.
- **Suggested test**: Test `redirect_pursuers` with a mock target that lacks `_pursuer_tracker` to verify guard behavior.

#### [MAJOR] game/strategy/data/naming.py — Exhaustion paths and to_roman edge cases
- **Shard**: 18
- **Location**: naming.py
- **Untested**:
  - `get_system_name` exhaustion path — empty `available_names` → `"Unknown-N"` fallback
  - `to_roman` out-of-range: n=0, n=-1, n=4000 (boundary values right at `if not (0 < n < 4000): return str(n)`)
- **Note**: No `test_to_roman` exists in entire test suite.
- **Suggested test**: Test `to_roman(0)`, `to_roman(-1)`, `to_roman(4000)` returning string representations. Test `get_system_name` with exhausted name pool.

#### [MAJOR] game/strategy/data/ship_instance.py — Pod storage, repair, activation, cache invalidation
- **Shard**: 18
- **Location**: ship_instance.py:465-479
- **Untested**:
  - `get_pod_storage_capacity` / `get_pod_storage_used` / `can_carry_pod` — actual implementations calling `self.get_calculated_stats()` and `sum(item.get('mass', 0.0))` are NOT tested (only mocked in tests)
  - `repair` — completely untested
  - `set_activation_state` / `get_activation_state` — tested at FACILITY level but not at ShipInstance level for ship abilities
  - `invalidate_stats_cache` — called indirectly at `test_resource_pipeline.py:240` but not tested in isolation
- **Note**: Pod storage has the most impact (colonization core 4X feature). Mock-only coverage proves interface contracts but not implementation correctness.
- **Suggested test**: Test pod storage capacity/usage with calculated stats fixtures. Test repair with damaged ship. Test activation state get/set on ShipInstance.

#### [MAJOR] game/strategy/engine/action_execution_engine.py — 6 return-None branches
- **Shard**: 18
- **Location**: action_execution_engine.py:116-159
- **Untested**: `_process_fleet_action_tick` 6 return-None branches tested only indirectly:
  1. Speed <= 0 (line 131)
  2. `tick % interval != 0` (line 138)
  3. No order (line 143)
  4. Movement order skip (line 147)
  5. BUILD order skip + auto-completion with `pop_order` when queue empty (line 151-156)
  6. Non-action order skip (line 159)
- **Note**: Indirect coverage via `process_action_ticks` public API. BUILD auto-completion (`pop_order` on empty queue writing back, line 154) is a state mutation without dedicated verification.
- **Suggested test**: Dedicated tests creating each scenario and asserting the `_process_fleet_action_tick` None return, especially BUILD queue auto-completion.

#### [MINOR] game/strategy/services/combat_modifier_collector.py — Private helper edge cases
- **Shard**: 18
- **Location**: combat_modifier_collector.py:88-91, 157-158, 183-184
- **Original severity**: MAJOR, downgraded to MINOR
- **Untested**:
  - `_entry_scope` — `entry.get('scope') == None` fallback to `get_ability_default_scope` (line 88-91)
  - `_find_reference_planet` — `galaxy=None` path (line 157-158)
  - `_find_empire` — no-match returns None path (line 183-184)
- **Note**: Public `collect_combat_modifiers` is well-tested and exercises helpers indirectly. Scope=None branch was a known PROJ-272 bugfix.
- **Suggested test**: Explicitly test scope=None entry using default scope; test reference planet lookup with None galaxy.

---

## Summary by Severity

| Severity | Count | Files |
|----------|-------|-------|
| CRITICAL | 5 | replay_outcome.py, economy_slice.py, seeker.py, protocols/common.py, ship_resource_manager.py, stat_contributors/weapons.py |
| MAJOR | 8 | strategy_fleet_command_router.py, deprecated statics (modifier_manager.py), gravity_target_editor.py, galaxy_test/screen.py, fleet_report_ctrl.py, formation.py, naming.py, ship_instance.py, action_execution_engine.py |
| MINOR | 11 | workshop_data_loader.py, replay_resolver.py, hex_radius_to_screen, event_bus.py, physics.py, strategy_camera_nav.py, orders_window.py, _load_initial_modifiers, spatial_index.py, system_slice.py, planetary.py (__init__ edge), fleet_pursuer_tracker.py, combat_modifier_collector.py |
| ADVISORY | 1 | _formation_utils.py |

---

## Highest Priority Gaps (CRITICAL)

1. **`economy_slice.py`** (188 LOC) — Completely untested facade slice. Heaviest untested DTO, feeds strategy UI demographic panels.
2. **`replay_outcome.py`** (49 LOC) — Roundtrip contract (serialize/deserialize/battle conversion) untested.
3. **`seeker.py`** (73 LOC) — 6 edge-case code paths in missile targeting/firing untested (target=None, out-of-arc, zero-length aim vector, velocity incorporation).
4. **`ship_resource_manager.py`** (53 LOC) — Silent 0.0 returns for bad attribute names untested.
5. **`stat_contributors/weapons.py`** (56 LOC) — `aggregate_targeting_scores` bool defense check and side-effect writes untested.
6. **`protocols/common.py`** (46 LOC) — Foundational duck-typing helper with no dedicated test.
