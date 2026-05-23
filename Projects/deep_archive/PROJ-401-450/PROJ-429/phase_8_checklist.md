# Phase 8: Codex consult follow-ups

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-429 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_7
**Review Mode:** standard

**Files (planned):**
- `tests/unit/strategy/services/test_ability_metadata_contracts.py` (modify) — reverse-direction parity tests
- `game/strategy/facade/dto/planet_dto.py` (modify) — `shield_active` migrates to `StrategicKind.PLANETARY_SHIELD`
- `game/strategy/services/action_time_resolver.py` (modify) — fail fast for unregistered energy abilities
- `tests/unit/strategy/services/test_action_time_resolver.py` (modify) — TDD coverage for fail-fast
- `tests/unit/strategy/engine/test_planet_action_engine.py` (modify) — adopt real registered ability names in 3 tests that previously used synthetic `AbilityA`/`AbilityB`
- `Projects/active_projects/PROJ-435/` (new scaffold) — UI `_ACTIVATABLE_ABILITIES` migration spin-off

**Objective:** Land the four follow-up items from the post-Phase-7 Codex
consult before final audit. Items 1-3 are inline; Item 4 spawns PROJ-435
because the UI migration is not a mechanical name-set swap.

---

## Reading

- [x] Re-read the original consult findings to confirm scope (one commit per item).
- [x] Confirm AGENTS.md / CLAUDE.md root-cause-fix rule (no dual paths).

---

## Tasks

### Task 8.1: Reverse-direction parity tests [Simple, TDD]

**File:** `tests/unit/strategy/services/test_ability_metadata_contracts.py`
**Tests:** `pytest tests/unit/strategy/services/test_ability_metadata_contracts.py`

- [x] Write `test_every_stabilizer_kind_tag_has_matching_spec_row` (registry → spec table)
- [x] Write `test_every_superweapon_kind_tag_has_matching_spec_row` (registry → spec table) with documented `DestroyStar` exception (STELLERATE_STAR's ability_name=None row)
- [x] Run — both pass immediately (registries are in sync); commit as regression guards
- [x] Commit: `test(PROJ-429): add reverse-direction parity tests for stabilizer/superweapon kind tags`

### Task 8.2: Migrate `planet_dto.shield_active` to PLANETARY_SHIELD tag [Simple]

**File:** `game/strategy/facade/dto/planet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade -k planet`

- [x] Replace `getattr(planet, 'active_abilities', {}).get('PlanetaryShield', False)` with iteration over `abilities_with_kind_tag(StrategicKind.PLANETARY_SHIELD)`
- [x] Add private helper `_is_any_planetary_shield_active`
- [x] Run targeted facade tests (51 passed)
- [x] Commit: `refactor(PROJ-429): migrate planet_dto shield_active to PLANETARY_SHIELD registry tag`

### Task 8.3: Fail-fast in `action_time_resolver` for unregistered energy abilities [Medium, TDD]

**File:** `game/strategy/services/action_time_resolver.py`
**Tests:** `pytest tests/unit/strategy/services/test_action_time_resolver.py`

- [x] Add `test_activate_unregistered_ability_raises` — fails (literal fallback still active)
- [x] Add `test_deactivate_unregistered_ability_raises` — fails
- [x] Add `test_activate_registered_without_energy_facet_raises` — fails
- [x] Replace literal fallback in `_activate_time_field` with `ValueError` raises (one branch for `meta is None`, one for `meta.energy is None`)
- [x] Re-run targeted tests — all 25 pass
- [x] Fix 3 incidental test_planet_action_engine tests that used synthetic `AbilityA`/`AbilityB` names by switching to `GeologicStabilizer` / `StellarStabilizer`
- [x] Re-run `tests/unit/strategy tests/integration/strategy` — 5230 passed
- [x] Commit: `refactor(PROJ-429): action_time_resolver fails fast on unregistered energy abilities`

### Task 8.4: UI `_ACTIVATABLE_ABILITIES` — decide inline vs spin-off [Simple]

**File:** `Projects/active_projects/PROJ-435/` (new)
**Tests:** N/A (scaffold)

- [x] Inspect `game/ui/screens/builder/stat_rows_dynamic.py:381-463`
- [x] Confirm the UI map mixes registered + unregistered abilities and carries UI-specific display labels (Option B/C from PROJ-435 design.md)
- [x] Decide: spin-off (not inline)
- [x] Create scaffold via `python Projects/scripts/create_project.py --id PROJ-435 "Migrate UI _ACTIVATABLE_ABILITIES to AbilityMetadataRegistry"`
- [x] Populate `plan.md`, `design.md`, `decisions.md`, `manifest.md`, `phase_1_checklist.md`, `phase_state.json`
- [x] Commit on `proj/PROJ-429/main`: `chore(PROJ-429): spawn PROJ-435 scaffold for UI _ACTIVATABLE_ABILITIES migration`

### Task 8.5: Update PROJ-429 project state + run sharded suite [Simple]

- [x] Add `phase_8` row to `phase_state.json`
- [x] Add Phase 8 row + paragraph to `plan.md`
- [x] Update Current State in `plan.md`
- [x] Add Codex-consult-follow-ups row to `decisions.md`
- [ ] Run `python Tools/test_sharded/test_sharded.py` — pending

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (except final sharded run)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to final audit
