# Phase 2: New cold read surfaces + narrow scene write handle

> **BEFORE MARKING COMPLETE:** `python Projects/scripts/validate_phase.py PROJ-477 2`; update plan.md.

**Status:** Not Started
**Objective:** Add the facade query surfaces and the scene write handle that Phases 3-4 migrate
onto, so migrations have a target. Read-only/projection queries + a composition-root write seam;
no consumer rewired yet.

---

## Tasks

### Task 2.1: `facade.systems.by_name` [Simple]
**File:** `game/strategy/facade/slices/system_slice.py`, `grouped_namespaces.py`
**Tests:** `pytest tests/unit/strategy/facade/ -k by_name`

- [ ] Failing test: `facade.systems.by_name("Sol")` returns a `SystemInfo` for a known system, `None` for unknown.
- [ ] Add `SystemSlice.get_system_by_name(name)` delegating to `self._state.session.galaxy.get_system_by_name(name)` → `SystemInfo.from_star_system` (or `None`).
- [ ] Expose `FacadeSystemQueries.by_name(name)` in `grouped_namespaces.py` (after `near_hex`, `:216-220`).
- [ ] Verify: test GREEN.

**Notes:**

---

### Task 2.2: `facade.systems.of_object` [Medium]
**File:** `system_slice.py`, `grouped_namespaces.py`
**Tests:** `pytest tests/unit/strategy/facade/ -k of_object`

- [ ] Failing test: `facade.systems.of_object(planet)` returns the containing `SystemInfo`; `None` when unresolved.
- [ ] Add `SystemSlice.get_system_of_object(obj)` delegating to `galaxy.get_system_of_object(obj)` (`galaxy.py:134`) → `SystemInfo`.
- [ ] Expose `FacadeSystemQueries.of_object(obj)`.
- [ ] Verify: test GREEN. (Used by `strategy_event_router` / `strategy_camera_nav`.)

**Notes:**

---

### Task 2.3: `facade.systems.at_map_hex(hex, radius=50)` — pathfinder semantics [Medium]
**File:** `system_slice.py`, `grouped_namespaces.py`
**Tests:** `pytest tests/unit/strategy/facade/ -k at_map_hex`

- [ ] Failing test pinning that `at_map_hex` uses **system-radius (default 50)** ownership semantics, distinct from `near_hex(max_dist=8)`. Include a case where the two differ.
- [ ] Add `SystemSlice.get_system_at_map_hex(hex, radius=50)` delegating to `GalaxyPathfindingService(...).get_system_at_hex(hex, radius)` (`galaxy_pathfinding_service.py:113-128`) → `SystemInfo`.
- [ ] Expose `FacadeSystemQueries.at_map_hex(hex, radius=50)`.
- [ ] Verify: test GREEN; semantic-difference assertion holds.

**Notes:** Do NOT reuse `near_hex` — different ownership semantics (design.md risk 2).

---

### Task 2.4: `facade.spatial.contents_at_hex` (new namespace, multi-hex aware) [Complex]
**File:** `game/strategy/facade/slices/spatial_slice.py` (NEW), `grouped_namespaces.py`, facade composer
**Tests:** `pytest tests/unit/strategy/facade/ -k contents_at_hex`

- [ ] Failing test: `facade.spatial.contents_at_hex(hex)` returns grouped planet/zone/warp-point membership, INCLUDING a multi-hex zone (Dyson Sphere) whose center is NOT the queried hex — proving it does not collapse to `planets.at_hex` exact-center semantics (`planet_slice.py:83-89`).
- [ ] Add `SpatialSlice` (takes `FacadeSessionState`) with `contents_at_hex(hex)` delegating to `galaxy.get_planets_at_global_hex` + `galaxy.get_zones_at_global_hex` (`galaxy.py:150,166`). Decide return DTO shape (grouped dataclass) — projection acceptable here (cold callers).
- [ ] Add `FacadeSpatialQueries` to `grouped_namespaces.py`; wire `facade.spatial` in the composer (mirror how `facade.systems` is wired).
- [ ] Verify: test GREEN; multi-hex membership preserved.

**Notes:** Confirm with composer how slices/namespaces are registered (search for `FacadeSystemQueries(` instantiation).

---

### Task 2.5: Narrow scene write handle [Medium]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/ -k order_writes`

- [ ] Failing test: `screen.order_writes.set_active_empire(emp)`, `.set_fleet_path(fleet, [])`, `.pop_fleet_order(fleet, index)` perform the same mutation the current `screen.session.<x>` writes do.
- [ ] Add an `order_writes` (name TBD; keep terse) handle on `StrategyScreen` exposing exactly those three methods, internally backed by `self._session.active_empire = ...` and `self._session.fleet_mutator.set_path/pop_order`. Composition-root only — no general-purpose session escape.
- [ ] Verify: test GREEN. Session guard does NOT regress (the handle reads `_session` inside `strategy_screen.py`, already Category A allowlisted).

**Notes:** This is the seam Phase 3 routes the Category B writes through.

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] All new facade queries + write handle covered by passing unit tests
- [ ] Sharded suite green; guards unaffected (no new property/session reads introduced)
- [ ] Update status `Complete`; update plan.md table + Current State → Phase 3
