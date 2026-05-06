# PROJ-334 File Manifest

> Generated during planning. Used for parallel-conflict detection per master plan §File-overlap matrix.

## Production files (READ-ONLY for this project)

| File | LOC | Notes |
|------|----:|-------|
| `game/strategy/data/pathfinding.py` | 503 | A* interstellar, deep-space linedraw, hybrid path, intercept. NOT modified. |
| `game/strategy/data/galaxy_system_generator.py` | 354 | System placement, planet/storm/archetype rolls, dual-RNG seed derivation. NOT modified. |

## Test files

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/pathfinding/test_basic_paths.py` | Test (extend) | Add gap-fill tests for `find_path_interstellar` (disconnected subgraph, single-hop) and `find_path_deep_space` (target == source). |
| `tests/unit/strategy/pathfinding/test_edge_cases.py` | Test (extend) | Add unreachable-target, intercept-with-zero-speed, intercept-with-empty-target-path coverage if gap audit confirms. |
| `tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py` | Test (extend) | Add hybrid-path-with-fleet-cannot-warp-fallback, missing-reciprocal-warp-point, same-system-deep-space-route gaps. |
| `tests/unit/strategy/data/test_galaxy_system_generator.py` | Test (NEW) | Full coverage for `GalaxySystemGenerator.generate_systems`, `generate_planets`, `generate_storms`, dual-RNG seed derivation, saturation counter, idempotent archetype roll. |

## Findings / docs

| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-334/findings/coverage_gap_audit.md` | Doc (NEW) | Phase 0 output: per-symbol coverage matrix. Source of truth for Phase 1 scope. |

## Cross-project overlap

Per master plan §File-overlap matrix:
- PROJ-334 owns `data/pathfinding.py` and `data/galaxy_system_generator.py` exclusively.
- PROJ-335 owns `data/planetary_facility.py`, `data/species_population.py`, `data/squadron.py`, `data/order_types.py`, `data/group_policy_registry.py` (zero overlap).
- PROJ-336 owns `services/*` (zero overlap).

Test directory `tests/unit/strategy/data/` is shared with PROJ-335; per-file ownership is exclusive (we add `test_galaxy_system_generator.py`; they add their own files).
