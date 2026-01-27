# Phase 5: Remove Delegation and Final Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-24 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove __getattr__/__setattr__ delegation after all accesses migrated

---

## Tasks

### Task 5.1: Add deprecation warning to delegation (temporary verification) [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** Run full test suite to catch any missed accesses

- [ ] Add `import warnings` at top of file (if not already present)
- [ ] Modify `__getattr__` method to log deprecation warning:
  ```python
  def __getattr__(self, name: str) -> Any:
      """Delegate attribute access to underlying ship."""
      warnings.warn(
          f"Direct attribute access '{name}' is deprecated. "
          f"Use interface method instead.",
          DeprecationWarning,
          stacklevel=2
      )
      return getattr(self._ship, name)
  ```
- [ ] Modify `__setattr__` method similarly for non-`_ship` attributes
- [ ] Run full test suite: `pytest tests/ -v 2>&1 | grep -i deprecation`
- [ ] Document any warnings found - these are missed accesses
- [ ] Fix any missed accesses found in Phases 2-4

**Notes:** This step is temporary to catch any missed direct accesses before removing delegation.

---

### Task 5.2: Remove delegation methods [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/ -v`

After confirming no deprecation warnings from Task 5.1:

- [ ] Remove `__getattr__` method entirely (currently lines 194-196)
- [ ] Remove `__setattr__` method entirely (currently lines 198-203)
- [ ] Update or remove comment block at lines 186-192 explaining the delegation
- [ ] Consider adding new comment explaining migration is complete

**Notes:**

---

### Task 5.3: Update documentation and comments [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** N/A

- [ ] Update module docstring to reflect completed migration
- [ ] Remove reference to PROJ-12 Phase 5 if migration is fully complete
- [ ] Update class docstring for ShipControllableAdapter
- [ ] Add comment noting `formation_master` and `formation_members` return raw Ships

**Notes:**

---

### Task 5.4: Final verification [Simple]
**Tests:** Full test suite + manual verification

- [ ] Run full test suite: `pytest tests/` - all 4563+ tests pass
- [ ] Verify no direct attribute access via grep:
  ```bash
  grep -n "self\.ship\.\w\+ =" game/ai/controller.py
  grep -n "ship\.\w\+ =" game/ai/behaviors.py
  grep -n "self\.ship\.\w\+ =" game/ai/core/system.py
  grep -n "ship\.\w\+ =" game/ai/core/behaviors.py
  ```
- [ ] Manual test: Start a combat battle and verify AI ships behave normally
- [ ] Test formations specifically: Create formation, verify position/rotation sync

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Deprecation warnings step completed with no issues
- [ ] Delegation methods removed
- [ ] Full test suite passes (4563+ tests)
- [ ] Grep verification shows no remaining direct access
- [ ] Manual combat test successful
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `COMPLETE`

---

## Project Completion

After Phase 5 is complete:

1. Update plan.md:
   - Set all phases to `Complete`
   - Update Current State to `COMPLETE`
   - Check all verification checkboxes

2. Consider follow-up work:
   - PROJ-25: Consolidate dual AI implementations (`controller.py` vs `core/system.py`)
