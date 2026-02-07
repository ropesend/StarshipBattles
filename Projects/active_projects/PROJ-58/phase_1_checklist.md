# Phase 1: Quick Wins (Zero-Risk Removals) [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-56 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove backward compat code that has zero callers or is already dead code.

---

## Tasks

### Task 1.1: Remove Workshop ViewModel Proxy Properties [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/ui/ tests/integration/ui/ -x`
- [ ] Remove the `ship` property and setter (~lines 357-363) - delegates to `self.viewmodel.ship`
- [ ] Remove the `selected_components` property and setter (~lines 365-373) - delegates to `self.viewmodel.selected_components`
- [ ] Remove the `available_components` property (~lines 375-379) - delegates to `self.viewmodel.available_components`
- [ ] Remove the section comment "Backward-Compatible Proxy Properties (delegate to ViewModel)" (~line 354-356)
- [ ] Verify: Search for `self.ship` usage in workshop_screen.py - any remaining uses should go through `self.viewmodel.ship`
- [ ] Run tests: `pytest tests/unit/ui/ tests/integration/ui/ -x`
**Notes:** Research confirmed zero external callers of these properties. All access goes through `self.viewmodel` directly.

### Task 1.2: Remove Dead _damage_layer Mixin Method [Simple]
**File:** `game/simulation/entities/ship_combat.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [ ] Verify: Search for `ship._damage_layer` or `self._damage_layer` callers outside the mixin itself - expect zero
- [ ] Remove `_damage_layer()` method (~lines 161-174) - delegates to `combat_engine._damage_layer()` which doesn't exist in ShipCombatEngine; actual `_damage_layer` lives in `DamageCalculator`
- [ ] Run tests: `pytest tests/unit/combat/ -x`
**Notes:** This method delegates to a non-existent method on ShipCombatEngine. DamageCalculator handles layer damage directly. This is dead code.

### Task 1.3: Remove "backward compatibility" Comments from Already-Clean Code [Simple]
**Files:** Multiple
**Tests:** `pytest tests/ --testmon`
- [ ] `game/ai/interfaces/controllable.py` (~line 255): Remove "backward-compatible access" comment from `ShipControllableAdapter` docstring - this is a proper adapter pattern, not a compat shim
- [ ] `game/core/registry.py`: Remove PROJ-38 deprecation timeline comment block (~lines 1-10) since deprecated functions are already removed
- [ ] Search for any other "backward compat" comments on code that's already been properly migrated
- [ ] Run tests: `pytest tests/ --testmon`
**Notes:** These are comment-only changes that remove misleading documentation.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
