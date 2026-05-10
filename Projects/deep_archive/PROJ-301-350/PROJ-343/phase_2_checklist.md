# Phase 2: T1.1 — Fleet-to-fleet TransferDialog fix

**Status:** Not Started
**Objective:** Make `IssueTransferCommand(planet_id=None, target_fleet_id=<id>)` succeed at the production handler. Carry `target_fleet_id` through to the persisted TRANSFER order. Update the prior-arc test that pins the false-positive behavior.

---

## Tasks

### Task 2.1: Verify order-execution path reads `target_fleet_id` [Medium]
**File:** `game/strategy/engine/order_*.py`, `game/strategy/data/order_types.py` (read-only audit)
**Tests:** none (research only)

- [ ] `git grep -n "OrderType.TRANSFER" game/strategy/` — find the order executor.
- [ ] Read the executor's TRANSFER branch. Determine whether it reads `params['target_fleet_id']` or only `params['planet_id']`.
- [ ] If executor only knows `planet_id`: extending PROJ-343 scope to executor is required (decision: do it; document in [decisions.md](../PROJ-343/decisions.md)). If executor already understands `target_fleet_id`: no change needed.
- [ ] Add finding to [decisions.md](../PROJ-343/decisions.md).

**Notes:**

### Task 2.2: Refactor `transfer.py:execute` to branch on target type [Medium]
**File:** `game/strategy/engine/handlers/transfer.py`
**Tests:** `pytest tests/unit/strategy/engine/handlers/test_transfer_handler_fleet_to_fleet.py -x` — must PASS

- [ ] Read [design.md](../PROJ-343/design.md) §T1.1 fix shape.
- [ ] After step 2 (owning empire resolved, line 44), insert branch:
  ```python
  if cmd.target_fleet_id is not None:
      target_fleet, error = self._resolve_player_fleet(session, cmd.target_fleet_id)
      if error:
          return error
      # Validate fleet-to-fleet (skip planet-target validator)
      # Use existing/new fleet-to-fleet validator
      ...
      transfer_params = {
          'direction': cmd.direction,
          'cargo_type': cmd.cargo_type,
          'amount': cmd.amount,
          'target_fleet_id': cmd.target_fleet_id,
          'species_id': cmd.species_id,
      }
      order = Order(OrderType.TRANSFER, target=transfer_params)
      fleet.add_order(order)
      return ValidationResult.ok()
  # Existing planet-target path follows
  planet, error = self._resolve_planet(session, cmd.planet_id)
  ...
  ```
- [ ] If Task 2.1 found the executor needs `target_fleet_id` support: extend executor in same commit.
- [ ] Run: failing test from Phase 1 task 1.1 now passes.

**Notes:**

### Task 2.3: Update `test_transfer_dialog_characterization.py:418-432` [Simple]
**File:** `tests/unit/ui/screens/test_transfer_dialog_characterization.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog_characterization.py -x`

- [ ] Read lines 418-432 to confirm the false-positive test.
- [ ] Rewrite to either (a) exercise the real handler end-to-end (preferred), or (b) delete and rely on the new Phase 1 task-1.1 test as the canonical assertion.
- [ ] If (b): include reason in commit message: `tests: remove false-positive pin of broken fleet-to-fleet transfer (PROJ-343 T1.1)`.

**Notes:**

### Task 2.4: Targeted test slice
**Tests:** `pytest tests/unit/strategy/engine/handlers/ tests/unit/ui/screens/test_transfer_dialog_characterization.py -x`

- [ ] All pass.
- [ ] No regression in the rest of `tests/unit/strategy/engine/handlers/`.

**Notes:**

### Task 2.5: Commit
- [ ] `git status` — verify no unrelated files staged
- [ ] Stage only the production change + the test rewrite + the new Phase 1 test
- [ ] Commit: `fix(transfer): support fleet-to-fleet transfer (PROJ-343 T1.1)`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] T1.1 commit landed
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update Current State to point to Phase 3
