# Phase 1: Spatial Narrow-Phase Distance Check

**Objective:** Add a `query_radius_exact()` method to `SpatialGrid` that filters broad-phase results by actual Euclidean distance, eliminating false positives from grid cell overlap.

**Key Principle:** Broad-phase (grid cells) is for fast candidate reduction. Narrow-phase (distance check) ensures correctness. Both are needed.

---

## Background

`SpatialGrid.query_radius()` returns all entities in overlapping grid cells within a radius-sized bounding box. For a radius of 500 and cell_size of 200, this returns entities from up to a 5x5 grid (25 cells) — many of which are beyond the actual radius. `_find_enemies_in_radius()` in the AI controller applies team/alive/combatant filters but no distance check.

## Design

1. Add `query_radius_exact(pos, radius) -> List` to `SpatialGrid`
2. Internally calls `query_radius()` for broad-phase, then filters by `distance_squared <= radius_squared`
3. Update `_find_enemies_in_radius()` to use `query_radius_exact()`
4. Entities must expose a position (via `.position`, `.get_position()`, or `.x/.y` attributes)

---

## Checklist

### Discovery
- [ ] Read `spatial.py` fully — understand grid structure and entity position API
- [ ] Read all callers of `query_radius()` — determine which need exact filtering
- [ ] Check how entities expose position (attribute name, tuple vs Vector2, etc.)

### Tests First (TDD)
- [ ] Write test: entity exactly at radius distance — included in results
- [ ] Write test: entity just beyond radius — excluded from results
- [ ] Write test: entity well within radius — included in results
- [ ] Write test: entity in adjacent cell but beyond radius — excluded (the key case)
- [ ] Write test: empty grid — returns empty list
- [ ] Write test: multiple entities at varying distances — only those within radius returned
- [ ] Run tests — confirm they fail

### Implementation
- [ ] Add `query_radius_exact(pos, radius) -> List` to `SpatialGrid`
- [ ] Use `distance_squared` comparison (avoid sqrt for performance)
- [ ] Determine entity position access pattern (attribute or method) and use consistently
- [ ] Update `_find_enemies_in_radius()` in `controller.py` to call `query_radius_exact()`
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python scripts/test_sharded.py`) — no regressions
- [ ] Run simulation tests (`python -m simulation_tests.run_tests`) — all pass
- [ ] Profile: in a 50-ship battle, count candidates returned by `query_radius()` vs `query_radius_exact()` — expect significant reduction
