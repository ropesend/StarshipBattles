# Phase 0: Retarget / prune

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-495 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Re-grep every PROJ-480-inherited task's described pattern in the live tree before any TDD. Update phase 1-4 checklists in-place with corrected line numbers, drop NULL tasks, expand under-counted occurrences. No production-code or test edits in this phase — analysis only.

## Retarget Decisions (2026-05-23)

All 31 files exist. PROJ-479 status checked: DUP-005 absorbed `_make_empire` for the engine cluster (now `make_mock_empire` in `tests/unit/strategy/engine/conftest.py`); DUP-003 added `_assert_roundtrip_property` helper to `tests/conftest.py` but per-test migration was deferred.

### Phase 1 (2 KEEP, 0 DROP)
- Task 1.1 (T1.16, weapon_firing_system) — KEEP. 17 occurrences of `ship.total_shots_fired = 0` confirmed.
- Task 1.2 (T1.21, damage_calculator mock_ship factory unused) — KEEP. Factory at fresh line 356 still present; later test classes at 829+ still construct inline. Factory needs optional kwargs for emissive_armor / SRA / shields.

### Phase 2 (2 KEEP, 4 DROP)
- Task 2.1 (T2.5, ai_controller_unit nested patches + _make_ai_controller) — DROP `[~]` out-of-scope. `AIController(...)` construction is one line; the nested patches target different functions per test so a generic helper context manager wouldn't fit. The 11 `TestNavigateTo` methods each set 3-4 ship attrs that vary per test; helper would save ~1-2 LOC per test.
- Task 2.2 (T2.8, ship_stats 43-line setup) — DROP `[~]` out-of-scope. The file is 55 LOC with **a single** test method using the SimpleNamespace + class + MagicMock setup. Extracting a fixture for one test adds indirection without reducing complexity.
- Task 2.3 (T2.11, container 5 wrappers) — DROP `[~]` out-of-scope. The 5 wrappers (`_any_policy`, `_metals`, `_energy`, `_human`, `_fighter`) are called 83 times across the file. Inlining would explode LOC; the wrappers function as named factories/constants.
- Task 2.4 (T2.12, test_resupply_engine.py 9 factories → conftest) — DROP. **Absorbed by PROJ-479** DUP-005 / Task 5.4: `_make_empire` was migrated to `make_mock_empire` in `tests/unit/strategy/engine/conftest.py`, leaving only a thin local wrapper. The remaining 8 helpers (`_make_mock_registries`, `_make_fuel_facility`, `_make_energy_facility`, `_make_colony`, `_make_mock_ship`, `_make_mock_fleet`, `_make_mock_galaxy`, `_make_planet_with_fuel`) are file-specific fuel/resupply scaffolding; moving them to engine/conftest.py would pollute the shared conftest with single-file symbols.
- Task 2.5 (T2.23, fleet_navigation_action_timing nested patches) — KEEP. 11 occurrences of `find_hybrid_path` patch; clean context-manager extraction.
- Task 2.6 (T2.29, tech_preset_loader autouse fixture) — KEEP. 30 occurrences of `TECH_PRESETS_DIR` patch wrapper across all test classes.

### Phase 3 (9 KEEP, 11 DROP)
- Task 3.1 (T3.3, deprecated_code_removed 4+4 hasattr) — KEEP. Two clean clusters: `TestDeprecatedRegistryFunctionsRemoved` (4 hasattr-negative tests at lines 12-34) and `TestGameStateAliasesRemoved` (4 hasattr-negative tests at lines 45-67).
- Task 3.2 (T3.6, 9 event-emission) — DROP `[~]` out-of-scope. Tests span 3 distinct spawn methods (`_spawn_ship`, `_spawn_fleet_ship`, `_create_and_place_facility`) with substantively different mock-setup (patch.multiple for ShipInstance+Fleet vs single patch vs no patch). Parametrize over `(spawn_method, input_params, expected_event_kwargs)` would require per-row setup-builder functions equivalent to original.
- Task 3.3 (T3.7, 5 squadron roundtrips) — DROP `[~]` out-of-scope. Each test asserts on a different attribute (battle_role enum, combat_policy fields, spatial_behavior strings, flagship_id, omitted-optional defaults); parametrizing on `(kwargs, assert_fn)` would require 5 distinct lambdas roughly the size of the current test bodies.
- Task 3.4 (T3.8, 4 velocity-by-angle) — KEEP. Lines 344-387 are 4 identical-shape tests differing only in `angle` and `expected_x/y`.
- Task 3.5 (T3.9, 5 shield-regen) — KEEP. `TestShieldRegeneration` class at lines 58-145 with 5 identical-shape tests parameterizable on `(initial, max, rate, ticks, expected)`.
- Task 3.6 (T3.11, 4 valid-op bodies) — KEEP. Lines 80-102 in `TestValidOperationsStillWork` — 4 tests with `target_dict / apply / assert` per operation.
- Task 3.7 (T3.17, 2 test pairs) — KEEP. 4 tests at lines 16-56 (default + set/read for `fleet_attack_bonus` and `fleet_defense_bonus`).
- Task 3.8 (T3.18, 3 NavigationState destination) — KEEP. 3 tests at lines 19-78 use identical NavigationState setup differing only in order_type/target.
- Task 3.9 (T3.24, 2 resources_consumed) — DROP `[~]` out-of-scope. Setup differs nontrivially (colony pause vs fleet pause); the task's own description acknowledged this. Parametrize would re-introduce both setups via builder functions.
- Task 3.10 (T3.25, 4 planet energy) — DROP `[~]` out-of-scope. Each test has materially different setup (generator+battery, generator-only, battery-only, shield+battery+component_state). Parametrize would need per-case factory functions.
- Task 3.11 (T3.27, 2 immutable-tuple) — DROP `[~]` out-of-scope. The 2 tests use fundamentally different construction (direct kwargs vs `FleetInfo.from_fleet(fleet)`); a single parametrized test would obscure the two distinct construction paths.
- Task 3.12 (T3.28, 5 roundtrip) — KEEP. Lines 328-361 in `TestRoundTrip` — 5 identical-shape tests (name, ship_class, theme_id, team_id, color) all on `basic_ship`. Uses the PROJ-479 `_assert_roundtrip_property` helper now available in `tests/conftest.py`.
- Task 3.13 (T3.35, 3 setup-shared pursuer) — DROP `[~]` out-of-scope. The 3 tests verify materially different facets (orders rewritten, return shape, pursuer registry); sharing setup via a fixture would be fine but parametrize obscures intent.
- Task 3.14 (T3.39, 3 warp_resource_costs) — KEEP. 3 tests (`single_ship`, `multiple_ships`, `mixed_resource_types`) + 1 empty-fleet edge at lines 70-108 share `_build_mock_warp_ship` and assert against `get_warp_resource_costs()`.
- Task 3.15 (T3.42, 5 stabilizer cancellation) — DROP `[~]` out-of-scope. Each handler test has 5-15 LOC of distinct setup (different processor methods, target shapes, patch needs). Parametrize would need per-case builder functions equivalent to original.
- Task 3.16 (T3.44, 3 registry-read) — DROP `[~]` out-of-scope. The candidate tests differ in registration count and assertion structure; sharing a parametrized fixture isn't clearly clearer than current.
- Task 3.17 (T3.46, 5 superweapon handler cluster) — DROP `[~]` out-of-scope. Each handler verifies a different target dict shape (None / target_hex+name / destination_id+target_hex / planet ref / mass-resource setup). Parametrize over `(handler_cls, expected_order_type, expected_target_shape)` requires per-handler target-assertion functions.
- Task 3.18 (T3.47, 5 validator clusters) — DROP `[~]` out-of-scope. The 5 validators (planet-implode, star-stellerate, warp-open, warp-close, dyson) have different signatures and setup (e.g., open_warp_point needs name_map, dyson needs different system setup). 5×3=15 cases each needing a setup_func makes the parametrize harder to read than the originals.
- Task 3.19 (T3.48, 3 missing-field) — KEEP. Lines 41-73 — 3 PersistenceException tests parameterizable on `missing_key`.
- Task 3.20 (T3.49, 2 resolve_fleet) — KEEP (borderline). Two tests at lines 44-68 with `(fleet_setup_func, expected_error_substring)` parametrize saves ~10 LOC.

### Phase 4 (3 KEEP, 1 DROP)
- Task 4.1 (T4.3, join_fleet exact dict) — KEEP. Lines 235-242 confirmed.
- Task 4.2 (T5.1, ship_loading logic-heavy body) — DROP. The 42-LOC logic-heavy validation body has been **replaced with a `pytest.skip(...)` 6-line body** in PROJ-478 Task 1.10 (file is now 97 LOC total with a 5-line skip body at lines 92-97). No work remains.
- Task 4.3 (T5.2, empire_economy_caching fixture) — KEEP. 4× repeated `session, galaxy, empires = smoke_turn1_scenario; service = _build_service(fresh_registries)`.
- Task 4.4 (T5.15, meta-test imports) — KEEP. Lines 60-75 (`test_phase_4_gates_still_pass`) — clean removal.

### Cross-file collisions: None within PROJ-495 manifest.
### Risky-file boundary verified: None of the explicitly risky files leaked into PROJ-495.

---

## Tasks

### Task 0.1: Re-grep every core-mechanical pending task target

- [x] For each task in `phase_1_checklist.md`, `phase_2_checklist.md`, `phase_3_checklist.md`, `phase_4_checklist.md`, re-grep the described pattern in the target file (file paths in `manifest.md` already verified).
- [x] Edit the task in-place if the count or line range differs from the PROJ-480 plan.
- [x] Strike-through (don't delete — preserve traceability) any task whose target pattern no longer exists in the live tree.
- [x] Verify `tests/conftest.py` and `tests/unit/strategy/engine/conftest.py` helpers before any task proposes adding new ones — duplicates are out of scope.

### Task 0.2: Confirm no same-file collisions inside this project

- [x] No same-file pairs are currently expected in PROJ-495 (Codex's collision list was UI-heavy). Verify by scanning `manifest.md` for duplicate file paths.
- [x] If a collision is found post-scaffold, decide execution order (typically Phase 2 fixture/helper extraction → Phase 3 parametrize uses the fixture).

### Task 0.3: Confirm risky-file boundary with PROJ-496

- [x] Verify none of the explicitly risky files (`test_turn_engine_lazy_properties.py`, `test_persistence_adapter.py`, `test_battle_engine_tick.py`, `test_colony_output.py`, `test_generation.py` atmosphere, `test_bug_regressions_2026_01.py`, `test_generator_crew_requirement_design.py`) leaked into PROJ-495's manifest. They live in PROJ-496.

### Task 0.4: Validate Phase 0 closure

- [x] Run `python Projects/scripts/validate_phase.py PROJ-495 0`.
- [x] Update plan.md Current State: "Phase 0 complete; phase 1-4 checklists retargeted in-place against live tree."

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 1
