# PROJ-275 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ui/screens/battle_setup/spec_compiler.py` | Production | Lift `_NUM_TEAMS`; `_route_team_for_scope` returns `List[int]` |
| `game/ui/screens/battle_setup_state.py` | Production | `side_0`/`side_1` → `sides: List[BattleSetupSide]` |
| `game/ui/screens/battle_setup/panels/` (multiple files) | Production | Dynamic sides — audit files in Phase 1 |
| `game/ui/screens/battle_setup/screen.py` | Production | `_complex_toggles` dict parameterizes on side index |
| `game/strategy/combat/spec_compiler.py` | Production | `build_strategy_battle_spec(fleets: Sequence[Fleet], ...)`; N `TeamSpec`s |
| `game/strategy/adapters/simulation_adapter.py` | Production | `SimulationBattleResolver.resolve_battle(fleets)` |
| `game/strategy/turn_engine/conflict_resolution_engine.py` | Production | Replace sequential 2-fleet loop with single N-team battle |
| `game/strategy/combat/post_battle_hook.py` | Production | Verify N-team in `apply_outcome_to_fleets` |
| `game/simulation/combat/ability_stat_registry.py` | Production | Multi-opponent fan-out (wider `num_teams` support) |
| `game/simulation/combat/formation.py` | Production | Add `resolve_team_entry_vectors(team_count, ...)` ring helper |
| `tests/integration/simulation/test_three_team_battle.py` | Test | Extend coverage |
| `tests/integration/simulation/test_four_team_battle.py` | Test | NEW — stress 4 teams |
| `tests/integration/strategy/test_three_empire_battle.py` | Test | NEW — strategy → outcome 3-team |
| `tests/integration/ui/test_battle_setup_three_sides.py` | Test | NEW — UI state → spec → outcome 3-side |
| `tests/unit/simulation/combat/test_formation.py` | Test | Ring-entry vectors unit tests |
| `tests/unit/ui/screens/battle_setup/test_spec_compiler.py` | Test | Update for N-team |
| `tests/unit/strategy/combat/test_spec_compiler.py` | Test | Update for N-team |
| `tests/unit/strategy/adapters/test_simulation_adapter.py` | Test | Update for N-team |
| `docs/systems/combat_simulation.md` | Doc | §9 fully rewritten — remove "2-team assumption" caveats |
| `docs/systems/strategy_layer.md` | Doc | Conflict-resolution section: sequential decomposition gone |
