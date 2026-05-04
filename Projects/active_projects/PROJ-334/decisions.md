# PROJ-334: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Project 4 of 10-project test-coverage arc. Master plan: `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md`. |
| 2026-05-04 | **D-001:** Coverage gap audit BEFORE writing tests | `pathfinding.py` already has 1209 LOC of tests under `tests/unit/strategy/pathfinding/`. Writing without an audit risks duplication. Phase 0 produces `findings/coverage_gap_audit.md`. |
| 2026-05-04 | **D-002:** Determinism = golden-hash + different-seeds | Per master plan §user testing philosophy: "test breaks if behavior changes." For `generate_systems(seed=42, count=5)`, pin a canonical representation (sorted list of `(name, global_location)` tuples) AND verify seed=43 produces a different list. Golden value is recorded in test, not in a separate fixture file (smaller blast radius on intentional regen). |
| 2026-05-04 | **D-003:** No property-based testing | User priority order is readability > maintainability > functionality > runtime. Hypothesis-style property tests obscure failure mode and add a dependency. Single canonical golden + sanity differs is enough to pin determinism. |
| 2026-05-04 | **D-004:** Extend existing pathfinding test directory, add new file for generator | `tests/unit/strategy/pathfinding/` is the established location; add gap-fill tests there. `GalaxySystemGenerator` has no dedicated unit-test file; create `tests/unit/strategy/data/test_galaxy_system_generator.py` (new). |
| 2026-05-04 | **D-005:** Mock `placement_strategy`, `star_generator`, `planet_generator`, `naming` for generator tests | These are constructor-injected dependencies. Pure-algorithm characterization should isolate `GalaxySystemGenerator`'s own logic (saturation counter, dual-RNG seed derivation, spatial-index reuse) from the placement / naming / planet-gen subsystems, which have their own test files. Use minimal hand-rolled fakes (no `unittest.mock` patching) to keep tests readable. |
| 2026-05-04 | **D-006:** Document, don't fix, observed oddities | Pathfinding has visible smells: `current_sys` reassigned twice in `find_path_interstellar` (lines 91 and 106 — first assignment is dead code with stale comment); `find_path_interstellar` mixes A* G-cost (path so far) with H-cost (heuristic) using `hex_distance` for both, which is admissible but overweights the heuristic; `_chaserProxy` carries `id=-1` for `NavigationState`, which leaks into log output. Record in this log under D-Observations as the gap audit confirms each. Bug-fix tickets are separate. |
| 2026-05-04 | **D-007:** Test naming convention | Each new test name MUST encode the behavior in active voice. Examples: `test_find_path_interstellar_returns_none_when_target_in_disconnected_subgraph`, `test_generate_systems_stops_after_10_consecutive_placement_failures`, `test_generate_systems_with_seed_42_produces_canonical_5_system_galaxy`. No `test_basic_*`, no `test_edge_*`, no `test_misc_*`. |
| 2026-05-04 | **D-008:** Single test file per production file (default per master plan) | Generator gets `test_galaxy_system_generator.py`. Pathfinding gap-fills slot into the existing per-feature split (`test_basic_paths.py` for `find_path_*`, `test_edge_cases.py` for failures, etc.) — overriding the "one file per production file" default per master plan §"Combine only if the production files share fixtures". |
| 2026-05-04 | **D-009:** Per-file commit, not per-class | Master plan calls for per-class commits but for this project the test additions are scattered across multiple existing files plus one new file. Land as: (1) coverage_gap_audit.md, (2) galaxy_system_generator new file, (3) pathfinding gap-fills (one commit per touched test file). 4-5 commits total. |

## D-Observations (record observed oddities; do NOT fix)

| ID | File:Line | Observation | Reproducer test |
|----|-----------|-------------|-----------------|
| _to be filled during Phase 0 audit_ | | | |
