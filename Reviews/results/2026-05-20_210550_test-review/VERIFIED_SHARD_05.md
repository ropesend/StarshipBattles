# Shard 05 — Verified Findings

## Summary
- Shard: 05 | Claims verified: 13 (11 shard + 2 cross-shard) | Confirmed: 12 | Disputed: 0 | Inconclusive: 0 | Cross-shard shard-misassignment: 1
- Verification method: read every cited file at cited line ranges + 10 lines above/below; inspected production code for one claim

---

## Verified Findings — Shard Report

### F-005-001: test_ship_fleet_attrs.py — CAT-10 near-identical test pairs

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MINOR (unchanged) |
| **Verification** | Read `tests/unit/simulation/entities/test_ship_fleet_attrs.py:1-56`. Tests at lines 16-24 (`fleet_attack_bonus_default_is_zero`) and 26-34 (`fleet_defense_bonus_default_is_zero`) are structurally identical except attribute name. Tests at lines 36-45 and 47-56 are structurally identical except attribute + hardcoded value. Both pairs are candidates for `@pytest.mark.parametrize("attr,new_val")`. |

### F-005-002: test_modifier_manager.py — CAT-4 legacy vs stateful duplication

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MAJOR (unchanged) |
| **Verification** | Read `tests/unit/simulation/components/test_modifier_manager.py:1-409`. Production code at `game/simulation/components/component.py:328-333` confirms `Component.add_modifier()` delegates to `ModifierManager.add_modifier()` + calls `recalculate_stats()`. `TestModifierManagerAddRemove` (lines 10-53) and `TestStatefulModifierManagerAddModifier` (lines 186-283) both test `add_modifier` success/replace/not-found on the same underlying `ModifierManager` logic. `TestModifierManagerQuery` (lines 55-75) and `TestStatefulModifierManagerQuery` (lines 312-379) both test `get_modifier` found/missing. **Nuance**: The legacy tests additionally verify `Component.recalculate_stats()` side effect (not covered by stateful tests), but this is likely covered in `Component`-level tests elsewhere. The stateful tests add deny_types/allow_types coverage the legacy tests lack. The deletion recommendation is sound. |

### F-005-003: test_process_colonize_validation.py — CAT-4 duplicate colonize tests

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MAJOR (unchanged) |
| **Verification** | Read `tests/unit/strategy/engine/test_process_colonize_validation.py:181-241`. `test_process_colonize_universal_drop_pod_succeeds` (line 181, pod_type="CONTINENTAL") and `test_process_colonize_correct_pod_type_succeeds` (line 212, pod_type="ICE_DWARF") are structurally identical: same fleet/setup/execute/assert pattern. The only difference is the pod type string. Since Phase 3 made drop pods universal, both exercise the same production code path. Docstrings differ (one references "Phase 3 universal", the other "PROJ-140 correct type") but functionally identical. |

### F-005-004: test_order_processor_fleet_merge.py — CAT-6 mocking internal implementation detail

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MAJOR (unchanged) |
| **Verification** | Read `tests/unit/strategy/engine/test_order_processor_fleet_merge.py:31-62`. The test patches `type(target).trigger_speed_recalculation` (an internal dispatch method) and inspects `call_args_list` with custom logic (line 52-58) to determine if the recalc was called with `target` as `self`. The test itself acknowledges brittleness in the docstring (line 20: "the documentation cost (this file) is the price of certainty"). The suggested behavior assertion (set known ship speeds and verify merged fleet speed equals the slowest) would test the contract instead of mirroring implementation wiring. |

### F-005-005: test_join_fleet_handler.py — CAT-11 exact dict equality on event payload

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MINOR (unchanged) |
| **Verification** | Read `tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py:217-242`. The test asserts exact 7-key dict equality `payload == {...}` covering `category`, `empire_id`, `message`, `fleet_id`, `target_fleet_id`, `ship_count`. Any new field added to the FLEET_JOINED event payload would break this test even if the contract is satisfied. Suggestion to assert only structural keys is valid. |

### F-005-006: test_destination_path.py — CAT-10 repeated NavigationState construction

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MINOR (unchanged) |
| **Verification** | Read `tests/unit/strategy/fleet_navigation/test_destination_path.py:19-131`. Three tests (lines 19-37, 39-57, 59-78) construct identical `NavigationState(location=HexCoord(0,0), path=(), speed=5.0, can_warp=True)` with only the `orders` parameter differing. The `TestGetDestination` class (line 16) has no shared fixture. Suggestion to extract common NavigationState construction as a fixture or parametrize is sound. |

### F-005-007: test_battle_engine_tick.py — CAT-12 for-loop tick counting tests

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MINOR (unchanged) |
| **Verification** | Read `tests/unit/simulation/systems/test_battle_engine_tick.py:610-617, 740-748`. `test_multiple_ticks_increment_counter` (line 610) loops `range(10)` calling `engine.update()` then asserts `tick_counter == 10`. `test_rapid_succession_ticks` (line 740) loops `range(100)` then asserts `tick_counter == 100`. These are for-loop-as-test-logic with different hardcoded counts. Parametrizing `(n, [1, 10, 100])` would merge them into one test. Suggestion is valid. |

### F-005-008: test_battle_engine_tick.py — CAT-12 call-order tracking with list indexing

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MINOR (unchanged) |
| **Verification** | Read `tests/unit/simulation/systems/test_battle_engine_tick.py:363-388`. The test replaces `ai.update` and `ship.update` with closures that append to `call_order`, then computes `max(ai_indices) < min(ship_indices)` via list comprehensions — 10+ lines of test logic beyond simple assertions. The suggested simplification `assert call_order.index("ai") < call_order.index("ship")` is valid for testing "AI comes before ships." However, note the current approach verifies ALL AIs come before ALL ships (stronger invariant), while `index()` only checks the first occurrence (weaker). The `max < min` approach is a stricter invariant test. Suggestion holds but with this nuance. |

### F-005-009: test_bug_04_display.py — CAT-8 5+ nested with patch() blocks

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MINOR (unchanged) |
| **Verification** | Read `tests/repro_issues/test_bug_04_display.py:35-105`. Outer `with patch(...)` block spans lines 45-60 with 15 patches. Inside this, nested `with patch.object(panel, ...)` at line 80, further nested `with patch.object(panel.stats_panel, ...)` at lines 82-83 (depth=4). A second nested cluster at lines 95-96 adds 2 more levels. Total: 4+ nesting levels, 15+ patches. The suggestion to extract patching into a fixture is valid and would significantly improve readability. |

### F-005-010: test_new_game_setup.py — CAT-12 for-loop with nested assertions (low-end)

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MINOR (unchanged) |
| **Verification** | Read `tests/unit/ui/test_new_game_setup.py:154-165`. The test uses a for-loop over `range(0, 100)` computing `max_jump = max(max_jump, v - prev)` then asserts `max_jump <= 1`. This is runtime computation embedded in the test. The suggested replacement `all(system_count_slider_curve(t+1) - system_count_slider_curve(t) <= 1 for t in range(0, 99))` is semantically equivalent and more declarative. |

### F-005-011: test_new_game_setup.py — CAT-12 for-loop with nested assertions (monotonic)

| Field | Value |
|-------|-------|
| **Rating** | CONFIRMED |
| **Severity** | MINOR (unchanged) |
| **Verification** | Read `tests/unit/ui/test_new_game_setup.py:185-191`. Same pattern as F-005-010: for-loop with assertion inside. The suggested replacement `all(curve(t) >= curve(t-1) for t in range(1, 1001))` is semantically equivalent and eliminates the manual loop-accumulator pattern. |

---

## Verified Findings — Cross-Shard Report

### XS-005-001: DUP-005 — _make_empire helper in test_harvesting_engine.py

| Field | Value |
|-------|-------|
| **Rating** | FILE VERIFIED; SHARD ASSIGNMENT DISPUTED |
| **Severity** | N/A — informational |
| **Verification** | Read `tests/unit/strategy/engine/test_harvesting_engine.py:27-43`. The file contains `_make_empire(colonies=None, resource_pool=None, max_storage=None, empire_id=0)` — a MagicMock(spec=Empire) constructor matching the cross-shard report description. The helper body and signature match the pattern described in DUP-005/HLP-006. **However**: `tests/unit/strategy/engine/test_harvesting_engine.py` is NOT listed in the SHARD_05 report file manifest (86 files, lines 56-141 of SHARD_05.md). The cross-shard report's assignment of this file to Shard 05 appears incorrect. The file content claim is accurate; the shard membership claim is not. |

### XS-005-002: HLP-006 — _make_empire helper duplication pattern

| Field | Value |
|-------|-------|
| **Rating** | FILE VERIFIED; SHARD ASSIGNMENT DISPUTED |
| **Severity** | N/A — informational |
| **Verification** | Same analysis as XS-005-001. The `_make_empire` helper in `test_harvesting_engine.py:27` matches the described pattern (MagicMock Empire with `resource_pool`, `max_storage`, `_storage_dirty`, `_booster_dirty`). Cross-shard report claims this file is in Shard 05, but SHARD_05.md does not list it. The `tests/unit/strategy/engine/conftest.py` has only one fixture (`economy_calculator`) — the recommendation to create shared engine test fixtures there is valid regardless of shard assignment. |

---

## Verification Notes

1. **F-005-002 nuance**: The legacy `TestModifierManager*` classes test through `Component.add_modifier()` which additionally calls `recalculate_stats()` internally (`component.py:332`). The stateful tests call `ModifierManager.add_modifier()` directly without triggering recalculate. Deleting the legacy classes would lose explicit coverage of the recalculate_stats side effect triggered by Component.add_modifier — this is likely covered elsewhere but is a coverage gap worth noting.

2. **F-005-008 nuance**: The current `max(ai_indices) < min(ship_indices)` assertion is stronger than the suggested `call_order.index("ai") < call_order.index("ship")` replacement. The former verifies that ALL AI updates happen before ALL ship updates (strict interleaving invariant). The latter only verifies the FIRST AI update comes before the FIRST ship update (weaker invariant). The suggestion should be adjusted to preserve the stronger invariant, e.g., `assert all(i < j for i in ai_indices for j in ship_indices)` or similar.

3. **Cross-shard shard membership**: Both DUP-005 and HLP-006 reference `tests/unit/strategy/engine/test_harvesting_engine.py` as belonging to Shard 05, but the SHARD_05 report file manifest does not include this file. The help duplication claims are valid at the code level; the shard assignment appears to be a cross-shard report error. Recommend the cross-shard report be corrected.
