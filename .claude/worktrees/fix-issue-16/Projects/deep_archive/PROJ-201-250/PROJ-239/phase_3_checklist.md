# Phase 3: Code Quality & Dead Code Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-239 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Deduplicate code patterns and remove dead code
**Priority:** High

---

## Tasks

### Task 3.1: CQ-003 — Deduplicate stabilizer check methods [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py:707-815`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

Three near-identical methods (`_is_planet_stabilized`, `_is_system_stellar_stabilized`, `_is_system_warp_stabilized`) differ only in ability name and scope list. ~100 lines of copy-paste.

- [x] Write test covering all three stabilizer check paths
- [x] Extract a single parameterized `_is_stabilized(ability_name, scope_list, ...)` method
- [x] Replace the three methods with calls to the unified method
- [x] Verify: superweapon tests pass

**Notes:** Added `_is_stabilized(ability_name, scopes, reference_entity, galaxy, empires)` — single loop. The three original methods are now thin wrappers (~5 lines each) that delegate to it. Reduced ~90 lines to ~60. 5 new tests in `test_superweapon_stabilizers.py`.

### Task 3.2: CQ-004 — Replace mock object hack in FleetNavigationService [Medium]
**File:** `game/strategy/services/fleet_navigation_service.py:185-200`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_service.py`

`compute_path()` creates an inline `MockCapabilities` class and a dynamic `fleet_like` object using `type()` to satisfy `find_hybrid_path`'s API. This is a workaround — the function should accept simpler parameters.

- [x] Write test for `compute_path` with both warp-capable and non-warp fleets
- [x] Refactor `find_hybrid_path` to accept `can_warp: bool` (or a simpler capabilities protocol) instead of requiring a full fleet-like object
- [x] Remove the MockCapabilities hack
- [x] Verify: all pathfinding tests pass

**Notes:** Added `can_warp` parameter to `find_hybrid_path()` in pathfinding.py. When provided, overrides fleet capability check. Removed MockCapabilities class + dynamic type() object from `compute_path()`. 3 new tests. 10 navigation integration tests still pass.

### Task 3.3: DC-003 — Remove dead methods from planet_energy_engine [Simple]
**File:** `game/strategy/engine/planet_energy_engine.py:34-81`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_energy_engine.py`

`get_strategic_generation_info()` and `get_resource_storage_info()` have zero callers anywhere in the codebase.

- [x] Confirm zero callers with grep across game/ and tests/
- [x] Delete both functions
- [x] Verify: tests pass

### Task 3.4: DC-004 — Remove dead methods from AstrophysicsLoader [Simple]
**File:** `game/strategy/generation/loaders/astrophysics_loader.py:58-110`
**Tests:** `pytest tests/unit/strategy/generation/`

`get_mass_distribution()`, `get_orbit_zone()`, and `get_habitable_zone_factors()` have no callers.

- [x] Confirm zero callers with grep
- [x] Delete the three methods (~53 lines)
- [x] Verify: tests pass

### Task 3.5: DC-005 — Remove dead methods from Empire, GameSession, DesignLibrary [Simple]
**Files:** `game/strategy/data/empire.py:57-60`, `game/strategy/engine/game_session.py`, `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/`

Three methods with zero callers: `Empire.remove_colony()`, `GameSession.get_current_player_empire()`, `DesignLibrary.delete_design()`.

- [x] Confirm zero callers for each with grep
- [x] Delete all three methods (~41 lines total)
- [x] Verify: tests pass

**Notes (3.3-3.5):** All dead methods confirmed zero callers via codebase-wide grep. Deleted: 2 functions from planet_energy_engine.py (~48 lines), 3 methods from astrophysics_loader.py (~53 lines), 3 methods from empire.py/game_session.py/design_library.py (~41 lines). Also fixed mock_find_path_selective in test_fleet_navigation_action_timing.py to accept new can_warp parameter. Total: ~142 lines removed.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
