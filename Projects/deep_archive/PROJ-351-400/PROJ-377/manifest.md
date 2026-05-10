# PROJ-377 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

### Phase 1: Golden-save fixture

| File | Type | Notes |
|------|------|-------|
| `tests/fixtures/saves/galaxy_proj372_baseline.json` | Fixture (NEW) | Generated 5-system synthetic save, seed=2, no planets, with warp lanes. JSON via `json.dump(..., indent=2, sort_keys=True)`. |
| `tests/fixtures/saves/galaxy_proj372_populated.json` | Fixture (NEW) | Generated 10-system save, seed=100, with planets + warp lanes + manually-added owned planet. |
| `tests/fixtures/saves/_capture_baseline.py` | Script (NEW) | Captures both fixtures deterministically; leading underscore prevents pytest discovery. Idempotent. |
| `tests/integration/strategy/test_save_round_trip.py` | Test (modify) | Add 2 functions: `test_round_trip_golden_baseline_fixture`, `test_round_trip_golden_populated_fixture`. |

### Phase 2: Pathfinding shim migration sweep

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/superweapon_order_processor.py` | Production (modify) | Drop `from game.strategy.data.pathfinding import get_system_at_hex`. Change all ~10 `get_system_at_hex(galaxy, …)` calls to `galaxy._pathfinder.get_system_at_hex(…)`. |
| `game/strategy/facade/slices/planet_slice.py` | Production (verify-then-modify) | Phase 2 Task 2.1 verifies whether `tests/unit/strategy/facade/test_facade_robust_resolution.py:73,87` patches reach this slice; if NO patch reaches it, migrate. If YES patch reaches it, defer (add row to `decisions.md`). |
| `game/ui/screens/strategy_screen.py` | Production (modify) | 3 sites at :436, :441, :446. Replace shim imports with `self.galaxy._pathfinder.<method>(…)` calls. |
| `game/ui/screens/strategy_colonization.py` | Production (modify) | 1 site at :258. `self.scene.galaxy._pathfinder.get_system_at_hex(…)`. |
| `game/strategy/data/pathfinding.py` | Production (read-only this phase) | Module untouched in Phase 2. |
| `game/strategy/services/galaxy_pathfinding_service.py` | Production (read-only) | Migration target — public API used by migrated callers. |
| `tests/integration/strategy/test_command_handlers.py` | Test (read-only) | Pins Class B site #1, #4 as deferred. Read-only verification. |
| `tests/integration/strategy/turn_engine/test_basics.py` | Test (read-only) | Pins Class B site #1. |
| `tests/unit/strategy/test_advanced_fleet_orders.py` | Test (read-only) | Pins Class B sites #2, #6. |
| `tests/unit/strategy/pathfinding/test_edge_cases.py` | Test (read-only) | Pins Class B site #5. |
| `tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py` | Test (read-only) | Pins Class B sites #5, #6. |
| `tests/unit/strategy/fleet_movement_engine/test_warp.py` | Test (read-only) | Pins Class B site #6. |
| `tests/unit/strategy/turn_engine/test_tick_mechanics.py` | Test (read-only) | Pins Class B site #6. |
| `tests/unit/ui/screens/test_strategy_superweapons.py` | Test (read-only) | Pins Class B site #13. |
| `tests/unit/strategy/facade/test_facade_robust_resolution.py` | Test (read-only) | Pins Class B site #9 if Task 2.1 confirms patches reach the slice. |

### Phase 3: Shim-scope freeze + AST guard

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/data/test_pathfinding_shim_scope.py` | Test (NEW) | AST walks `pathfinding.py`; asserts top-level FunctionDef names exactly equal the Phase 2 final list (free functions + `_pathfinder_for` + `_intercept_for`). Test-author-friendly: docstring directs future agents to update the list deliberately, not silently. |
| `game/strategy/data/pathfinding.py` | Production (modify) | Module docstring update only. Replace "Phase 5 closed without the caller-site migration sweep; tracked as PROJ-376 follow-up" with "PROJ-377 closed the partial sweep; the surviving free functions exist as a permanent test-patch transparency surface for tests patching `pathfinding.X`. See PROJ-377 decisions.md and `test_pathfinding_shim_scope.py` for the pinned set." |
| `Projects/active_projects/PROJ-372/decisions.md` | Doc (modify) | Append row dated PROJ-377 close: "PROJ-377 closed MAJ-001 (golden fixture) + MIN-002 (partial shim sweep + AST guard). Deferred sites pinned in PROJ-377 plan + decisions." |
| `docs/systems/strategy_layer.md` | Doc (modify if it mentions shim status) | Update only if the doc references the shim's "deprecated" status or "PROJ-376 follow-up". Otherwise leave alone. |
| `Projects/active_projects/PROJ-377/plan.md` | Project doc (modify) | Phase status table updates as phases close. |

### Read-only references (touched zero times)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/galaxy.py` | Production (read-only) | `Galaxy._pathfinder` construction at :65; facade pattern reference. |
| `game/strategy/services/intercept_calculator.py` | Production (read-only) | Class C sites :121, :169 stay shim-routed by design. |
| `game/strategy/services/fleet_navigation_service.py` | Production (read-only) | Class B sites :36, :206 deferred. |
| `game/strategy/engine/game_session.py` | Production (read-only) | Class B sites :321, :340 deferred. |
| `game/strategy/engine/handlers/base.py` | Production (read-only) | Class B site :20 deferred. |
| `game/strategy/data/galaxy_state.py` | Production (read-only) | `GalaxyState` shape unchanged. |
| `game/strategy/data/planet.py`, `game/strategy/data/planet_serde.py` | Production (read-only) | Save format unchanged; PROJ-377 takes a snapshot of the current shape. |
| `game/strategy/data/star_system.py`, `game/strategy/data/stars.py`, `game/strategy/data/spectrum.py` | Production (read-only) | Save format unchanged. |
| `tests/integration/strategy/test_save_round_trip_phase{1,2,3,4}.py` | Test (read-only) | Per-phase boundary checks; PROJ-372 marked them "kept for now"; PROJ-377 leaves them. |
