# Phase 3: Performance Optimizations

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-52 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Ensure 2500 systems render at 60 FPS

---

## Task 3.1: Add System Name Cache [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `python -m pytest tests/unit/strategy/data/test_galaxy.py`

- [ ] Verify `name_map` (line 91) is used consistently
- [ ] Add `get_system_by_name(name) -> Optional[StarSystem]` method using `name_map`
- [ ] Update all O(n) name lookups to use this method

**Notes:**

---

## Task 3.2: Optimize Warp Lane Rendering [Medium]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** Manual FPS testing at 2500 systems

- [ ] Replace line 220 O(n) lookup with `galaxy.get_system_by_name()` O(1)
- [ ] Cache reciprocal warp points to avoid repeated lookups (line 223)
- [ ] Add viewport culling for warp lanes (skip if both endpoints off-screen)
- [ ] Consider pre-computing warp lane draw list on galaxy change

**Notes:**

---

## Task 3.3: Cache Fonts and Assets [Simple]
**File:** `game/ui/screens/strategy_renderer.py`
**Tests:** Manual FPS testing

- [ ] Move `pygame.font.SysFont()` calls to `__init__` with size-keyed cache
- [ ] Cache `get_asset_manager()` reference in `__init__`
- [ ] Replace per-frame lookups with cached references

**Notes:**

---

## Task 3.4: Optimize Warp Lane Generation [Medium]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `python -m pytest tests/integration/strategy/test_galaxy_gen.py`

- [ ] Replace all-pairs edge generation (lines 327-331) with k-nearest-neighbors
- [ ] Use spatial index (quadtree or grid) for neighbor lookup
- [ ] Target: 2500 systems generates in < 5 seconds
- [ ] Maintain MST connectivity guarantee

**Notes:**

---

## Task 3.5: Add Spatial Index for Distance Checks [Medium]
**File:** `game/strategy/data/galaxy.py` or new `spatial_index.py`
**Tests:** `python -m pytest tests/unit/strategy/data/test_spatial_index.py`

- [ ] Implement simple grid-based spatial index
- [ ] Use in `generate_systems()` for min_dist checks (lines 216-223)
- [ ] Use in warp lane generation for neighbor lookup
- [ ] Target: O(1) average case for nearby system queries

**Notes:**

---

## Phase 3 Verification
- [ ] All unit tests pass: `python -m pytest tests/unit/strategy/`
- [ ] 2500 systems generate in < 10 seconds
- [ ] 2500 systems render at > 30 FPS when zoomed out
- [ ] No visible rendering artifacts
- [ ] Full test suite still passes: `python -m pytest tests/`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

## Handoff Notes
(To be filled when phase completes)
