# Phase 6: Superweapon Stub Methods & Final Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-198 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add missing UI methods that superweapons module expects, handle remaining edge cases, and do final audit.

---

## Tasks

### Task 6.1: StrategyUI — Add Missing Methods [Medium]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

- [ ] Add `show_confirmation_dialog(title, message, on_confirm, is_warning=False)` method
  - Implement using existing pygame_gui confirmation dialog pattern
  - Wire through window manager
- [ ] Add `show_ship_picker(ships, ability_name, on_selected)` method
  - Implement minimal ship selection dialog
- [ ] `strategy_superweapons.py` L374: Remove `hasattr`. Call directly.
- [ ] `strategy_superweapons.py` L390: Remove `hasattr`. Call directly.
- [ ] `strategy_superweapons.py` L407: Remove `hasattr`. Call directly.
- [ ] Remove all fallback else-branches (L377-379, L394-396, L410-412)
- [ ] Add tests for new methods
- [ ] Verify: superweapon UI flows work

**Notes:**

### Task 6.2: Battle Panels — Ship/Projectile ID Cleanup [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/panels/ --testmon`

- [ ] Verify `_get_ship_id` and `_get_projectile_id` work after Phase 2 (Ship.id added)
- [ ] Simplify if both ShipDTO and Ship now have `.id`
- [ ] Verify: tests pass

**Notes:**

### Task 6.3: Final Audit [Simple]
**Tests:** Full suite

- [ ] Grep for remaining `hasattr`/`getattr` in `game/ui/`
- [ ] Verify all remaining are in exempt list (keybindings, input_mapper, modifier_row, column traversal, stats_config)
- [ ] Document count of remaining vs eliminated
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete - Audit Passed"
