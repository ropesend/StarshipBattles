# PROJ-444 Phase 3: PROJ-436 deletion-shim retirement (STACKED PR with PROJ-446, gated on PROJ-443)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-444 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 1 + Phase 2 complete; **PROJ-443 Phase 5b decision settled**; **PROJ-446 has confirmed F-C-020 will land as a stacked dependency or as part of this PR**
**Objective:** Retire the two coupled deletion shims (`_planet_init_with_legacy_kwargs` + `_ship_instance_init_with_legacy_kwargs`) and their @property clusters that PROJ-436 Phase 3f/4f intentionally deferred. **This phase requires a stacked PR or single-PR-spanning-two-buckets approach.** The fixture migration in PROJ-446 F-C-020 (`tests/fixtures/strategy_entities.py`) is the structural unblock — without it, the wrapper deletes leave the shared fixture broken across the entire suite.

**Cross-bucket file-ownership rule:** This phase is the documented exception to the "stay in your lane" rule. PROJ-444 (this project) edits `game/strategy/data/planet.py`, `ship_instance.py`, `planet_serde.py` AND `tests/fixtures/strategy_entities.py` (the latter normally PROJ-446's territory) as a single coordinated change. Coordinate via decisions.md before starting; if PROJ-446's agent is mid-phase, sequence behind them.

**Source-of-truth findings:** [`findings/bucket_a_data_facade_scan.md`](findings/bucket_a_data_facade_scan.md) — F-A-002, F-A-003, F-A-004, F-A-005, F-A-011. Also read PROJ-446's [`findings/bucket_c_ui_core_tests_scan.md`](../PROJ-446/findings/bucket_c_ui_core_tests_scan.md) — F-C-020. And the Codex consult response at `AgentCoordination/Scratchpad/Consult/20260518T174511Z_post-refactor-residue-review-verification/response.md` for sizing context (Codex confirmed the test footprint is materially larger than the original PROJ-443 18-file estimate).

---

## Tasks

### Task 3.0: Pre-flight audit — fresh `rg` count [Simple, MANDATORY before any code change]

- [ ] Run `rg -n "Planet\(.*stockpile=|Planet\(.*max_stockpile=|Planet\(.*staging_yard=" tests/` — count call sites; record in decisions.md as the "Phase 3 pre-flight audit"
- [ ] Run `rg -n "ShipInstance\(.*consumable_levels=|ShipInstance\(.*cargo_contents=" tests/` — count call sites; record
- [ ] Run `rg -n "PlanetaryFacility\(.*consumable_levels=" tests/` — count call sites; record
- [ ] Open `Projects/active_projects/PROJ-443/decisions.md`. Confirm Phase 5b decision is settled — either (a) PROJ-443 owner explicitly delegates wrapper retirement to PROJ-444 here, or (b) PROJ-443 has already shipped a partial migration that informs scope. If neither: STOP and surface to user.
- [ ] Open `Projects/active_projects/PROJ-446/phase_3_checklist.md` (UI shim retirement). Confirm F-C-020 (`tests/fixtures/strategy_entities.py` migration) is either pending OR will land as a stacked dependency to this phase. Communicate via decisions.md before starting.
- [ ] **GATE**: If the combined call-site count is dramatically larger than the original 18-file PROJ-443 estimate (Codex 2026-05-18 advisory says it is), PAUSE and re-scope Phase 3 with the user. Don't barrel into a 200-file sweep without confirmation.

### Task 3.1: F-C-020 (PROJ-446-owned, included here as structural dependency) — Migrate shared fixture [Small]
**File:** `tests/fixtures/strategy_entities.py:140, 318, 320` (`create_test_planetary_facility`, `create_test_ship_instance`); **plus line 421-426** (`create_test_planet(..., stockpile=...)` — Codex 2026-05-18 spot)
**Tests:** Run sharded suite after; many tests across the codebase depend on this fixture.

- [ ] **RED before any edit**: Add a quick-and-dirty smoke test (or just `rg` confirmation) that the suite currently passes WITH the legacy kwargs flowing through the wrappers. This is the baseline RED → after wrapper deletion, this should still pass with the migrated kwargs (effectively, this task is a no-op behavior change; correctness comes from later tasks).
- [ ] Read existing `create_test_planetary_facility` and `create_test_ship_instance` fixture functions
- [ ] Replace `consumable_levels={...}` kwarg with `_consumable_levels={...}` (private spelling) at lines 140, 318, 320
- [ ] Replace `cargo_contents={...}` kwarg with `_cargo_contents={...}` (private spelling)
- [ ] **Don't miss**: `create_test_planet(..., stockpile=...)` at lines 421-426 (Codex r3 verified) — change `stockpile=` to `_stockpile=`. Also check the function for `max_stockpile=` / `staging_yard=` legacy spellings; migrate any found.
- [ ] Run sharded suite to surface any test that constructs `PlanetaryFacility(...)`, `ShipInstance(...)`, OR `Planet(...)` directly with the legacy kwargs (bypassing the fixture)
- [ ] Note the count of newly-failing tests; this is the size of the downstream sweep handled in Task 3.2

### Task 3.2: Sweep direct call sites of legacy kwargs in tests [Medium]
**File:** Various test files revealed by Task 3.1's audit
**Tests:** Iterate the sharded suite

- [ ] **TDD note**: Task 3.2 follows-on from Task 3.1's sharded-suite RED. The "test that fails" is each individual test that breaks after the fixture migration; each migration in this task converts a failing test back to green. Not strict RED-then-GREEN per task, but the aggregate is correct (RED = whole suite broken; GREEN = whole suite green).
- [ ] For each failing test from Task 3.1: change `consumable_levels=` → `_consumable_levels=` (or refactor to use the fixture); change `cargo_contents=` → `_cargo_contents=`; change `stockpile=` → `_stockpile=`; change `max_stockpile=` → `_max_stockpile=`; change `staging_yard=` → `_staging_yard=`
- [ ] Migrate `planet_serde.py:160-162` — `planet_from_dict_kwargs` reconstructs through the wrapper today. Rewrite to construct directly with the private kwargs. **WARNING**: this is the save-load path. Run `pytest tests/integration/save_load/` after the rewrite to catch any save-shape regression before continuing.
- [ ] Run sharded suite to confirm zero remaining call sites use the public legacy kwargs

### Task 3.3: F-A-002 + F-A-004 — Delete _planet_init_with_legacy_kwargs + @property cluster [Simple after Task 3.2]
**File:** `game/strategy/data/planet.py:398-420` (wrapper), `:224-262` (three @property/@setter pairs for `stockpile`, `max_stockpile`, `staging_yard`)

- [ ] Delete the `_planet_init_with_legacy_kwargs` module-level function + the `Planet.__init__ = _planet_init_with_legacy_kwargs` assignment at line 420
- [ ] Delete the three @property/@setter pairs at lines 224-262
- [ ] Confirm `Planet.__init__` is now the dataclass-generated `__init__` taking only the private spellings
- [ ] Run sharded suite. ALL tests must pass — any failure means Task 3.2 missed a call site.

### Task 3.4: F-A-003 + F-A-005 — Delete _ship_instance_init_with_legacy_kwargs + @property cluster [Simple after Task 3.2]
**File:** `game/strategy/data/ship_instance.py:787-833` (wrapper), `:237-262` (@property/@setter pairs for `consumable_levels`, `cargo_contents`)

- [ ] Delete the `_ship_instance_init_with_legacy_kwargs` wrapper + the `ShipInstance.__init__ = _ship_instance_init_with_legacy_kwargs` assignment
- [ ] Delete the two @property/@setter pairs at lines 237-262
- [ ] Run sharded suite. ALL tests must pass.

### Task 3.5: PROJ-446 F-C-014 protocol completion [Simple]
**File:** `game/core/protocols/strategy_domain.py:188` (already narrowed to `Mapping[str, int]` in PROJ-446 Phase 2)
**Tests:** `pytest tests/static_guards/ tests/unit/core/protocols/ -v`

- [ ] Verify the protocol annotation is already `Mapping[str, int]` (PROJ-446 Phase 2 did this)
- [ ] Now that the concrete-class setter is gone (Tasks 3.3-3.4), update the protocol docstring to drop the "**not** read-only in absolute terms" caveat — the surface is now actually read-only
- [ ] Same update for `IFacility.consumable_levels` if the static-guard `test_ifacility_still_declares_consumable_levels` allows (check the guard test in `tests/static_guards/test_no_legacy_protocol_names.py`)

### Task 3.6: F-A-011 — Profile Empire.resource_pool [Small]
**File:** `game/strategy/data/empire.py:229-250`
**Tests:** New profiling test under `tests/perf/` (create if dir doesn't exist) OR a benchmark in `Tools/`

- [ ] Construct a late-game scenario fixture: 200+ colonies, each with non-trivial stockpiles
- [ ] Profile `Empire.resource_pool` access pattern: time N reads, measure walk cost
- [ ] Decision matrix:
  - If <1ms for 1000 reads: leave uncached. Document the finding in decisions.md as "no cache needed pre-N colonies."
  - If ≥1ms for 1000 reads: add cached aggregation with explicit invalidation hooks on `Planet.add_to_stockpile`, `Planet.consume_from_stockpile`, `IPlanetMutator.set_stockpile_amount`, `Empire.add_colony`, `Empire.remove_colony`. Use the PROJ-293 cache pattern as reference.
- [ ] Document the profiling result in decisions.md

---

## Phase Completion Checklist

- [ ] All 7 task groups complete (Task 3.0 audit + Tasks 3.1-3.6)
- [ ] Both wrappers (`_planet_init_with_legacy_kwargs`, `_ship_instance_init_with_legacy_kwargs`) deleted from the codebase
- [ ] All @property/@setter shim clusters (Planet stockpile/max_stockpile/staging_yard, ShipInstance consumable_levels/cargo_contents) deleted
- [ ] `tests/fixtures/strategy_entities.py` migrated to private kwargs
- [ ] `planet_serde.py:160-162` rewritten
- [ ] `Empire.resource_pool` profiling result recorded in decisions.md
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-444 3` — PASSED
- [ ] PROJ-446 F-C-020 marked `Complete` in PROJ-446's phase_3_checklist.md
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 4
- [ ] PROJ-443 Phase 5b marker updated in PROJ-443's plan.md (wrapper retirement is no longer deferred)
- [ ] Any new findings discovered during the sweep are logged to `discovered_issues/log.jsonl`

## Risks / Mitigations

- **Risk: sweep is larger than expected.** Codex 2026-05-18 indicates the real test footprint exceeds PROJ-443's original 18-file estimate. Task 3.0 pre-flight audit catches this; the explicit GATE step pauses if the count is dramatic.
- **Risk: PROJ-446 agent is mid-phase touching `tests/fixtures/`.** Coordinate via decisions.md before starting. The agent for this phase should claim `tests/fixtures/strategy_entities.py` for the duration of the phase.
- **Risk: save-load tests break.** `planet_serde.py:160-162` rewrite needs explicit testing. Run `pytest tests/integration/save_load/` separately as a smoke check after Task 3.2.
