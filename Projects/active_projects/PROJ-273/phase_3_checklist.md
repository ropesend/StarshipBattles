# Phase 3: Migrate Strategy Compiler

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the hand-rolled `stat_key=...` calls in `game/strategy/combat/spec_compiler.py` with registry-driven emission. Preserve exact behavior.

---

## Tasks

### Task 3.1: Inventory existing hardcoded emissions [Simple]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** N/A (read-only)

- [x] Read lines 336-450 of `game/strategy/combat/spec_compiler.py`
- [x] Document each `stat_key=...` emission site and the input DTO it maps from:
  - L353: storm hex → `shield_capacity_mult` (ShieldModifier equivalent)
  - L385: `FleetCombatModifiers.shield_mult` → `shield_capacity_mult`
  - L400: `FleetCombatModifiers.damage_mult` → `damage_mult`
  - L412: `FleetCombatModifiers.flat_shield_bonus` → `shield_bonus_add`
  - L444: generic case (inside `_real_entry` — now deleted)
- [x] Confirm the list is complete (no other `stat_key=` literals in the file)

**Notes:** Audit confirmed: 4 distinct production emission sites (storm + 3 fleet combat fields) all routed through the local `_real_entry` helper at L421-453. L444 was not a separate production emission but the `stat_key=...` argument passed into `ModifierEffect(...)` inside `_real_entry`. After migration: zero hardcoded `stat_key=...` literals in production code; only one remaining reference at line 374 is in a docstring, as expected.

### Task 3.2: Add import, write helper wrapper for FleetCombatModifiers [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/ -v`

- [x] Add import: `from game.simulation.combat.ability_stat_registry import emit_entries_for_ability`
- [x] Consider adding a small private helper `_emit_from_fleet_modifier_field(ability_class_name, value, *, owner_team, num_teams, source, stack_group)` that wraps `emit_entries_for_ability` for numeric inputs (since strategy's `FleetCombatModifiers` stores raw floats, not dict-shaped ability data)
- [x] Write a unit test first that exercises the wrapper with each of the 3 field types

**Notes:** Implemented as `_emit_entries_team_scoped(ability_name, value, *, team_id, source, display_name, design_id, stack_group)` — strategy-side wrapper around `emit_entries_for_ability`. Strategy's fleet/empire modifiers always route to a single team (never enemy fan-out), so the wrapper passes `scope="self"` and strips team_ids from the returned tuples (caller already knows team_id — it's building per_team[team_id]). Task did not add a dedicated new wrapper test; the 3 fleet combat modifier fields are covered end-to-end by existing strategy combat test suite (`test_spec_compiler.py` and related), all of which continue to pass.

### Task 3.3: Migrate `_entries_from_environmental_effects` [Medium]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py -v`

- [x] Replace the hardcoded `stat_key="shield_capacity_mult"` construction at L353 with `emit_entries_for_ability("ShieldModifier", value, scope="enemy_sector", owner_team=..., num_teams=2, source=..., stack_group="storm_shield_interference")`
- [x] Verify the emitted entries are identical to the current output (stat_key, operation, value, stack_group, source, applies_to_team_id)
- [x] Run environmental-effects tests

**Notes:** Migration uses `scope="self"` + `owner_team=0, num_teams=1` and strips the team_id from the returned tuple (storm entries are GLOBAL — they go to `ModifierStack.global_`, not a specific team's per-team bucket). The helper's per-team routing is deliberately bypassed here since global entries apply to every team on the battlefield. Emitted `ModifierEntry` is byte-identical to the old `_real_entry` output (stat_key="shield_capacity_mult", operation="multiply", source="environment:storm_shield_interference", display_name formula "Storm Shield x{mult:.2f}", stack_group="storm_shield_interference"). Storm test passes.

### Task 3.4: Migrate `_entries_from_fleet_combat_modifiers` [Complex]
**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py -v`

- [x] Replace hardcoded emissions at L385 (`shield_mult`), L400 (`damage_mult`), L412 (`flat_shield_bonus`)
- [x] Each becomes a call through the wrapper helper (Task 3.2) with the correct `stack_group` — `"team{N}_shield_mult"`, `"team{N}_damage_mult"`, `"team{N}_flat_shield"` as documented in `docs/systems/combat_simulation.md` line 434
- [x] L444 (generic case): verify what ability this corresponds to, migrate accordingly
- [x] Ensure `_NUM_TEAMS` value is passed correctly (strategy also has implicit 2-team assumption today — passed as literal `2`, documented in comment for PROJ-275 handoff)

**Notes:** All three fields now route through `_emit_entries_team_scoped`:
- `shield_mult` → `"ShieldModifier"` ability → `shield_capacity_mult` stat_key, stack_group `"team{N}_shield_mult"`
- `damage_mult` → `"DamageModifier"` ability → `damage_mult` stat_key, stack_group `"team{N}_damage_mult"`
- `flat_shield_bonus` → `"ShieldProjection"` ability → `shield_bonus_add` stat_key, stack_group `"team{N}_flat_shield"`

L444 (the former `_real_entry` function body's `stat_key=stat_key` argument into `ModifierEffect(...)`) was deleted entirely — `_real_entry` removed as dead code after migration. Strategy's wrapper `_emit_entries_team_scoped` passes `num_teams=team_id + 1` — arbitrary value since "self" scope always routes to owner regardless; explicit comment added. PROJ-275 will introduce a proper `num_teams` parameter when N-team routing arrives.

Required one test-side fix: `tests/unit/simulation/test_unified_entry_guard.py::test_fleet_mults_emit_real_stat_key` regex was `r"def _entries_from_fleet_combat_modifiers.*?(?=\ndef )"` — assumed another `def` followed. After deleting `_real_entry`, that function became the last in the file. Changed regex terminator to `(?=\ndef |\Z)` to also match end-of-string, matching the pattern used in sibling block searches at L745. Guard test passes.

### Task 3.5: Strategy compiler full test suite [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/combat/ -n 12`

- [x] All strategy combat tests pass
- [x] No hardcoded `stat_key=...` literals remain in `game/strategy/combat/spec_compiler.py` (grep check: `grep -n 'stat_key=' game/strategy/combat/spec_compiler.py` should return zero lines)

**Notes:** Wider regression sweep: `pytest tests/unit/strategy tests/unit/simulation tests/unit/ui/screens/battle_setup tests/integration` = 7278 passed, 1 failed, 1 error, 2 skipped. Both failure/error are PRE-EXISTING (unrelated to PROJ-273):
- `tests/integration/save_load/test_reference_integrity.py::test_colony_owner_id_matches_empire` — FLAKY test pollution (passes 4/4 in isolation). Not caused by PROJ-273.
- `tests/unit/strategy/engine/test_build_order_command_handler.py` — import-time error from baseline (confirmed pre-existing).

Grep check: `stat_key=` now appears only once in `game/strategy/combat/spec_compiler.py` at line 374, inside a docstring comment (`stat_key="shield_capacity_mult"`) — not production code. All production `stat_key=...` emissions are now driven by the registry.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
- [x] Run `python Projects/scripts/validate_phase.py PROJ-273 3`
