# Phase 1: Introduce typed assembly DTOs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-426 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):**
- `game/strategy/combat/battle_assembly.py` (NEW)
- `tests/unit/strategy/combat/test_battle_assembly.py` (NEW — red tests FIRST)
- `game/strategy/combat/spec_compiler.py` (edit — add `build_strategy_battle_assembly`)

**Objective:** Create the new typed seam without changing runtime behavior. Add `BattleSpecExtensions` (frozen dataclass with the four current side-channel fields) and `StrategyBattleAssembly` (frozen dataclass containing `spec`, `extensions`, `pre_tick_setup`). Add `build_strategy_battle_assembly(...)` that — for this phase only — reads the existing side-channels off the already-built spec to populate `extensions`. Do **not** remove the side-channel writes yet. TDD throughout: red tests first.

---

## Reading

- [x] Re-read [TD-01 source plan §"Phase 1"](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-01_battle_spec_compilation.md) for exact implementation rules.
- [x] Read [design.md §"Goal / End State (target architecture)"](design.md) for the exact dataclass field shapes.
- [x] Read `game/simulation/battle_spec.py` to confirm `BattleSpec` remains untouched.

---

## Tasks

### Task 1.1: Add the three red tests for the new typed seam [Simple]
**File:** `tests/unit/strategy/combat/test_battle_assembly.py` (NEW)
**Tests:** `pytest tests/unit/strategy/combat/test_battle_assembly.py -x`

- [x] Create the new test module with import `from game.strategy.combat.battle_assembly import BattleSpecExtensions, StrategyBattleAssembly, build_strategy_battle_assembly` (collection-error red is acceptable — confirms the module does not yet exist).
- [x] Add `test_strategy_battle_assembly_holds_spec_extensions_and_setup_registry` — asserts the dataclass has exactly three fields: `spec`, `extensions`, `pre_tick_setup`.
- [x] Add `test_battle_spec_extensions_exposes_all_four_current_side_channel_fields` — asserts `BattleSpecExtensions` has exactly the four fields: `mine_groups`, `owner_to_team_id`, `combat_fleets`, `engine_ref`. Asserts `engine_ref` is a mutable `list` (one-slot list contract — see [design.md side-channel inventory](design.md)).
- [x] Add `test_build_strategy_battle_assembly_returns_typed_wrapper_around_existing_spec` — given a known input scenario, asserts the returned `StrategyBattleAssembly.spec` equals the result of `build_strategy_battle_spec(...)` and the four extension fields match the spec's current side-channels.
- [x] Run focused test; confirm all 3 tests fail for the right reason (collection error or `AttributeError`).

**Notes:**

### Task 1.2: Implement `BattleSpecExtensions` and `StrategyBattleAssembly` [Simple]
**File:** `game/strategy/combat/battle_assembly.py` (NEW)
**Tests:** Task 1.1 tests

- [x] Create the new module with `from __future__ import annotations` header.
- [x] Define `BattleSpecExtensions` as a frozen dataclass with `mine_groups: tuple[Fleet, ...]`, `owner_to_team_id: Mapping[Any, int]`, `combat_fleets: tuple[Fleet, ...]`, `engine_ref: list[Any]`. The `engine_ref` field is intentionally a mutable list inside an otherwise frozen dataclass (one-slot pattern; see [design.md](design.md) side-channel inventory).
- [x] Define `StrategyBattleAssembly` as a frozen dataclass with `spec: BattleSpec`, `extensions: BattleSpecExtensions`, `pre_tick_setup: PreTickBattleSetupRegistry` (Phase 1 may use `Any` or a stub placeholder for `pre_tick_setup` since the real registry lands in Phase 3).
- [x] Add `__all__` listing the three public names.
- [x] Run Task 1.1 tests; confirm the first two pass and the third still fails (`build_strategy_battle_assembly` not yet defined).

**Notes:**

### Task 1.3: Implement `build_strategy_battle_assembly` (compat layer) [Medium]
**File:** `game/strategy/combat/spec_compiler.py` (edit) and/or `game/strategy/combat/battle_assembly.py`
**Tests:** Task 1.1 tests + `pytest tests/unit/strategy/combat/test_spec_compiler.py tests/unit/strategy/combat/test_spec_compiler_formation.py -x`

- [x] Add `build_strategy_battle_assembly(...)` (signature matching `build_strategy_battle_spec(...)`).
- [x] Implementation: call `build_strategy_battle_spec(...)` internally; read the four side-channels off the returned spec via `getattr`; package them into `BattleSpecExtensions`; return `StrategyBattleAssembly(spec, extensions, PreTickBattleSetupRegistry())`. (For Phase 1, the registry can be empty or a stub — Phase 3 wires it.)
- [x] **Do NOT remove** the four `object.__setattr__(spec, ...)` writes in `spec_compiler.py`. They stay for compat through Phases 1-3.
- [x] **Do NOT change** `build_strategy_battle_spec(...)` behavior — the public entry point is unchanged.
- [x] Run Task 1.1 tests; confirm all 3 now pass.
- [x] Run the existing compiler + formation tests; confirm they still pass (no regressions).

**Notes:**

### Task 1.4: Commit Phase 1 [Simple]
**File:** N/A
**Tests:** Task 1.1 tests + existing compiler/formation tests

- [x] `git status --short` confirms only Phase 1 files dirty.
- [x] Run `python Projects/scripts/phase_complete.py PROJ-426 phase_1 --repo .worktrees/phases/PROJ-426/phase_1` (or per coordinator instructions).
- [x] Suggested commit message: `PROJ-426 phase 1: introduce StrategyBattleAssembly/BattleSpecExtensions typed seam (compat layer)`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All Phase 1 task checkboxes checked.
- [x] `battle_assembly.py` exists with `BattleSpecExtensions`, `StrategyBattleAssembly`, `build_strategy_battle_assembly`.
- [x] Three new red-to-green tests pass.
- [x] Existing compiler + formation tests still pass.
- [x] Side-channel writes still present in `spec_compiler.py` (intentional for this phase).
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 2.
