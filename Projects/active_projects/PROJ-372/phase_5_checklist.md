# Phase 5: AST guards, perf bench, doc updates, final audit

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-372 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Depends on:** Phase 4 (verified)
**Review Mode:** cumulative (Phases 0-5; final audit gate)
**Files (planned):** see manifest.md Phase 5 row group

**Status:** Not Started
**Objective:** Lock in the post-decomposition shape: delete the deprecated `pathfinding.py` shims (now that all 82 callers should be migrated to services), add a "no method body > 5 LOC on Galaxy/Planet/Star" AST guard, re-run the Phase 0 perf bench and assert within ±5%, run save round-trip on 5 fixture saves, update `docs/systems/strategy_layer.md` + `docs/02_PATTERNS.md` + `docs/01_ARCHITECTURE.md`, and run the final audit gate.

---

## Reading

- [ ] Phase 4 outcomes — `galaxy.py` / `planet.py` / `stars.py` at target ceilings; sharded green
- [ ] `docs/systems/strategy_layer.md`, `docs/02_PATTERNS.md`, `docs/01_ARCHITECTURE.md`
- [ ] Phase 0's `findings/facade_template.md`

---

## Tasks

### Task 5.1: Migrate remaining `pathfinding.py` callers off the deprecated shims [Medium]
**File:** various callers (sweep)
**Tests:** sharded suite

- [ ] `grep -rn 'from game.strategy.data.pathfinding import' game/ tests/` — list all 82 (or whatever's left) caller sites.
- [ ] For each, replace the import with `from game.strategy.services.galaxy_pathfinding_service import GalaxyPathfindingService` and call via `galaxy._pathfinder.X(...)` (or accept the service explicitly).
- [ ] **Verify:** zero remaining `from game.strategy.data.pathfinding import` lines.

**Notes:**

### Task 5.2: Delete `pathfinding.py` shim file [Simple]
**File:** `game/strategy/data/pathfinding.py` (DELETE)

- [ ] Confirm Task 5.1's grep returns zero hits.
- [ ] `git rm game/strategy/data/pathfinding.py`.
- [ ] Also delete `tests/unit/strategy/data/test_pathfinding.py` (replaced by `test_galaxy_pathfinding_service.py` and `test_intercept_calculator.py` from Phase 4).
- [ ] **Verify:** sharded suite green; nothing imports the deleted file.

**Notes:**

### Task 5.3: AST guard: no Galaxy/Planet/Star method body > 5 LOC (except allow-listed) [Medium]
**File:** `tests/unit/strategy/data/test_no_method_body_over_5_loc.py` (new)

- [ ] Walk `galaxy.py`, `planet.py`, `stars.py`. For each method on `Galaxy`, `Planet`, `Star`, count statement nodes (`ast.FunctionDef.body` excluding pure-string `Expr`s like docstrings).
- [ ] Allow-list: `__init__`, `__eq__`, `__hash__`, `__repr__`, `to_dict`, `from_dict` (these are inherently long because of field counts).
- [ ] Assert all other method bodies have ≤ 5 statement nodes.
- [ ] **Verify:** test passes; if it fails, the implementer hasn't fully thinned the facade.

**Notes:**

### Task 5.4: Per-service LOC ceiling guards [Simple]
**File:** `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` (modify)

- [ ] Add per-service ceilings: `galaxy_state.py ≤ 150`, `galaxy_protocols.py ≤ 150`, `spectrum.py ≤ 80`, `spectrum_math.py ≤ 200`, `star_generator.py ≤ 500`, `planet_query_service.py ≤ 250`, `planet_habitability_service.py ≤ 200`, `galaxy_pathfinding_service.py ≤ 350`, `intercept_calculator.py ≤ 150`.
- [ ] **Verify:** all ceilings met.

**Notes:**

### Task 5.5: Re-run perf bench; assert within ±5% [Medium]
**File:** `tests/perf/bench_galaxy_planet_star.py` (modify)

- [ ] Re-run the Phase 0 baseline bench on the same synthetic 150-system / 600-planet galaxy.
- [ ] Compare against the baseline JSON committed in Phase 0. Assert each of the 3 benches is within ±5% of baseline.
- [ ] If a bench regresses > 5%, raise an issue and fix before audit close.
- [ ] **Verify:** all benches pass.

**Notes:**

### Task 5.6: Save round-trip on 5 fixture saves [Medium]
**File:** `tests/integration/strategy/test_save_round_trip.py` (new — replaces phase-temporary tests)

- [ ] Use 5 saves from `saves/` (or build 5 fixture saves at varying complexity: empty, 10 systems, 50 systems, 150 systems, full game state).
- [ ] For each, load → `to_dict()` → `from_dict()` → `to_dict()` and assert dict equality.
- [ ] **Verify:** all 5 pass; delete phase-temporary `test_save_round_trip_phase{1,2,3}.py`.

**Notes:**

### Task 5.7: Update strategy-layer docs [Medium]
**File:** `docs/systems/strategy_layer.md` (modify)

- [ ] Add a "Galaxy/Planet/Star Decomposition (PROJ-372)" section reflecting:
  - Galaxy now composes `GalaxyEntityRegistry`, `GalaxySpatialIndex`, `GalaxyWarpGenerator`, `GalaxySystemGenerator`, `GalaxyPathfindingService`, `InterceptCalculator` over a `GalaxyState` data object.
  - Planet exposes a thin facade backed by `PlanetQueryService` and `PlanetHabitabilityService`.
  - Star data class is in `stars.py`; `StarGenerator` is in `generation/star_generator.py`; `Spectrum` is in `data/spectrum.py`; spectral math is in `core/spectrum_math.py`.
- [ ] Update `> **Last verified:** 2026-XX-XX` blockquote per `docs/03_CONVENTIONS.md` §9.
- [ ] **Verify:** doc renders cleanly; cross-links work.

**Notes:**

### Task 5.8: Update `docs/02_PATTERNS.md` Facade-Delegate Pattern entry [Simple]
**File:** `docs/02_PATTERNS.md` (modify)

- [ ] Add or extend a "Facade-Delegate Pattern" section pointing at `Galaxy → GalaxyState + 6 services` as the canonical example.
- [ ] Reference Phase 0's `findings/facade_template.md`.
- [ ] Update `> **Last verified:**` blockquote.
- [ ] **Verify:** rendered cleanly.

**Notes:**

### Task 5.9: Update `docs/01_ARCHITECTURE.md` strategy-layer service inventory [Simple]
**File:** `docs/01_ARCHITECTURE.md` (modify)

- [ ] Add new services to the inventory table.
- [ ] Add `game/core/spectrum_math.py` to the `core/` layer's pure-math module list.
- [ ] Update `> **Last verified:**` blockquote.

**Notes:**

### Task 5.10: Backfill PROJ-370 cross-link [Simple]
**File:** `Projects/active_projects/PROJ-370/decisions.md` (modify)

- [ ] Add row: "PROJ-372 introduced 5 read protocols (`IGalaxySystemGraph`, `IGalaxySpatialQuery`, `IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`); PROJ-370 layers contract testing on top of them."
- [ ] **Verify:** PROJ-370's plan.md and decisions.md are mutually consistent re: sequencing.

**Notes:**

### Task 5.11: Final audit gate [Complex]
**File:** N/A (audit only)

- [ ] All goals G1-G9 from plan.md verified:
  - G1: `galaxy.py` ≤ 350 LOC + every method ≤ 5-LOC body (AST guard) ✓
  - G2: `planet.py` ≤ 350 LOC ✓
  - G3: `stars.py` ≤ 280 LOC + 4-file split landed ✓
  - G4: habitability service swappable via context (acceptance test) ✓
  - G5: pathfinding callable on 3-system stub (acceptance test) ✓
  - G6: PROJ-173-Phase-2 delegates take `GalaxyState` not `Galaxy` ✓
  - G7: AST guards green (LOC + method body + state encapsulation) ✓
  - G8: perf bench within ±5% of baseline ✓
  - G9: save round-trip green on 5 fixture saves ✓
- [ ] Sharded suite green; pass count ≥ baseline + new tests.
- [ ] Audit Log entry added to plan.md (cycle 1, PASSED).

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] All 9 plan.md goals verified
- [ ] Sharded suite green; pass count grew monotonically across all 6 phases
- [ ] Perf bench within ±5%; save round-trip green
- [ ] Docs updated (`strategy_layer.md`, `02_PATTERNS.md`, `01_ARCHITECTURE.md`); `Last verified:` blockquotes refreshed
- [ ] PROJ-370 cross-link backfilled
- [ ] Audit cycle 1 PASSED
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`; Current State to "Awaiting user verification"
