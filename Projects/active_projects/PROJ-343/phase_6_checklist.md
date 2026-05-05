# Phase 6: T1.4 — TransferDialog selective-close on validation aborts

**Status:** Not Started
**Objective:** Replace always-kill `try/finally` with selective-close. Dialog stays open when `confirm_pending` aborts for input-validation reasons (no source/target, both endpoints non-fleet). Dialog still kills when orders successfully issue OR an unrecoverable exception occurs.

---

## Tasks

### Task 6.1: Update controller return contract (Option A) [Medium]
**File:** `game/ui/screens/transfer_controller.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_controller* -x`

- [ ] Per [decisions.md](../PROJ-343/decisions.md), implementing Option A: `confirm_pending` returns a richer result.
- [ ] Add `@dataclass class ConfirmResult: orders_issued: int; aborted_for_correction: bool` near `confirm_pending`.
- [ ] Refactor `confirm_pending` to return `ConfirmResult` instead of plain `int`:
  - Source/target missing → `ConfirmResult(0, aborted_for_correction=True)`.
  - Both endpoints non-fleet → `ConfirmResult(0, aborted_for_correction=True)`.
  - All pending entries zero → `ConfirmResult(0, aborted_for_correction=True)` (or False — implementer decides; user-correction is plausible).
  - Otherwise → `ConfirmResult(orders_issued, aborted_for_correction=False)`.

**Notes:**

### Task 6.2: Find all `confirm_pending` callers [Simple]
**File:** read-only

- [ ] `git grep -n "confirm_pending" game/ tests/` — list every caller.
- [ ] For each, decide if it consumes the int return; update to use `.orders_issued` field where it does.

**Notes:**

### Task 6.3: Apply selective-close to `_on_confirm` [Simple]
**File:** `game/ui/screens/transfer_dialog.py:372-378`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py -x` — must PASS

- [ ] Replace:
  ```python
  def _on_confirm(self) -> None:
      try:
          self._controller.confirm_pending()
      finally:
          self.kill()
  ```
  with:
  ```python
  def _on_confirm(self) -> None:
      try:
          result = self._controller.confirm_pending()
      except Exception:
          self.kill()
          raise
      if not result.aborted_for_correction:
          self.kill()
  ```
- [ ] Run Phase 1 task-1.5 test → passes.

**Notes:**

### Task 6.4: Locate and update the 4 `patch.object(dialog, "kill")` tests [Medium]
**File:** `tests/unit/ui/screens/test_transfer_dialog*.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog* -x`

- [ ] `git grep -n 'patch.object.*kill\|dialog\.kill' tests/unit/ui/screens/` — enumerate.
- [ ] For each test, classify: does it pin "always kill" (now wrong) or "kill on success" (still correct)?
- [ ] Rewrite/delete the wrong ones with rationale in commit message.

**Notes:**

### Task 6.5: Update PROJ-328 phase_C_checklist.md Note 3 [Simple]
**File:** `Projects/active_projects/PROJ-328/phase_C_checklist.md`

- [ ] Read Note 3 to find the misdocumentation of always-kill.
- [ ] Update with the correct behavior: "selective-close — dialog stays open on validation aborts so user can correct; closes on success or unrecoverable exception."
- [ ] Reference PROJ-343 in the update note.

**Notes:**

### Task 6.6: Commit
- [ ] Stage transfer_controller.py + transfer_dialog.py + test updates + Phase 1 task-1.5 test + PROJ-328 doc fix
- [ ] Commit: `fix(transfer-dialog): keep dialog open on confirm-abort paths (PROJ-343 T1.4)`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] T1.4 commit landed
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update Current State to point to Phase 7
