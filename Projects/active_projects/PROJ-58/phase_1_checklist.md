# Phase 1: Quick Wins (Zero-Risk Removals) [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove dead code, update workshop proxy internal usages, remove stale comments.

---

## Tasks

### Task 1.1: Update Workshop ViewModel Proxy Usages and Remove Properties [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/ui/ tests/integration/ui/ -x`

The proxy properties have 11 internal usages of `self.ship`, 3 of `self.selected_components`, 1 of `self.available_components`. All must be replaced before removing the properties.

- [ ] Replace all `self.ship` with `self.viewmodel.ship` in workshop_screen.py (~11 occurrences at lines 113, 299, 311, 490, 511, 624, 625, 682, 702, 714, 801)
- [ ] Replace all `self.selected_components` with `self.viewmodel.selected_components` (~3 occurrences at lines 311, 314, 633)
- [ ] Replace `self.available_components` with `self.viewmodel.available_components` (~1 occurrence at line 621)
- [ ] Fix line 621: `self.available_components = self.viewmodel.available_components` is a broken write to a read-only property - remove the entire line
- [ ] Fix line 314 setter: `self.selected_components = new_list` → use `self.viewmodel._selected_components = new_list` or add proper setter to ViewModel
- [ ] Remove the `ship` property and setter (~lines 357-364)
- [ ] Remove the `selected_components` property and setter (~lines 366-374)
- [ ] Remove the `available_components` property (~lines 376-379)
- [ ] Remove section comment "Backward-Compatible Proxy Properties" (~line 354-356)
- [ ] Run tests: `pytest tests/unit/ui/ tests/integration/ui/ -x`
**Notes:** The setter for `selected_components` directly accesses `viewmodel._selected_components` - check if ViewModel needs a public setter.

### Task 1.2: Remove Dead Mixin Methods [Simple]
**File:** `game/simulation/entities/ship_combat.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [ ] Verify `_calculate_firing_solution()` has zero callers (search codebase)
- [ ] Verify `_find_pdc_target()` has zero callers (search codebase)
- [ ] Verify `_damage_layer()` has zero callers outside the mixin itself
- [ ] Remove `_calculate_firing_solution()` method (~lines 90-103)
- [ ] Remove `_find_pdc_target()` method (~lines 105-148)
- [ ] Remove `_damage_layer()` method (~lines 161-174)
- [ ] Run tests: `pytest tests/unit/combat/ -x`
**Notes:** `_damage_layer` delegates to `combat_engine._damage_layer()` which doesn't exist in ShipCombatEngine - confirmed dead code.

### Task 1.3: Remove Stale "Backward Compatibility" Comments [Simple]
**Files:** Multiple
**Tests:** `pytest tests/ --testmon`
- [ ] `game/ai/interfaces/controllable.py`: Remove "backward-compatible access" comment from adapter docstring (not a shim - proper adapter pattern)
- [ ] `game/core/registry.py`: Remove PROJ-38 deprecation timeline comment block if deprecated functions are already removed
- [ ] `game/strategy/data/stars.py` (~line 466-467): Remove "original generation logic for backward compatibility" comment
- [ ] `game/ui/panels/battle_panels.py` (~lines 34-35): Remove "backward compatibility for tests that set scene.ships directly" comment if tests are updated
- [ ] Search for remaining "backward compat" comments on already-clean code
- [ ] Run tests: `pytest tests/ --testmon`
**Notes:** Comment-only changes - no functional impact.

### Task 1.4: Remove planet_list_presets.py Method Alias [Simple]
**File:** `game/ui/screens/planet_list_presets.py`
**Tests:** `pytest tests/unit/ui/ -x`
- [ ] Verify `add_preset()` has zero callers (only `save_preset()` should be used)
- [ ] If zero callers: remove the `add_preset()` method alias (~lines 63-64)
- [ ] If callers exist: update them to use `save_preset()` directly, then remove alias
- [ ] Run tests: `pytest tests/unit/ui/ -x`
**Notes:** "Alias for save_preset for backward compatibility"

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
