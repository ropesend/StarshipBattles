# Phase 2: Both spec compilers emit real stat_keys for all remaining placeholder entries

> **SCOPE EXTENDED 2026-04-12:** Originally just `flat_shield_bonus` on the
> strategy compiler. PROJ-270 Phase 9 audit surfaced that the Battle Setup
> compiler (`game/ui/screens/battle_setup/spec_compiler.py::_complex_entries`)
> also emits `stat_key="placeholder"` for EVERY complex toggle (shield booster,
> damage booster, suppressors, etc.). Phase 2 now covers both compilers.


> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-271 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** LOW (follows Track A Phase 6.2 pattern from PROJ-270)
**Depends On:** Phase 1 (needs `SHIELD_BONUS_ADD` stat_key registered)
**Objective:** Strategy compiler emits `ModifierEntry(stat_key="shield_bonus_add", value=planet.modifiers.flat_shield_bonus, operation="add")` instead of the current `stat_key="placeholder"` stub. Visible effect: planets with a flat-shield-bonus aura actually buff the friendly fleet's ship `max_shields` in combat.

---

## Tasks

### Task 2.1: Replace placeholder entry with real stat_key [Simple]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/simulation/test_unified_entry_guard.py --tb=short`

- [x] Locate the current `flat_shield_bonus` emission in `_entries_from_fleet_combat_modifiers` (line 420-429 — the `if flat_shield:` block using `_placeholder_entry`)
- [x] Write failing test `test_fleet_compiler_emits_shield_bonus_add` in `TestStrategyCompilerBehavioralStatKeys` asserting the compiler emits `ModifierEntry(stat_key="shield_bonus_add", value=50.0, operation="add")` when `FleetCombatModifiers.flat_shield_bonus=50`.
- [x] Run — failed: `assert shield_bonus, "Expected at least one shield_bonus_add entry..."`
- [x] Replace the placeholder with `_real_entry(stat_key="shield_bonus_add", value=flat_shield, operation="add")`
- [x] Remove the "PROJ-271 deferred" comment
- [x] Run — passes

**Notes:** Uses the existing `_real_entry` helper (added PROJ-270 Phase 6.1) — no helper changes needed, just pass `operation="add"`.

---

### Task 2.2: End-to-end compiler → pipeline test [Medium]
**File:** `tests/integration/strategy/combat/test_storm_shield_interference.py` (extend)
**Tests:** `pytest tests/integration/strategy/combat/test_storm_shield_interference.py --tb=short`

- [x] Add `test_flat_shield_bonus_raises_max_shields` — direct `shield_bonus_add=75` ModifierStack entry → ship `max_shields = 500 + 75 = 575` after `run_battle`. Opposing team must be unaffected (`max_shields == 500`).
- [x] Add `test_flat_shield_bonus_with_storm_mult_composes_correctly` — `shield_bonus_add=50` + `shield_capacity_mult=0.5` → `(500 + 50) × 0.5 = 275`. Locks pipeline ordering end-to-end.
- [x] Add `test_flat_shield_bonus_via_compiler_helper` — calls `_entries_from_fleet_combat_modifiers(FleetCombatModifiers(flat_shield_bonus=100), team_id=0)` and runs the resulting `ModifierStack` through `run_battle`. `max_shields == 600`.
- [x] Run — all 3 new tests pass; existing 3 tests still pass (6/6 total in file).

**Notes:** E2E tests bundled into the existing storm shield interference file per PROJ-270 decision (Track A + Track B modifier tests co-located).

---

### Task 2.3: Regression guard in `test_unified_entry_guard.py` [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [x] Extended `TestNoPlaceholderStatKeyInStrategyCompiler::test_fleet_mults_emit_real_stat_key` to also scan the `if flat_shield:` block for `placeholder` substring. Removed the "flat_shield_bonus is intentionally still placeholder (PROJ-271 deferred)" allowance.
- [x] Behavioral assertion already in Task 2.1's `test_fleet_compiler_emits_shield_bonus_add` — asserts `stat_key != "placeholder"` and value/operation are correct.

**Notes:** Both text-based and behavioral guards cover the new stat_key. 17/17 tests in test_unified_entry_guard.py green.

---

### Task 2.4: Battle Setup complex toggles — parse design JSON, map ability → stat_key [Complex] — REVISED 2026-04-13
**File:** `game/ui/screens/battle_setup/spec_compiler.py:258-294` (`_complex_entries`)
**Tests:** `pytest tests/unit/ui/battle_setup/ --tb=short` (create test file if missing)

**Scope correction:** The original checklist proposed a `design_id → (stat_key, value, operation)` lookup table from `data/modifiers.json`. That file defines component-mount modifiers (hardened_mount, turret_mount) — it does NOT define complex effects. Complex toggles come from `data/designs/qs_*_complex.json`, and their effects are expressed through the design's **components + abilities**, not a lookup table. See [decisions.md](decisions.md) 2026-04-13 "Battle Setup Phase 2.4 parses complex design JSON" entry.

**Scope routing:** A complex ability with scope `enemy_*` (e.g. `qs_sector_damage_suppressor_complex` with `DamageModifier` scoped `enemy_sector`) routes to `per_team[opponent_team_id]`. Scope `player_*`/`allied_*`/`fleet`/`system` routes to `per_team[owner_team_id]`. See Phase 3 for the scope routing logic.

- [x] Audit `data/designs/qs_*_complex.json` for complexes that carry non-SELF-scoped abilities. Document findings in Notes:
  - `qs_sector_shield_projector_complex` (component `sector_shield_projector` → `ShieldProjection` with sector/fleet scope → maps to `shield_bonus_add`)
  - `qs_sector_damage_booster_complex` / `qs_system_damage_booster_complex` → maps to `damage_mult` (with value > 1.0)
  - `qs_sector_damage_suppressor_complex` / `qs_system_damage_suppressor_complex` → maps to `damage_mult` (value < 1.0, scope enemy_*)
  - `qs_sector_shield_booster_complex` / `qs_system_shield_booster_complex` → maps to `shield_capacity_mult` (value > 1.0)
  - `qs_sector_shield_suppressor_complex` / `qs_system_shield_suppressor_complex` → maps to `shield_capacity_mult` (value < 1.0, scope enemy_*)
- [x] Design the ability-class-name → stat_key map at module level (`_ABILITY_TO_STAT_KEY` in spec_compiler.py).
- [x] Write failing test: shield projector → `shield_bonus_add` on `per_team[0]`. (6 failing tests total written before impl.)
- [x] Write failing test for suppressor: damage suppressor on side 0 → `damage_mult` entry on `per_team[1]` (opponent).
- [x] Implement `_complex_to_entries(complex_data, *, scope_prefix, owner_team, registries)`:
  1. Load design JSON via `load_json_required(Paths.STARTER_DESIGNS_DIR/<design_id>.json)`.
  2. Walk all layers' components via `_iter_components`.
  3. Look up each component in `registries.get_components()` (supports dict + Component-object shapes).
  4. For each ability in `_ABILITY_TO_STAT_KEY` with `scope != "self"`, extract value (multiplier/value field) and emit ModifierEntry.
  5. Route team via `_route_team_for_scope(scope_str, owner_team)` — `enemy_*` → opponent, else → owner.
- [x] Verify no placeholder entries remain — all 10 `qs_*_complex` designs survey clean (Task 2.5's behavioral guard).

**Notes:** `_complex_to_entries` returns `List[Tuple[int, ModifierEntry]]` — routing team is per-ability, so one complex can emit entries to BOTH per_team[0] and per_team[1] if it carries mixed scopes. `_build_modifier_stack` pivots the pairs into the final per_team dict. 16/16 tests in test_spec_compiler.py green.

---

### Task 2.5: Extend placeholder-stat_key guard to Battle Setup compiler [Simple] — NEW 2026-04-13
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [x] Added `TestNoPlaceholderStatKeyInBattleSetupCompiler` class — text-based regex over `_complex_to_entries` body; fails if `stat_key="placeholder"` appears.
- [x] Added `TestBattleSetupCompilerBehavioralStatKeys` class — 4 behavioral tests covering shield projector, shield booster > 1, shield suppressor routes to opponent, no-placeholder survey of all 10 complexes.
- [x] Run — 22/22 tests green in test_unified_entry_guard.py (17 pre-existing + 5 new).

**Notes:** Guard is both text-based (regression defense) and behavioral (exercises every complex design). Survey test provides survivorship coverage — any new un-mapped complex added later will fail this test.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Strategy tests green (6/6 integration + 17/17 unified entry guards)
- [x] Battle Setup compiler tests green (16/16 unit tests)
- [x] Placeholder-stat_key regression guard extended to include BOTH compilers + `flat_shield_bonus` + complex toggles (22/22 guard tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
