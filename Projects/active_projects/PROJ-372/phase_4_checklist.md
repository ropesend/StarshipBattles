# Phase 4: Galaxy algorithmic services (pathfinding, intercept, warp resolution)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-372 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Depends on:** Phase 3 (verified)
**Review Mode:** cumulative (Phases 0-4)
**Files (planned):** see manifest.md Phase 4 row group

**Status:** Not Started
**Objective:** Move pathfinding (`pathfinding.py`, 503 LOC) into `GalaxyPathfindingService` (≤ 350 LOC) and `InterceptCalculator` (≤ 150 LOC), accepting `IGalaxySystemGraph` from `galaxy_protocols.py` so unit tests can inject 3-system stubs. Convert each free function in `pathfinding.py` to a 1-line deprecated wrapper calling the service. Wire the pathfinding service through `ApplicationContext`. Final reduction of `galaxy.py` to ≤ 350 LOC.

---

## Reading

- [ ] Phase 3 outcomes — `galaxy.py` ≤ 420; `GalaxyState` in place; sharded green
- [ ] `game/strategy/data/pathfinding.py` lines 1-503 — full file
- [ ] All 82 callers of `find_path_*` / `find_hybrid_path` / `project_fleet_path` / `calculate_intercept_point` / `find_nearest_system` / `get_system_at_hex` (per design.md grep)
- [ ] `game/strategy/services/fleet_navigation_service.py` (called by `pathfinding.project_fleet_path`)

---

## Pre-flight

- [ ] Run `pytest tests/unit/strategy/data/test_pathfinding.py -v` (or equivalent) — capture baseline
- [ ] `grep -rn 'from game.strategy.data.pathfinding import' game/ tests/` — pin every caller for Task 4.4

---

## Tasks

### Task 4.1: Acceptance test for pathfinding stub graph (TDD-first) [Medium]
**File:** `tests/unit/strategy/services/test_galaxy_pathfinding_service.py` (new)

- [ ] Build a stub implementing `IGalaxySystemGraph` with exactly 3 systems and 2 warp lanes (A↔B, B↔C). NO `Galaxy()` construction.
- [ ] Test `find_path_interstellar(stub, A, C)` returns `[A, B, C]`.
- [ ] Test `find_hybrid_path(stub, A_global_hex, C_global_hex)` returns a path containing both warp jumps.
- [ ] Confirm tests **FAIL** (service doesn't exist yet).
- [ ] **Verify:** failure with `ModuleNotFoundError`.

**Notes:**

### Task 4.2: Implement `GalaxyPathfindingService` [Complex]
**File:** `game/strategy/services/galaxy_pathfinding_service.py` (new)
**Tests:** Task 4.1 + per-method unit tests

- [ ] Class taking `graph: IGalaxySystemGraph` and (optionally) `state: GalaxyState` in constructor.
- [ ] Methods (moved from `pathfinding.py`):
  - `find_path_deep_space(start, end) -> List[HexCoord]` (`pathfinding.py:51-62`)
  - `find_path_interstellar(start_system, end_system) -> Optional[List[StarSystem]]` (`:64-143`)
  - `find_hybrid_path(start_hex, end_hex, fleet=None, can_warp=None) -> List[HexCoord]` (`:200-295`)
  - `find_nearest_system(hex_c) -> Optional[StarSystem]` (`:179-198`)
  - `get_system_at_hex(hex_c, radius=50) -> Optional[StarSystem]` (`:145-177`)
  - `strip_start_hex(current_location, path)` (`:21-48`)
- [ ] Replace `galaxy.systems[...]` / `galaxy.get_system_by_name(...)` calls with `self._graph.systems[...]` / `self._graph.get_system_by_name(...)`.
- [ ] Module ≤ 350 LOC.
- [ ] **Verify:** Task 4.1 acceptance test passes; per-method unit tests pass.

**Notes:**

### Task 4.3: Implement `InterceptCalculator` [Medium]
**File:** `game/strategy/services/intercept_calculator.py` (new)
**Tests:** `pytest tests/unit/strategy/services/test_intercept_calculator.py -v` (new)

- [ ] Class taking `pathfinding: GalaxyPathfindingService` and (optionally) `graph: IGalaxySystemGraph`.
- [ ] Methods (moved from `pathfinding.py:297-503`):
  - `project_fleet_path(fleet, max_turns=10) -> List[dict]` — keep delegate to `FleetNavigationService` (no functional change)
  - `calculate_intercept_point(chaser, target_fleet) -> Optional[HexCoord]`
- [ ] Helpers `_evaluate_intercept_candidates`, `_extract_chaser_info`, `_ChaserProxy`, `_ChaserProxyCapabilities` move with the calculator (private).
- [ ] Module ≤ 150 LOC.
- [ ] Unit tests with stub fleets + stub pathfinding.

**Notes:**

### Task 4.4: Convert `pathfinding.py` to deprecated 1-line wrappers [Medium]
**File:** `game/strategy/data/pathfinding.py` (modify)
**Tests:** existing `test_pathfinding.py` + new `DeprecationWarning` assertions

- [ ] Each free function becomes a 1-line wrapper: `def find_path_interstellar(start_system, end_system, galaxy): warnings.warn("PROJ-372: use GalaxyPathfindingService.find_path_interstellar; pathfinding free functions deleted at PROJ-372 Phase 5", DeprecationWarning, stacklevel=2); return galaxy._pathfinder.find_path_interstellar(start_system, end_system)`.
- [ ] Apply to all 8 functions (`find_path_deep_space`, `find_path_interstellar`, `find_hybrid_path`, `find_nearest_system`, `get_system_at_hex`, `strip_start_hex`, `project_fleet_path`, `calculate_intercept_point`).
- [ ] Module ≤ 60 LOC.
- [ ] Add tests asserting `DeprecationWarning` fires.
- [ ] **Verify:** all 82 caller sites still compile and work; warnings are visible but not test-fatal.

**Notes:**

### Task 4.5: Wire pathfinding into ApplicationContext + Galaxy [Simple]
**File:** `game/context.py`, `game/strategy/data/galaxy.py` (modify)

- [ ] Add `get_default_galaxy_pathfinding_service()` accessor (mirrors PROJ-258 pattern). Returns `None` until a Galaxy is constructed; the Galaxy facade sets the default on `__init__`. Alternative: leave it bound to a per-Galaxy instance (decided at impl time).
- [ ] In `Galaxy.__init__`, instantiate `self._pathfinder = GalaxyPathfindingService(self)` (Galaxy satisfies `IGalaxySystemGraph`).
- [ ] **Verify:** existing tests using `find_path_interstellar(start, end, galaxy)` still pass via the deprecated shim.

**Notes:**

### Task 4.6: Final Galaxy facade cleanup [Medium]
**File:** `game/strategy/data/galaxy.py` (modify)
**Tests:** sharded suite

- [ ] Audit every method on `Galaxy`. Each must be ≤ 5 LOC OR be `__init__` / `to_dict` / `from_dict` (allow-listed in Phase 5's AST guard).
- [ ] Final target: `galaxy.py` ≤ 350 LOC.
- [ ] Possible move: if `StarSystem` (~95 LOC) and `WarpPoint` (~47 LOC) at the top of `galaxy.py` push the budget over, move them to their own files (`star_system.py`, `warp_point.py`) per Open Question Q2 in design.md.
- [ ] **Verify:** `galaxy.py` ≤ 350 LOC; AST guard tightened.

**Notes:**

### Task 4.7: Tighten AST guards [Simple]

- [ ] `GALAXY_LOC_CEILING` from 420 → 350.
- [ ] **Verify:** test passes.

**Notes:**

### Task 4.8: Save round-trip regression test [Simple]

- [ ] As Phase 3 Task 3.8, but on the post-Phase-4 facade. Confirm save format unchanged.

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/strategy/services/test_galaxy_pathfinding_service.py tests/unit/strategy/services/test_intercept_calculator.py -v` green
- [ ] All 82 caller sites still pass (sharded suite green)
- [ ] `galaxy.py` ≤ 350 LOC; `pathfinding.py` ≤ 60 LOC
- [ ] Pathfinding callable on a 3-system stub graph (acceptance test green)
- [ ] Update status / plan.md / Current State pointing to Phase 5
