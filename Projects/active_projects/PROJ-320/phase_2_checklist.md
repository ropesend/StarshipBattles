# Phase 2: Pre-existing Fleet-Merge Speed-Recalc Fix

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the pre-existing bug where `OrderProcessor._execute_fleet_merge` does not recalculate the target fleet's speed after merging in a slower ship. The new combat-trigger model depends on accurate per-fleet movement intervals — without this fix, a merged fleet's opportunity-tick cadence would be wrong. Small, isolated change. Test from Phase 1 Task 1.3 is the gate.

---

## Tasks

### Task 2.1: Apply the speed-recalc fix in `_execute_fleet_merge` [Simple]

**File:** `game/strategy/engine/order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_fleet_merge.py -v`

- [ ] Open `game/strategy/engine/order_processor.py` and locate `_execute_fleet_merge` (search for `def _execute_fleet_merge`)
- [ ] Confirm the method copies ships from source → target then deletes the source fleet but does NOT call any speed recalculation
- [ ] Add the recalc call AFTER the ship transfer completes and BEFORE the source fleet is removed:
  ```python
  # PROJ-320: target fleet's slowest-ship speed may have changed after merge
  from game.strategy.services.fleet_speed_calculator import update_fleet_speed
  update_fleet_speed(target_fleet)
  ```
- [ ] Confirm `from game.strategy.services.fleet_speed_calculator import update_fleet_speed` is correctly placed (top of file with other strategy-services imports, not inside the method) unless there's an import cycle — the file already imports other things from `game.strategy.services` so this should be fine. If a cycle is encountered, fall back to the local import shown above and add a `# Intentional local import: avoids cycle with order_processor → fleet → ...` comment.
- [ ] Run the failing Phase-1 test: it should now PASS (`test_fleet_merge_recalculates_target_speed`)
- [ ] Run the full `tests/unit/strategy/engine/test_order_processor*.py` directory to confirm no regressions

**Notes:** Reference Risk Assessor finding §3 (HIGH). The function `update_fleet_speed(fleet)` lives at `game/strategy/services/fleet_speed_calculator.py:149-161` and is the existing public API for this exact recalc.

---

### Task 2.2: Audit other Fleet-mutation sites for the same gap [Medium]

**File:** Search across `game/strategy/`
**Tests:** `pytest tests/unit/strategy/ -k "fleet_speed or update_fleet_speed" -v`

The merge bug suggests other paths may forget to recalc. Sweep them.

- [ ] Search for every site that mutates `Fleet.ships` (add or remove): `Grep` pattern `fleet\.ships\.(append|extend|remove|pop|clear)|self\.ships\s*=\s*` scoped to `game/strategy/`. Confirm each call site that adds/removes ships is followed by `update_fleet_speed(fleet)` OR by a method that does (e.g. `Fleet.add_ship`, `Fleet.remove_ship`).
- [ ] Specifically check:
  - `Fleet.add_ship` (`game/strategy/data/fleet.py:158`) — already calls `update_fleet_speed`
  - `Fleet.remove_ship` (`game/strategy/data/fleet.py:164`) — already calls `update_fleet_speed`
  - `Fleet.merge_with` (`game/strategy/data/fleet.py:371`) — verify it transfers ships through `add_ship` (which recalcs) or directly mutates the list
  - `apply_outcome_to_fleets` (`game/strategy/combat/post_battle_hook.py:120-126`) — when destroyed/retreated ships are removed, is `update_fleet_speed` called on each affected fleet?
  - `ProductionEngine` ship-spawn paths
  - `OrderProcessor._execute_fleet_split` (if it exists)
- [ ] For each site that DOES mutate `fleet.ships` directly without recalc, add a `update_fleet_speed(fleet)` call AND a regression test in `tests/unit/strategy/engine/test_fleet_speed_invariants.py` (NEW or extend) asserting the speed is correct after the mutation.
- [ ] Document each fixed site in this checklist's `Notes` section.

**Notes:** Bound the audit to ~30 minutes of investigation. If the sweep surfaces a large number of sites, escalate to the user — that's a separate project, not PROJ-320 scope. Phase 2 expects ≤3 fix sites total (`_execute_fleet_merge` plus at most a couple of sweeps).

---

### Task 2.3: Run the affected test directories [Simple]

**Tests:**
```bash
.venv/Scripts/python.exe -m pytest tests/unit/strategy/engine/ tests/integration/strategy/ -v
```

- [ ] All previously-passing tests still pass
- [ ] Phase 1 Task 1.3 test now passes (`test_fleet_merge_recalculates_target_speed`)
- [ ] Phase 1 Tasks 1.1 and 1.2 tests still FAIL (they're gated by Phases 3 and 4 — not Phase 2)
- [ ] Run `--testmon` first for speed: `.venv/Scripts/python.exe -m pytest tests/strategy/ --testmon -v`

**Notes:** If Task 2.2 found additional sites, expect a small number of new tests added there to also pass.

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Phase 1 Task 1.3 test now passes (the merge speed-recalc test)
- [ ] No regression in `tests/unit/strategy/engine/` or `tests/integration/strategy/`
- [ ] Update status at top of this file to `Complete`
- [ ] Update [plan.md](plan.md) phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
