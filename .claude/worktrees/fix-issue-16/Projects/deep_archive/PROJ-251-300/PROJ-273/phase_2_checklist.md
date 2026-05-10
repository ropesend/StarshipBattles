# Phase 2: Migrate Battle Setup Compiler

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-273 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace Battle Setup's local `_ABILITY_TO_STAT_KEY` dict with the shared registry. Preserve exact emission behavior.

---

## Tasks

### Task 2.1: Delete local `_ABILITY_TO_STAT_KEY` [Simple]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [x] Remove `_ABILITY_TO_STAT_KEY = {...}` definition at lines 67-74 (the dict and its PROJ-271 Phase 2.4 comment)
- [x] Add import: `from game.simulation.combat.ability_stat_registry import ABILITY_STAT_REGISTRY, emit_entries_for_ability, OPPONENT_SCOPES`
- [x] Run existing compiler tests — many may fail with `NameError` on `_ABILITY_TO_STAT_KEY` references

**Notes:** Also removed local `_OPPONENT_SCOPES` constant (L78) — now imported from the registry as `OPPONENT_SCOPES` (single source of truth). Also removed unused `ModifierEffect` import at L58 (the helper now owns ModifierEffect construction). IDE correctly flagged stale references in `_complex_to_entries` and `_route_team_for_scope` — addressed in Task 2.2 + one-line fix to `_route_team_for_scope`.

### Task 2.2: Migrate `_complex_to_entries` to use shared helper [Medium]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ -v`

- [x] At line ~349: replace `if ability_name not in _ABILITY_TO_STAT_KEY:` with `if ability_name not in ABILITY_STAT_REGISTRY:`
- [x] At line ~354: replace tuple-unpacking `stat_key, operation = _ABILITY_TO_STAT_KEY[ability_name]` — instead, pass ability through to `emit_entries_for_ability`
- [x] Refactor the inner loop body to delegate to `emit_entries_for_ability(ability_name, ability_data, scope=scope_str, owner_team=owner_team, num_teams=_NUM_TEAMS, source=f"{scope_prefix}:complex:{design_id}:{ability_name}", stack_group=...)`
- [x] Preserve the existing stack_group computation (if any) and pass through
- [x] Verify manual inspection: no remaining references to `_ABILITY_TO_STAT_KEY` in the file

**Notes:** The migration also enabled removal of the now-dead-code helper `_extract_ability_value` — the registry helper's internal `_extract_value` handles the same extraction logic per Clean-Sheet rule. Inner loop body shrank from ~25 lines of explicit `ModifierEffect` / `ModifierEntry` construction to a single `out.extend(emit_entries_for_ability(...))` call. Kept `if scope_str == "self": continue` guard in the caller (helper intentionally doesn't filter scope="self" — caller decides whether self-scoped abilities are team-scoped or component-local). Also fixed `_route_team_for_scope` at L452 to use `OPPONENT_SCOPES` (registry import) rather than the deleted local `_OPPONENT_SCOPES`.

### Task 2.3: Run Battle Setup test suite [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/ui/screens/battle_setup/ tests/integration/ui/screens/battle_setup/ -n 12`

- [x] All Battle Setup tests pass
- [x] If any test was asserting the dict presence (e.g. `_ABILITY_TO_STAT_KEY`), either update it to assert via registry or remove (it's internal detail)

**Notes:** 30/30 Battle Setup unit tests passed (integration/ui/screens/battle_setup/ does not exist — unit suite is the coverage). Wider sweep across `tests/unit/ui/screens/battle_setup tests/unit/simulation/combat tests/unit/strategy/combat tests/unit/simulation/test_unified_entry_guard.py` was 405/405 passing in 4.48s. No test asserted `_ABILITY_TO_STAT_KEY` presence directly — internal refactor landed clean. The 4 `_route_team_for_scope` tests in `test_spec_compiler.py:359-383` still pass (PROJ-275 will change the signature; PROJ-273 preserved it).

### Task 2.4: Regression guard — `qs_*_complex` designs still compile [Simple]
**File:** N/A (uses existing `test_unified_entry_guard.py`)
**Tests:** `pytest tests/unit/simulation/test_unified_entry_guard.py -v`

- [x] Existing placeholder-survey test passes (confirms no drift in emitted entries)
- [x] If the test fails, diff the emitted `ModifierEntry` list before/after and correct the shared helper

**Notes:** 4/4 unified entry guard tests passed. Emitted `ModifierEntry` list is identical to pre-migration behavior — the registry helper produces byte-identical `ModifierEffect` + `ModifierEntry` objects from the same inputs.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
- [x] Run `python Projects/scripts/validate_phase.py PROJ-273 2`
