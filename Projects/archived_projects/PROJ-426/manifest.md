# PROJ-426 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/combat/spec_compiler.py` | Production (edit) | 1, 2, 3, 4, 5 | Currently 959 LOC. Add `build_strategy_battle_assembly` in Phase 1; delegate to new builders in Phase 2; remove embedded pre-tick setup builders in Phase 3; delete four `object.__setattr__(spec, ...)` writes in Phase 4; reduce to `<= 120 LOC` thin facade in Phase 5. Preserve public import path. |
| `game/strategy/adapters/simulation_adapter.py` | Production (edit) | 4 | Currently 620 LOC. Migrate `_build_spec` → `_build_assembly` (or equivalent). Replace runtime reads of `_mine_groups`, `_owner_to_team_id`, `_combat_fleets`, `_engine_ref` with `assembly.extensions.*`. Pre-tick callback comes from `assembly.pre_tick_setup.composed_callback()`. |
| `game/strategy/combat/post_battle_hook.py` | Production (edit if needed) | 2 | Behavior intact; only adjust imports if extraction of `_build_strategy_post_battle_hook` into `PostBattleHookBuilder` requires it. |
| `game/strategy/combat/battle_assembly.py` | Production (new) | 1 | `BattleSpecExtensions` (frozen dataclass: `mine_groups`, `owner_to_team_id`, `combat_fleets`, `engine_ref`); `StrategyBattleAssembly` (frozen dataclass: `spec`, `extensions`, `pre_tick_setup`); `StrategyBattleAssembler.assemble(...)` orchestrator (carries the temporary `mine_group_filter` param for PROJ-431 handoff). |
| `game/strategy/combat/team_spec_builder.py` | Production (new) | 2 | `TeamSpecBuilder` — owns `_team_spec_for_fleet_group`, `_pick_formation_for_fleet`, `_ship_spec_from_instance`, `_split_mine_groups_from_fleets` (now a public method). |
| `game/strategy/combat/strategy_modifier_stack_builder.py` | Production (new) | 2 | `StrategyModifierStackBuilder` — owns `_build_modifier_stack`, `_entries_from_sector_effects`, `_entries_from_fleet_combat_modifiers`. |
| `game/strategy/combat/post_battle_hook_builder.py` | Production (new) | 2 | `PostBattleHookBuilder` — owns `_build_strategy_post_battle_hook` closure construction. |
| `game/strategy/combat/pre_tick_setup_registry.py` | Production (new) | 3 | `PreTickBattleSetupRegistry` with `register(name, setup)` and `composed_callback() -> Callable | None`. Deterministic composition order. |
| `game/strategy/combat/pre_tick_setup/__init__.py` | Production (new) | 3 | Package marker. |
| `game/strategy/combat/pre_tick_setup/mine_setup.py` | Production (new) | 3 | Ex-`build_mine_resolver_setup` (was at `spec_compiler.py:494-549`). |
| `game/strategy/combat/pre_tick_setup/reboard_setup.py` | Production (new) | 3 | Ex-`build_fighter_reboard_setup` (was at `spec_compiler.py:454-491`). |
| `tests/unit/strategy/combat/test_battle_assembly.py` | Test (new) | 1 | Red tests first: `test_strategy_battle_assembly_holds_spec_extensions_and_setup_registry`, `test_battle_spec_extensions_exposes_all_four_current_side_channel_fields`, `test_build_strategy_battle_assembly_returns_typed_wrapper_around_existing_spec`. |
| `tests/unit/strategy/combat/test_team_spec_builder.py` | Test (new) | 2 | Seam tests for `TeamSpecBuilder`. |
| `tests/unit/strategy/combat/test_strategy_modifier_stack_builder.py` | Test (new) | 2 | Seam tests for `StrategyModifierStackBuilder`. |
| `tests/unit/strategy/combat/test_post_battle_hook_builder.py` | Test (new) | 2 | Seam tests for `PostBattleHookBuilder`. |
| `tests/unit/strategy/combat/test_pre_tick_setup_registry.py` | Test (new) | 3 | Red tests: registry composes in registration order, returns None when empty, mine + reboard setups register without knowing about each other. |
| `tests/unit/strategy/combat/test_spec_compiler.py` | Test (migrate) | 2, 5 | 831 LOC. Existing pins on team building, modifiers, boundary, components, multi-fleet grouping. Update imports to follow extracted builders; remove any private-helper references. |
| `tests/unit/strategy/combat/test_spec_compiler_formation.py` | Test (migrate) | 2 | 173 LOC. `FormationResolver` call-site test; update to point at `TeamSpecBuilder` if the formation-pick logic moved with it. |
| `tests/unit/strategy/combat/test_post_battle_hook.py` | Test (migrate) | 2 | 640 LOC. Outcome → ship-instance writeback pinning; update imports to follow `PostBattleHookBuilder`. |
| `tests/unit/strategy/combat/test_fighter_group_combat_join.py` | Test (migrate) | 2 | 145 LOC. Currently imports `_split_mine_groups_from_fleets` private helper. Migrate to `TeamSpecBuilder` public method in the same phase the helper moves; do **not** re-export. |
| `tests/unit/strategy/combat/test_satellite_group_combat_join.py` | Test (migrate) | 2 | 129 LOC. Same situation as `test_fighter_group_combat_join.py`. |
| `tests/unit/strategy/adapters/test_simulation_adapter.py` | Test (migrate) | 4 | Adapter-side reads of `_mine_groups`, `_owner_to_team_id`, `_combat_fleets`, `_engine_ref`. Migrate to `assembly.extensions.*` and `assembly.pre_tick_setup.composed_callback()`. |
| `tests/integration/test_fms_b_e2e.py` | Test (migrate) | 4 | 535 LOC. Pins `spec._mine_groups` and `spec._owner_to_team_id` at lines 414, 415, 420, 493. Migrate to `assembly.extensions.*` reads; migration MUST land before the `object.__setattr__` deletes. |
| `tests/integration/strategy/combat/test_damage_persistence.py` | Test (verify) | 4 | Integration test; indirectly exercises the side-channels via adapter integration. Re-run after Phase 4 seam migration; edit only if a source-edit is required for greenness. |
| `tests/integration/test_fms_c_carrier_ai_launch.py` | Test (verify) | 4 | Listed in TD-01 Phase 4 validation command. Should pass without source edits if adapter migration is correct; surface if it doesn't. |
| `docs/systems/strategy_layer.md` | Docs (edit) | 5 | Replace any prose describing spec mutation / side-channels with the assembler pipeline. |
| `docs/01_ARCHITECTURE.md` | Docs (edit) | 5 | Reflect the new `StrategyBattleAssembly` boundary between strategy and simulation. |
| `docs/02_PATTERNS.md` | Docs (edit) | 5 | Add typed-extensions / setup-registry pattern; remove references to private-attr side-channels as a pattern. |
