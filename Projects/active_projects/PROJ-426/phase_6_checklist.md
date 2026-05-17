# Phase 6: Codex consult follow-ups — single owner→team mapping + tightened integration tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-426 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_5
**Review Mode:** standard
**Files (planned):**
- `game/strategy/combat/team_spec_builder.py` (edit — add `group_fleets_by_owner` + `compute_owner_to_team_id` helpers)
- `game/strategy/combat/post_battle_hook_builder.py` (edit — accept `owner_to_team_id` kwarg; fall back for legacy direct-construction callers)
- `game/strategy/combat/battle_assembly.py` (edit — derive owner→team mapping once via the helper, pass the same dict to `PostBattleHookBuilder.build(...)` and `BattleSpecExtensions.owner_to_team_id`)
- `tests/unit/strategy/combat/test_battle_assembly.py` (edit — add structural drift-detection test that asserts identity between the two consumers)
- `tests/integration/test_fms_b_e2e.py` (edit — replace direct `build_mine_resolver_setup(...)` calls with `assembly.pre_tick_setup.composed_callback()` at lines 420-425 and 495-500)
- `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` (edit — assert captured `pre_tick_loop_callback` is non-None, callable, and installs `reboard_tracker` on the engine)

**Objective:** Close two follow-ups raised by the Codex consult after Phase 5: (a) eliminate the owner→team mapping drift surface where `StrategyBattleAssembler` and `PostBattleHookBuilder` independently re-derived the same mapping; (b) tighten the integration tests that bypassed the public `assembly.pre_tick_setup.composed_callback()` seam.

---

## Reading

- [x] Codex consult artifact (the two action items captured in the executor prompt).
- [x] Phase 5 final state of `battle_assembly.py`, `post_battle_hook_builder.py`, `team_spec_builder.py`.
- [x] `tests/integration/test_fms_b_e2e.py` lines 420-425 and 495-500.
- [x] `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` lines 105-112.

---

## Issue 1: Single source of truth for owner→team mapping

- [x] Write failing TDD test `test_owner_to_team_mapping_is_single_sourced_between_assembler_and_hook` in `test_battle_assembly.py`. Test patches `PostBattleHookBuilder.build` with a spy that captures the `owner_to_team_id` kwarg; asserts the captured mapping is **the same Python object** (identity, not equality) as `assembly.extensions.owner_to_team_id`. Run, confirm fail (kwarg not passed; identity is False).
- [x] Add `TeamSpecBuilder.group_fleets_by_owner(combat_fleets) -> (Dict[owner_id, List[Fleet]], List[owner_id])` helper.
- [x] Add `TeamSpecBuilder.compute_owner_to_team_id(combat_fleets) -> Dict[owner_id, team_id]` helper.
- [x] `PostBattleHookBuilder.build(...)` accepts `owner_to_team_id: Optional[Mapping]` kwarg; uses it directly when provided; falls back to re-deriving (with the same rule) only when `None` so legacy direct-construction tests still work.
- [x] `StrategyBattleAssembler.assemble(...)` calls `self._team_builder.group_fleets_by_owner(...)` once, computes `empire_to_team_id` once, passes the **same dict** to both `PostBattleHookBuilder.build(..., owner_to_team_id=empire_to_team_id)` and `BattleSpecExtensions(owner_to_team_id=empire_to_team_id, ...)` (no `dict(...)` copy).
- [x] Run new test — green.
- [x] Run full battle_assembly + post_battle_hook_builder + post_battle_hook + team_spec_builder + spec_compiler unit tests — 57/57 green.

---

## Issue 2: Tighten integration tests on the assembler-pipeline surface

- [x] `tests/integration/test_fms_b_e2e.py` test `test_spec_compiler_filters_mine_groups_and_wires_resolver`: replace the direct `build_mine_resolver_setup(assembly.extensions.mine_groups, owner_map)` call with `assembly.pre_tick_setup.composed_callback()`. Assert composed callback is non-None and produces the same `engine.mine_resolvers` wiring.
- [x] Same change in `test_post_battle_hook_calls_writeback_and_prunes_empty_mine_group`. Drop the now-unused `build_mine_resolver_setup` import.
- [x] `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py::test_resolve_battle_threads_injected_registries`: add assertions that the captured `pre_tick_loop_callback` is non-None, callable, and — when invoked against a fake engine — installs `reboard_tracker` (proves the assembly registry surface, not a stale closure, is flowing into `run_battle`).
- [x] Run `tests/integration/test_fms_b_e2e.py` — 7/7 green.
- [x] Run `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` — 4/4 green.

---

## Validation

- [x] `python Tools/test_sharded/test_sharded.py` — **20954/20954 passed**, 0 failed.
- [x] Commit on `proj/PROJ-426/main` with the standard Co-Authored-By trailer. No `--amend`, no `--no-verify`.
