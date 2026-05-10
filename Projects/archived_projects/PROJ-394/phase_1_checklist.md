# Phase 1: Doc + guard cleanup, expose public `Galaxy.state`, migrate `_state.X` callers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-394 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Close PROJ-387 review findings MAJ-001, MAJ-002, MIN-003, MIN-004, MIN-005. Replace the `galaxy._state.<field>` access pattern with a true public `galaxy.state.<field>` API; clean up the AST guard and stale docstrings.

---

## Tasks

### Task 1.1: Add public `Galaxy.state` property [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/ -k galaxy -q`

- [x] Add a `@property` named `state` on `Galaxy` returning `self._state` (typed `GalaxyState`).
- [x] Add a 1-line docstring: "Public access to the underlying `GalaxyState`. Use this instead of `_state` for cross-module reads."
- [x] Do NOT rename `_state`. Do NOT add a setter (state is mutable in-place; callers should not reassign it).
- [x] Verify: `pytest tests/unit/strategy/data/ -k galaxy -q` passes.

**Notes:** Property added immediately above the existing `radius` forwarder block (galaxy.py line ~69). Return type annotation `-> GalaxyState`; one-line docstring per spec.

### Task 1.2: Migrate production readers from `_state.X` → `state.X` [Simple]
**File:** `game/strategy/engine/handlers/movement.py`, `game/strategy/services/fleet_navigation_service.py`, `game/ui/screens/strategy_render/hex_outlines.py`
**Tests:** `pytest tests/unit/strategy/ tests/unit/ui/screens/strategy_render/ -q`

- [x] `grep -rn "galaxy\._state\." game/` to enumerate every production reader site.
- [x] Replace each `galaxy._state.<field>` (or `r.galaxy._state.<field>`, `session.galaxy._state.<field>`) with `galaxy.state.<field>` (preserving the variable prefix).
- [x] Verify: `pytest tests/unit/strategy/ tests/unit/ui/screens/strategy_render/ -q` passes.

**Notes:** 5 production sites migrated:
- `game/strategy/engine/handlers/movement.py:242` (warp validation)
- `game/strategy/services/fleet_navigation_service.py:315` (`_resolve_warp_exit`)
- `game/ui/screens/strategy_render/hex_outlines.py:34, 45, 57` (3 reads)
- Plus internal `Galaxy.from_dict` (galaxy.py:283-284) — internal-but-through-facade access, migrated for consistency with the "no `galaxy._state.` anywhere" goal.

### Task 1.3: Migrate test sites from `_state.X` → `state.X` [Medium]
**File:** `tests/unit/strategy/...`, `tests/unit/ui/screens/test_strategy_renderer.py`, `tests/integration/strategy/test_warp_orders.py`, `tests/unit/ui/screens/strategy_render/test_hex_outlines.py`
**Tests:** `pytest tests/unit/strategy/ tests/unit/ui/screens/strategy_render/ tests/integration/strategy/ -q`

- [x] `grep -rn "galaxy\._state\." tests/` to enumerate every test reader/writer site.
- [x] Replace each `galaxy._state.<field>` with `galaxy.state.<field>` (read AND write sites — both work since `state` returns the same `GalaxyState` instance).
- [x] In `tests/unit/strategy/engine/handlers/test_movement_handlers.py`, the `_FakeGalaxy` exposes `_state` directly. Add a public `state` property to the fake (one-liner returning `self._state`) so production code calling `galaxy.state.global_hex_warp_points` works against the fake. Do NOT remove `_state` from the fake — only add `state`.
- [x] Verify: targeted suites pass.

**Notes:** Migrated 8 test files:
- `tests/integration/strategy/test_warp_orders.py`
- `tests/unit/strategy/fleet_navigation/test_navigation_pure.py`
- `tests/unit/strategy/engine/handlers/test_movement_handlers.py`
- `tests/unit/strategy/data/test_galaxy_cleanup.py`
- `tests/unit/strategy/services/test_fleet_navigation_gaps.py`
- `tests/unit/strategy/services/test_fleet_navigation_action_timing.py`
- `tests/unit/ui/screens/test_strategy_renderer.py`
- `tests/unit/ui/screens/strategy_render/test_hex_outlines.py`

`_FakeGalaxy` in `test_movement_handlers.py` got an added `@property state` returning `self._state` (typed `_FakeGalaxyState`); `_state` left in place untouched.

`test_hex_outlines.py` used `SimpleNamespace(_state=...)` for the galaxy fake (NOT MagicMock, so attributes don't auto-create). Renamed the kwarg to `state=...` so production code's `r.galaxy.state.global_hex_planets` resolves. The fake had no other consumers of `_state`, so no compat shim needed.

### Task 1.4: MAJ-001 — Empty `GRANDFATHERED_EXTERNAL_READS` and update docstring [Simple]
**File:** `tests/unit/strategy/data/test_galaxy_state_encapsulation.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_state_encapsulation.py -q`

- [x] Replace `GRANDFATHERED_EXTERNAL_READS` (currently 5 entries at lines ~45-52) with `frozenset()` and update the comment block above it to note "PROJ-394 emptied this after PROJ-387 deleted the forwarders. Kept as the API for surfacing future grandfathered reads if any are ever needed."
- [x] Update the module docstring (lines 1-17) to reflect the post-PROJ-387 state: the 5 underscore-prefixed indexes were DELETED in PROJ-387, the guard now defends against any reintroduction of those names. The docstring should read like a guard-rail description, not a "phase 3 transitional" description.
- [x] Verify: the guard test still passes (with empty grandfathered set, no live code should violate).

**Notes:** Both module docstring and `GRANDFATHERED_EXTERNAL_READS` rewritten; guard test passes (4 passed in 1.34s on the encapsulation file).

### Task 1.5: MIN-004 — Update `galaxy_state.py` docstring [Simple]
**File:** `game/strategy/data/galaxy_state.py`
**Tests:** —

- [x] Update the module docstring (lines 12-16) to remove the "Galaxy re-exposes the under-prefixed names as @property forwarders for backwards-compat with the five grandfathered external read sites" claim. Replace with text describing the current architecture: PROJ-387 deleted the underscore forwarders; readers go through `Galaxy.state` (a public `@property` returning `GalaxyState`) added in PROJ-394.
- [x] Update the `GalaxyState` class docstring (line 35-40) similarly — the "Galaxy facade exposes the same surface via @property forwarders" sentence is now inaccurate.

**Notes:** Both docstrings rewritten to describe the post-PROJ-387 / PROJ-394 architecture; `Galaxy.state` named explicitly.

### Task 1.6: MIN-005 — Fix PROJ-387 plan.md path [Trivial]
**File:** `Projects/active_projects/PROJ-387/plan.md`
**Tests:** —

- [x] On line 40, replace `game/strategy/data/movement.py` (does not exist) with `game/strategy/engine/handlers/movement.py` (the actual reader). Also clean up the "(continued)" rows so the table accurately lists the 3 readers: `engine/handlers/movement.py`, `services/fleet_navigation_service.py`, `ui/screens/strategy_render/hex_outlines.py`.

**Notes:** Replaced the placeholder rows with three explicit per-reader rows pointing at the real paths.

### Task 1.7: Final verification [Required]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full sharded suite. Result must show 0 NEW failures vs the existing 3-failure baseline (`test_scalene_workflow_files_are_documented`, `test_skill_does_not_claim_coverage_json_is_supported`, `test_pathfinder_attached_after_init`).
- [x] `grep -rn "galaxy\._state\." .` returns zero hits in production OR test code (only this project's tracking files / archived docs may match).
- [x] `python Projects/scripts/validate_phase.py PROJ-394 1` shows PASSED.

**Notes:** Sharded run: `19091 tests | 19084 passed | 3 failed | 0 errors | 4 skipped` in 75.3s. The 3 failures are exactly the documented baseline — no new failures introduced. Production-code grep across `*.py` shows zero hits for `galaxy._state.` (only docstring text matches in the encapsulation guard test, plus assignment writes in `tests/fixtures/galaxy_fixtures.py` which are setting the attribute, not reading through it).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-08_231159_code_proj-387-galaxy-backward-compat-property-forwarder_req-req_20260508_231157_6165cf/report.md`_
