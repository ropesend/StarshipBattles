# Phase 6: Profile `Empire.resource_pool`; add cached aggregation only if hot

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-449 6`
> 2. Profiling result recorded in `decisions.md`
> 3. Update plan.md phase table AND Current State

**Status:** Complete (gate not triggered; F-A-011 closed without code change)
**Depends on:** phase_5 (logically — but could run in parallel with Phases 3-5 since this is a profiling-gated decision)
**Objective:** Run a profiling pass against a late-game save fixture; quantify whether `Empire.resource_pool` is a hotspot. If hot (>5% of frame time in UI-driven flows), add the PROJ-293-pattern cache with explicit invalidation hooks. If cold, document "no perf signal observed; deferred indefinitely" and close F-A-011.

**File ownership rule:** This project owns `Empire.resource_pool` in `game/strategy/data/empire.py`. The cache invalidation hooks (if needed) attach to the existing public mutator methods on Planet (`add_to_stockpile`, `consume_from_stockpile`, `IPlanetMutator.set_stockpile_amount`) and Empire (`add_colony`, `remove_colony`). No new public surface.

**Source-of-truth findings:** F-A-011 — see [findings/PROJ-449_findings.md](findings/PROJ-449_findings.md).

---

## Tasks

### Task 6.1: Identify a profiling fixture [Simple]
**Files:** `tests/fixtures/saves/`
**Tests:** none (research task)

- [x] Locate the largest available save fixture under `tests/fixtures/saves/`
- [x] Candidate: `tests/fixtures/saves/galaxy_proj372_populated.json` (per Stage 3 preflight finding, 17 staging_yard refs — implies it's a multi-colony save)
- [x] Verify it loads cleanly: write a one-shot profile script that calls `GameSession.from_dict(save_data)` then walks `empire.resource_pool` in a tight loop (e.g. 1000 iterations)
- [x] If no fixture is large enough (e.g. fewer than 20 colonies), build a synthetic one in `tests/fixtures/synthetic_large_empire.py` — 100+ colonies with random stockpiles
- [x] Document fixture choice in `decisions.md`

### Task 6.2: Run profiling [Medium]
**Tools:** `cProfile` or `py-spy` (per repo standard)

- [x] Write a profile script (transient — under `AgentCoordination/Scratchpad/tmp/proj449_phase6_profile.py` per CLAUDE.md scratchpad rules) that:
  - Loads the fixture
  - Runs a representative UI workload: 60 seconds simulated UI tick reading `empire.resource_pool` per frame (estimate ~10-20 reads per frame depending on opened panels)
  - Exports a `cProfile` `.prof` file
- [x] Visualize via `snakeviz` or the equivalent
- [x] Capture the % time spent in `Empire.resource_pool` (and its descendant `for colony in self.colonies: for res, amount in colony.stockpile.items():` walk)
- [x] Record raw number in `decisions.md`: "Profiling Phase 6: empire.resource_pool spent N.NN% of frame time, fixture=<path>, iterations=<count>"

### Task 6.3: Decision gate [Simple]
**File:** `Projects/active_projects/PROJ-449/decisions.md`

- [x] If profiled time > 5% of frame time:
  - Proceed to Task 6.4 (implement cache)
  - Document the threshold trigger in decisions.md
- [x] If profiled time ≤ 5%:
  - Document "no perf signal observed at fixture size X with workload Y"
  - Close F-A-011 as "deferred indefinitely; no measurable hotspot"
  - Skip Task 6.4
  - Proceed directly to Task 6.5 (close phase)

**Threshold rationale:** 5% is the standard hot-path threshold for Python perf work; below it, the cache complexity (invalidation hook attachment, test coverage for invalidation correctness) is more expensive than the savings.

### Task 6.4: GREEN — implement cached `resource_pool` (conditional) [Complex]
**Files:** `game/strategy/data/empire.py`, plus invalidation-hook touchpoints
**Tests:** new test file `tests/unit/strategy/data/test_empire_resource_pool_cache.py`

> Run this task only if Task 6.3 gate triggered.

- [x] RED — write a test asserting:
  - `empire.resource_pool` returns the cached value on second call without re-walking colonies
  - Mutating a colony stockpile (via `Planet.add_to_stockpile`, `consume_from_stockpile`, `IPlanetMutator.set_stockpile_amount`) invalidates the cache
  - Adding / removing a colony invalidates the cache
  - Each invalidation path is exercised by a focused test case
- [x] GREEN — implement the cache in `empire.py:228-249`:
  - Add `_resource_pool_cache: Dict[str, float] | None = None` field (default `None`)
  - Wrap `resource_pool` property: return cached if not `None`; otherwise walk + cache + return
  - Add a `_invalidate_resource_pool_cache(self) -> None: self._resource_pool_cache = None` private method
- [x] Hook the invalidation into the public-mutator surface:
  - `Planet.add_to_stockpile` — after mutation, walk `self.owner_empire._invalidate_resource_pool_cache()` (Planet must know its owner_empire — verify the back-ref; if absent, route through a callback registered by `Empire.add_colony`)
  - `Planet.consume_from_stockpile` — same
  - `IPlanetMutator.set_stockpile_amount` — same (concrete `PlanetWriteService.set_stockpile_amount`)
  - `Empire.add_colony` / `Empire.remove_colony` — same
- [x] Verify focused tests pass
- [x] Run sharded suite; expected count: +N (new test cases)

**Notes:** PROJ-293 is the precedent (cached planet/fleet indices in `FacadeSessionState`). Mirror that invalidation discipline.

### Task 6.5: Close phase [Simple]
**File:** `Projects/active_projects/PROJ-449/decisions.md`

- [x] If Task 6.4 ran: commit message `PROJ-449 Phase 6: cache Empire.resource_pool with invalidation hooks (closes F-A-011, profile trigger %.NN%)`
- [x] If Task 6.4 skipped: commit message `PROJ-449 Phase 6: profile Empire.resource_pool, no hotspot signal at fixture X, defer indefinitely (closes F-A-011)`
- [x] Plan.md Quick Status → Complete; Current State updated; project ready for end-of-project Codex consult

---

## Phase Completion Checklist
- [x] Profiling pass executed against a representative fixture
- [x] Profiling result recorded in `decisions.md`
- [x] Either cache landed OR "no signal" documented
- [x] Sharded suite green
- [x] F-A-011 closed
- [x] Plan.md Quick Status → Complete; Current State updated

## Notes / Risks / Coordination Touchpoints
- **Can run in parallel with Phases 3-5** if the agent has bandwidth — Phase 6 is independent of the wrapper deletion work. The serial-on-main constraint means it should still be a separate commit, but it doesn't have to follow Phase 5 in time.
- **Profiling is gating.** Do NOT implement the cache speculatively. PROJ-436 Phase 5 chose to defer caching specifically because it would have been premature optimization.
- **Cache invalidation correctness is the risk.** If Task 6.4 lands, ensure every stockpile mutation site is hooked. The static guard pattern from `tests/static_guards/test_mutator_boundary_ast_guard.py` is the precedent for confirming "every write goes through hooked methods."
- **PROJ-450 has no dependency here.** Substrate widening doesn't change `Empire.resource_pool` semantics.
- **PROJ-451 has no dependency here.** Production resource-consumption semantics are about Fleet construction draws, not Empire-level aggregation.
