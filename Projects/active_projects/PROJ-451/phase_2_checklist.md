# Phase 2: GREEN — emit RESOURCE_SHORTAGE when affordability passes but consumption charges 0

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-451 2`
> 2. Phase 1 RED tests now GREEN
> 3. Sharded suite green
> 4. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1 (RED tests in place)
**Objective:** Close DI-006 on BOTH sides:
1. **Data-side gate symmetry (NEW Task 2.0, codex r5 review)**: round the consume-side gate in `Fleet.consume_cargo_resource` at `fleet.py:285` so it matches `has_cargo_resources` (currently asymmetric — see plan.md scope note).
2. **Engine-side detection (Tasks 2.1+)**: in `_apply_resource_consumption`, when `amount > 0` was requested but `actually_consumed == 0` (computed from the existing `production_get_resource` before/after diff), route to the existing `_log_resource_shortage` path. Make the Phase 1 RED tests turn GREEN.
3. **Module docstring polish (NEW Task 2.5, codex r5 NEW-2)**: update `production_engine.py:10-16` to drop the stale "empire pool" framing.

**File ownership rule:** This project owns `production_engine.py` and `fleet.py:271-288` (`consume_cargo_resource`). Phase 2 touches only those files plus the validation Phase 1 tests (un-xfail them) plus a new symmetry-ratchet test.

**Source-of-truth findings:** DI-2026-05-18-006 (data half partially-resolved + engine UX gap half) — see [findings/PROJ-451_findings.md](findings/PROJ-451_findings.md). NEW codex r5 findings folded in below.

---

## Tasks

### Task 2.0: GREEN — round `Fleet.consume_cargo_resource` gate to match `has_cargo_resources` (codex r5 — closes DI-006 data half) [Simple]
**File:** `game/strategy/data/fleet.py:285`
**Tests:** `pytest tests/unit/strategy/data/test_fleet.py tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py -n 4 -v`

- [x] Read current `Fleet.consume_cargo_resource` body at `fleet.py:271-288`. Note line 285: `if total < amount:` compares total (integer) against RAW float `amount`.
- [x] Note that line 287 already rounds: `self._resource_agg.unload_cargo_from_fleet(resource_type, int(round(amount)))`. The gate vs unload disagree.
- [x] **RED**: Add `tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py` with:
  ```python
  def test_consume_and_has_agree_on_rounded_to_zero():
      # cargo=0, request=0.5 → both must return False (rounded gate)
      fleet = _make_fleet_with_cargo({"metals": 0})
      assert fleet.has_cargo_resources({"metals": 0.5}) is False
      assert fleet.consume_cargo_resource("metals", 0.5) is False

  def test_consume_and_has_agree_on_rounded_to_one():
      # cargo=1, request=0.5 → both must return True; consume actually unloads 0
      fleet = _make_fleet_with_cargo({"metals": 1})
      assert fleet.has_cargo_resources({"metals": 0.5}) is True
      assert fleet.consume_cargo_resource("metals", 0.5) is True
      assert fleet.get_cargo_resource("metals") == 1.0  # rounded-to-zero unload
  ```
  First test must initially FAIL (consume returns False today on `cargo=0 / amount=0.5`, matching codex's reproduction; but has returns True ⇒ asymmetry). Actually re-verify: with cargo=0, has returns True (`0 < int(round(0.5))=0` is False); consume returns False (`0 < 0.5` is True). The test asserts both are False AFTER the fix.
- [x] **GREEN**: Change line 285 from `if total < amount:` to `if total < int(round(amount)):`. Mirror `has_cargo_resources` exactly. Add a comment cross-referencing DI-2026-05-18-006 + codex r5 review.
- [x] Re-run the symmetry test — both tests pass.
- [x] Re-run existing `tests/unit/strategy/data/test_fleet.py` — must remain green (the test_fleet suite should already cover the cargo>=1 case; the fix only changes behavior for cargo<rounded-amount).
- [x] Cross-reference in `decisions.md`: this completes PROJ-444 Phase 2 Option B (which rounded only `has_cargo_resources`). After this task, both methods agree.

### Task 2.1: GREEN — implement zero-consume detection in `_apply_resource_consumption` [Medium]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/integration/test_production_engine_fractional_fleet_cost.py tests/unit/strategy/engine/test_production_engine_consumption.py -n 4 -v`

- [x] Locate `_apply_resource_consumption` at lines 649-687. Current body (lines 677-686):
  ```python
  for res, amount in cost_this_step.items():
      if amount > 0:
          before = colony_or_fleet.production_get_resource(res)
          colony_or_fleet.production_consume_resource(res, amount)
          after = colony_or_fleet.production_get_resource(res)
          actually_consumed = before - after
          item['resources_consumed'][res] = (
              item.get('resources_consumed', {}).get(res, 0.0)
              + actually_consumed
          )
  ```
- [x] Add zero-consume detection. The new shape needs to also accept `empire` to pass to `_log_resource_shortage`:
  ```python
  zero_consume_detected = False
  for res, amount in cost_this_step.items():
      if amount > 0:
          before = colony_or_fleet.production_get_resource(res)
          colony_or_fleet.production_consume_resource(res, amount)
          after = colony_or_fleet.production_get_resource(res)
          actually_consumed = before - after
          item['resources_consumed'][res] = (
              item.get('resources_consumed', {}).get(res, 0.0)
              + actually_consumed
          )
          if actually_consumed == 0:
              zero_consume_detected = True

  # DI-2026-05-18-006 closure: emit RESOURCE_SHORTAGE when affordability
  # passed but consumption actually charged 0 (rounded-to-zero against
  # integer cargo store). The shortage indicates the queue cannot make
  # progress at this fractional cost; player needs the signal.
  if zero_consume_detected and not item.get('_shortage_logged'):
      self._log_resource_shortage(empire, item, cost_this_step, colony_or_fleet)
      item['_shortage_logged'] = True
  ```
- [x] Run focused tests; both Phase 1 RED tests should now pass

### Task 2.2: Un-xfail the Phase 1 RED tests [Simple]
**Files:** `tests/integration/test_production_engine_fractional_fleet_cost.py`, `tests/unit/strategy/engine/test_production_engine_consumption.py`
**Tests:** `pytest tests/integration/test_production_engine_fractional_fleet_cost.py tests/unit/strategy/engine/test_production_engine_consumption.py -v`

- [x] Remove `@pytest.mark.xfail(reason="PROJ-451 Phase 1 RED — fixed by Phase 2")` from both tests added in Phase 1
- [x] Run focused tests; both should now GREEN unconditionally

### Task 2.3: Verify `_log_resource_shortage` payload includes the cause [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** verify in Task 2.1's tests

- [x] The existing `_log_resource_shortage` (lines 588-647) computes the "limiting resource" by looking for the largest shortfall ratio. For the rounded-to-zero case, the limiting resource is the one whose requested amount > 0 but rounded amount == 0
- [x] Verify the existing shortage-finding logic handles this case correctly. If the resource has `available == requested` (which would happen with the post-PROJ-444 Phase 2 `Fleet.has_cargo_resources` returning True for `amount=0.1` against `cargo=1` after rounding), the existing logic may not flag it as "limiting" — verify by reading the logic at lines 605-624 and tracing through
- [x] If the existing logic does NOT correctly identify the rounded-to-zero case as the bottleneck, augment it OR add an explicit cause field to the event when zero_consume_detected is true:
  ```python
  if zero_consume_detected and not item.get('_shortage_logged'):
      # Custom cause for the rounded-to-zero stall
      if self._event_bus:
          self._event_bus.log_event(
              EventType.RESOURCE_SHORTAGE,
              category=EventCategory.PRODUCTION,
              empire_id=empire.id,
              message=f"Production stalled: fractional cost rounds to zero against integer cargo for {item.get('design_id', 'unknown')}",
              design_id=item.get('design_id', 'unknown'),
              vehicle_type=item.get('type', 'ship'),
              limiting_resource=next(iter(cost_this_step), ""),
              cause="rounded_to_zero",
              location_hex=...,
          )
      item['_shortage_logged'] = True
  ```
- [x] Decide between (a) re-using `_log_resource_shortage` with augmented cause detection inside it, or (b) a sibling emit path for the rounded-to-zero case. Either works; (b) is cleaner and easier to test.

### Task 2.4: Sharded suite + commit [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Sharded suite green
- [x] Phase 1 RED tests now GREEN (no xfail markers)
- [x] Symmetry-ratchet test (Task 2.0) green
- [x] Commit message: `PROJ-451 Phase 2 GREEN: close DI-006 data-side gate asymmetry + emit RESOURCE_SHORTAGE on zero-consume despite affordability`

### Task 2.5: Update production_engine.py module docstring (codex r5 NEW-2) [Simple]
**File:** `game/strategy/engine/production_engine.py:10-16`

- [x] Read current docstring at `:10-16`. It still references "construction consumes from the empire pool" — pre-PROJ-436 framing.
- [x] Replace with current-state description: "Construction reads inputs and writes outputs through `IProductionResourceSource` (see Protocol contract at :60-95). Planet and Fleet are the two production implementers."
- [x] No test change required; this is a docstring polish.

---

## Phase Completion Checklist
- [x] `_apply_resource_consumption` detects `actually_consumed == 0` despite `amount > 0`
- [x] On detection, RESOURCE_SHORTAGE event emitted with cause indicating fractional / rounded-to-zero stall
- [x] Phase 1 RED tests are GREEN unconditionally (no xfail markers)
- [x] Existing tests still green (no regression in the shortage-emit path)
- [x] Sharded suite green
- [x] DI-2026-05-18-006 engine UX gap closed
- [x] Plan.md Quick Status → Complete; Current State updated

## Notes / Risks / Coordination Touchpoints
- **`_shortage_logged` flag**: the existing path at `_process_queue_tick_dynamic:424-428` sets `item['_shortage_logged'] = True` after `_log_resource_shortage`. The Phase 2 path must respect that flag to avoid duplicate emits within a single turn.
- **Event_bus may be None**: production code paths sometimes run without an event bus (tests, headless contexts). The new emit guard `if self._event_bus:` must be present.
- **Edge case: queue item is not a dict.** `_process_queue_tick_dynamic:371-374` already guards `isinstance(q_item, dict)` for the shortage-flag reset; same guard should be applied to the new emit-flag-write.
- **PROJ-449 / PROJ-450 unaffected.**
