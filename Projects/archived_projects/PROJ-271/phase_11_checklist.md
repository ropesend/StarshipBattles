# Phase 11: Test hardening (audit follow-up)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 11`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** LOW (test additions; no production code changes)
**Depends On:** Phase 7 (stack_group fix), Phase 9 (compiler cleanup)
**Objective:** Close test coverage gaps identified by the test-coverage skeptic audit. Prevents regressions in the areas where current tests can be trivially defeated or where edge cases aren't covered.

## Context

Test skeptic audit (2026-04-13) findings to address:
- H1: `test_no_placeholder_from_any_real_complex` uses hardcoded list (10 designs). New designs added to disk are invisible.
- H2: No test locks ModifierStack external entry lifecycle.
- H3: `TestNoDirectBattleEngineConstruction` whitelist can grow silently.
- M4 (E2E): No 3+ team battle test — routing assumption unverified.
- N1: No UI-level modifier-number render test (covered by Phase 8).
- N2: No save/load test asserts `external_stats` is NOT serialized. Real Rule-3 leak risk.
- N3: No test proves `FleetAuraManager._apply_bonuses` actually invokes `recalculate_stats`.
- Ship-plumbing gaps: negative bonus, mid-damage recalc, component-destruction-with-bonus, triple-stack.

## Tasks

### Task 11.1: Glob-based complex survey test [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [ ] Modify `test_no_placeholder_from_any_real_complex` (in `TestBattleSetupCompilerBehavioralStatKeys`) to glob `data/designs/qs_*_complex.json` instead of using a hardcoded list.
- [ ] Filter to only scope-affecting complexes (those containing `ShieldModifier`, `DamageModifier`, or `ShieldProjection` in any component's abilities).
- [ ] Any new complex added to disk is now automatically checked.

### Task 11.2: Whitelist meta-assertion [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [ ] Add `test_whitelist_has_exactly_three_entries` to `TestNoDirectBattleEngineConstruction`. Asserts `len(WHITELIST_FILES) == 3`.
- [ ] Same for any other whitelist-based guard — forces explicit review if an entry is added.

### Task 11.3: 3+ team routing test [Medium]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [ ] Write test: `ModifierStack(per_team={0: ..., 1: ..., 2: ...})` → ships on 3 different teams all get the right external_stats.
- [ ] Write test: Battle Setup `_NUM_TEAMS = 2` assumption — if a 3+ team battle reached the compiler today, what happens? Document the expected failure mode (either loud crash or missing route). If missing route, add a NotImplementedError explicit guard in `_route_team_for_scope`.

### Task 11.4: external_stats save/load leak guard [Medium]
**File:** `tests/unit/simulation/test_ship_serialization.py` (or similar)

- [ ] Write test: a ship with `external_stats = {"shield_bonus_add": 50}` → serialize via ShipSerializer → deserialize → new ship's `external_stats == {}`.
- [ ] Locks the invariant: external_stats is battle-scoped composition, never persisted.
- [ ] Add regression guard grep: `external_stats` must not appear in `ShipSerializer.to_dict`.

### Task 11.5: FleetAuraManager invokes recalculate_stats [Simple]
**File:** `tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py`

- [ ] Write a test using a `MagicMock` ship with a `recalculate_stats` method. Apply a modifier. Assert `recalculate_stats.assert_called()` after `initialize`.
- [ ] Locks the wiring between FleetAuraManager._apply_bonuses and Ship.recalculate_stats.

### Task 11.6: Ship-plumbing edge cases [Medium]
**File:** `tests/unit/simulation/entities/test_ship_shield_bonus_add.py`

- [ ] Mid-battle recalc: ship takes damage → current_shields drops; apply flat bonus mid-battle; recalculate_stats → max_shields should raise WITHOUT auto-refilling current_shields past the new max.
- [ ] Negative bonus: `shield_bonus_add = -20` → max_shields = max(0, base - 20). Is that the desired semantic? Document and test.
- [ ] Triple-stack: simultaneous `shield_bonus_add`, `shield_capacity_mult`, `capacity_mult` (component-local) — verify pipeline ordering.

### Task 11.7: Battle Setup compiler edge cases [Medium]
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`

- [ ] Test: complex with design_id that doesn't exist → warning logged, no entries, no crash.
- [ ] Test: complex whose component isn't in registry → skipped silently.
- [ ] Test: ability_data as string (malformed) → gracefully skipped.
- [ ] Test: booster on side 0 + suppressor on side 0 → entries correctly split across per_team[0] (booster) and per_team[1] (suppressor).
- [ ] Test: same complex toggled on BOTH sides → each side's entries routed correctly.

### Task 11.8: Regression gate [Simple]

- [ ] `pytest tests/ --tb=no -q` — net delta vs baseline documented in Notes.
- [ ] No new regressions.

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] New tests cover all audit-identified gaps
- [ ] Regression gate green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
