# PROJ-387 Implementation Review

**Project:** PROJ-387 - Legacy removal: Galaxy backward-compat property forwarders  
**Review date:** 2026-05-09  
**Reviewer:** Codex  
**Verdict:** **Not audit-clean.** The production goal is substantially met: the five `Galaxy` private-index forwarders are gone, and the current production readers no longer use `galaxy._global_hex_*`, `galaxy._planet_to_system`, or `galaxy._zone_to_system`. However, focused unit tests for the same state/delegate seam still fail because their test doubles were not migrated to the `GalaxyState` field shape, and the project checklist/Current State overclaims test cleanup.

## Validation Result

- `python Projects/scripts/validate_audit_ready.py PROJ-387`: **PASSED**
  - Warning: `Projects/projects_index.md` still lists PROJ-387 as `Planning`.
- `python Projects/scripts/validate_phase.py PROJ-387 1`: **PASSED**
  - Warnings: Tasks 1.1 through 1.4 are complete but have empty Notes.

## Tests And Checks Run

- `pytest -p no:cacheprovider tests/ -k movement`: **251 passed**
- `pytest -p no:cacheprovider tests/ -k fleet_navigation`: **119 passed**
- `pytest -p no:cacheprovider tests/ -k hex_outlines`: **6 passed**
- `pytest -p no:cacheprovider tests/unit/strategy/data/test_galaxy_state_encapsulation.py tests/unit/strategy/data/test_galaxy_state.py tests/unit/strategy/data/test_galaxy_cleanup.py`: **24 passed**
- `pytest -p no:cacheprovider tests/unit/strategy/data/test_galaxy_entity_registry.py tests/unit/strategy/data/test_galaxy_spatial_index.py`: **36 failed, 21 passed**
- `rg -n "galaxy\._(global_hex|planet_to_system|zone_to_system)" game tests combat_lab Tools docs Projects/active_projects/PROJ-387 --glob '!docs/_ignore/**'`: no production hits under `game/`, but many test hits remain.

## Plan Goals Vs Actual Implementation

The plan had two concrete goals:

1. Migrate three external readers away from the `Galaxy` backward-compat private forwarders.
2. Delete the five `Galaxy` forwarders: `_global_hex_planets`, `_global_hex_zones`, `_global_hex_warp_points`, `_planet_to_system`, and `_zone_to_system`.

Those production goals are met in the current checkout:

- `game/strategy/data/galaxy.py` exposes `state`, `radius`, `systems`, `name_map`, `planets_by_id`, `fleets_by_id`, `_next_planet_id`, and `_next_fleet_id`, but no `_global_hex_*`, `_planet_to_system`, or `_zone_to_system` property definitions remain.
- `game/strategy/engine/handlers/movement.py:242` reads `session.galaxy.state.global_hex_warp_points`.
- `game/strategy/services/fleet_warp_resolution.py:65` reads `galaxy.state.global_hex_warp_points`.
- `game/ui/screens/strategy_render/hex_outlines.py:34`, `:45`, and `:57` read `r.galaxy.state.global_hex_planets`, `global_hex_zones`, and `global_hex_warp_points`.

The current code is actually cleaner than the PROJ-387 checklist wording in one respect: the checklist says callers moved to `galaxy._state.<field>`, while the current implementation uses the public `galaxy.state.<field>` property added by follow-up work.

## Literal Checklist Execution

- Task 1.1 says `movement.py` was corrected from nonexistent `game/strategy/data/movement.py` to `game/strategy/engine/handlers/movement.py`; that correction is accurate in the checklist, but `manifest.md` still contains the obsolete path.
- Tasks 1.1, 1.2, and 1.3 are checked complete and their named broad selectors now pass.
- Task 1.4 is checked complete and the forwarder definitions are gone from `Galaxy`.
- The checklist's grep claim is too narrow for audit evidence. There are no live production hits, but the exact private-field pattern still appears in multiple tests, including two currently failing unit-test files.
- `plan.md` Current State says "4 affected test files" were migrated, but the manifest does not list them and the state/delegate tests below remain stale.

## Plan Gaps And Missed Assumptions

- The initial plan scoped only the three production readers. It did not account for tests that instantiate `GalaxyEntityRegistry` and `GalaxySpatialIndex` directly with fake pre-`GalaxyState` objects.
- The plan treated "external readers" as the only migration risk, but unit tests are executable consumers of the same field contract. That gap let stale test doubles survive the deletion.
- The plan described the destination as "public `GalaxyState` accessors" but the checklist encoded `galaxy._state.<field>`. The current public `Galaxy.state` property resolves that API gap, apparently via PROJ-394, but PROJ-387's own plan did not cleanly specify the intended public access surface.
- The file manifest started with a wrong path (`game/strategy/data/movement.py`) and was not corrected after the phase checklist discovered the real target.

## Findings

### Major: State-delegate unit tests still fail after the field-shape migration

`tests/unit/strategy/data/test_galaxy_entity_registry.py` and `tests/unit/strategy/data/test_galaxy_spatial_index.py` still build `_MockGalaxy` doubles with the deleted private field names instead of `GalaxyState`'s current fields. They then pass those doubles directly into `GalaxyEntityRegistry` / `GalaxySpatialIndex`, whose constructors and methods now expect `next_planet_id`, `planet_to_system`, `global_hex_planets`, `global_hex_zones`, `global_hex_warp_points`, and `zone_to_system`.

Evidence:

- `tests/unit/strategy/data/test_galaxy_entity_registry.py:16-27` defines `_MockGalaxy` with `_next_planet_id`, `_planet_to_system`, `_global_hex_planets`, `_global_hex_zones`, and `_zone_to_system`.
- `tests/unit/strategy/data/test_galaxy_entity_registry.py:73-75` passes that object into `GalaxyEntityRegistry`.
- `game/strategy/data/galaxy_entity_registry.py:30-36` documents/assigns the constructor dependency as `GalaxyState`.
- `game/strategy/data/galaxy_entity_registry.py:75-88` reads `planets_by_id`, `planet_to_system`, `global_hex_planets`, and `next_planet_id`.
- `tests/unit/strategy/data/test_galaxy_spatial_index.py:16-27` defines `_MockGalaxy` with the deleted private field names.
- `tests/unit/strategy/data/test_galaxy_spatial_index.py:78-80` passes that object into `GalaxySpatialIndex`.
- `game/strategy/data/galaxy_spatial_index.py:49-66` reads `planet_to_system`, `global_hex_planets`, and `global_hex_zones`.

Observed result:

- `pytest -p no:cacheprovider tests/unit/strategy/data/test_galaxy_entity_registry.py tests/unit/strategy/data/test_galaxy_spatial_index.py` produced **36 failures**. Representative errors include `AttributeError: '_MockGalaxy' object has no attribute 'next_planet_id'`, `planet_to_system`, and `global_hex_planets`.

Impact:

- The project cannot honestly claim "all tests passing" or clean audit completion in the current checkout.
- The tests most directly exercising the delegates behind the deleted `Galaxy` forwarders are stale, which weakens confidence that the migration was fully verified.

### Minor: Project metadata still says PROJ-387 is Planning

`validate_audit_ready.py` passed but warned that the index status is still `Planning`. `Projects/projects_index.md:19` lists PROJ-387 with status `Planning`, while `plan.md` and `phase_1_checklist.md` mark Phase 1 complete and awaiting verification.

Impact:

- This does not block code behavior, but it is project-system drift and should be fixed before archival.

### Minor: Manifest still references a nonexistent implementation file

`Projects/active_projects/PROJ-387/manifest.md` lists `game/strategy/data/movement.py` as a migration target, but the checklist later corrected the task to `game/strategy/engine/handlers/movement.py` because `data/movement.py` does not exist.

Impact:

- This did not hide a production gap here, but it makes the audit trail unreliable and was a preventable plan-maintenance miss.

## Residual Risks

- Many tests still contain `galaxy._global_hex_planets` or `galaxy._planet_to_system` in fake objects. Some may be harmless local test scaffolds, but the failing state-delegate tests prove this pattern is not uniformly safe.
- I did not run the full sharded suite because the focused state-delegate failures are already sufficient to fail the audit. The project's recorded full-suite claim should be rechecked after the stale tests are migrated.
- Later follow-up work (PROJ-394) appears to have improved the access path from `galaxy._state` to `galaxy.state`; this review evaluates the current checkout, where that follow-up is present.

## Recommended Follow-Up

Create an audit-fix phase for PROJ-387 or route to the appropriate follow-up project:

- Replace the stale `_MockGalaxy` test doubles in `test_galaxy_entity_registry.py` and `test_galaxy_spatial_index.py` with `GalaxyState` instances or the shared `make_galaxy_stub()` helper.
- Re-run the two failing test files, then the listed PROJ-387 selectors.
- Update `manifest.md` and `Projects/projects_index.md` so the project metadata matches the completed implementation.
