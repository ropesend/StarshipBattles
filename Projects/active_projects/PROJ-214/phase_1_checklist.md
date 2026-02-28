# Phase 1: Implementation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-214 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add inner hex outlines for occupied hexes with ownership-based coloring

---

## Tasks

### Task 1.1: Add Color Constants [Simple]
**File:** `game/ui/colors.py`
**Tests:** N/A (constants only)

- [x] Add `HEX_OUTLINE_OCCUPIED = (200, 60, 60)` after line 413
- [x] Add `HEX_OUTLINE_PLAYER_OWNED = (220, 220, 220)` after line 413

**Notes:** Added in the "Strategy Map (additional)" section alongside ZONE_HIGHLIGHT.

### Task 1.2: Add Imports and Cache Fields [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py`

- [x] Add `HEX_OUTLINE_OCCUPIED, HEX_OUTLINE_PLAYER_OWNED` to color import block
- [x] Add `self._hex_outline_cache = None` to `__init__`
- [x] Add `self._hex_outline_cache_turn = -1` to `__init__`

### Task 1.3: Implement Data Collection Methods [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -k "TestHexOutlineDataCollection or TestHexOutlineCaching"`

- [x] Implement `_build_hex_outline_data()` - builds Dict[HexCoord, (has_player, has_non_player)]
- [x] Iterate `galaxy._global_hex_planets` checking `owner_id` vs player ID
- [x] Iterate `galaxy._global_hex_zones` (stars/storms always non-player, Dyson Spheres check `owner_id`)
- [x] Iterate `galaxy._global_hex_warp_points` (always non-player)
- [x] Iterate all empires' fleets checking `fleet.owner_id`
- [x] Handle `fleet.location is None` edge case
- [x] Implement `_get_hex_outline_data()` caching wrapper with turn-based invalidation

### Task 1.4: Implement Rendering Methods [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -k "TestHexOutlineRendering or TestDrawInnerHex"`

- [x] Implement `_draw_hex_outlines(screen)` with viewport culling (50px margin)
- [x] Both flags → dual outline: white at 0.90, red at 0.80
- [x] Player only → white at 0.88
- [x] Non-player only → red at 0.88
- [x] Implement `_draw_inner_hex(screen, cx, cy, scale, color)` using 6-corner hex polygon

### Task 1.5: Integrate into draw() [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -k "TestHexOutlineRendering"`

- [x] Insert `_draw_hex_outlines` call between grid and warp lanes, gated on `zoom >= 0.5`
- [x] Verify render order: grid → hex outlines → warp lanes → systems → fleets → move preview → hover hex

### Task 1.6: Write Tests [Medium]
**File:** `tests/unit/ui/screens/test_strategy_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_renderer.py -v`

- [x] TestHexOutlineDataCollection: 11 tests (empty, unowned, player, enemy, mixed, zones, warp, fleets, None location, combined)
- [x] TestHexOutlineCaching: 2 tests (cache hit, cache invalidation)
- [x] TestHexOutlineRendering: 2 tests (zoom gating below/at threshold)
- [x] TestDrawInnerHex: 2 tests (6-corner polygon, correct color)
- [x] Verify: all 64 tests pass (48 existing + 16 new)

### Task 1.7: Full Test Suite Regression Check [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full suite: 13,021 passed, 1 skipped, 0 regressions
- [x] 1 pre-existing flaky failure (test_different_warp_points_get_different_offsets - hash collision, unrelated)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
