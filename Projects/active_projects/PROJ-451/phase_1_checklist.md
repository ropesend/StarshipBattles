# Phase 1: RED — write the rounded-to-zero stall reproduction tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-451 1`
> 2. Both new tests FAIL (this is RED — Phase 2 implements GREEN)
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Write failing tests that reproduce:
1. The DI-006 engine-side UX gap (Fleet build with fractional per-step cost rounding to 0; queue stalls without a RESOURCE_SHORTAGE event).
2. The DI-006 unit-test analog: `_apply_resource_consumption` zero-consume / no-diff detection — `production_consume_resource.return_value = True` but `production_get_resource` reports constant pre/post values so `actually_consumed == 0`. (Task 1.2.)

**Scope note (2026-05-19 codex audit fix):** Phase 1 reproduces the DI-006 *rounded-to-zero stall path*. DI-007 proper — the bool-return-false path where `production_consume_resource` returns False after affordability returned True — is deferred to **Phase 3 Task 3.X** (the bool-return-handling decision). The unit test at Task 1.2 covers only the "consume runs successfully but contributes nothing" sub-case (production_consume_resource still returns True), not the contract-breach case.

**File ownership rule:** This project owns engine-side production tests + production engine modifications. Phase 1 touches only test files. No production code changes.

**Source-of-truth findings:** DI-2026-05-18-006 + DI-2026-05-18-007 — see [findings/PROJ-451_findings.md](findings/PROJ-451_findings.md).

---

## Tasks

### Task 1.1: RED — integration test for the fractional-cost stall [Medium]
**File:** `tests/integration/test_production_engine_fractional_fleet_cost.py` (extend existing)
**Tests:** `pytest tests/integration/test_production_engine_fractional_fleet_cost.py -k test_fractional_cost_rounds_to_zero_emits_resource_shortage -v`

- [ ] Add test:
  ```python
  def test_fractional_cost_rounds_to_zero_emits_resource_shortage(
      session_registries, ...
  ):
      """PROJ-451 Phase 1 RED: DI-2026-05-18-006 engine-side UX gap.

      When Fleet construction has a fractional per-step cost that
      rounds to 0 against the integer cargo store, the queue stalls
      AND a RESOURCE_SHORTAGE event must be emitted. Pre-fix: the
      affordability check passes vacuously (Fleet.has_cargo_resources
      rounds to int(round(0.1)) = 0, which is ≤ stored amount), the
      engine consumes 0, tick_capacity decrements, queue stalls
      without emitting shortage.
      """
      # Setup: empire with one fleet, cargo = {"metals": 1} (integer)
      # Queue: one build item with cost_per_tick = {"metals": 0.1}
      # Expected: after _process_queue_tick_dynamic for tick 1:
      #   - turns_remaining unchanged (no progress)
      #   - RESOURCE_SHORTAGE event emitted with empire_id, design_id,
      #     limiting_resource="metals", cause indicating "amount
      #     rounded to zero against integer cargo store"
      assert resource_shortage_event_was_emitted(event_log, empire.id, "metals")
  ```
- [ ] Fixture setup: use `tests/fixtures/strategy_entities.py` helpers to build a minimal empire + fleet + cargo state
- [ ] Run; verify RED — the test fails because no RESOURCE_SHORTAGE event is emitted today

**Notes:** Check `tests/integration/test_production_engine_fractional_fleet_cost.py` for existing fixture patterns. If a similar test exists, mirror its setup.

### Task 1.2: RED — unit test for `_apply_resource_consumption` zero-consume detection [Medium]
**File:** `tests/unit/strategy/engine/test_production_engine_consumption.py` (extend existing)
**Tests:** `pytest tests/unit/strategy/engine/test_production_engine_consumption.py -k test_apply_resource_consumption_emits_shortage_on_zero_consume -v`

**Scope:** This test exercises the DI-006 unit-test analog (zero-consume / no-diff path), NOT the DI-007 bool-return-false contract-breach path. DI-007 is deferred to Phase 3 Task 3.X (the bool-return-handling decision).

- [ ] Add test:
  ```python
  def test_apply_resource_consumption_emits_shortage_on_zero_consume(
      mock_event_bus, ...
  ):
      """PROJ-451 Phase 1 RED: when actually_consumed == 0 despite
      amount > 0 being requested, the engine must emit a
      RESOURCE_SHORTAGE event (currently does not).

      Setup a mock IProductionResourceSource where:
        production_has_resources({'metals': 0.1}) → True
        production_get_resource('metals') → 1.0 (constant, no consume)
        production_consume_resource('metals', 0.1) → True (returns True but doesn't actually deduct)

      Call ProductionEngine._apply_resource_consumption(...);
      expect the engine to detect actually_consumed == 0 and emit
      a RESOURCE_SHORTAGE event.
      """
      mock_source = Mock(spec=IProductionResourceSource)
      mock_source.production_has_resources.return_value = True
      mock_source.production_get_resource.return_value = 1.0
      mock_source.production_consume_resource.return_value = True
      mock_source.location = HexCoord(0, 0)

      item = {'design_id': 'x', 'type': 'ship', 'resources_consumed': {}}
      engine._apply_resource_consumption(empire, item, {'metals': 0.1}, mock_source)

      # Currently FAILS: no shortage event emitted
      assert any(e.event_type == EventType.RESOURCE_SHORTAGE for e in mock_event_bus.events)
  ```
- [ ] Run; verify RED

### Task 1.3: Verify both tests RED (without xfail), then add xfail and commit [Simple]
**Tests:** `pytest tests/integration/test_production_engine_fractional_fleet_cost.py tests/unit/strategy/engine/test_production_engine_consumption.py -k "test_fractional_cost_rounds_to_zero_emits_resource_shortage or test_apply_resource_consumption_emits_shortage_on_zero_consume" -v`

**Sequencing (2026-05-19 codex audit fix):** TDD discipline requires that the RED state is proven before xfail masks it. Follow these steps in order:

- [ ] **Step 1 — Targeted raw RED run.** Run the focused pytest invocation above WITHOUT any xfail markers on either test. Confirm BOTH tests fail (this is the literal RED proof; without this step, an xfail-on-passing-test could silently hide an already-green contract).
- [ ] **Step 2 — Add xfail markers.** Once RED is proven, add `@pytest.mark.xfail(reason="PROJ-451 Phase 1 RED — fixed by Phase 2")` to both tests. This is the standard pattern for committing failing tests on `main` while keeping the sharded suite green.
- [ ] **Step 3 — Targeted xfail run.** Re-run the focused pytest; both tests now show `xfailed`.
- [ ] **Step 4 — Sharded suite green.** Run sharded; the suite passes at +2 xfail-passing tests.
- [ ] **Step 5 — Commit.** Commit message: `PROJ-451 Phase 1 RED: reproduction tests for DI-006 engine UX gap + zero-consume detection (xfail-marked; Phase 2 GREEN removes markers)`. The commit captures both the raw-failing test bodies AND the xfail markers; the targeted-raw-RED step is recorded in the commit message body for the audit trail.

**Rationale:** xfail is for tests that are *expected to fail today and will fix in a known future commit*. The "expected" part is only credible if the unmarked test was demonstrated failing first. Committing xfail-from-the-start risks shipping a green test masquerading as RED (e.g. if test setup is wrong and the assertion never gets reached).

---

## Phase Completion Checklist
- [ ] `test_fractional_cost_rounds_to_zero_emits_resource_shortage` exists and is RED (`xfail` preferred)
- [ ] `test_apply_resource_consumption_emits_shortage_on_zero_consume` exists and is RED (`xfail` preferred)
- [ ] Sharded suite green (with the 2 new tests as `xfail`-passing)
- [ ] Plan.md Quick Status → Complete; Current State updated → ready for Phase 2 GREEN

## Notes / Risks / Coordination Touchpoints
- **`xfail` preferred over `skip` for RED tests.** It expresses "this is expected to fail today; GREEN comes in Phase 2." Sharded suite stays green because xfail is not a failure.
- **No production changes in Phase 1.** TDD discipline: confirm RED before any GREEN code touches production.
- **The integration test fixture is the bigger work.** Building a minimal empire + fleet + cargo state through `tests/fixtures/strategy_entities.py` may require ~30-50 LOC of fixture setup. Reuse existing helpers where possible.
- **PROJ-449 / PROJ-450 unaffected.** Engine internals are orthogonal to wrapper retirement or staging-yard substrate work.
