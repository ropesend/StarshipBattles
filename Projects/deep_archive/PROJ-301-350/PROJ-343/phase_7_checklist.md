# Phase 7: T1.5 — CargoQuickDialog teardown guarantee

**Status:** Not Started
**Objective:** Wrap `_issue_orders` body in `try/finally: self.kill()` mirroring TransferDialog audit S1.2.

---

## Tasks

### Task 7.1: Confirm no validation-abort path needs kept-open [Simple]
**File:** read-only

- [ ] Read `game/ui/screens/cargo_quick_dialog_controller.py:issue_orders` (and the dialog's `_issue_orders`).
- [ ] If controller has aborts that should keep dialog open (none expected per design.md): switch to T1.4-style selective-close instead of plain try/finally; add note in [decisions.md](../PROJ-343/decisions.md).
- [ ] Otherwise: proceed with plain try/finally.

**Notes:**

### Task 7.2: Apply try/finally [Simple]
**File:** `game/ui/screens/cargo_quick_dialog.py:300-306`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog_kills_on_dispatch_failure.py -x` — must PASS

- [ ] Replace:
  ```python
  def _issue_orders(self) -> None:
      orders_issued = self.controller.issue_orders(self.cargo_items)
      if orders_issued > 0:
          logger.info(...)
      self.kill()
  ```
  with:
  ```python
  def _issue_orders(self) -> None:
      try:
          orders_issued = self.controller.issue_orders(self.cargo_items)
          if orders_issued > 0:
              logger.info(...)
      finally:
          self.kill()
  ```
- [ ] Run Phase 1 task-1.6 test → passes.

**Notes:**

### Task 7.3: Find and update no-finally pinning tests [Simple]
**File:** `tests/unit/ui/screens/test_cargo_quick_dialog*.py`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog* -x`

- [ ] `git grep -n "kill\|_issue_orders" tests/unit/ui/screens/test_cargo_quick_dialog*` — enumerate.
- [ ] For each test: rewrite or delete pins of no-finally behavior; commit-message rationale.

**Notes:**

### Task 7.4: Commit
- [ ] Stage cargo_quick_dialog.py + test updates + Phase 1 task-1.6 test
- [ ] Commit: `fix(cargo-quick-dialog): guarantee window teardown on dispatch failure (PROJ-343 T1.5)`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] T1.5 commit landed
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update Current State to point to Phase 8
