# Phase 2: Migrate Battle Setup Compiler

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace Battle Setup's local `_ABILITY_TO_STAT_KEY` dict with the shared registry. Preserve exact emission behavior.

---

## Tasks

### Task 2.1: Delete local `_ABILITY_TO_STAT_KEY` [Simple]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [ ] Remove `_ABILITY_TO_STAT_KEY = {...}` definition at lines 67-74 (the dict and its PROJ-271 Phase 2.4 comment)
- [ ] Add import: `from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY, emit_entries_for_ability`
- [ ] Run existing compiler tests — many may fail with `NameError` on `_ABILITY_TO_STAT_KEY` references

**Notes:**

### Task 2.2: Migrate `_complex_to_entries` to use shared helper [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [ ] At line ~349: replace `if ability_name not in _ABILITY_TO_STAT_KEY:` with `if ability_name not in ABILITY_STAT_REGISTRY:`
- [ ] At line ~354: replace tuple-unpacking `stat_key, operation = _ABILITY_TO_STAT_KEY[ability_name]` — instead, pass ability through to `emit_entries_for_ability`
- [ ] Refactor the inner loop body to delegate to `emit_entries_for_ability(ability_name, ability_data, scope=scope_str, owner_team=owner_team, num_teams=_NUM_TEAMS, source=f"{scope_prefix}:complex:{design_id}:{ability_name}", stack_group=...)`
- [ ] Preserve the existing stack_group computation (if any) and pass through
- [ ] Verify manual inspection: no remaining references to `_ABILITY_TO_STAT_KEY` in the file

**Notes:**

### Task 2.3: Run Battle Setup test suite [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ tests/integration/ui/screens/battle_setup/ -n 12`

- [ ] All Battle Setup tests pass
- [ ] If any test was asserting the dict presence (e.g. `_ABILITY_TO_STAT_KEY`), either update it to assert via registry or remove (it's internal detail)

**Notes:**

### Task 2.4: Regression guard — `qs_*_complex` designs still compile [Simple]
**File:** N/A (uses existing `test_unified_entry_guard.py`)
**Tests:** `pytest tests/unit/simulation/test_unified_entry_guard.py -v`

- [ ] Existing placeholder-survey test passes (confirms no drift in emitted entries)
- [ ] If the test fails, diff the emitted `ModifierEntry` list before/after and correct the shared helper

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-273 2`
