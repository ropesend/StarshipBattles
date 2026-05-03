# Phase 3: Multi-Fleet-per-Empire Combat Support

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Today, when one empire has multiple fleets at the same hex, `_resolve_combat_at_hex` keeps only the FIRST fleet per empire (`conflict_resolution_engine.py:298-300`); the others sit silently idle. Change `fleets_by_empire: Dict[int, Fleet]` to `Dict[int, List[Fleet]]` so every fleet at the contested hex participates in the battle. The spec compiler already maps fleets to teams by `owner_id`, so multi-fleet-per-team is a natural extension. Independent of the trigger rewrite (Phase 4) — done first so Phase 4's logic operates on the corrected fleet-batching shape.

---

## Tasks

### Task 3.1: Promote `fleets_by_empire` to `Dict[int, List[Fleet]]` [Medium]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/ tests/integration/strategy/test_three_empire_battle.py -v`

- [ ] Locate `_resolve_combat_at_hex` (around line 269)
- [ ] Find the `fleets_by_empire` construction loop (around lines 295-300). Today it's roughly:
  ```python
  fleets_by_empire: Dict[int, Fleet] = {}
  for empire, fleet in occupants:
      if empire.id not in fleets_by_empire:
          fleets_by_empire[empire.id] = fleet  # silently drops extras
  ```
  Replace with:
  ```python
  fleets_by_empire: Dict[int, List[Fleet]] = {}
  for empire, fleet in occupants:
      fleets_by_empire.setdefault(empire.id, []).append(fleet)
  ```
- [ ] Update the iteration that flattens these into the resolver's `fleets` argument. After the build, flatten in the same deterministic order:
  ```python
  empire_order: List[int] = sorted(fleets_by_empire.keys())
  fleets_for_battle: List[Fleet] = []
  for emp_id in empire_order:
      # Deterministic intra-empire order: by fleet.id
      for fleet in sorted(fleets_by_empire[emp_id], key=lambda f: f.id):
          fleets_for_battle.append(fleet)
  ```
- [ ] Pass `fleets_for_battle` (flat list) to `self._battle_resolver.resolve_battle(...)` — its current signature already accepts `Sequence[Fleet]` (PROJ-275 N-team).
- [ ] Update any local-variable usage of `fleets_by_empire[emp_id]` that previously assumed a single Fleet, to iterate the list.
- [ ] Confirm `empires={team_id: Empire}` argument continues to map correctly — the team_id is `empire.id`, not "first fleet's empire". This is unchanged.

**Notes:** PROJ-275 already supports N-team battles. The spec compiler at `game/strategy/combat/spec_compiler.py::build_strategy_battle_spec` accepts `fleets: Sequence[Fleet]`, groups them by `owner_id` internally, and emits one `TeamSpec` per empire — so multi-fleet-per-team works out of the box.

---

### Task 3.2: Verify the spec compiler groups multi-fleet-per-team correctly [Simple]

**File:** `game/strategy/combat/spec_compiler.py` (read-only verification)
**Tests:** `pytest tests/unit/strategy/combat/test_strategy_spec_compiler.py -v`

- [ ] Read `build_strategy_battle_spec` and confirm it builds teams by `fleet.owner_id`. Specifically: when given a flat list of [Fleet1(owner=0), Fleet2(owner=0), Fleet3(owner=1)], it should emit one TeamSpec per unique owner_id, with ships from BOTH owner-0 fleets in team 0.
- [ ] If a unit test for this case does not exist, add one in `tests/unit/strategy/combat/test_strategy_spec_compiler.py` named `test_multi_fleet_per_empire_groups_into_one_team`. Build two fleets owned by the same empire, one fleet owned by another empire, call `build_strategy_battle_spec`, assert exactly two `TeamSpec` entries and ship counts match.
- [ ] Run the test and confirm it PASSES (no compiler change needed — Task 3.1 just exposes existing capability).

**Notes:** This is a verification step, not a code-change step. If the test fails, that means the compiler does NOT group fleets by `owner_id` and Phase 3 needs an additional task to teach it. Highly unlikely given PROJ-275 design — but check.

---

### Task 3.3: Update `_log_combat_result` event payload to include all participating fleets [Simple]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_resolution_event_replay.py -v`

- [ ] Locate `_log_combat_result` (around line 107)
- [ ] Verify `participating_fleet_ids` is built from the flattened `fleets_for_battle` list (every participating fleet, not just one-per-empire). Today's code uses an iteration over the old `fleets_by_empire` dict; rewrite to iterate the flat list.
- [ ] `surviving_fleet_ids` and `destroyed_fleet_ids` should already be derived from post-battle ship counts per fleet — confirm those iterations also use the flat list.
- [ ] `empire_id = min(participating_empire_ids)` for the event filter column stays unchanged (Data-Flow Tracer agent verified).

**Notes:** This is the data-flow side of Task 3.1. If `participating_fleet_ids` was previously computed from the dict-of-singletons, it would silently undercount. Make sure the event payload reflects every fleet that fought.

---

### Task 3.4: Add integration test asserting all empire fleets participate [Medium]

**File:** `tests/integration/strategy/test_combat_round_budget.py` (extend, created in Phase 1)
**Tests:** `pytest tests/integration/strategy/test_combat_round_budget.py -v`

- [ ] Add `test_two_fleets_one_empire_both_participate_in_battle`:
      Empire A has Fleet1 (1 ship) and Fleet2 (1 ship) co-located at hex H. Empire B has Fleet3 (1 ship) at hex H. Run conflict resolution. Mock resolver records the `fleets` it receives. Assert the recorded fleets list has all THREE fleets (Fleet1, Fleet2, Fleet3) — not two.
- [ ] Add `test_event_payload_includes_all_participating_fleets`:
      Same setup. Assert the emitted COMBAT_RESOLVED event's `details["participating_fleet_ids"]` contains all three fleet IDs.
- [ ] **Note:** The Phase-1 test `test_empire_with_two_fleets_each_contributes_rounds` (Task 1.2) checks the per-fleet-per-tick round count and is gated by Phase 4. It will still fail at the end of Phase 3 — that's expected.

**Notes:** Use the same `_RecordingResolver` pattern from `test_three_empire_battle.py`. Keep the assertions focused — Phase 4 will land the round-count assertion.

---

### Task 3.5: Run the affected test directories [Simple]

**Tests:**
```bash
.venv/Scripts/python.exe -m pytest tests/unit/strategy/conflict_resolution/ tests/unit/strategy/combat/ tests/unit/strategy/engine/test_conflict_resolution_event_replay.py tests/integration/strategy/test_three_empire_battle.py tests/integration/strategy/test_combat_round_budget.py tests/integration/strategy/test_combat_shortcut_paths.py -v
```

- [ ] All Phase-3-relevant tests pass (the two new ones from Task 3.4 + the existing N-team battle tests)
- [ ] Phase 1 Task 1.3 test still passes (Phase 2 fix)
- [ ] Phase 1 Tasks 1.1 and 1.2 tests STILL fail (Phase 4 lands the trigger predicate) — except `test_empire_with_two_fleets_each_contributes_rounds` may shift its failure count from 10 to 14 partial after Phase 3 since the fleet-batching is fixed but trigger is still per-tick. Both numbers are wrong; Phase 4 makes it 14.
- [ ] Run the full sharded baseline once: `.venv/Scripts/python.exe Tools/test_sharded/test_sharded.py` — confirm no regression in totals beyond the deliberate Phase-1 reds.

**Notes:** If `test_combat_shortcut_paths.py` regresses, check whether its assertions assume one-fleet-per-empire batching. If so, those are next-Phase-Cleanup candidates — flag them with a `# PROJ-320 Phase 3` marker but only update them if their pass/fail flips here.

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `_resolve_combat_at_hex` correctly batches all fleets per empire
- [ ] `_log_combat_result` event payload reflects all participating fleets
- [ ] New integration tests for multi-fleet-per-empire pass
- [ ] No regression in N-team battle tests
- [ ] Phase 1 Task 1.3 (merge fix) still passes
- [ ] Phase 1 Tasks 1.1 + 1.2 still fail (Phase 4 territory)
- [ ] Update status at top of this file to `Complete`
- [ ] Update [plan.md](plan.md) phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
