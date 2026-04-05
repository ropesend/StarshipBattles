# Phase 5 Checklist: Performance Verification and Cleanup
**Status:** Not Started

## Task 5.1: Full regression testing [Simple]
- [ ] `python scripts/test_sharded.py` -- all tests pass
- [ ] `python -m simulation_tests.run_tests --fast` -- all simulation tests pass
- [ ] `python -m simulation_tests.run_tests` -- all simulation tests including HT pass
**Notes:**

## Task 5.2: Code cleanup [Simple]
- [ ] Verify: `grid.clear()` is only called in `start()` and test setup, never in tick loop
- [ ] Verify: no dead entities remain in grid after any tick (add assertion in debug mode if desired)
- [ ] Verify: all grid consumers (`AIController`, `ProjectileManager`) work identically -- API unchanged
- [ ] Remove any temporary debug code
**Notes:**

## Task 5.3: Documentation updates [Simple]
- [ ] Update `docs/systems/combat_simulation.md` if it documents grid rebuild behavior
- [ ] Update `docs/01_ARCHITECTURE.md` if SpatialGrid API is described there
- [ ] Add `update()` and `remove()` to any API documentation for SpatialGrid
**Notes:**

## Task 5.4: Optional performance benchmark [Simple]
- [ ] Create a simple timing script: run a 1000-tick 20v20 battle, measure average tick time
- [ ] Compare before (full rebuild) vs after (incremental) -- expect modest improvement
- [ ] Log results in decisions.md -- not a hard requirement, just informational
**Notes:**
