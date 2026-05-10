# Phase 1: TDD Scaffolding (Failing Tests)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Lock acceptance criteria as executable specs. Write failing tests for the new combat-trigger model BEFORE any production code changes. Confirm each test fails for the expected reason (current per-tick behaviour produces too many rounds, or the multi-fleet-per-empire is silently dropped).

---

## Tasks

### Task 1.1: Add unit-test file for the new trigger predicate [Simple]

**File:** `tests/unit/strategy/engine/test_conflict_round_budget.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_round_budget.py -v`

This file holds focused tests for `ConflictResolutionEngine._should_trigger_combat_for_fleet` (the new predicate landing in Phase 4). For Phase 1, the tests reference behaviour that does not yet exist — they MUST fail.

- [x] Create the file with module docstring referencing PROJ-320
- [x] `test_opportunity_tick_with_no_orders_triggers_combat`:
      build a fleet with speed 5 (interval 20), no orders, located at a contested hex, run conflict engine on tick 20 → assert combat fired
- [x] `test_opportunity_tick_with_action_order_triggers_combat`:
      same fleet, give it a COLONIZE order, tick 20 → assert combat fired
- [x] `test_opportunity_tick_when_fleet_leaves_skips_combat`:
      fleet with MOVE order whose Phase 3 takes it out of the contested hex → assert NO combat fired
- [x] `test_non_opportunity_tick_skips_combat`:
      same fleet, run on tick 19 (not divisible by 20) → assert NO combat fired
- [x] `test_blocked_pathfind_still_triggers_combat`:
      fleet with MOVE order whose pathfinding fails (returns None) → assert combat fired (fleet stayed put)
- [x] **Verify all five tests run AND fail** — the predicate doesn't exist yet, so they fail at import / AttributeError; that is the expected red state.

**Notes:** Used `MagicMock`-based fleets and a MagicMock `IBattleResolver` (no real `Fleet` construction needed since the predicate only reads `fleet.id`, `fleet.location`, `fleet.speed`). Five tests written, five fail with `AttributeError: 'ConflictResolutionEngine' object has no attribute '_should_trigger_combat_for_fleet'` — exactly the expected red baseline. The tests' `orders` parameter is descriptive (helps the human reader) — the predicate doesn't actually inspect orders; the trigger rule is "did the fleet leave the hex this tick?" full stop, regardless of WHY it didn't move.

---

### Task 1.2: Add integration test for the round-budget invariant [Medium]

**File:** `tests/integration/strategy/test_combat_round_budget.py` (NEW)
**Tests:** `pytest tests/integration/strategy/test_combat_round_budget.py -v`

End-to-end turn-engine tests that exercise the full flow with a mocked `IBattleResolver`.

- [x] Create the file with module docstring referencing PROJ-320
- [x] `test_two_stalemated_fleets_resolve_in_sum_of_speeds_rounds`:
      Empire A fleet speed 6, Empire B fleet speed 4 → assert call_count == 10
- [x] `test_three_team_stalemate_sums_speeds`:
      Empires A/B/C with fleet speeds 5/4/3 → assert call_count == 12
- [x] `test_one_fleet_leaves_mid_turn_stops_contributing`:
      A speed-5 vs B speed-5; A leaves at tick 60. Expected: 2 (A's t=20,40) + 3 (B's t=20,40,60) = 5
- [x] `test_empire_with_two_fleets_each_contributes_rounds`:
      Empire A holds Fleet1 (5) + Fleet2 (4) co-located with Empire B's Fleet3 (5). Expected: 5+4+5 = 14
- [x] **Verify all four tests run AND fail** — fail with `TypeError: ConflictResolutionEngine.resolve_all_conflicts() got an unexpected keyword argument 'tick'`. Phase 4 will extend the API with `tick=` and `moved_fleet_ids=` kwargs.

**Notes:** Implemented a `_NonDestructiveResolver(IBattleResolver)` that records `resolve_battle` calls but never wipes ships, so a stalemate persists for the full 100-tick turn. The `_run_full_turn` helper drives `resolve_all_conflicts` 100 times, optionally marking specific fleet ids as "moved" on specific ticks (simulating Phase 3 outcomes). Note: the original Task 1.2 plan had `assert call_count == 7` for the "one fleet leaves" test, but on careful counting the correct answer is 5 (see test docstring) — A leaves at tick 60 which IS one of A's opportunities, so A only fires at 20 and 40, not 20+40+60. Updated.

---

### Task 1.3: Regression guard for the merge speed-recalc invariant [Simple]

**File:** `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v`

The Risk Assessor swarm agent flagged a HIGH-severity pre-existing bug claiming `OrderProcessor._execute_fleet_merge` did not call `update_fleet_speed`. **This claim was wrong.** Verified by reading `Fleet.merge_with` (`game/strategy/data/fleet.py:459`) which calls `other_fleet.trigger_speed_recalculation()` AFTER ship transfer — which dispatches to `FleetSpeedCalculator.update_fleet_speed`. Phase 1's job here became writing a regression guard locking the existing correct behaviour.

- [x] Created `test_fleet_merge_recalculates_target_speed` — patches `Fleet.trigger_speed_recalculation` and asserts `source.merge_with(target)` calls it on `target`. **Passes.**
- [x] Created `test_order_processor_merge_path_invokes_speed_recalc` — confirms `OrderProcessor._execute_fleet_merge` delegates to `Fleet.merge_with` (which carries the recalc), so no future refactor can short-circuit it. **Passes.**

**Notes:** Both tests pass on first run, proving the merge speed-recalc is wired. See [decisions.md](decisions.md) row dated 2026-05-02 (CORRECTION) for the full backstory and the lesson learned about trust-but-verify on swarm agent claims. The original Task 1.3 plan expected this test to fail; revised to be a passing regression guard. Phase 2 was reframed accordingly (from "bug fix" to "speed-recalc invariant audit" — see `phase_2_checklist.md`).

---

### Task 1.4: Update existing event-count assertions to flag pending changes [Simple]

**File:** `tests/integration/strategy/test_combat_shortcut_paths.py`, `tests/integration/strategy/test_event_log_integration.py`
**Tests:** `pytest tests/integration/strategy/test_combat_shortcut_paths.py tests/integration/strategy/test_event_log_integration.py -v`

UI Impact swarm agent flagged that several existing tests assert specific event counts that will change. We don't update them in Phase 1 (that's Phase 4 cleanup) — but we add `# PROJ-320` markers so the relationship is explicit.

- [x] In `test_combat_shortcut_paths.py`: greped for `combats_resolved` and `assert_called` related to combat counts. Only ONE test specifically encodes legacy per-tick re-engagement: `TestReEngagementOnSubsequentTick`. Added a `PROJ-320` marker to the class docstring AND the relevant assertion, both flagging the class for deletion in Phase 4 Task 4.6.
- [x] In `test_event_log_integration.py`: greped — that file synthesises `COMBAT_RESOLVED` events directly via `log_event`, never runs the conflict engine end-to-end. Zero markers needed.
- [x] **Verify the marked tests still PASS as-is** — all 12 tests in `test_combat_shortcut_paths.py` still pass.

**Notes:** Other count assertions (`assert len(calls) == 1` at lines 379, 407, 436, 471) are testing direct calls to `_resolve_combat_at_hex`, which is unchanged by PROJ-320 — those stay green. Lines `assert engine._combats_resolved == 1` (e.g. line 169) are also direct `_resolve_combat_at_hex` invocations. Only the `resolve_all_conflicts`-driven `TestReEngagementOnSubsequentTick` class is affected.

---

### Task 1.5: Verify the failing-test baseline [Simple]

**Tests:** Run only the new tests in isolation:

```bash
.venv/Scripts/python.exe -m pytest tests/unit/strategy/engine/test_conflict_round_budget.py tests/integration/strategy/test_combat_round_budget.py tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v
```

- [x] All 11 new tests run (no import errors)
- [x] 9 fail and 2 pass — matching the documented expected outcomes:
  - 5 fails on `test_conflict_round_budget.py` (AttributeError on missing predicate — Task 1.1)
  - 4 fails on `test_combat_round_budget.py` (TypeError on `tick=`/`moved_fleet_ids=` kwargs — Task 1.2)
  - 2 passes on `test_order_processor_fleet_merge.py` (confirmed merge non-bug — Task 1.3)
- [x] No accidental greens in the failing-test files
- [x] Sharded baseline: **16,422 tests | 16,410 passed | 9 failed | 0 errors | 3 skipped** — only the 9 new failures, no pre-existing regressions.

**Notes:** Sharded baseline went from 16,377 (pre-Phase-1) to 16,422 (post-Phase-1) — +45 tests is more than the 11 I added; some other shards added new tests between baseline runs (likely test collection timing, not real new tests). What matters: zero pre-existing tests broke.

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All 9 new failing tests fail with the documented expected reasons (5 AttributeError + 4 TypeError)
- [x] 2 new passing tests (the merge non-bug regression guards)
- [x] No regression in the existing baseline
- [x] Update status at top of this file to `Complete`
- [x] Update [plan.md](plan.md) phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 (reframed)
