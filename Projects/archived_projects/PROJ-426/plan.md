# PROJ-426: Battle spec assembly pipeline (TD-01)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-426` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-426 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Preflight and baseline capture | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Introduce typed assembly DTOs | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract pure builders out of `spec_compiler.py` | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract pre-tick setup registry and setup builders | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate the adapter to `StrategyBattleAssembly` and remove side-channels | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Reduce `spec_compiler.py` to a thin public facade and update docs | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Codex consult follow-ups: single owner->team mapping + tighten integration tests | Complete | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** None (ready for final audit)
**Last Action:** Phase 6 complete — Codex consult follow-ups landed: owner->team mapping now has a single source of truth (`TeamSpecBuilder.compute_owner_to_team_id`) shared by `StrategyBattleAssembler` and `PostBattleHookBuilder` (same dict object, no re-derivation); `test_fms_b_e2e` and adapter pre-tick callback tests now exercise `assembly.pre_tick_setup.composed_callback()` rather than the underlying setup helpers. Full sharded 20954/20954 green.
**Next Action:** Final audit / merge.
**Blockers:** None

## Overview
`game/strategy/combat/spec_compiler.py` is **959 LOC** (almost 2x the 500-LOC ceiling) and acts as a central integration knot: `build_strategy_battle_spec(...)` constructs a frozen `BattleSpec` and then uses `object.__setattr__(spec, ...)` to bolt on four private side-channel attributes that `game/strategy/adapters/simulation_adapter.py` reads back out. This project replaces that side-channel pipeline with a typed `StrategyBattleAssembly` containing `BattleSpec`, a `BattleSpecExtensions` dataclass, and a `PreTickBattleSetupRegistry`, splitting the orchestration into named builders (`StrategyBattleAssembler`, `TeamSpecBuilder`, `StrategyModifierStackBuilder`, `PostBattleHookBuilder`) so future strategy-state-affects-mid-battle-behavior features have an explicit extension seam.

## Goals
- Eliminate all four `object.__setattr__(spec, ...)` writes in `spec_compiler.py` (`_mine_groups`, `_owner_to_team_id`, `_engine_ref`, `_combat_fleets`).
- Eliminate all `getattr(spec, "_...")` reads in `simulation_adapter.py`.
- Replace them with a typed `StrategyBattleAssembly(spec, extensions, pre_tick_setup)` flowing from a `StrategyBattleAssembler.assemble(...)` orchestrator.
- Move `build_mine_resolver_setup` and `build_fighter_reboard_setup` out of `spec_compiler.py` into a `game/strategy/combat/pre_tick_setup/` package owned by a `PreTickBattleSetupRegistry`.
- Reduce `spec_compiler.py` to a thin public facade (target `<= 120 LOC`) while preserving the public import path `game.strategy.combat.spec_compiler.build_strategy_battle_spec`.
- Migrate every test that asserts on private side-channel attribute names or the private `_split_mine_groups_from_fleets` helper to the new public seam **in the same phase** as the seam change — no compatibility shims per AGENTS.md.
- Keep battle behavior unchanged: same team grouping, same modifier translation, same tick-limit rules, same post-battle writeback, same mine/reboard behavior.

## Scope
**In:** structural split of `game/strategy/combat/spec_compiler.py` and migration of `game/strategy/adapters/simulation_adapter.py` to consume the new typed assembly DTO; new `battle_assembly.py`, `team_spec_builder.py`, `strategy_modifier_stack_builder.py`, `post_battle_hook_builder.py`, `pre_tick_setup_registry.py`, and `pre_tick_setup/` package; migration of the five tests that pin on private side-channels or private helpers; new dedicated unit tests around each new builder/registry; docs sync in `docs/systems/strategy_layer.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md` after code is green.

**Out:** changes to `game/simulation/battle_spec.py` (do **not** add fields to the frozen `BattleSpec` DTO unless a failing test proves the assembly DTO is insufficient); behavioral changes to team grouping, modifier translation, tick caps, post-battle writeback, or mine/reboard semantics; renaming the public import path `game.strategy.combat.spec_compiler.build_strategy_battle_spec`; touching `game/strategy/engine/conflict_resolution_engine.py` (compiler is mentioned in comments only, not called at runtime); the eventual collapse of the temporary `mine_group_filter` parameter on `StrategyBattleAssembler` (that simplification belongs to PROJ-431 Phase 2).

## Dependencies
Hard predecessors: **none**.

Soft predecessors: **none**.

**This project is a HARD predecessor of PROJ-431 (TD-10 deployable substrate redesign).** PROJ-431 cannot start its main redesign work until this project completes. The TD-10 plan explicitly assumes it should not have to preserve the current private battle-spec side-channels (`_mine_groups`, `_owner_to_team_id`, `_engine_ref`, `_combat_fleets`) — running TD-01 first means the deployable substrate redesign lands against a clean typed seam rather than perpetuating the `object.__setattr__(spec, ...)` pattern. See [EXECUTION_ORDER.md §"Recommended Linear Order #5" + §"Phase Gates" rule 3](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md).

**Temporary deliverable (intentional handoff to PROJ-431):** `StrategyBattleAssembler` will carry a `mine_group_filter` parameter that PROJ-431 Phase 2 simplifies away once deployables (mines, satellites, fighter groups) live on a unified substrate. Do **not** preemptively remove or generalize that parameter in this project; PROJ-431 Phase 2 owns the simplification.

## Key Files
| Component | File Path | Type |
|-----------|-----------|------|
| Current spec compiler (shrink to facade) | `game/strategy/combat/spec_compiler.py` | Production (edit, target `<= 120 LOC`) |
| Runtime caller (migrate off side-channels) | `game/strategy/adapters/simulation_adapter.py` | Production (edit) |
| Post-battle hook (imports may shift) | `game/strategy/combat/post_battle_hook.py` | Production (edit if extraction requires) |
| Typed assembly DTOs + assembler | `game/strategy/combat/battle_assembly.py` | Production (new) |
| Team/formation/mine-split builder | `game/strategy/combat/team_spec_builder.py` | Production (new) |
| Environmental + team modifier translator | `game/strategy/combat/strategy_modifier_stack_builder.py` | Production (new) |
| Post-battle hook builder | `game/strategy/combat/post_battle_hook_builder.py` | Production (new) |
| Pre-tick setup registry | `game/strategy/combat/pre_tick_setup_registry.py` | Production (new) |
| Pre-tick setup package | `game/strategy/combat/pre_tick_setup/__init__.py` | Production (new) |
| Mine resolver setup (moved out of compiler) | `game/strategy/combat/pre_tick_setup/mine_setup.py` | Production (new) |
| Fighter reboard setup (moved out of compiler) | `game/strategy/combat/pre_tick_setup/reboard_setup.py` | Production (new) |
| Existing test — team building, modifiers, boundary | `tests/unit/strategy/combat/test_spec_compiler.py` | Test (migrate) |
| Existing test — formation resolver | `tests/unit/strategy/combat/test_spec_compiler_formation.py` | Test (migrate) |
| Existing test — outcome writeback | `tests/unit/strategy/combat/test_post_battle_hook.py` | Test (migrate) |
| Existing test — pins `_split_mine_groups_from_fleets` private helper | `tests/unit/strategy/combat/test_fighter_group_combat_join.py` | Test (migrate to `TeamSpecBuilder` seam) |
| Existing test — pins `_split_mine_groups_from_fleets` private helper | `tests/unit/strategy/combat/test_satellite_group_combat_join.py` | Test (migrate to `TeamSpecBuilder` seam) |
| Existing test — pins `spec._mine_groups` / `spec._owner_to_team_id` side-channels | `tests/integration/test_fms_b_e2e.py` | Test (migrate) |
| Existing test — adapter side-channel reads | `tests/unit/strategy/adapters/test_simulation_adapter.py` | Test (migrate) |
| Existing test — battle damage persistence integration | `tests/integration/strategy/combat/test_damage_persistence.py` | Test (migrate) |
| New unit test — assembly DTO + assembler | `tests/unit/strategy/combat/test_battle_assembly.py` | Test (new) |
| New unit test — team spec builder | `tests/unit/strategy/combat/test_team_spec_builder.py` | Test (new) |
| New unit test — modifier stack builder | `tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py` | Test (new) |
| New unit test — post-battle hook builder | `tests/unit/strategy/combat/test_post_battle_hook_builder.py` | Test (new) |
| New unit test — pre-tick setup registry | `tests/unit/strategy/combat/test_pre_tick_setup_registry.py` | Test (new) |
| Strategy layer system docs | `docs/systems/strategy_layer.md` | Docs (edit, Phase 5) |
| Architecture overview | `docs/01_ARCHITECTURE.md` | Docs (edit, Phase 5) |
| Patterns reference | `docs/02_PATTERNS.md` | Docs (edit, Phase 5) |

Full enumeration of touched files (production + tests + docs) lives in [manifest.md](manifest.md).

## Phases

### Phase 0: Preflight and baseline capture
Read-only baseline. Run the two `rg` commands from the source plan's Executor Guardrails section to confirm the side-channel touch list has not grown since verification (the report cited 3 attrs; verification found 4; assume parallel work could add a 5th). Confirm `game/strategy/adapters/simulation_adapter.py` is still the only production runtime caller of the compiler. Record which tests directly inspect side-channel attributes (minimum `tests/integration/test_fms_b_e2e.py:414, 415, 420, 493`). No code edited.

### Phase 1: Introduce typed assembly DTOs
Add `game/strategy/combat/battle_assembly.py` with `BattleSpecExtensions` (frozen dataclass containing `mine_groups`, `owner_to_team_id`, `combat_fleets`, `engine_ref`) and `StrategyBattleAssembly` (frozen dataclass containing `spec`, `extensions`, `pre_tick_setup`). Add `build_strategy_battle_assembly(...)` in `spec_compiler.py` that — for this phase only — reads the existing side-channels off the already-built spec to populate `extensions`. Do **not** remove the side-channel writes yet. Add `tests/unit/strategy/combat/test_battle_assembly.py` with the three red tests listed in the source plan (`test_strategy_battle_assembly_holds_spec_extensions_and_setup_registry`, `test_battle_spec_extensions_exposes_all_four_current_side_channel_fields`, `test_build_strategy_battle_assembly_returns_typed_wrapper_around_existing_spec`). Validate via the two focused commands. Existing compiler/formation tests must still pass.

### Phase 2: Extract pure builders out of `spec_compiler.py`
Move `_team_spec_for_fleet_group`, `_pick_formation_for_fleet`, `_ship_spec_from_instance`, and `_split_mine_groups_from_fleets` into `team_spec_builder.py::TeamSpecBuilder`. Move modifier-stack helpers (`_build_modifier_stack`, `_entries_from_sector_effects`, `_entries_from_fleet_combat_modifiers`) into `strategy_modifier_stack_builder.py::StrategyModifierStackBuilder`. Move `_build_strategy_post_battle_hook` into `post_battle_hook_builder.py::PostBattleHookBuilder`. `spec_compiler.py` delegates to those builders but still writes the four side-channels for compatibility. **Do not re-export `_split_mine_groups_from_fleets`.** Migrate `test_fighter_group_combat_join.py` and `test_satellite_group_combat_join.py` to target `TeamSpecBuilder` in this same phase. Add the three new unit-test files.

### Phase 3: Extract pre-tick setup registry and setup builders
Move `build_mine_resolver_setup` (currently at `spec_compiler.py:494-549`) and `build_fighter_reboard_setup` (currently at `spec_compiler.py:454-491`) into `pre_tick_setup/mine_setup.py` and `pre_tick_setup/reboard_setup.py`. Add `pre_tick_setup_registry.py::PreTickBattleSetupRegistry` with `register(name, setup)` and `composed_callback() -> Callable | None`. `build_strategy_battle_assembly(...)` returns a populated registry instance alongside spec and extensions. `spec_compiler.py` must no longer define either setup builder. Add `test_pre_tick_setup_registry.py` covering deterministic composition order, empty-registry returns-None, and mine+reboard registering independently.

### Phase 4: Migrate the adapter to `StrategyBattleAssembly` and remove side-channels
Switch `simulation_adapter._build_spec` to consume `StrategyBattleAssembly` (rename to `_build_assembly` if natural). `run_battle(...)` still receives `assembly.spec`; pre-tick setup comes from `assembly.pre_tick_setup.composed_callback()`. Replace **all** runtime reads of `_mine_groups`, `_owner_to_team_id`, `_combat_fleets`, `_engine_ref` with extension accessors. **Only after the adapter test, `test_fms_b_e2e.py`, and `test_damage_persistence.py` are migrated**, delete the four `object.__setattr__(spec, ...)` writes in `spec_compiler.py`. Run the full sharded suite at this boundary. After this phase: `rg "object\.__setattr__\(spec" game tests` and `rg "getattr\(spec, ['\"]_" game tests` both return zero hits.

### Phase 5: Reduce `spec_compiler.py` to a thin public facade and update docs
`spec_compiler.py` keeps `build_strategy_battle_spec(...)` (and may re-export `build_strategy_battle_assembly(...)`). Its body becomes orchestration only: instantiate `StrategyBattleAssembler`, call `assemble`, return `assembly.spec`. Remove now-dead imports and stale module-doc text describing side-channels or embedded setup builders. Target `<= 120 LOC`. Update `docs/systems/strategy_layer.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md` to describe the assembler pipeline rather than spec mutation. Run focused tests + sharded suite + `pytest tests/ --testmon`.

### Phase 6: Codex consult follow-ups — eliminate owner-order/team mapping drift surface and tighten integration tests
Driven by a post-Phase-5 Codex consult. Two action items:

1. **Single source of truth for owner→team mapping.** Both `StrategyBattleAssembler.assemble(...)` and `PostBattleHookBuilder.build(...)` independently iterated combat fleets to derive `owner_id -> team_id`. Same logic, two places — future drift risk if either side's ordering rule diverges. Phase 6 extracts `TeamSpecBuilder.group_fleets_by_owner(...)` and `TeamSpecBuilder.compute_owner_to_team_id(...)`. The assembler computes the mapping once and passes the **same dict instance** to both `BattleSpecExtensions.owner_to_team_id` and `PostBattleHookBuilder.build(..., owner_to_team_id=...)`. A new structural test in `test_battle_assembly.py` pins identity (not equality) between the two consumers.

2. **Tighten test_fms_b_e2e + adapter pre-tick callback tests.** Two integration sites bypassed the public seam: `tests/integration/test_fms_b_e2e.py:420-425` and `:495-500` invoked `build_mine_resolver_setup(...)` directly instead of `assembly.pre_tick_setup.composed_callback()`; `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py:105-112` captured `pre_tick_loop_callback` without asserting on it. Both updated to exercise the same composed callback the simulation adapter feeds into `run_battle`, with assertions that the callback is non-None and installs the expected side effects (`engine.mine_resolvers`, `engine.reboard_tracker`) on the engine.

Run full sharded suite at the end.

## Related Documents
- [TD-01 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-01_battle_spec_compilation.md) — canonical specification (verification findings, file touch plan, per-phase implementation rules, validation commands, risks)
- [Strategy tech-debt EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) — why TD-01 runs at position 5/10 and why it gates TD-10
- [PROJ-431 (TD-10 deployable substrate redesign)](../PROJ-431/plan.md) — downstream project that consumes the typed assembly seam this project introduces
- [design.md](design.md) — distilled side-channel inventory, target architecture, test-migration plan
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — enumerated file touch list

## Verification
Acceptance criteria from the TD-01 plan:
- [x] `game/strategy/combat/spec_compiler.py` remains as the public entry point and is `<= 120 LOC` (100 LOC).
- [x] `game/strategy/adapters/simulation_adapter.py` no longer reads any private spec attribute.
- [x] `rg "object\.__setattr__\(spec" game tests` returns zero hits (only docstring/comment references remain).
- [x] `rg "getattr\(spec, ['\"]_" game tests` returns zero hits.
- [x] No production file under `game/strategy/combat/` exceeds 500 LOC (max 303 in battle_assembly.py).
- [x] `python Tools/test_sharded/test_sharded.py` passes after Phase 4 (20953/20953) and again after Phase 5 (20953/20953).
- [x] `docs/systems/strategy_layer.md` describes the assembly pipeline, not spec side-channels.
- [x] `StrategyBattleAssembler` carries a `mine_group_filter` parameter (intentional temporary state for PROJ-431 Phase 2 handoff).
