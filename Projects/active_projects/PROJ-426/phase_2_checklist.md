# Phase 2: Extract pure builders out of `spec_compiler.py`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-426 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/strategy/combat/team_spec_builder.py` (NEW)
- `game/strategy/combat/strategy_modifier_stack_builder.py` (NEW)
- `game/strategy/combat/post_battle_hook_builder.py` (NEW)
- `tests/unit/strategy/combat/test_team_spec_builder.py` (NEW — red FIRST)
- `tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py` (NEW — red FIRST)
- `tests/unit/strategy/combat/test_post_battle_hook_builder.py` (NEW — red FIRST)
- `tests/unit/strategy/combat/test_fighter_group_combat_join.py` (MIGRATE — target `TeamSpecBuilder`)
- `tests/unit/strategy/combat/test_satellite_group_combat_join.py` (MIGRATE — target `TeamSpecBuilder`)
- `game/strategy/combat/spec_compiler.py` (edit — delegate to new builders)

**Objective:** Move large cohesive helpers out of the spec compiler before changing the adapter. `spec_compiler.py` delegates to new builders but still writes the four side-channels for compat. The two `*_combat_join.py` tests that pin on the private `_split_mine_groups_from_fleets` helper migrate **in this same phase** — do NOT re-export the old private helper.

---

## Reading

- [x] Re-read [TD-01 source plan §"Phase 2"](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-01_battle_spec_compilation.md).
- [x] Read [design.md §"Test Migration Plan"](design.md) — the Phase 2 row covers the two `*_combat_join.py` tests.
- [x] Read [decisions.md row "Migrate tests... in the same phase"](decisions.md).
- [x] Locate the existing helpers in `spec_compiler.py`: `_team_spec_for_fleet_group` (lines 166-190 region), `_pick_formation_for_fleet`, `_ship_spec_from_instance`, `_split_mine_groups_from_fleets` (lines 430-451), `_build_modifier_stack`, `_entries_from_sector_effects`, `_entries_from_fleet_combat_modifiers`, `_build_strategy_post_battle_hook` (lines 245-251 caller; helper at later line).

---

## Tasks

### Task 2.1: Add red tests for `TeamSpecBuilder` [Medium]
**File:** `tests/unit/strategy/combat/test_team_spec_builder.py` (NEW)
**Tests:** `pytest tests/unit/strategy/combat/test_team_spec_builder.py -x`

- [x] Import `from game.strategy.combat.team_spec_builder import TeamSpecBuilder` (red — module does not yet exist).
- [x] Add tests covering: fleet grouping by `owner_id`, mine-group split (covers the existing `_split_mine_groups_from_fleets` behavior — see migrating `*_combat_join.py` tests for the canonical shape), team spec assembly for a single owner, formation selection per fleet, `_ship_spec_from_instance` extraction shape.
- [x] Run; confirm all red for the right reason.

**Notes:**

### Task 2.2: Implement `TeamSpecBuilder` [Medium]
**File:** `game/strategy/combat/team_spec_builder.py` (NEW)
**Tests:** Task 2.1 tests + existing `test_spec_compiler.py`, `test_spec_compiler_formation.py`

- [x] Move (do NOT duplicate) `_team_spec_for_fleet_group`, `_pick_formation_for_fleet`, `_ship_spec_from_instance`, `_split_mine_groups_from_fleets` from `spec_compiler.py` into `TeamSpecBuilder`. Promote `_split_mine_groups_from_fleets` to a public method (e.g., `split_mine_groups(fleets) -> tuple[list[Fleet], list[Fleet]]`).
- [x] Update `spec_compiler.py` to delegate to `TeamSpecBuilder` for these concerns.
- [x] **Do NOT re-export** `_split_mine_groups_from_fleets` from `spec_compiler` (no compat shims).
- [x] Run Task 2.1 tests; confirm green. Run existing compiler + formation tests; still green.

**Notes:**

### Task 2.3: Migrate `*_combat_join.py` tests to `TeamSpecBuilder` [Medium]
**File:** `tests/unit/strategy/combat/test_fighter_group_combat_join.py` (MIGRATE), `tests/unit/strategy/combat/test_satellite_group_combat_join.py` (MIGRATE)
**Tests:** `pytest tests/unit/strategy/combat/test_fighter_group_combat_join.py tests/unit/strategy/combat/test_satellite_group_combat_join.py -x`

- [x] Replace `from game.strategy.combat.spec_compiler import _split_mine_groups_from_fleets` with `from game.strategy.combat.team_spec_builder import TeamSpecBuilder`.
- [x] Update each call site to use the new public method on `TeamSpecBuilder`.
- [x] Run both test files; confirm green.

**Notes:**

### Task 2.4: Add red tests + implement `StrategyModifierStackBuilder` [Medium]
**File:** `tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py` (NEW), `game/strategy/combat/strategy_modifier_stack_builder.py` (NEW)
**Tests:** `pytest tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py -x`

- [x] Write red tests covering environmental-effect translation, per-team modifier translation, modifier-stack assembly order.
- [x] Move `_build_modifier_stack`, `_entries_from_sector_effects`, `_entries_from_fleet_combat_modifiers` from `spec_compiler.py` into `StrategyModifierStackBuilder`.
- [x] `spec_compiler.py` delegates.
- [x] Run; confirm green. Run existing compiler tests; still green.

**Notes:**

### Task 2.5: Add red tests + implement `PostBattleHookBuilder` [Medium]
**File:** `tests/unit/strategy/combat/test_post_battle_hook_builder.py` (NEW), `game/strategy/combat/post_battle_hook_builder.py` (NEW)
**Tests:** `pytest tests/unit/strategy/combat/test_post_battle_hook_builder.py -x`

- [x] Write red tests covering the closure construction (NOT the writeback behavior — that stays pinned by `test_post_battle_hook.py`).
- [x] Move `_build_strategy_post_battle_hook` from `spec_compiler.py` into `PostBattleHookBuilder`.
- [x] Update `game/strategy/combat/post_battle_hook.py` imports if extraction requires.
- [x] Run; confirm green. Run existing `test_post_battle_hook.py`; still green.

**Notes:**

### Task 2.6: Sweep + commit Phase 2 [Simple]
**File:** N/A
**Tests:** `pytest tests/unit/strategy/combat/ -x`

- [x] Run the entire `tests/unit/strategy/combat/` directory.
- [x] Confirm `rg "_split_mine_groups_from_fleets" tests` returns zero hits (helper is fully migrated).
- [x] Confirm `spec_compiler.py` still writes the four side-channels (still needed for Phase 3).
- [x] Commit: `PROJ-426 phase 2: extract TeamSpecBuilder, StrategyModifierStackBuilder, PostBattleHookBuilder`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All Phase 2 task checkboxes checked.
- [x] `spec_compiler.py` delegates team/modifier/hook work to the three new builders.
- [x] No tests import `_split_mine_groups_from_fleets`.
- [x] All `tests/unit/strategy/combat/` tests pass.
- [x] Side-channel writes still present (intentional for this phase).
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 3.
