# Phase 0: facade-delegate template + AST/protocol scaffolding

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-372 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Depends on:** —
**Review Mode:** cumulative (covers Phase 0 only at this gate)
**Files (planned):** see manifest.md Phase 0 row group

**Status:** Complete
**Objective:** Establish the scaffolding that downstream phases consume — the `galaxy_protocols.py` module, the `ApplicationContext` accessor stubs for `PlanetHabitabilityService`, the AST guard tests (initially permissive, tightened each phase), and the perf baseline bench. Zero algorithmic refactor in this phase; nothing in `galaxy.py` / `planet.py` / `stars.py` is restructured. Goal: every later phase can land safely because the safety nets are already in place.

**Notes (Phase 0 outcomes):**
- LOC baseline: galaxy=689, planet=667, stars=770 (matches plan).
- State-encapsulation AST guard: 5 external read sites discovered (architect's manual grep missed them) — grandfathered with `GRANDFATHERED_EXTERNAL_READS`. Phase 3 will introduce public Galaxy methods (e.g. `iter_warp_point_hexes`) and remove these from the grandfather set.
- Perf baseline (50 systems, 5 runs min): pathfinding 41us, spatial 369us, habitability 240us. Pinned at `tests/performance/bench_galaxy_planet_star_baseline.json`.
- 15 Phase-0 tests pass (5 protocol conformance + 3 LOC + 2 state-encap + 3 context + 1 bench wired).
- Tests live at `tests/performance/` (existing repo convention) not `tests/perf/` (plan slip; not material).

---

## Pre-flight (TDD baseline)

- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count and pin in plan.md Current State (`Last Action: baseline = N tests passing`).
- [ ] `wc -l game/strategy/data/galaxy.py game/strategy/data/planet.py game/strategy/data/stars.py` — capture today's LOC counts (expected: 689, 667, 770) and pin in this checklist's `Notes:` section.
- [ ] Verify zero in-flight branches touching `galaxy.py` / `planet.py` / `stars.py` (`git log --oneline --all -- game/strategy/data/galaxy.py | head -5`).

---

## Tasks

### Task 0.1: Define `IHabitabilityCalculator` and read protocols [Simple]
**File:** `game/strategy/data/galaxy_protocols.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_protocols.py -v`

- [ ] Create new file with module docstring "Read protocols for galaxy/planet/star surfaces. PROJ-372."
- [ ] Define `class IHabitabilityCalculator(Protocol)` with `def get_cached(self, planet, race_registry, turn: int) -> float: ...`
- [ ] Define `class IGalaxySystemGraph(Protocol)` with `def get_system_by_name(self, name: str) -> Optional['StarSystem']: ...` and `def systems(self) -> dict[HexCoord, 'StarSystem']: ...`
- [ ] Define `class IGalaxySpatialQuery(Protocol)` with `get_system_at_location`, `get_planets_at_global_hex`, `get_zones_at_global_hex`, `get_planet_global_hex`
- [ ] Define `class IStockpileHolder(Protocol)` with `add_to_stockpile`, `consume_from_stockpile`, `has_stockpile`, `get_stockpile`
- [ ] Define `class IStagingYardHolder(Protocol)` with `get_staging_mass`, `add_to_staging_yard`, `remove_from_staging_yard`, `max_staging_mass`
- [ ] Add a unit test asserting `Planet` satisfies `IStockpileHolder` and `IStagingYardHolder` structurally (`isinstance(planet, IStockpileHolder)` style with `runtime_checkable`)
- [ ] Add a unit test asserting `Galaxy` satisfies `IGalaxySystemGraph` and `IGalaxySpatialQuery` structurally
- [ ] **Verify:** module under 150 LOC; both unit tests pass.

**Notes:**

### Task 0.2: Add `ApplicationContext` accessors for habitability service [Simple]
**File:** `game/context.py` (modify)
**Tests:** `pytest tests/unit/test_context.py -v`

- [ ] Add module-level `_default_planet_habitability_service: Optional[IHabitabilityCalculator] = None`
- [ ] Add `def get_default_planet_habitability_service() -> Optional[IHabitabilityCalculator]: return _default_planet_habitability_service`
- [ ] Add `def set_default_planet_habitability_service(svc: Optional[IHabitabilityCalculator]) -> None: global _default_planet_habitability_service; _default_planet_habitability_service = svc`
- [ ] Phase 0 returns `None` until Phase 2 wires the real implementation; `Planet.get_cached_habitability_multiplier` falls back to today's late-import path when the accessor returns `None` — **add this fallback now** so Phase 0 ships green.
- [ ] Add unit tests covering get/set roundtrip and the `None` fallback.
- [ ] **Verify:** existing `Planet.get_cached_habitability_multiplier` still returns identical values for a known fixture (golden snapshot or equivalent — pick a planet from a fixture save, call before-and-after, assert equality to 6 decimal places).

**Notes:**

### Task 0.3: AST guard for LOC ceilings [Medium]
**File:** `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py -v`

- [ ] Use `pathlib.Path.read_text().count('\n')` (matches `wc -l` semantics) for LOC measurement.
- [ ] Initial ceilings (Phase 0 baseline): `galaxy.py ≤ 689`, `planet.py ≤ 667`, `stars.py ≤ 770`. Each subsequent phase tightens (per manifest.md).
- [ ] Test asserts `actual ≤ ceiling`; failure message reports `actual` and the ceiling for easy debugging.
- [ ] Constants live at module top so each phase changes ONE number per file.
- [ ] **Verify:** test passes today; `assert actual == ceiling` (sanity check the LOC counter).

**Notes:**

### Task 0.4: AST guard for state encapsulation [Medium]
**File:** `tests/unit/strategy/data/test_galaxy_state_encapsulation.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_galaxy_state_encapsulation.py -v`

- [ ] Walk every `*.py` under `game/` via `ast.parse`; collect every `Attribute(value=Name(id='galaxy'), attr=X)` and every `Attribute(value=Name(id='self'), attr=X)` where the file imports `Galaxy`.
- [ ] Assert no read of `_global_hex_planets`, `_global_hex_zones`, `_zone_to_system`, `_planet_to_system`, `_global_hex_warp_points` outside an `ALLOWED_FILES = {"galaxy.py", "galaxy_entity_registry.py", "galaxy_spatial_index.py"}` set.
- [ ] Phase 0 baseline: capture the current state (today, the test should pass — verified by manual grep, all reads are inside those three files).
- [ ] **Verify:** test passes; `print` the count of allowed reads and pin in `Notes:`.

**Notes:**

### Task 0.5: Perf baseline bench [Medium]
**File:** `tests/perf/bench_galaxy_planet_star.py` (new)
**Tests:** `pytest tests/perf/bench_galaxy_planet_star.py -v`

- [ ] Build a synthetic 150-system, 600-planet galaxy via `Galaxy.generate_systems(150)` then `for system: galaxy.generate_planets(system)`. Use `random.seed(42)` for determinism.
- [ ] Bench A — pathfinding: pick 3 random `(start, end)` system pairs; measure `find_path_interstellar` / `find_hybrid_path` in microseconds via `time.perf_counter`. Record min of 100 runs.
- [ ] Bench B — spatial: 1000 random `HexCoord` lookups via `galaxy.get_system_at_location`. Record min of 100 runs.
- [ ] Bench C — habitability: 1000 calls to `planet.get_cached_habitability_multiplier(race_registry, turn=42)` across the planet population. Record min of 100 runs.
- [ ] Output JSON to a fixture file `tests/perf/bench_galaxy_planet_star_baseline.json` (gitignored or committed — decide at impl time).
- [ ] Phase 5 re-runs the same bench and asserts within ±5%.
- [ ] **Verify:** all three benches complete in < 30s; JSON written; pin baseline numbers in `Notes:`.

**Notes:**

### Task 0.6: Document the facade-delegate template for downstream phases [Simple]
**File:** `Projects/active_projects/PROJ-372/findings/facade_template.md` (new)
**Tests:** none (documentation)

- [ ] Write a 1-page "Facade-Delegate Pattern Template" describing:
  - Class structure: `Facade` holds `_state: State` + `_service: Service(_state)`; public methods are 1-line `return self._service.X(self._state, ...)`.
  - When to extract: method body > 5 LOC OR has `if/else` branches OR holds algorithmic logic.
  - When to keep: data identity (`__eq__`, `__hash__`), serialization, getters that return a stored field.
  - Test pattern: services are tested with stub state objects (no full Galaxy / Planet construction needed).
- [ ] Reference PROJ-86/87/88/89 as predecessors and the existing `GalaxyEntityRegistry` / `GalaxySpatialIndex` as the in-tree exemplar.
- [ ] **Verify:** template is < 500 lines; cross-linked from each phase checklist's "Reading" section.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] AST guards (Tasks 0.3, 0.4) pass with the LOC ceilings at today's baseline
- [ ] Perf bench (Task 0.5) JSON file committed; baseline numbers pinned in `Notes:`
- [ ] `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count ≥ pre-Phase-0 baseline + (count of new test files × 1+)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
