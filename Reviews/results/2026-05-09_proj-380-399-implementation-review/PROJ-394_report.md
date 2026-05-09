# PROJ-394 Implementation Review

**Project:** PROJ-394 - PROJ-387 follow-up: Galaxy state public property + guard cleanup  
**Review date:** 2026-05-09  
**Reviewer:** Codex  
**Verdict:** **Not audit-clean.** The central production API goal is mostly met: `Galaxy.state` exists, the known production readers use `galaxy.state`, the guard allowlist is empty, and the PROJ-387 path table was corrected. However, the project's own Task 1.1 test selector does not pass in the current checkout. The same stale state-delegate test doubles identified around PROJ-387 still fail, so the checklist and full-suite claims cannot be accepted.

## Validation Result

- `git status --short`: pre-existing unrelated modified skill-usage counter plus the untracked review-results directory. I did not touch unrelated files.
- `python Projects/scripts/validate_audit_ready.py PROJ-394`: **PASSED**
  - Warning: `Projects/projects_index.md` still lists PROJ-394 as `Planning`.
- `python Projects/scripts/validate_phase.py PROJ-394 1`: **PASSED**

## Tests And Checks Run

- `pytest tests/unit/strategy/data/test_galaxy_state_encapsulation.py -q -p no:cacheprovider`: **2 passed**
- `pytest tests/unit/strategy/data/ -k galaxy -q -p no:cacheprovider`: **36 failed, 156 passed**
- `pytest tests/unit/strategy/engine/handlers/test_movement_handlers.py tests/unit/strategy/fleet_navigation/test_navigation_pure.py tests/unit/strategy/services/test_fleet_navigation_gaps.py tests/unit/strategy/services/test_fleet_navigation_action_timing.py tests/unit/ui/screens/strategy_render/test_hex_outlines.py tests/unit/ui/screens/test_strategy_renderer.py tests/integration/strategy/test_warp_orders.py tests/unit/strategy/data/test_galaxy_cleanup.py -q -p no:cacheprovider`: **143 passed**
- `rg -n "galaxy\._state\." game tests combat_lab Tools Projects/active_projects/PROJ-387 Projects/active_projects/PROJ-394`: no live production/test code hits outside tracking/docstring text.
- I did not run the full sharded suite after the required focused selector failed; the failure is already enough to block audit completion.

## Plan Goals Vs Actual Implementation

- **Expose public `Galaxy.state`: met.** `game/strategy/data/galaxy.py:69-72` defines a typed `state` property returning `self._state`.
- **Migrate production readers: mostly met, with stale manifest/checklist paths.** `game/strategy/engine/handlers/movement.py:242`, `game/strategy/services/fleet_warp_resolution.py:65`, and `game/ui/screens/strategy_render/hex_outlines.py:34,45,57` use `galaxy.state`. The plan/manifest still names `fleet_navigation_service.py`, but the live direct reader is in the extracted helper `fleet_warp_resolution.py`.
- **Migrate listed test sites: partially met.** The eight files listed in the checklist pass in the targeted 143-test run, but two state-delegate test files outside the manifest still use the deleted private field shape and fail.
- **Empty `GRANDFATHERED_EXTERNAL_READS`: met.** `tests/unit/strategy/data/test_galaxy_state_encapsulation.py:47-49` leaves the set empty, and the guard test passes.
- **Update specified docstrings: met for the files named in the plan.** `game/strategy/data/galaxy_state.py:12-17` and `:36-43` now describe `Galaxy.state`; the guard docstring also reflects PROJ-394.
- **Fix PROJ-387 path table: met.** `Projects/active_projects/PROJ-387/plan.md:39-42` lists the real three reader files.

## Literal Checklist Execution

- Task 1.1 marks `pytest tests/unit/strategy/data/ -k galaxy -q` as passing (`phase_1_checklist.md:15-22`), but that exact focused selector fails now with 36 failures.
- Task 1.2 and Task 1.3 overstate broad strategy-suite validation (`phase_1_checklist.md:26-47`). The narrower migrated-file set passes, but the broader state-delegate area does not.
- Task 1.7 claims a full sharded suite result with only the three known baseline failures (`phase_1_checklist.md:90-97`). Given the current 36 focused failures in tests that full-suite discovery should include, that claim needs revalidation after the stale tests are fixed.
- The manifest omits `tests/unit/strategy/data/test_galaxy_entity_registry.py`, `tests/unit/strategy/data/test_galaxy_spatial_index.py`, and `game/strategy/services/fleet_warp_resolution.py`, even though those are part of the same state access seam.

## Plan Gaps And Missed Assumptions

- The plan searched for `galaxy._state.` and listed the eight files from the PROJ-387 `_state` migration, but it did not account for tests still using the older deleted direct private field names such as `_global_hex_planets` and `_planet_to_system`.
- The design document remained a template (`Projects/active_projects/PROJ-394/design.md:7-23`), so the project did not record the actual dependency/risk analysis that should have caught executable delegate tests as consumers of the state shape.
- The plan focused on correcting two stale docstring locations, but it did not include the nearby stale `Galaxy` facade comment/header that still frames this block as preserving a "grandfathered private API".

## Findings

### Major: The planned Galaxy data selector still fails

`phase_1_checklist.md:15-22` requires `pytest tests/unit/strategy/data/ -k galaxy -q` to pass before Task 1.1 is complete. Re-running that selector produced **36 failures**. The failures are not random; they come from stale `_MockGalaxy` fixtures that still mirror the deleted pre-`GalaxyState` field names and are passed directly into delegates that now require `GalaxyState` fields.

Evidence:

- `tests/unit/strategy/data/test_galaxy_entity_registry.py:16-27` defines `_MockGalaxy` with `_next_planet_id`, `_planet_to_system`, `_global_hex_planets`, `_global_hex_zones`, and `_zone_to_system`.
- `tests/unit/strategy/data/test_galaxy_entity_registry.py:73-75` passes that mock into `GalaxyEntityRegistry`.
- `game/strategy/data/galaxy_entity_registry.py:30-36` documents the constructor dependency as a `GalaxyState`, and `:75-88` reads `planets_by_id`, `planet_to_system`, `global_hex_planets`, and `next_planet_id`.
- `tests/unit/strategy/data/test_galaxy_spatial_index.py:16-27` defines the same stale field shape, and `:78-80` passes it into `GalaxySpatialIndex`.
- `game/strategy/data/galaxy_spatial_index.py:26-28` stores a `GalaxyState`, and `:49-66` reads `planet_to_system`, `global_hex_planets`, and `global_hex_zones`.

Representative failures include `AttributeError: '_MockGalaxy' object has no attribute 'next_planet_id'`, `planet_to_system`, and `global_hex_planets`.

### Minor: Project manifest and checklist name a stale production reader path

`Projects/active_projects/PROJ-394/manifest.md:12-14` and `phase_1_checklist.md:34-38` say the fleet-navigation reader lives in `game/strategy/services/fleet_navigation_service.py`. The current direct `galaxy.state.global_hex_warp_points` read is in `game/strategy/services/fleet_warp_resolution.py:65`, reached through `FleetNavigationService._resolve_warp_exit`.

Impact: the code path is migrated correctly, but the audit trail is not accurate and future agents would inspect the wrong implementation file.

### Minor: The `Galaxy` facade still has stale wording around the migrated state seam

The plan fixed docstrings in `galaxy_state.py` and the guard test, but `game/strategy/data/galaxy.py:67` still labels the forwarder block as preserving "public + grandfathered private API". That is misleading after PROJ-387/394, where the five spatial private forwarders were intentionally removed and cross-module readers should use `Galaxy.state`.

Impact: low behavioral risk, but this is exactly the kind of stale architecture wording PROJ-394 was meant to clean up.

## Residual Risks

- The full sharded-suite claim should be re-run after the failing state-delegate tests are migrated; I did not rely on the recorded result because a required focused selector currently fails.
- `Projects/projects_index.md` still marks PROJ-394 as `Planning`, which is project-system drift before archival.
- The guard test scans `game/` for restricted production attributes, not `tests/`; stale test fixtures can still survive unless the broader test selectors are actually run.

## Recommended Follow-Up

- Replace the stale `_MockGalaxy` fixtures in `test_galaxy_entity_registry.py` and `test_galaxy_spatial_index.py` with real `GalaxyState` instances or a shared stub using the `GalaxyState` field names.
- Add those two test files and `game/strategy/services/fleet_warp_resolution.py` to the manifest/checklist evidence.
- Re-run `pytest tests/unit/strategy/data/ -k galaxy -q`, then the full sharded suite.
