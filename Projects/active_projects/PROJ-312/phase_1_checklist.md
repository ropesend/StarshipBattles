# Phase 1: Determinism Baseline

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-312 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate the last unseeded RNG consumers in the battle/AI hot
path so replay determinism is bulletproof, then add a regression guard
preventing future drift. This phase ships before any replay capture code is
written — Phase 2+ depends on the contract this phase establishes.

---

## Tasks

### Task 1.1: Thread seeded RNG through `ErraticBehavior` [Medium]
**File:** `game/ai/behaviors.py`
**Tests:** `pytest tests/unit/ai/ -k erratic`

The four unseeded `random.*` calls at lines 330-331 and 370-371 must consume
the engine's seeded `Random` instance instead of the module-level `random`.

- [ ] Add a `rng: random.Random` parameter to `ErraticBehavior.__init__()`.
      Store as `self._rng`. No default — callers must pass an RNG.
- [ ] Replace `random.choice([-1, 1])` at line 330 with `self._rng.choice([-1, 1])`.
- [ ] Replace `random.uniform(AIConfig.ERRATIC_TURN_INTERVAL_MIN, AIConfig.ERRATIC_TURN_INTERVAL_MAX)`
      at line 331 with `self._rng.uniform(...)`.
- [ ] Replace `random.choice([-1, 0, 1])` at line 370 with `self._rng.choice([-1, 0, 1])`.
- [ ] Replace `random.uniform(min_interval, max_interval)` at line 371 with `self._rng.uniform(...)`.
- [ ] Verify no other `random.*` calls remain in `game/ai/behaviors.py`.
- [ ] Update any other behavior class that takes RNG-shaped inputs for symmetry
      (audit other `AIBehavior` subclasses; if none, document so).

**Notes:** [Filled during implementation]

### Task 1.2: Wire RNG through the AI controller / factory [Medium]
**File:** `game/ai/controller.py`, `game/ai/ai_factory.py`
**Tests:** `pytest tests/unit/ai/`

The engine's `random.Random` instance must reach `ErraticBehavior` via the
controller construction path.

- [ ] Identify how `AIController` is built today (likely
      `AIControllerFactory.create_controller(...)` in `game/ai/ai_factory.py`).
- [ ] Add an `rng` parameter to the factory's create method (or its callers).
      Default policy: when missing, **raise** — no silent fallback to
      module-level `random`. (Battle replay determinism is non-negotiable.)
- [ ] Trace the construction call sites and ensure `engine.rng` is passed in.
      Likely call site: `BattleEngine._initialize_start_state` or wherever AI
      controllers are minted per-ship.
- [ ] When the controller selects an `ErraticBehavior`, pass `rng` to it.
- [ ] Audit all other `AIBehavior` subclasses (Kite, AttackRun, Ram, Flee,
      Orbit, StationaryFire, DoNothing, StraightLine, RotateOnly + base) for
      any module-level `random.*` calls. Fix any found with the same pattern.

**Notes:** [Filled during implementation]

### Task 1.3: Add AST guard test against unseeded `random.*` in battle/AI layer [Simple]
**File:** `tests/unit/quality/test_no_unseeded_random.py` (new)
**Tests:** `pytest tests/unit/quality/test_no_unseeded_random.py`

Prevent regressions where a future change reintroduces module-level
`random.*` calls in the simulation hot path.

- [ ] Write a test that walks the AST of every `.py` file under
      `game/simulation/`, `game/engine/`, and `game/ai/`.
- [ ] Flag any `Call` node whose target is `random.<X>` (e.g.,
      `random.random`, `random.choice`, `random.uniform`, `random.randint`,
      `random.gauss`, `random.shuffle`, `random.sample`, `random.choices`).
- [ ] Allow `random.Random(...)` constructor calls (these are seeded
      instances, fine).
- [ ] Allowlist explicit `# noqa: replay-determinism` markers for any
      genuinely-justified module-level use (none expected today; the marker
      exists for future flexibility).
- [ ] Test FAILS if any non-allowlisted `random.*` call is found, with a clear
      error message naming file:line and the recommended fix
      ("inject `rng: random.Random` via DI").

**Notes:** [Filled during implementation]

### Task 1.4: Extend battle determinism harness with state-hash regression [Simple]
**File:** `tests/integration/fleet_combat/test_battle_determinism.py`
**Tests:** `pytest tests/integration/fleet_combat/test_battle_determinism.py`

The existing harness asserts winner + tick_count + survivors match across
seeded re-runs. Extend with a stronger fingerprint.

- [ ] Add `test_seeded_battle_outcome_state_hash()`: run a known seeded
      battle, hash the full `BattleOutcome` (use a stable serialization —
      sort tuples, use `json.dumps(..., sort_keys=True)` or similar), assert
      the hash is bit-stable across two runs in the same process.
- [ ] Add a second test that runs the same seeded battle in two
      *separate* fresh registries (no shared module state) and asserts the
      same hash. Catches any latent module-level state contamination.
- [ ] Use `seed=42`, a small 2-team scenario built via `make_minimal_spec`
      from `tests/fixtures/battle.py`. Keep runtime under 1 second.
- [ ] Run the test 10 times in a loop within a single `test_*` to surface
      flakiness early.

**Notes:** [Filled during implementation]

### Task 1.5: Verify ErraticBehavior determinism end-to-end [Simple]
**File:** `tests/unit/ai/test_erratic_behavior_seeded.py` (new)
**Tests:** `pytest tests/unit/ai/test_erratic_behavior_seeded.py`

- [ ] Construct an `ErraticBehavior` with `rng = random.Random(42)`.
- [ ] Call its update path 100 times against a mocked ship; record the resulting
      direction-change events / interval choices.
- [ ] Repeat with a fresh `rng = random.Random(42)`. Assert the recorded
      sequences are identical.
- [ ] Repeat with `rng = random.Random(43)`. Assert the sequence differs from
      the seed=42 run (sanity that the seed actually steers behavior).

**Notes:** [Filled during implementation]

### Task 1.6: Document the Per-Battle RNG pattern coverage [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** Manual review — no executable tests.

- [ ] Section #18 (Per-Battle RNG) currently lists `BattleEngine.rng`,
      `CollisionSystem.rng`, `DamageCalculator.rng`,
      `ConflictResolutionEngine._rng`. Add `ErraticBehavior` (and any other
      behavior fixed in 1.2) to the "Where" list.
- [ ] Add a sentence under "When to Use" referencing the AST guard
      (Task 1.3) as the regression contract.
- [ ] Update the doc's `> **Last verified:**` blockquote to today's date with
      a one-sentence summary mentioning PROJ-312 Phase 1.

**Notes:** [Filled during implementation]

### Task 1.7: Phase 1 sharded suite verification [Simple]
**File:** N/A (test execution)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full sharded suite passes: target ≥15672 tests passed (baseline + new
      Phase 1 tests), 0 failed, 0 errors.
- [ ] Record final test count in plan.md "Current State Snapshot" for
      future phases to compare against.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] AST guard (Task 1.3) is green and visible in CI
- [ ] Determinism harness (Task 1.4) passes 10/10 in a loop
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 (`phase_2_checklist.md`
      already exists — no need to create)
