# Rule 3 Compliance + Phase 1 Verification Report

**Date:** 2026-05-09
**Review:** PROJ-380 audit-shrink cleanup (phases 1–3), Items A/B/C
**Scope:** 6 private helpers from phase 3, 1 dead-import removal from phase 1, 5 test files from phase 3.3

---

## Item A: Rule 3 Compliance — Helper Verifications

AGENTS.md Rule 3: *"No compatibility shims, fallback systems, monkey patches, or duplicate logic."*

### FND-050 — `_distribute_cargo_to_fleet` (fleet_consumable_aggregator.py:291)

**Severity:** INFO — Clean factorization

**Analysis:** The original `load_cargo_to_fleet` and `unload_cargo_from_fleet` were perfect mirrors differing only in `ship.load_cargo(...)` vs `ship.unload_cargo(...)`. The helper captures the shared 4-step skeleton:

1. Short-circuit on `amount <= 0`
2. `remaining = amount; total_moved = 0`
3. Iterate `self._fleet.ships`, break on exhaustion
4. `moved = ship_method(ship, cargo_type, remaining)` → accumulate

**Comparison:** Every statement in the helper maps 1:1 to the original bodies. The only abstraction is parameterizing the per-ship callable. `load_cargo_to_fleet` now delegates with `lambda ship, t, a: ship.load_cargo(t, a)`; `unload_cargo_from_fleet` with `lambda ship, t, a: ship.unload_cargo(t, a)`.

**Verdict:** No new logic, no fallback paths, no surprise behavior. Clean DRY extraction.

**Git:** `eae776ae0` (PROJ-380 phase 3.2)

---

### FND-051 — `_get_cell_detail` (event_log_data_source.py:150)

**Severity:** INFO — Clean factorization

**Analysis:** The original `get_cell_replay_id` and `get_cell_replay_unavailable_reason` shared an identical 4-step guard:
1. `get_event_at_index(row_index)` → None check
2. `event.get("category") != "combat"` → None
3. `event.get("details", {}).get(KEY)` → specific value extraction
4. Falsy-to-None coercion (`value if value else None`)

The helper parameterizes only step 3 via `detail_key`. The coercion on step 4 (`value if value else None`) is identical to the originals' `replay_id if replay_id else None` / `reason if reason else None`.

**Comparison:** Line-for-line identical logic. Both callers become one-liner delegates.

**Verdict:** No new logic, no surprise behavior. Clean DRY extraction.

**Git:** `c0e0ed5f2` (PROJ-380 phase 3.4)

---

### FND-052 — `_format_result_error` (strategy_fleet_ops.py:25)

**Severity:** MINOR — Clean factorization, documented log casing change

**Analysis:** Three callers (`execute_move`, `execute_intercept`, `execute_join`) all built identical error-result trailers:
```python
msg = result.message if result else 'Unknown'
logger.warning(f"{Verb} failed/failed: {msg}")
return {'type': 'error', 'message': msg}
```

The helper faithfully captures this 3-statement pattern. The dict returned is structurally identical.

**Behavior change (documented in commit):** Log message casing was normalized:
- `"Intercept Failed:"` → `"Intercept failed:"`
- `"Join Fleet Failed:"` → `"Join Fleet failed:"`
- `"Move failed:"` was already lowercased, unchanged.

The commit message (`afe1c4984`) explicitly calls this out: *"Minor casing change in log message: 'Intercept Failed' → 'Intercept failed', 'Join Fleet Failed' → 'Join Fleet failed'."* This is a cosmetic normalization in warning-level logs, not a functional change. No consumer parses these log strings.

**Verdict:** Clean factorization. Log casing normalization is cosmetic and documented. No shim.

**Git:** `afe1c4984` (PROJ-380 phase 3.5)

---

### FND-053 — `_cancel_input_mode` (strategy_click_dispatcher.py:83)

**Severity:** INFO — Clean factorization, well-scoped extension point

**Analysis:** The 9 mode-click handlers all shared the same 3-line right-click cancel block:
```python
self.input_mode = 'SELECT'
logger.debug("Input Mode: SELECT")
return True
```

The helper captures this verbatim. `_handle_edit_move_click` — the one divergent case that also clears `_edit_move_ghost_hex` / `_edit_move_order_index` / `_edit_move_fleet` — uses the `on_cancel` callback to inject its extra cleanup before the mode reset. The callback preserves the original execution order (clear fields, then flip mode).

**Behavior delta (additive only):** The callback introduces a debug log for `_handle_edit_move_click`'s cancel path that previously had no debug statement. This is strictly additive; debug lines have no functional impact.

**Verdict:** Clean factorization. `on_cancel` is a targeted extension hook, not a shim. Original behaviors are reproduced exactly.

**Git:** `f09893a5c` (PROJ-380 phase 3.7)

---

### FND-054 — `_check_fleet_ability` (strategy_superweapons.py:32)

**Severity:** MINOR — Clean factorization, undocumented cosmetic change in returned error message

**Analysis:** Five designation handlers repeated:
```python
if not fleet.capabilities.has_ability("AbilityName"):
    logger.warning("Fleet has no Component component.")
    return {'type': 'error', 'message': 'Fleet has no Component component'}
```

The helper parameterizes `ability_name` and `error_msg`. Callers pass the raw message string (without trailing period), and the helper appends `"."` for the log message while returning the unmodified `error_msg` in the dict.

**Behavior delta:** The original returned `{'type': 'error', 'message': 'Fleet has no Planet Imploder component.'}` (with trailing period). The helper returns `{'type': 'error', 'message': 'Fleet has no Planet Imploder component'}` (without trailing period). The **log** message is unchanged (helper does `error_msg + "."`). Only the **returned dict message** loses the trailing period.

This is a cosmetic difference in the error message string. No caller logic depends on trailing punctuation in error messages. The commit message does NOT document this difference — it was likely unintentional.

**Recommendation:** Either restore the trailing period in the returned message by using `error_msg + "."` in the dict too, or update callers to pass messages with the period already included. Low priority — this has zero functional impact.

**Verdict:** Clean factorization. Minor cosmetic drift in returned error message text. Not a shim.

**Git:** `2ecbad1a4` (PROJ-380 phase 3.3)

---

### FND-055 — `_iter_hex_filtered_sources` (ability_iterator.py:121)

**Severity:** INFO — Clean factorization, well-scoped

**Analysis:** The audit's original claim of "7 providers sharing the same skeleton" was overstated (and the commit message correctly acknowledges this reduction in scope). Only 3 providers (`_storm_provider`, `_planet_intrinsic_provider`, `_warp_point_provider`) share the 5-step pattern:

1. `system is None` short-circuit
2. Walk `getattr(system, container_attr, None) or []`
3. Filter items via `item_filter` predicate
4. Build adapter via `adapter_factory(item, system)`
5. Yield when `hex_coord is None or adapter.affects_hex(hex_coord)`

The helper faithfully captures all 5 steps. Provider-specific behavior is injected via two callables (`adapter_factory`, `item_filter`).

**Per-provider verification:**
- **`_storm_provider`**: `item_filter=lambda _: True` (no filtering, matching original). `container_attr='storms'`. Equivalent.
- **`_planet_intrinsic_provider`**: `item_filter=lambda planet: bool(getattr(planet, 'intrinsic_abilities', None))`. Original: `if not getattr(planet, 'intrinsic_abilities', None): continue`. Equivalent.
- **`_warp_point_provider`**: Same pattern as planet provider. Equivalent.

**Non-refactored providers (correctly excluded):**
- `_facility_provider`: Nested iteration (planets → facilities) doesn't fit the flat walk pattern.
- `_star_provider`: Has scope-aware fallback logic with system-scope ability inspection.
- `_fleet_provider`: Uses lookup callbacks, not `system.<attr>`.
- `_system_archetype_provider`: Emits 0 or 1 source, no list walk.

**Verdict:** Faithful reproduction. No new logic. Correctly scoped — divergent providers left alone.

**Git:** `ac76fddf1` (PROJ-380 phase 3.8)

---

## Item B: Phase 1 Dead Import Verification

### FND-056 — IControllableShip import successfully removed

**Severity:** INFO — Verified

**Checks:**

| Check | Result | Location |
|-------|--------|----------|
| `IControllableShip` no longer imported in `controller.py` | PASS — no grep match in `game/ai/` | `game/ai/controller.py:54-55` (only `SpatialGrid` remains in TYPE_CHECKING) |
| `IControllableShip` not referenced anywhere in `game/` | PASS — zero grep matches | Entire repo (search scope: `game/`) |
| String annotation updated to `'ShipControllableAdapter'` | PASS | `game/ai/controller.py:85` |
| `ShipControllableAdapter` is runtime-imported | PASS | `game/ai/controller.py:68`: `from game.ai.interfaces.controllable import ShipControllableAdapter` |
| `ShipControllableAdapter` is the actual runtime type | PASS — `AIController.__init__` receives `ShipControllableAdapter` wrappers; the class is defined at `game/ai/interfaces/controllable.py:221` |

**Verdict:** Dead import `IControllableShip` is fully removed. String annotation now references the correct type. No stale references remain.

**Git:** `ff66211b0` (PROJ-380 phase 1)

---

## Item C: Test Changes Verification (Phase 3.3 — `hex_at_screen` Migration)

### FND-057 — Test files rewritten, no deletions

**Severity:** INFO — Verified

**Affected files** (commit `2ecbad1a4`, phase 3.3):

| File | Change type | Tests deleted? | Tests added? |
|------|------------|----------------|--------------|
| `tests/unit/ui/screens/test_strategy_superweapons.py` | 11 `@patch('game.ui.screens.strategy_superweapons.pixel_to_hex')` decorators removed; `scene.camera.hex_at_screen = Mock(return_value=(5, 5))` added to `mock_scene` fixture | **No** | **No** |
| `tests/unit/ui/screens/test_strategy_fleet_ops.py` | 5 `with patch("game.ui.screens.strategy_fleet_ops.pixel_to_hex", ...)` blocks → `ops.scene.camera.hex_at_screen.return_value = target_hex` | **No** | **No** |
| `tests/unit/ui/screens/test_strategy_click_dispatcher.py` | `_IdentityCamera` gains `hex_at_screen` method + `hex_at_screen_return` attr; 5 `with patch("...pixel_to_hex", ...)` blocks → `scene.camera.hex_at_screen_return = hex_value` | **No** | **No** |
| `tests/unit/ui/screens/test_strategy_input_handler_transfer.py` | 3 `with patch('...pixel_to_hex') as mock_pixel_to_hex:` blocks → `mock_scene.camera.hex_at_screen = MagicMock(return_value=target_hex)` + dedented bodies | **No** | **No** |
| `tests/unit/ui/screens/test_strategy_input_handler_core.py` | 1 line added: `mock_scene.camera.hex_at_screen = MagicMock(return_value=HexCoord(0, 0))` inside `TestZoneSelection` setup | **No** | **No** |

**Verification details:**

- **test_strategy_superweapons.py**: 11 test methods lost `@patch(...)` decorators but gained camera mock in the shared `mock_scene` fixture. All test function signatures simplified (removed `mock_pixel_to_hex` parameter). All assertions preserved.
- **test_strategy_fleet_ops.py**: All 5 `with patch(...)` context managers replaced with direct mock assignment on `ops.scene.camera.hex_at_screen`. Same assertions, same expected values.
- **test_strategy_click_dispatcher.py**: `_IdentityCamera` updated to expose `hex_at_screen` and `hex_at_screen_return`. All patching contexts dedented/removed. Same assertions.
- **test_strategy_input_handler_transfer.py**: 3 test methods had `with patch(...)` blocks dedented by one level; mock assignment moved to `mock_scene.camera.hex_at_screen`. Same assertions.
- **test_strategy_input_handler_core.py**: Single additional mock assignment line in zone selection test setup. No assertions changed.

**Verdict:** All 5 test files underwent mock-rewrite only. Zero test cases were deleted. Zero test cases were added. All assertions remain identical. The migration is a pure replacement of `pixel_to_hex` patching with `camera.hex_at_screen` mocking.

---

## Summary

| ID | Item | Severity | Verdict |
|----|------|----------|---------|
| FND-050 | `_distribute_cargo_to_fleet` | INFO | Clean factorization |
| FND-051 | `_get_cell_detail` | INFO | Clean factorization |
| FND-052 | `_format_result_error` | MINOR | Clean; documented log casing change only |
| FND-053 | `_cancel_input_mode` | INFO | Clean factorization with well-scoped callback |
| FND-054 | `_check_fleet_ability` | MINOR | Clean; undocumented period drop in returned message |
| FND-055 | `_iter_hex_filtered_sources` | INFO | Clean factorization, well-scoped |
| FND-056 | Phase 1 dead import | INFO | `IControllableShip` fully removed, annotation corrected |
| FND-057 | Phase 3.3 test migration | INFO | Mock-rewrite only, zero test deletions |

**Overall assessment: All 6 helpers are clean, faithful factorizations with no shims, fallback systems, or duplicate logic violations. Phase 1 dead import removal is confirmed complete. Test migration rewrote mocks without deleting test cases.**

**No CRITICAL or MAJOR findings. Two MINOR findings (FND-052, FND-054) for cosmetic drift — neither introduces shim-like behavior.**
