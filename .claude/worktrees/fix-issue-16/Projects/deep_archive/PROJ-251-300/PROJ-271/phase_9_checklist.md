# Phase 9: Resolve `_entries_from_modifier_source` dead-with-landmine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** LOW (investigation + targeted delete or wire)
**Depends On:** None
**Objective:** `game/strategy/combat/spec_compiler.py::_entries_from_modifier_source` still emits `stat_key="placeholder"` for `sector.modifiers` / `system.modifiers` / `empire.combat_modifiers` iterables. Production currently passes None (confirmed by Phase 2 testing — no placeholder warnings logged in full regression). BUT: if ANY future code populates these fields, strategic modifiers will silently drop — reproducing the exact PROJ-269 bug class.

Either (a) delete the helper + prove no production code populates the fields, or (b) wire the helper to real stat_key mapping.

## Context

Architecture skeptic audit (2026-04-13) finding H4: "dead-with-landmine". The helper is called only when `sector`, `system`, or `empire` objects carry a `modifiers` / `combat_modifiers` attribute with at least one entry. Audit confirmed no production code currently populates these attributes. But the silent-drop failure mode is preserved by keeping the placeholder emission.

## Tasks

### Task 9.1: Audit current populators [Simple]
**File:** grep across `game/`

- [ ] Find every place where a `sector` object's `modifiers` attribute is set/appended to.
- [ ] Same for `system.modifiers`, `empire.combat_modifiers`.
- [ ] Document in Notes: "currently populated by: X / not populated by any production code".

### Task 9.2: Decide and execute [Medium]
**File:** `game/strategy/combat/spec_compiler.py` (+ tests)

Based on 9.1:

**If NO populators exist:**
- [ ] Delete `_entries_from_modifier_source` entirely.
- [ ] Delete the two call sites in `_build_modifier_stack` (lines ~319, 322).
- [ ] Update regression guard to grep for `stat_key="placeholder"` across the entire strategy compiler (previously only scanned `_entries_from_fleet_combat_modifiers`).
- [ ] Run — the zero-placeholder-in-strategy-compiler test should now PASS cleanly.

**If populators exist:**
- [ ] Design a real stat_key mapping for each modifier source type.
- [ ] Wire similar to `_entries_from_fleet_combat_modifiers` — real `_real_entry` calls with correct stat_key + value + operation.
- [ ] Add behavioral test in `test_unified_entry_guard.py` proving the populated source emits a real entry.

### Task 9.3: Extend placeholder regression guard [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [ ] Once `_entries_from_modifier_source` is gone or wired, add a CLASS-LEVEL guard: no `stat_key="placeholder"` emission anywhere in `game/strategy/combat/spec_compiler.py` (not just per-function). Prevents new placeholders from sneaking back in.

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Strategy compiler emits zero placeholder entries (or each remaining placeholder has a specific, documented follow-up)
- [ ] Extended regression guard
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
