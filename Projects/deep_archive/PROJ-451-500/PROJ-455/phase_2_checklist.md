# PROJ-455 Phase 2: Parametrised end-to-end test across 5 FMS order types

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-455 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extend the Phase-1 smoke test into a parametrised end-to-end test covering all 5 entries in `order_metadata.planet_fms_action_order_types`. Add a registry-view guard test so the parametrise list can't drift from the canonical FMS handler set.

**Cross-bucket file-ownership rule:** Same as Phase 1 — touches only `tests/integration/test_process_planet_action_tick_end_to_end.py`. No production code touched.

**Source-of-truth findings:** [`findings/PROJ-455_findings.md`](findings/PROJ-455_findings.md) — read the "Context: what archived PROJ-445 Phase 1 closed (and what it did NOT close)" section. PROJ-455 Phase 2's assertion set must cover the gaps that PROJ-445 Phase 1's direct-call test bypassed.

---

## Tasks

### Task 2.1: Add `test_process_planet_action_tick_end_to_end` parametrised across all 5 FMS order types [Medium]
**File:** `tests/integration/test_process_planet_action_tick_end_to_end.py`
**Tests:** `pytest tests/integration/test_process_planet_action_tick_end_to_end.py::test_process_planet_action_tick_end_to_end -v`

- [x] Add the parametrised test (adapt the structure from `test_fms_planet_lay_mines.py:230-277`, but call `process_action_ticks` instead of `_execute_planet_action`):
  ```python
  @pytest.mark.parametrize(
      "order_type",
      [
          OrderType.LAY_MINES,
          OrderType.LAUNCH_FIGHTERS,
          OrderType.LAUNCH_SATELLITES,
          OrderType.RECOVER_FIGHTERS,
          OrderType.RECOVER_SATELLITES,
      ],
  )
  def test_process_planet_action_tick_end_to_end(
      engine_and_processor, order_type: OrderType
  ) -> None:
      """Every planet-FMS order type must dispatch cleanly through the
      full engine entry point ``ActionExecutionEngine.process_action_ticks``.
  
      This is the engine-mediated counterpart of
      ``tests/integration/test_fms_planet_lay_mines.py`` (which drives
      ``_execute_planet_action`` directly). PROJ-455 closes the
      ActionExecutionEngine half of DI-2026-05-18-001 by exercising
      ``_process_planet_action_tick``'s order-progression and
      action-time-resolution logic that the precedent bypassed.
      """
      engine, _processor = engine_and_processor
  
      hex_c = HexCoord(0, 0)
      planet = _StubPlanet(planet_id=42, owner_id=7, location=hex_c)
      empire = SimpleNamespace(
          id=7,
          name="E",
          fleets=[],
          colonies=[planet],
          deployed_groups=[],
      )
      empire.deployed_groups_of = lambda cls, _e=empire: [
          g for g in _e.deployed_groups if isinstance(g, cls)
      ]
  
      _SCENARIO_BUILDERS[order_type](planet, empire)
      assert planet.get_current_order() is not None
      assert planet.get_current_order().type is order_type
  
      # Drive the FULL engine entry point, not _execute_planet_action.
      results = engine.process_action_ticks(
          empires=[empire],
          galaxy=None,
          tick=1,
          component_registry=None,
      )
  
      # ----- Assert: ActionTickResult shape -----
      assert len(results) == 1, (
          f"Expected exactly one ActionTickResult for the planet's "
          f"{order_type.name} order; got {len(results)}."
      )
      result = results[0]
      assert result.order_type is order_type
      assert result.action_completed is True, (
          f"With _FixedActionTimeResolver(1), tick 1 should complete the "
          f"{order_type.name} action; got action_completed={result.action_completed}."
      )
      assert result.fleet_consumed is False, (
          "Planets are never consumed by an action; only fleet-issuer paths set fleet_consumed=True."
      )
  
      # ----- Assert: order queue advanced (handler reached and popped) -----
      assert planet.get_current_order() is None, (
          f"Planet order queue should advance after the engine-mediated "
          f"{order_type.name} dispatch — handler may have raised before "
          f"reaching pop_order(), or returned without popping."
      )
  
      # ----- Assert: deployed-group / staging-yard state transition -----
      # For launch / lay orders: the staging yard should have lost the item.
      # For recovery orders: the deployed group should be empty (recovered) OR removed entirely.
      _assert_post_dispatch_state(planet, empire, order_type)
  ```
- [x] Add the `_assert_post_dispatch_state` helper above the test:
  ```python
  def _assert_post_dispatch_state(planet, empire, order_type: OrderType) -> None:
      """Per-order-type observable post-condition checks."""
      if order_type is OrderType.LAY_MINES:
          # The mine should have moved from staging_yard into a MineGroup.
          mine_groups = [g for g in empire.deployed_groups if g.__class__.__name__ == "MineGroup"]
          assert len(mine_groups) == 1, "LAY_MINES should produce 1 MineGroup."
          assert len(planet.staging_yard) == 0, "Mine should have left the staging yard."
      elif order_type in (OrderType.LAUNCH_FIGHTERS, OrderType.LAUNCH_SATELLITES):
          # The fighter/satellite should have moved from staging_yard into a group.
          assert len(planet.staging_yard) == 0, (
              f"{order_type.name} should have emptied the staging yard."
          )
          assert len(empire.deployed_groups) == 1, (
              f"{order_type.name} should produce 1 deployed group."
          )
      elif order_type in (OrderType.RECOVER_FIGHTERS, OrderType.RECOVER_SATELLITES):
          # The recovered ship should be back in the staging yard; the deployed group is empty or removed.
          for group in empire.deployed_groups:
              assert len(group.ships) == 0, (
                  f"{order_type.name} should empty the deployed group's ships."
              )
          # Note: handlers MAY remove an empty group from empire.deployed_groups;
          # the precise post-condition depends on the handler's policy. Tolerant check:
          # the recovered ship should be in the staging yard.
          assert len(planet.staging_yard) >= 1, (
              f"{order_type.name} should have placed the recovered ship into the staging yard."
          )
      else:
          pytest.fail(f"Unhandled order_type in _assert_post_dispatch_state: {order_type!r}")
  ```
- [x] **Implementation watch**: the precise post-conditions of LAY_MINES, LAUNCH_*, RECOVER_* depend on the production handler behaviours. **Verify each branch's expected post-state by reading the handler's `execute_for_issuer` implementation** before checking off this task. If a handler's actual behaviour differs from the assertion (e.g., RECOVER_* leaves a non-empty group), adjust the assertion to match — the goal is observable correctness, not a hardcoded handler-specific expectation.
- [x] Run all 5 parametrise cases; confirm green.

**Notes:** The `_assert_post_dispatch_state` helper is the load-bearing piece of Phase 2 — it's what makes the test "behavioural" rather than just "structural." Be conservative: if a handler's post-state contract is genuinely ambiguous (handler-defined policy), encode the looser assertion and document the decision in `decisions.md`.

---

### Task 2.2: Add the `test_planet_fms_e2e_parametrise_matches_registry_view` guard [Simple]
**File:** `tests/integration/test_process_planet_action_tick_end_to_end.py`
**Tests:** `pytest tests/integration/test_process_planet_action_tick_end_to_end.py::test_planet_fms_e2e_parametrise_matches_registry_view -v`

- [x] Add the guard test (adapt verbatim from `test_fms_planet_lay_mines.py:280-296`, retargeting the message to mention PROJ-455 / e2e):
  ```python
  def test_planet_fms_e2e_parametrise_matches_registry_view() -> None:
      """Sanity guard: the parametrise list in ``test_process_planet_action_tick_end_to_end``
      must match the live planet-FMS registry view. If a sixth handler
      is added but the parametrise list isn't extended, this test surfaces
      the drift before the next CI run sees an under-covered handler.
      """
      from game.strategy.engine.commands.order_metadata_view import order_metadata
  
      parametrised = frozenset({
          OrderType.LAY_MINES,
          OrderType.LAUNCH_FIGHTERS,
          OrderType.LAUNCH_SATELLITES,
          OrderType.RECOVER_FIGHTERS,
          OrderType.RECOVER_SATELLITES,
      })
      assert parametrised == order_metadata.planet_fms_action_order_types, (
          "planet_fms_action_order_types drift: the parametrise list in "
          "test_process_planet_action_tick_end_to_end must be updated to "
          "keep coverage exhaustive."
      )
  ```
- [x] Run the guard. It should pass today because the precedent test in `test_fms_planet_lay_mines.py` already verifies the same set.

**Notes:** This guard is the safety net against future drift. If a sixth planet-FMS handler is added, both this guard AND the precedent guard fire.

---

### Task 2.3: Verify Phase 2 cross-coverage against Phase 1's smoke test [Simple]
**File:** `tests/integration/test_process_planet_action_tick_end_to_end.py`

- [x] After Tasks 2.1-2.2 land, the LAY_MINES case is covered by **both** `test_lay_mines_e2e_smoke` (Phase 1) and `test_process_planet_action_tick_end_to_end[OrderType.LAY_MINES]` (Phase 2).
- [x] Decide whether to keep the Phase-1 smoke test as a distinct entry or delete it. **Recommendation**: keep it. The smoke test exercises the simplest scenario in isolation; it's faster to debug than the parametrised version when a future regression hits. The marginal cost (one extra test on the LAY_MINES path) is negligible.
- [x] Document the decision in `decisions.md` (either "Phase-1 smoke retained as fast-path debug aid" or "Phase-1 smoke removed; parametrise covers it").

**Notes:**

---

### Task 2.4: In-progress branch coverage — parametrised across 5 FMS order types [Medium]
**File:** `tests/integration/test_process_planet_action_tick_end_to_end.py`
**Tests:** `pytest tests/integration/test_process_planet_action_tick_end_to_end.py::test_process_planet_action_tick_in_progress_branch -v`

**Why this task exists:** Tasks 2.1-2.2 close the **completion** branch of `_process_planet_action_tick` (`game/strategy/engine/action_execution_engine.py:278-289`). The **in-progress** branch (`game/strategy/engine/action_execution_engine.py:290-297`, where `action_completed=False` is returned because `order.execution_progress < action_time`) is acknowledged in `findings/PROJ-455_findings.md:41-43` as uncovered but never exercised by the executable checklist. This task closes that gap.

**Per the audit-fix decision (2026-05-19; codex consult + claude subagent reviews), Option A is chosen**: add a dedicated in-progress parametrised test alongside the completion test rather than parametrising one test across `(order_type, expected_completion)` tuples. Option B (extend Task 2.1) was rejected because Task 2.1's fixture is tightly built around a single `_FixedActionTimeResolver(1)` and a single `_assert_post_dispatch_state` helper that asserts handler-level post-conditions (which only fire on completion). Document the choice in `decisions.md` (entry: "Phase 2 in-progress branch coverage uses a dedicated parametrised test (Option A); Option B rejected because Task 2.1's completion-only post-condition helper would need to bifurcate.").

- [x] Add a `_FixedActionTimeResolver` variant that returns `action_time > 1` (e.g., `_FixedActionTimeResolver(3)`), so a single tick increments `execution_progress` to `1` and the action does NOT complete on that tick. Reuse the existing resolver shape; just pass a different `action_time` value at construction.
- [x] Add the parametrised in-progress test:
  ```python
  @pytest.mark.parametrize(
      "order_type",
      [
          OrderType.LAY_MINES,
          OrderType.LAUNCH_FIGHTERS,
          OrderType.LAUNCH_SATELLITES,
          OrderType.RECOVER_FIGHTERS,
          OrderType.RECOVER_SATELLITES,
      ],
  )
  def test_process_planet_action_tick_in_progress_branch(
      order_type: OrderType,
  ) -> None:
      """Drive ONE tick with action_time=3 so the action does NOT complete.

      Exercises the in-progress return path at
      ``game/strategy/engine/action_execution_engine.py:290-297``:
      the order remains queued, execution_progress increments to 1,
      action_completed is False, and the handler is NOT invoked.
      """
      processor = OrderProcessor()
      engine = ActionExecutionEngine(
          order_processor=processor,
          action_time_resolver=_FixedActionTimeResolver(3),
      )
      hex_c = HexCoord(0, 0)
      planet = _StubPlanet(planet_id=42, owner_id=7, location=hex_c)
      empire = SimpleNamespace(
          id=7,
          name="E",
          fleets=[],
          colonies=[planet],
          deployed_groups=[],
      )
      empire.deployed_groups_of = lambda cls, _e=empire: [
          g for g in _e.deployed_groups if isinstance(g, cls)
      ]

      _SCENARIO_BUILDERS[order_type](planet, empire)
      assert planet.get_current_order() is not None
      current_order = planet.get_current_order()
      assert current_order.type is order_type

      results = engine.process_action_ticks(
          empires=[empire],
          galaxy=None,
          tick=1,
          component_registry=None,
      )

      # ----- Assert: ActionTickResult shape (in-progress branch) -----
      assert len(results) == 1
      result = results[0]
      assert result.order_type is order_type
      assert result.action_completed is False, (
          f"With _FixedActionTimeResolver(3) and one tick, {order_type.name} "
          f"should NOT complete; got action_completed={result.action_completed}."
      )
      assert result.execution_progress == 1, (
          f"After one tick the order's execution_progress should be 1; "
          f"got {result.execution_progress}."
      )
      assert result.action_time == 3
      assert result.fleet_consumed is False

      # ----- Assert: order still queued -----
      assert planet.get_current_order() is current_order, (
          f"{order_type.name} in-progress: order must remain queued; "
          f"the handler should NOT have been dispatched on this tick."
      )
      assert current_order.execution_progress == 1
  ```
- [x] Run all 5 parametrise cases; confirm green.
- [x] **Sanity check**: temporarily change the resolver to `_FixedActionTimeResolver(1)` and re-run; the in-progress assertions should FAIL (the action completes on tick 1). Revert. Proves the assertions are non-trivial.

**Notes:** This task closes the second branch of `_process_planet_action_tick`. With Tasks 2.1 and 2.4 both landed, both the completion path (`:278-289`) and the in-progress path (`:290-297`) have engine-mediated coverage for all 5 FMS order types.

---

## Phase Completion Checklist

When all tasks above are checked off:

- [x] `test_process_planet_action_tick_end_to_end` runs 5 parametrise cases, all green (completion branch)
- [x] `test_process_planet_action_tick_in_progress_branch` runs 5 parametrise cases, all green (in-progress branch)
- [x] **Both branches of `_process_planet_action_tick` covered** for all 5 FMS order types (audit-fix gate 2026-05-19)
- [x] `test_planet_fms_e2e_parametrise_matches_registry_view` green
- [x] `test_lay_mines_e2e_smoke` decision documented in `decisions.md`
- [x] In-progress branch coverage Option-A vs Option-B decision documented in `decisions.md`
- [x] `pytest tests/integration/test_process_planet_action_tick_end_to_end.py -v` green (11 tests total: 5 completion parametrised + 5 in-progress parametrised + 1 guard + optionally the smoke)
- [x] `pytest tests/integration/test_fms_planet_lay_mines.py -v` still green (PROJ-445 Phase 1 precedent — must not regress)
- [x] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [x] Run `python Projects/scripts/validate_phase.py PROJ-455 2` — PASSED
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3

## Notes / Deferrals

- **Post-dispatch assertions for RECOVER_*** — the handler may or may not remove an empty deployed group from `empire.deployed_groups`. Phase 2 uses a tolerant assertion ("any group has 0 ships AND recovered item is in staging yard"). If during implementation the test reveals the handler is strict-removes, tighten the assertion. Document in `decisions.md`.
- **`fleet_consumed`** — for planet-issuer paths this is always `False` per the engine code at action_execution_engine.py:286. The assertion is a forward-contract guard against future drift.
