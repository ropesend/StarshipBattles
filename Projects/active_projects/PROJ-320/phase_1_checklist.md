# Phase 1: TDD Scaffolding (Failing Tests)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Lock acceptance criteria as executable specs. Write failing tests for the new combat-trigger model BEFORE any production code changes. Confirm each test fails for the expected reason (current per-tick behaviour produces too many rounds, or the multi-fleet-per-empire is silently dropped).

---

## Tasks

### Task 1.1: Add unit-test file for the new trigger predicate [Simple]

**File:** `tests/unit/strategy/engine/test_conflict_round_budget.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_round_budget.py -v`

This file holds focused tests for `ConflictResolutionEngine._should_trigger_combat_for_fleet` (the new predicate landing in Phase 4). For Phase 1, the tests reference behaviour that does not yet exist — they MUST fail.

- [ ] Create the file with module docstring referencing PROJ-320
- [ ] `test_movement_opportunity_tick_with_no_orders_triggers_combat`:
      build a fleet with speed 5 (interval 20), no orders, located at a contested hex, run conflict engine on tick 20 → assert combat fired
- [ ] `test_movement_opportunity_tick_with_action_order_triggers_combat`:
      same fleet, give it a COLONIZE order, tick 20 → assert combat fired
- [ ] `test_movement_opportunity_tick_when_fleet_leaves_skips_combat`:
      fleet with MOVE order whose Phase 3 takes it out of the contested hex → assert NO combat fired
- [ ] `test_non_movement_tick_skips_combat`:
      same fleet, run on tick 19 (not divisible by 20) → assert NO combat fired
- [ ] `test_blocked_pathfind_still_triggers_combat`:
      fleet with MOVE order whose pathfinding fails (returns None) → assert combat fired (fleet stayed put)
- [ ] **Verify all five tests run AND fail** — the predicate doesn't exist yet, so they fail at import / AttributeError; that is the expected red state.

**Notes:** Use existing fixtures in `tests/conftest.py` (`session_registries`, `ship_factory`) and `tests/fixtures/strategy_entities.py` (`create_test_fleet`, `create_test_empire`). Mock `IBattleResolver` with a recording stub so each test asserts `resolver.resolve_battle.call_count == 0` or `== 1`.

---

### Task 1.2: Add integration test for the round-budget invariant [Medium]

**File:** `tests/integration/strategy/test_combat_round_budget.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_combat_round_budget.py -v`

End-to-end turn-engine tests that exercise the full flow with a mocked `IBattleResolver`.

- [ ] Create the file with module docstring referencing PROJ-320
- [ ] `test_two_stalemated_fleets_resolve_in_sum_of_speeds_rounds`:
      Empire A fleet speed 6, Empire B fleet speed 4, co-located at hex H, neither moving. Run one full turn. Mock resolver returns no destruction every round. Assert `resolver.resolve_battle.call_count == 10` (NOT 100).
- [ ] `test_three_team_stalemate_sums_speeds`:
      Empires A/B/C with fleet speeds 5/4/3, all at hex H, none moving. Assert `resolver.resolve_battle.call_count == 12`.
- [ ] `test_one_fleet_leaves_mid_turn_stops_contributing`:
      A speed-5 vs B speed-5 in hex H. A has MOVE order to leave at tick 60. Total expected rounds: A contributes opportunities at 20, 40 (2 rounds — leaves at 60 so that one is skipped); B contributes at 20, 40, 60, 80, 100 (5 rounds). Assert call_count == 7.
- [ ] `test_empire_with_two_fleets_each_contributes_rounds`:
      Empire A has Fleet1 (speed 5) and Fleet2 (speed 4) co-located at hex H with Empire B's Fleet3 (speed 5). Total: 5 + 4 + 5 = 14 rounds.
- [ ] **Verify all four tests run AND fail** — today's per-tick scanning produces ~100 rounds for the first three tests; the fourth test additionally exposes the multi-fleet-per-empire batching bug (Empire A's Fleet2 will be silently dropped, so call_count will be 5+5=10, not 14).

**Notes:** Build the turn engine via the canonical `tests/fixtures/strategy_entities.py` factories. Use a `_RecordingResolver(IBattleResolver)` patterned on `tests/integration/strategy/test_three_empire_battle.py:26-60` to count invocations.

---

### Task 1.3: Add baseline unit test for the fleet-merge speed-recalc bug [Simple]

**File:** `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` (NEW or extend existing)
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v`

The Phase 2 fix needs its own failing test in Phase 1 to prove the bug exists before fixing it.

- [ ] Check whether `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` already exists. If yes, extend; if no, create.
- [ ] `test_fleet_merge_recalculates_target_speed`:
      Build Fleet A (single ship, raw_strategic_movement=10, mass=400 → speed 0). Build Fleet B (single ship, raw_strategic_movement=200, mass=400 → speed 5). Both at same hex. Issue Fleet A → JOIN_FLEET → Fleet B. Process Phase 1 instant orders. Assert `Fleet B.speed == min(5, 0) == 0` (because the merged ship pool now contains the slow ship from A).
- [ ] **Verify the test runs AND fails** — today's `_execute_fleet_merge` does not call `update_fleet_speed`, so `Fleet B.speed` stays at 5 even after the slow ship is merged in. That's the bug Phase 2 fixes.

**Notes:** Reference Risk Assessor finding §3 (HIGH). Use `FleetSpeedCalculator.calculate_fleet_speed` to compute expected merged speed. Consult `game/strategy/services/fleet_speed_calculator.py:119-146` for the formula.

---

### Task 1.4: Update existing event-count assertions to flag pending changes [Simple]

**File:** `tests/integration/strategy/test_combat_shortcut_paths.py`, `tests/integration/strategy/test_event_log_integration.py`
**Tests:** `pytest tests/integration/strategy/test_combat_shortcut_paths.py tests/integration/strategy/test_event_log_integration.py -v`

UI Impact swarm agent flagged that several existing tests assert specific event counts that will change. We don't update them in Phase 1 (that's Phase 4 cleanup) — but we add `# PROJ-320` markers so the relationship is explicit.

- [ ] In `test_combat_shortcut_paths.py`: grep for `combats_resolved` and `assert_called` related to combat counts. For each one whose expected value will change with the new model, add a `# PROJ-320: count changes when round-budget triggering lands; updated in Phase 4` comment on the assertion line.
- [ ] In `test_event_log_integration.py`: same grep, same marker. Specifically the test around line 155-180 that asserts `combat_resolved_event_visible_in_facade` — flag any count assertions inside it.
- [ ] **Verify the marked tests still PASS as-is** — Phase 1 only adds comments, no behavioural changes.

**Notes:** Use `Grep` tool with pattern `combats_resolved|resolve_battle\.call_count|COMBAT_RESOLVED.*assert` scoped to `tests/integration/strategy/`. Don't touch tests outside `tests/integration/strategy/` — they'll be triaged in Phase 4.

---

### Task 1.5: Verify the failing-test baseline [Simple]

**Tests:** Run only the new tests in isolation:

```bash
.venv/Scripts/python.exe -m pytest tests/unit/strategy/engine/test_conflict_round_budget.py tests/integration/strategy/test_combat_round_budget.py tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v
```

- [ ] All 10 new tests run (no import errors)
- [ ] All 10 new tests FAIL for one of the three expected reasons:
  - AttributeError on `_should_trigger_combat_for_fleet` (Task 1.1 tests — predicate doesn't exist yet)
  - Wrong call count due to per-tick scanning (Task 1.2 tests one through three)
  - Wrong call count due to multi-fleet-per-empire bug (Task 1.2 fourth test)
  - Wrong post-merge speed (Task 1.3 test)
- [ ] No accidental green test (any test that passes here means it's broken — investigate)
- [ ] Run the full sharded baseline once: `.venv/Scripts/python.exe Tools/test_sharded/test_sharded.py` — confirm 16,374 + 10 new failing = 16,384 total, baseline still otherwise green.

**Notes:** Document the EXACT failure messages in this checklist's `Notes` section as evidence the red state is correctly captured. Phase 2 starts only after Phase 1 is fully red.

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 10 new tests fail with the documented expected reasons
- [ ] No regression in the existing 16,374-test baseline
- [ ] Update status at top of this file to `Complete`
- [ ] Update [plan.md](plan.md) phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
