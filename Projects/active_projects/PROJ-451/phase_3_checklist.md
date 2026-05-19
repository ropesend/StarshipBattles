# Phase 3: Decide — `_apply_resource_consumption` bool-return handling

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-451 3`
> 2. Decision recorded in `decisions.md`
> 3. Implementation matches chosen option; sharded suite green
> 4. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_2 (zero-consume detection in place)
**Objective:** Decide between option (a) "defensive bool capture + tick_capacity skip" and option (b) "strict Protocol contract hard-assert" for DI-007 closure. Codex r4 recommends (b) as cheaper; CLAUDE.md "Capability validation is hard, not soft" supports (b) on principle. Either option closes DI-007.

**File ownership rule:** This project owns `production_engine.py` end-to-end for the bool-return handling. Phase 3 either adds a bool-capture path (option a) or a hard assertion (option b). Decision recorded in `decisions.md`.

**Source-of-truth findings:** DI-2026-05-18-007 (engine bool-return), F-B-019 (Protocol contract) — see [findings/PROJ-451_findings.md](findings/PROJ-451_findings.md).

---

## Tasks

### Task 3.1: Decide between option (a) and option (b) [Simple]
**File:** `Projects/active_projects/PROJ-451/decisions.md`

- [ ] Review the two options:
  - **(a) Defensive**: capture `production_consume_resource` return in `_apply_resource_consumption`; signal back to `_process_queue_tick_dynamic` so it can skip the `tick_capacity` decrement when consume returned False. Preserves capacity for retry. Adds plumbing complexity.
  - **(b) Strict assertion**: add `assert colony_or_fleet.production_consume_resource(res, amount), f"Contract breach: ..."` in `_apply_resource_consumption`. Failure is a programmer error. Tighten Protocol contract docstring at `:60-95` to make the affordability/consumption symmetry MUST-language explicit.
- [ ] Per Codex r4: "(b) is cheaper; (a) is more defensive against future implementers." Also: "CLAUDE.md 'Capability validation is hard, not soft' supports this." → option (b) is the recommended default.
- [ ] User may override; if no override, default to (b).
- [ ] Record the decision in `decisions.md` with rationale (date 2026-05-19+).

### Task 3.2A — IF OPTION (A): defensive bool capture + tick_capacity skip [Complex]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `tests/unit/strategy/engine/test_production_engine_consumption.py` (extend)

> SKIP this task if option (b) was chosen.

- [ ] RED — add a failing unit test:
  ```python
  def test_apply_resource_consumption_skips_tick_capacity_on_false_consume():
      """Option (a): when production_consume_resource returns False
      after affordability passed, _apply_resource_consumption signals
      back via return value; _process_queue_tick_dynamic skips the
      tick_capacity decrement.
      """
      mock_source = Mock(spec=IProductionResourceSource)
      mock_source.production_has_resources.return_value = True
      mock_source.production_get_resource.side_effect = [1.0, 1.0]  # no change
      mock_source.production_consume_resource.return_value = False  # contract breach
      result = engine._apply_resource_consumption(empire, item, {'metals': 0.1}, mock_source)
      assert result is False  # signal back to caller
  ```
- [ ] GREEN — change `_apply_resource_consumption` signature to return `bool` (False if any consume returned False; True otherwise)
- [ ] GREEN — update `_process_queue_tick_dynamic:432` call site to capture the return and skip `tick_capacity -= expenditure.ticks_to_spend` if False
- [ ] Update DI-007's resolution_note via `decisions.md` row

### Task 3.2B — IF OPTION (B): strict assertion + Protocol contract docstring [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `tests/unit/strategy/engine/test_production_engine_consumption.py` (extend)

> SKIP this task if option (a) was chosen.

- [ ] RED — add a failing unit test:
  ```python
  def test_apply_resource_consumption_raises_on_contract_breach():
      """Option (b): when production_consume_resource returns False
      after affordability passed, _apply_resource_consumption raises
      AssertionError (or ValueError). Failure is a programmer error.
      """
      mock_source = Mock(spec=IProductionResourceSource)
      mock_source.production_has_resources.return_value = True
      mock_source.production_get_resource.return_value = 1.0
      mock_source.production_consume_resource.return_value = False  # contract breach
      mock_source.location = HexCoord(0, 0)
      with pytest.raises(AssertionError, match="Contract breach"):
          engine._apply_resource_consumption(empire, item, {'metals': 0.1}, mock_source)
  ```
- [ ] GREEN — modify `_apply_resource_consumption` body:
  ```python
  for res, amount in cost_this_step.items():
      if amount > 0:
          before = colony_or_fleet.production_get_resource(res)
          consume_succeeded = colony_or_fleet.production_consume_resource(res, amount)
          # DI-2026-05-18-007 closure: the Protocol contract MUST guarantee
          # consume succeeds when affordability passed. Failure is a
          # programmer error in the implementer, not a runtime degradation.
          assert consume_succeeded, (
              f"Contract breach: production_consume_resource({res!r}, {amount}) "
              f"returned False on {type(colony_or_fleet).__name__} but "
              f"production_has_resources passed earlier in this tick."
          )
          after = colony_or_fleet.production_get_resource(res)
          # ... rest of the loop
  ```
- [ ] Verify Protocol contract docstring at `production_engine.py:60-95` carries MUST-language (verified at HEAD 2026-05-19; if any weakening, restore the MUST). Suggested doc text addition if missing:
  ```python
  """
  Affordability/consumption symmetry contract (PROJ-445 Phase 2,
  DI-2026-05-18-006/007): an implementation MUST return ``True``
  whenever :meth:`production_has_resources` returned ``True`` for the
  same ``(resource_type, amount)`` in the same engine tick. ...
  """
  ```
- [ ] Run the new test; verify it passes (the engine now raises)

### Task 3.3: Sharded suite + commit [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Sharded suite green
- [ ] Commit message: `PROJ-451 Phase 3: $option — close DI-2026-05-18-007 + F-B-019 (engine enforces affordability→consumption symmetry contract)`. Replace `$option` with `option-A-defensive-capture` or `option-B-strict-assertion` per the Task 3.1 decision.

---

## Phase Completion Checklist
- [ ] Decision recorded in `decisions.md` (option a or b)
- [ ] Implementation matches chosen option
- [ ] New unit test exercises the contract-breach path
- [ ] Sharded suite green
- [ ] DI-2026-05-18-007 closed (either option)
- [ ] F-B-019 closed (Protocol contract MUST-language landed; engine enforces)
- [ ] Plan.md Quick Status → Complete; Current State updated

## Notes / Risks / Coordination Touchpoints
- **Default: option (b).** Codex r4 + CLAUDE.md "Capability validation is hard, not soft" both support strict assertion. Soft degradation paths hide contract bugs from implementers. Choose (a) only if a concrete future implementer expects to legitimately fail consume after passing affordability (no such implementer exists today; speculative implementers shouldn't drive the decision).
- **Risk in option (a)**: the bool plumbing creates a new code path in `_process_queue_tick_dynamic` that needs its own test coverage. The defensive path also reduces the engine's ability to detect implementer bugs (False return is silently absorbed).
- **Risk in option (b)**: the assertion fires production-side if a future implementer has a bug. CLAUDE.md tradition: surfacing bugs is better than hiding them. Fail-fast is the project convention.
- **Phase 4 ratchet tests reinforce option (b).** Adding ratchet tests for every implementer means the contract is verified at the implementer level — the engine's assertion is then a defense-in-depth, not the primary enforcement.
- **PROJ-449 / PROJ-450 unaffected.**
