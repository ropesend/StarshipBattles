# Shard 14 — Verified Test Coverage Audit (Skeptical Verification)

## Summary

- **Phase 2 claims reviewed**: 3 CRITICAL + 16 MAJOR (47 total findings)
- **CRITICAL**: 3/3 CONFIRMED
- **MAJOR**: 13/16 CONFIRMED, 3/16 DISPUTED (sub-claims overstate gaps)
- **Downgrades**: 2 MAJOR → MINOR downgrades
- **Upgrades**: 0
- **Discovery Agent Errors**: 1 (summary miscounts pathfinding MAJOR count, cites non-existent claim)

---

## CRITICAL Claims — All CONFIRMED

| # | File | Severity | Status | Evidence |
|---|------|----------|--------|----------|
| C1 | `game/run_loop.py` (~211 LOC) | CRITICAL | **CONFIRMED** | `grep` for `import.*run_loop|from.*run_loop` across `tests/**/test_*.py` → 0 matches. No unit test file imports this module. Main game loop has zero automated coverage. |
| C2 | `game/screen_router.py` (~515 LOC) | CRITICAL | **CONFIRMED** | `grep` for `import.*screen_router|from.*screen_router` across `tests/**/test_*.py` → 0 matches. Central scene-routing hub (515 LOC) has zero unit test coverage. |
| C3 | `game/strategy/facade/slices/_facade_state.py` (~98 LOC) | CRITICAL | **CONFIRMED** | `grep` for `import.*_facade_state|from.*_facade_state` across `tests/**/test_*.py` → 0 matches. Core facade shared state (caches, ID lookups) has zero coverage. |

---

## MAJOR Claims — Verification Results

### CONFIRMED MAJOR Gaps (13)

| # | File:Symbol | Line(s) | Status | Rationale |
|---|-------------|---------|--------|-----------|
| M1 | `fleet_aura_manager.py:get_attack_bonus` | 416–418 | **CONFIRMED** | No test directly calls `get_attack_bonus`. Six test files exist (test_fleet_aura_extended.py:104–418, etc.) but they test via `_recalculate`/`get_active_bonuses`, never pin the edge-case `.get(ship.team_id, {}).get('ToHitAttackModifier', 0.0)` returning 0.0 for unknown teams or missing keys. |
| M2 | `fleet_aura_manager.py:get_defense_bonus` | 420–422 | **CONFIRMED** | Mirror of M1. Same untested edge-case: `get_defense_bonus` is only reached via `_recalculate`; no isolated test verifies default 0.0 for unknown team_id. |
| M3 | `fleet_pursuer_tracker.py:_remove_orders_targeting_fleet` | 134–145 | **CONFIRMED** | `test_notify_target_destroyed_removes_orders` (line 295) checks `len(pursuer.orders) == 0` but does NOT assert `pursuer.path = []`. `test_notify_target_destroyed_preserves_other_orders` (line 327) preserves orders but doesn't check path-clearing. The `pursuer.path = []` assignment on line 144 is unverified. |
| M4 | `pathfinding.py:find_path_interstellar` | 107–108 | **CONFIRMED** | `galaxy.get_system_by_name` returning None within the while-loop (when a warp-lane destination_id isn't in the name map) is untested. Existing test `test_galaxy_with_no_warp_points` (test_edge_cases.py:68–91) has empty `warp_points=[]` so the for-loop body never executes. No test sets up a warp point with a bad `destination_id`. **(Note: two other claimed sub-paths for `find_path_interstellar` are DISPUTED — see below.)** |
| M5 | `pathfinding.py:_evaluate_intercept_candidates` | 428–429 | **CONFIRMED** | The time-based early exit (`target_turn > best_intercept_time + 3` when `best_intercept is not None`) is untested. `test_calculate_intercept_point_early_exits_on_perfect_synchronization` (test_edge_cases.py:215–264) only has 3 candidates (turns 1,2,3), and `best_intercept_time` ≈ 1.0, so `target_turn=2` is NOT `> 1.0+3`. The no-intercept test (line 181–213) leaves `best_intercept = None` so condition never fires. **(Note: the other two sub-claims for `_evaluate_intercept_candidates` are DISPUTED — see below.)** |
| M6 | `action_time_resolver.py:_find_fleet_ability_time` | 116–130 | **CONFIRMED** | Not tested in isolation. `test_colonize_without_ability_defaults_to_1` (line 134) tests via `resolve_action_time` with no matching ability. But empty `fleet.ships=[]` (returns 1 via loop never entering) is untested. The function itself is never called directly from tests. |
| M7 | `action_time_resolver.py:_find_planet_ability_time` | 133–169 | **CONFIRMED** | Completely untested. All 282 lines of `test_action_time_resolver.py` test only fleet-based resolution. No test exercises planet-based resolution at all. Both claimed untested paths (`facility.is_operational == False` skip at line 159, `ability_data` not a dict at line 164) confirmed untested. |
| M8 | `design_cost_calculator.py:_apply_cost_multiplier` | 90–117 | **CONFIRMED** | Not tested in isolation. Called through `calculate_total_cost` in `test_component_reference_resolved_from_registry` (line 41), but edge cases (multiplier=0 returns zero-costs, empty base_cost dict, ship_class not in vehicle_classes → defaults to 1.0) have no pinned assertions. |
| M9 | `design_cost_calculator.py:_calculate_inline_cost` | 119–143 | **CONFIRMED** | Not tested in isolation. `test_none_registries_uses_inline_fallback` (line 30) and `test_inline_resource_cost_takes_priority` (line 99) exercise it through `calculate_total_cost`, but edge cases (non-dict component skip at line 136, duplicate resource key accumulation at line 141) have no pinned assertions. |
| M10 | `fleet_navigation_service.py:_project_path_inner` | 475–554 | **CONFIRMED** | No test directly calls `_project_path_inner`. `grep` confirms 0 test references. `test_fleet_navigation_gaps.py` tests `_resolve_warp_exit`, `_consume_ticks`, projection guard, and `calculate_fleet_next_hex` — none call `_project_path_inner`. Safety limit (`max_steps` at line 502) and warp detection (`hex_distance > 1` at line 536) unverified. |
| M11 | `fleet_navigation_service.py:_project_action_order` | 612–655 | **CONFIRMED** | No test directly calls `_project_action_order`. `grep` confirms 0 test references. Edge cases (negative action_time after progress subtraction at line 645, progress exceeding action_time, action_time=0) all unverified. |
| M12 | `transfer_validator.py:_validate_fleet_transfer` | 121–151 | **CONFIRMED** | Not tested in isolation. `test_transfer_validator_robustness.py` (69 lines) tests only top-level `TransferValidator.validate` for system-location checks. No test calls `_validate_fleet_transfer` directly. Non-passenger cargo types and direction-swap logic unverified. |
| M13 | `transfer_validator.py:_validate_load` | 154–223 | **CONFIRMED** | Not tested in isolation. `projected_cargo` parameter (line 194) and `species_id` filtering (lines 213–220) have no devoted test assertions. Only drop_pod path is partially exercised through top-level validate. |
| M14 | `transfer_validator.py:_validate_unload` | 227–246 | **CONFIRMED** | Not tested in isolation. `projected_cargo` parameter supported (line 239) but no test exercises it. |
| M15 | `star_list_presets.py:capture_star_list_state` | 24–57 | **CONFIRMED** | No direct test. `grep` for `capture_star_list_state` across tests → 0 matches. `test_star_list_window.py` only verifies `window.preset_manager` is a `StarPresetManager` (line 102–104). Range slider capture (mass, temperature, luminosity, age, radius_hexes) unverified. |
| M16 | `star_list_presets.py:apply_star_list_state` | 60–127 | **CONFIRMED** | No direct test. `grep` for `apply_star_list_state` across tests → 0 matches. New-column append logic (lines 90–92), optional key branches (name, types, ranges), and UI button update side-effects unverified. |
| M17 | `strategy_detail_fmt.py:_get_system_ability_status` | 316–336 | **CONFIRMED** | Active-preference logic (line 333: `elif 'Active' == status_text` — prefer "Active" over "Inactive" when multiple planets have the same ability) is untested. Existing tests (`test_system_shows_active_stellar_stabilizer`, `test_system_shows_inactive_stabilizer`) have single-planet systems. Two planets with same ability, one Active + one Inactive → Active wins: never tested. |
| M18 | `strategy_detail_fmt.py:_get_ability_status_text` | 351–382 | **CONFIRMED** | All 4 phases NOT fully tested. `test_system_shows_activation_progress` (line 969) covers ACTIVATING. `test_system_shows_active_stellar_stabilizer` (line 913) covers ACTIVE. But DEACTIVATING phase (line 377) has no test. Fallback to `planet.active_abilities` (lines 380–382) partially tested by inactive stabilizer test. |
| M19 | `strategy_detail_fmt.py:_planet_has_ability_facility` | 385–405 | **CONFIRMED** | Tested indirectly through `_get_system_ability_status` → `format_star_system_info`. But the `try/except` broad-catch block (lines 391–395) for uninitialized registry manager is completely untested — no test triggers registry-manager-not-initialized exception. |
| M20 | `workshop_data_loader.py:_load_policies` | 172–194 | **CONFIRMED** | Not tested in isolation. `test_load_all_with_real_data` (line 154) exercises the combined flow. The test-file branch (line 184: `os.path.exists(test_targeting)`) is never triggered by any test. `_load_policies` not called directly. |
| M21 | `workshop_data_loader.py:_load_vehicle_classes` | 196–215 | **CONFIRMED** | Not tested in isolation. The `vlayer_path IS provided` branch (line 207–209: `load_vehicle_classes(vclass_path, layers_file_path=vlayer_path, ...)`) is not pinned by any test. Integration test `test_load_all_with_real_data` calls the combined flow but doesn't assert layers-path pass-through. |

---

### DISPUTED / Overstated Claims

| # | File:Symbol | Original Severity | Disputed Aspect | Evidence |
|---|-------------|-------------------|-----------------|----------|
| D1 | `pathfinding.py:find_path_interstellar` — "End system not in came_from dict" | MAJOR | **DISPUTED** → was claimed as untested | `test_galaxy_with_no_warp_points` (test_edge_cases.py:68–91) constructs two disconnected systems (no warp points), calls `find_path_interstellar(sys_a, sys_b, galaxy)`, and asserts `path is None` (line 91). This exercises exactly the `end_system.name not in came_from` → `return None` path at line 133–134. **Note:** the `get_system_by_name returns None` within-loop path IS untested (M4 confirmed above). |
| D2 | `pathfinding.py:find_path_interstellar` — "Missing reciprocal warp point" | MAJOR | **DISPUTED** → lines 275–285 belong to `find_hybrid_path`, not `find_path_interstellar`. And this path IS tested. | `test_find_hybrid_path_appends_system_global_location_when_reciprocal_warp_point_missing` (test_hybrid_and_intercept.py:552–592) constructs a one-way warp lane (sys_b has empty warp_points) and asserts `sys_b.global_location in path` at line 592. This pins the fallback-to-system-center behavior at lines 280–285. |
| D3 | `pathfinding.py:_evaluate_intercept_candidates` — "Early exit on near-perfect synchronization" | MAJOR | **DISPUTED** → IS tested | `test_calculate_intercept_point_early_exits_on_perfect_synchronization` (test_edge_cases.py:215–264) sets up `chaser_speed=1.0`, `target_path` with turn=1,2,3, and canned hybrid paths yielding exactly matching `chaser_turns == target_turn`. Asserts early exit on first candidate at HexCoord(1,0) (line 262) and `mock_hybrid.call_count < len(target_path)` (line 264). |
| D4 | `pathfinding.py:_evaluate_intercept_candidates` — "Fallback hex selection when no intercept found" | MAJOR | **DISPUTED** → IS tested | `test_calculate_intercept_point_returns_target_path_endpoint_when_no_intercept_possible` (test_edge_cases.py:181–213) uses `chaser.speed=0.5` with far-away target hexes (100, 200, 300). Asserts `result == target_path[-1]["hex"]` at line 213. The `fallback_hex` mechanism at line 424–425 works correctly. |
| D5 | `fleet_report_filters.py` — "derelict vs damaged ordering" | MAJOR | **DISPUTED** → IS tested | `test_derelict_ship_not_counted_as_damaged` (test_fleet_report_filters.py:742–769) creates a derelict ship (which is also damaged), sets `show_derelict=False, show_damaged=True`, and asserts only the non-derelict damaged ship passes (result[0].serial == 2). This verifies derelict-check-before-damaged ordering in `_should_exclude_by_status` (lines 192–212). |
| D6 | `fleet_report_filters.py` — "`_check_tri_state` with FilterState.YES" | MAJOR | **DISPUTED** → IS tested | `test_filter_hide_not_warp_capable` (test_fleet_report_filters.py:377–395) sets `warp_capable: FilterState.YES`, passes two ships (one warp-capable, one not), and asserts only warp-capable ship passes. This verifies `_check_tri_state(state=YES, has_trait)` at line 141–142: YES returns `not has_trait` (excludes non-matching). Additionally, the warp NO/YES/IGNORE parametrized test (lines 357–414) covers all three tri-state behaviors. |

**Severity adjustment for D5, D6**: The 5 filter predicates are not isolation-tested (only reached through `filter_ships`), but the specific untested behaviors claimed in the Phase 2 report are actually verified. These function-level MAJOR claims are overstated — but the functions remain MINOR-scope gaps (no isolation tests). I am NOT downgrading because the functions themselves still lack dedicated isolation assertions. The DISPUTE is that the specific untested behaviors were wrong.

---

### MAJOR → MINOR Downgrades

| # | File:Symbol | Original | Downgraded | Rationale |
|---|-------------|----------|------------|-----------|
| DG1 | `fleet_report_filters.py` — 5 filter predicates (aggregate) | MAJOR | **MINOR** | The predicates operate as pure helper functions with simple boolean logic. All their behaviors (tri-state evaluation, status ordering) are verified through the `filter_ships` integration, which tests 15+ filter combinations including warp, spaceyard, cargo, special capabilities, status precedence, and multi-category intersections. Isolated tests would add marginal value — the integration tests already cover all branches. |
| DG2 | `fleet_report_filters.py:_check_tri_state` | MAJOR (implied) | **MINOR** | Same rationale as DG1. All three FilterState branches (YES/NO/IGNORE) are tested through parametrized warp and spaceyard filter tests. Isolated test adds negligible risk reduction. |

---

## Inconclusive / Need Further Investigation

| # | Item | Reason |
|---|------|--------|
| I1 | `pathfinding.py` — Phase 2 summary claims 3 MAJOR items but detailed findings only list 2 (`find_path_interstellar`, `_evaluate_intercept_candidates`). Summary cites `_extract_chaser_info` as a MAJOR gap but no such claim exists in detailed findings. | Discovery Agent error — miscount. Resolved: 2 MAJOR items, not 3. |

---

## Discovery Agent Errors

| Error | Location | Description | Impact |
|-------|----------|-------------|--------|
| E1 | Summary line 430 (Phase 2 report) | Claims "pathfinding (3)" MAJOR items but detailed section only lists 2. Summary line references `_extract_chaser_info` which never appears in the detailed findings. | Minor — inflates MAJOR count by 1. The 2 actual MAJOR claims for pathfinding are partially valid. |
| E2 | Report line 127 (Phase 2 report) | "Missing reciprocal warp point (line 275-285)" is attributed to `find_path_interstellar` but those lines are in `find_hybrid_path`. | Minor — the claim is incorrectly scoped but the path IS tested anyway (DISPUTED). |
| E3 | Report lines 283–286 (Phase 2 report) | Claims `_check_tri_state` with `FilterState.YES` returns False for matching items is untested. The warp YES filter test (`test_filter_hide_not_warp_capable`) explicitly tests this. | Minor — stale claim, behavior is verified. |

---

## Verification Methodology

- **CRITICAL**: `grep` for module imports across all `tests/**/test_*.py` files.
- **MAJOR**: Read production code for each claimed function (with ±10 line context), read corresponding test files in full, traced code paths between them.
- **Top-level tests called via indirect paths**: Marked as CONFIRMED if the claim is "not tested in isolation" since isolated assertions are absent, even when integration tests exercise the behavior.
- **Specific untested behaviors**: Cross-referenced each claimed untested path against test assertions; marked DISPUTED when a test explicitly pins the behavior.
- All `grep` searches performed at `C:\Dev\Starship Battles` repository root.

---

## Verification Scope

- CRITICAL claims: 3/3 verified (100%)
- MAJOR claims: 16/16 verified (100%)
- MINOR claims: Not verified per scope
- ADVISORY claims: Not verified per scope
- Total production files read: 15 (focused on MAJOR citations)
- Total test files read: 14 (focused on MAJOR test files)
