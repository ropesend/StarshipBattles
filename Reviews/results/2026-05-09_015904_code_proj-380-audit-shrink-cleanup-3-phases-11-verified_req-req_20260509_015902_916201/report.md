# Review Report: PROJ-380 Audit-Shrink Cleanup

**Review Type:** code
**Request ID:** req_20260509_015902_916201
**Review Mode:** standard
**Scope:** PROJ-380 — 3 phases, 11 verified items, 12 commits on `feat/03c-phase-aware-execution`
**Completed:** 2026-05-09T02:00:00Z
**Agents:** 6 (ProviderFactory/Phase2, Camera.hex_at_screen, MissionHandler/BattleEndCondition, DUP-X-07 narrowing, DUP-X-12 narrowing, Rule3/Phase1)

---

## Executive Summary

**0 CRITICAL, 5 MAJOR, 8 MINOR, 30 INFO.** All 9 Phase 3 consolidations pass functional review. The two audit-claim narrowings (DUP-X-07, DUP-X-12) were **over-conservative** — 4 of 5 MAJOR findings arise from missed consolidation opportunities.

---

## MAJOR Findings

### FND-012 — No test validates real `screen_to_world` → `pixel_to_hex` chain
**File:** `game/ui/renderer/camera.py:154-172`  
**Severity:** MAJOR

Every test exercising `hex_at_screen` mocks or stubs the method. No test verifies the real `screen_to_world → pixel_to_hex` chain. Regressions in `screen_to_world` viewport math would pass all existing tests.

**Recommendation:** Add a dedicated unit test in `tests/unit/ui/renderer/` that creates a Camera with known position/zoom/offset, calls `hex_at_screen`, and asserts the returned `HexCoord` matches the expected transform.

---

### FND-017 — `handle_colonize_designation` has no test coverage
**File:** `game/ui/screens/strategy_colonization.py:158`  
**Severity:** MAJOR

`handle_colonize_designation` is the single `hex_at_screen` call in the colonization module. It has zero test coverage. `test_strategy_colonization.py` tests `on_colonize_click` (fleet-location based) but never exercises the screen-click path.

**Recommendation:** Add tests covering no-fleet → returns None, no-system-at-hex → None, no-colonizable-planets → None, valid planets → returns prompt.

---

### FND-031 — DROP_CARGO / LOAD_CARGO left-click bodies are identical
**File:** `game/ui/screens/strategy_click_dispatcher.py:255-277`  
**Severity:** MAJOR

`_handle_drop_cargo_mode_click` (line 255) and `_handle_load_cargo_mode_click` (line 267) differ by a single string literal (`'unload'` vs `'load'`). Both follow: `resolve target_hex → get fleet → open_cargo_quick_dialog → reset SELECT`. The agent's claim that "left-click bodies diverge significantly" is wrong for these two.

**Recommendation:** Consolidate into parameterized handler: `_handle_cargo_quick_click(self, mx, my, button, operation: str)`.

---

### FND-032 — TRANSFER shares same skeleton as DROP/LOAD_CARGO
**File:** `game/ui/screens/strategy_click_dispatcher.py:228-238`  
**Severity:** MAJOR

`_handle_transfer_mode_click` uses the identical 4-line skeleton (`resolve → fleet → open dialog → reset SELECT`) as DROP_CARGO and LOAD_CARGO. Only diff: `open_transfer_dialog(fleet, target_hex)` vs `open_cargo_quick_dialog(fleet, target_hex, operation_string)`.

**Recommendation:** A broader parameterized `_handle_dialog_mode_click(dialog_method, *args)` handler would cover all three. The DUP-X-07 narrowing was over-conservative.

---

### FND-041 — `_star_provider` over-conservatively excluded from consolidation
**File:** `game/strategy/services/ability_iterator.py:229-261`, `game/strategy/services/ability_sources/star.py:45`  
**Severity:** MAJOR

The agent excluded `_star_provider` because of its scope-aware fallback logic (system-scope ability introspection). This logic can be moved into `StarAbilitySource.affects_hex` — the semantic home for "does this source affect this hex?" queries. With the scope check in the adapter, `_star_provider` collapses to a 5-line delegation to `_iter_hex_filtered_sources`.

**Recommendation:** Move scope-aware fallback into `StarAbilitySource.affects_hex` (`star.py:63`), then consolidate `_star_provider`. Correct narrowing: 7 → 4, not 7 → 3.

---

## MINOR Findings

| ID | File:Line | Description |
|----|-----------|-------------|
| FND-010 | `strategy_superweapons.py:8`, fleet_ops/colonization docstrings | Stale `pixel_to_hex` references in 3 module docstrings |
| FND-011 | `test_strategy_superweapons.py:27` | Mock returns `tuple(5,5)` instead of `HexCoord(5,5)` |
| FND-013 | `test_strategy_fleet_ops.py:66` | `screen_to_world.assert_not_called` should be `hex_at_screen.assert_not_called` |
| FND-018 | `camera.py:154` | No dedicated `Camera.hex_at_screen` unit test |
| FND-031b | `test_battle_end_conditions.py:583` | `MassRatioCondition` missing from protocol conformance parametrize (ID clash resolved in report) |
| FND-032b | `battle_end_conditions.py:245` | `TeamIncapacitatedCondition` relies on base `_serialize_fields` default (cosmetic, not a bug) |
| FND-052 | `strategy_fleet_ops.py:25` | Cosmetic log casing normalization (`Failed` → `failed`) |
| FND-054 | `strategy_superweapons.py:32` | Trailing period dropped from returned error message in `_check_fleet_ability` |

---

## INFO Findings (Key Highlights)

### DUP-X-02 ProviderFactory: All passes
- Both consumers genuinely delegate to `resolve_provider` (not renamed internal classes).
- The shared base captures real behavioral logic (env-var resolution, dict lookup, config error raising, deferred validation).
- Zero layer violations — `game/services/provider_factory.py` imports only stdlib + `game.core.exceptions`.
- No shim introduced.

### Phase 2 superseded marker: VERIFIED
`grep -n "_static" game/simulation/components/modifier_manager.py` returns 0 hits. PROJ-384's deletion of all 6 `*_static` methods is complete. The superseded marker is correct.

### DUP-X-08 Camera.hex_at_screen: Semantics preserved
Coordinate transform chain (`screen_to_world` → `pixel_to_hex`) is identical to the inline pattern it replaced. All 11 call sites migrated. No unreconstructible camera state. Grid renderer exception (`strategy_render/grid.py`) confirmed correct — operates on world coords, not screen clicks.

### DUP-X-01 MissionCommandHandler: All passes
Genuine `BaseCommandHandler` subclass, not a shim. All 5 mission handlers fit the `_validate_mission` hook cleanly. Template is minimal (2 attrs + 1 hook + 5-line execute). No conflict with PROJ-383. All 11 handlers register correctly via `@command_spec` + `CommandRegistry`.

### DUP-X-11 BattleEndCondition serialization: All passes
Base `to_dict` correctly delegates to per-subclass `_serialize_fields`. All 9 subclasses inherit cleanly. `EscapeCondition` tuple coercion handled both ways. `AnyCondition`/`AllCondition` nested recursion round-trips correctly. Keeping `from_dict` per-subclass is the correct decision (divergent extraction rules).

### DUP-X-07 right-click consolidation: Correct
`_cancel_input_mode` faithfully replicates all 9 right-click cancel branches. `_handle_edit_move_click`'s `on_cancel` callback is correctly wired — cleanup runs before mode flip.

### DUP-X-12 consolidated providers: Correct
`_iter_hex_filtered_sources` correctly handles `_storm_provider`, `_planet_intrinsic_provider`, and `_warp_point_provider`. `_facility_provider` (nested iteration), `_fleet_provider` (lookup callbacks), and `_system_archetype_provider` (0-or-1 yield) correctly excluded.

### Rule 3 compliance: All passes
All 6 private helpers (`_distribute_cargo_to_fleet`, `_get_cell_detail`, `_format_result_error`, `_cancel_input_mode`, `_check_fleet_ability`, `_iter_hex_filtered_sources`) are clean factorizations — no shims, fallback paths, or surprise behavior.

### Phase 1 dead import: VERIFIED
`IControllableShip` fully removed. String annotation updated to `'ShipControllableAdapter'`. Zero stale references.

### Test migration: VERIFIED
5 test files underwent mock-rewrite only (`pixel_to_hex` patches → `camera.hex_at_screen` mocks). Zero test cases deleted, zero added. All assertions preserved.

---

## Findings Tally

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 5 |
| MINOR | 8 |
| INFO | 30 |

---

## Overall Assessment

The 9 Phase 3 consolidations are functionally sound and conform to project conventions. The Phase 2 superseded marker is correct. Phase 1 dead import removal is complete. No regressions or design flaws found.

The two audit-claim narrowings (DUP-X-07, DUP-X-12) were **over-conservative**, accounting for 4 of the 5 MAJOR findings. The audit's classification was closer to correct than the agent credited — 3 click-handler dup-pairs (TRANSFER/DROP_CARGO/LOAD_CARGO) and 1 ability provider (`_star_provider`) remain unconsolidated but could be.
