# Phase 4: End-to-end integration tests + manual smoke

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Mostly Complete (manual smoke user-blocked)
**Risk:** LOW (tests over working code)
**Depends On:** Phases 1 + 2 + 3
**Objective:** Integration-tier coverage for Track A + Track B modifier battle-math end-to-end (real ships, real battles). Includes the `test_storm_shield_interference.py` test deferred from PROJ-270 Task 6.5.

---

## Tasks

### Task 4.1: Storm shield interference integration test [Medium] — PROJ-270 Task 6.5 DEFERRED
**File:** `tests/integration/strategy/combat/test_storm_shield_interference.py` (new)
**Tests:** `pytest tests/integration/strategy/combat/test_storm_shield_interference.py --tb=short`

- [x] File already exists (`tests/integration/strategy/combat/test_storm_shield_interference.py`) from PROJ-270 Phase 9 — 6/6 tests green including `test_shield_capacity_mult_halves_max_shields`, `test_shield_capacity_mult_only_applies_to_target_team`, `test_damage_mult_halves_weapon_damage`.
- [x] Extended with 3 new flat_shield_bonus tests (Phase 2.2).
- [x] Run — 6/6 passes.

**Notes:** Task 4.1 is effectively verification-only because the storm file landed during PROJ-270 Phase 9. Track A + B tests co-located per original plan.

---

### Task 4.2: Flat shield bonus integration test [Medium]
**File:** `tests/integration/strategy/combat/test_flat_shield_bonus.py` (new)

- [x] Created `tests/integration/strategy/combat/test_flat_shield_bonus.py` with 3 tests: direct ModifierStack entry (`test_flat_shield_bonus_appears_in_outcome`), pipeline ordering `(base+flat)×mult` (`test_flat_bonus_and_storm_mult_compose`), strategy compiler helper end-to-end (`test_flat_shield_bonus_from_strategy_compiler_helper`).
- [x] Run — 3/3 passes.

**Notes:** Tests assert `ShipOutcome.max_shields` directly — proves the full pipeline: ModifierStack entry → FleetAuraManager._apply_bonuses → ship.external_stats → ship_stats._apply_aggregated_stats → ShipOutcome.max_shields (serialized through BattleOutcome).

---

### Task 4.3: Suppressor integration test [Medium]
**File:** `tests/integration/strategy/combat/test_suppressor_effects.py` (new)

- [x] Created `tests/integration/strategy/combat/test_suppressor_effects.py` with 3 tests exercising full UI-state → compiler → ModifierStack → run_battle flow:
  - `test_battle_setup_shield_suppressor_targets_opponent_team` — `qs_system_shield_suppressor_complex` on side 0 → side 1 ships have `max_shields=375` (500 × 0.75); side 0 unaffected.
  - `test_battle_setup_shield_booster_targets_owner_team` — `qs_system_shield_booster_complex` on side 0 → side 0 ships have `max_shields=625` (500 × 1.25); side 1 unaffected.
  - `test_battle_setup_shield_projector_gives_flat_bonus_to_owner` — `qs_system_shield_projector_complex` on side 0 → side 0 gains +50 flat; side 1 unaffected.
- [x] Run — 3/3 passes.

**Notes:** These are full UI-to-battle-outcome tests — `BattleSetupState` with toggled complex → `build_manual_battle_spec` → `run_battle` → `BattleOutcome` with correct max_shields per team. Proves scope routing AND the complete Battle Setup pipeline.

---

### Task 4.4: Regression gate + manual launcher smoke [Simple]
**Tests:** Full suites + interactive manual test

- [x] `pytest tests/ --tb=no -q` — 14683 passed (+37 over baseline 14646), 3 pre-existing failures (build queue), 3 pre-existing errors (AI imports), 2 skipped. Full suite in 200s.
- [x] `python -m combat_lab.run_tests --fast --no-history` — **162/162 green**.
- [x] `python -m combat_lab.run_tests --no-history` — **170/170 green**.
- [x] Grep audit: deleted unused `_placeholder_entry` helper from strategy compiler (dead code after Phase 2.1). Remaining `stat_key="placeholder"` emission is in `_entries_from_modifier_source` for ad-hoc `sector.modifiers` / `system.modifiers` dicts — explicitly out of PROJ-271 scope per decisions.md; tracked as follow-up project.
- [ ] Manual smoke (interactive): Strategy fleet battle in a storm hex + with a flat-bonus-aura planet + opposing a suppressor planet. **USER-BLOCKED: requires interactive launcher session.**

**Notes:** Automated gates all green. Manual smoke remains pending — user-only step since it requires the desktop launcher. Documented as outstanding for user verification before archival.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All automated task checkboxes above are checked (manual smoke remains user-blocked)
- [x] 3 integration-tier test files green (`test_storm_shield_interference.py` 6/6, `test_flat_shield_bonus.py` 3/3, `test_suppressor_effects.py` 3/3)
- [x] Full regression gate green (14683 passed / 3 pre-existing fails / 3 pre-existing errors; Combat Lab fast 162/162, full 170/170)
- [ ] Manual launcher smoke verified — **USER-BLOCKED**
- [x] Grep audit: strategy compiler no longer emits placeholder for PROJ-271 sources; remaining placeholder in `_entries_from_modifier_source` explicitly out of scope
- [x] Update status at top of this file to `Complete (pending manual smoke)`
- [x] Update plan.md phase table row to `Complete`
- [ ] PROJ-271 ready for archival via protocol 05 — after manual smoke
