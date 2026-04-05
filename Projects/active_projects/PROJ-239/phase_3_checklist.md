# Phase 3: Code Quality & Dead Code Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-239 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Deduplicate code patterns and remove dead code
**Priority:** High

---

## Tasks

### Task 3.1: CQ-003 — Deduplicate stabilizer check methods [Simple]
**File:** `game/strategy/engine/superweapon_order_processor.py:707-815`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_order_processor.py`

Three near-identical methods (`_is_planet_stabilized`, `_is_system_stellar_stabilized`, `_is_system_warp_stabilized`) differ only in ability name and scope list. ~100 lines of copy-paste.

- [ ] Write test covering all three stabilizer check paths
- [ ] Extract a single parameterized `_is_stabilized(ability_name, scope_list, ...)` method
- [ ] Replace the three methods with calls to the unified method
- [ ] Verify: superweapon tests pass

### Task 3.2: CQ-004 — Replace mock object hack in FleetNavigationService [Medium]
**File:** `game/strategy/services/fleet_navigation_service.py:185-200`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_service.py`

`compute_path()` creates an inline `MockCapabilities` class and a dynamic `fleet_like` object using `type()` to satisfy `find_hybrid_path`'s API. This is a workaround — the function should accept simpler parameters.

- [ ] Write test for `compute_path` with both warp-capable and non-warp fleets
- [ ] Refactor `find_hybrid_path` to accept `can_warp: bool` (or a simpler capabilities protocol) instead of requiring a full fleet-like object
- [ ] Remove the MockCapabilities hack
- [ ] Verify: all pathfinding tests pass

### Task 3.3: DC-003 — Remove dead methods from planet_energy_engine [Simple]
**File:** `game/strategy/engine/planet_energy_engine.py:34-81`
**Tests:** `pytest tests/unit/strategy/engine/test_planet_energy_engine.py`

`get_strategic_generation_info()` and `get_resource_storage_info()` have zero callers anywhere in the codebase.

- [ ] Confirm zero callers with grep across game/ and tests/
- [ ] Delete both functions
- [ ] Verify: tests pass

### Task 3.4: DC-004 — Remove dead methods from AstrophysicsLoader [Simple]
**File:** `game/strategy/generation/loaders/astrophysics_loader.py:58-110`
**Tests:** `pytest tests/unit/strategy/generation/`

`get_mass_distribution()`, `get_orbit_zone()`, and `get_habitable_zone_factors()` have no callers.

- [ ] Confirm zero callers with grep
- [ ] Delete the three methods (~53 lines)
- [ ] Verify: tests pass

### Task 3.5: DC-005 — Remove dead methods from Empire, GameSession, DesignLibrary [Simple]
**Files:** `game/strategy/data/empire.py:57-60`, `game/strategy/engine/game_session.py`, `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/`

Three methods with zero callers: `Empire.remove_colony()`, `GameSession.get_current_player_empire()`, `DesignLibrary.delete_design()`.

- [ ] Confirm zero callers for each with grep
- [ ] Delete all three methods (~41 lines total)
- [ ] Verify: tests pass


---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
