# PROJ-244 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/systems/battle_engine.py | Production | Rename start() params team1/team2 → team0/team1 |
| game/simulation/services/battle_service.py | Production | Update keyword args in _start_battle() call |
| game/ui/screens/battle_screen.py | Production | Rename start() params and body |
| game/ui/services/battle_factories.py | Production | Rename create_manual_battle() params and body |
| game/app.py | Production | Rename start_battle() params and call |
| game/ui/panels/battle_panels.py | Production | Rename local variables team1/team2 → team0/team1 |
| game/strategy/adapters/simulation_adapter.py | Production | Rename local variables in simulate_battle() |
| game/ui/screens/setup_screen.py | Production | Rename local variables and return tuple |
| tests/fixtures/battle.py | Test | Rename create_battle_engine_with_ships() params, locals, ship names |
| tests/integration/fleet_combat/test_service_integration.py | Test | Update keyword arg in fixture call |
| tests/unit/ui/test_battle_screen_simulation.py | Test | Update docstring |
| tests/integration/fleet_combat/test_battle_determinism.py | Test | Rename _run_battle() params and _make_teams() locals (added 2026-04-10) |
| docs/systems/combat_simulation.md | Docs | Update code example team1_ships/team2_ships → team0/team1 (added 2026-04-10) |
| tests/fixtures/README.md | Docs | Update code example team1_count/team2_count → team0/team1 (added 2026-04-10) |
| tests/unit/ui/services/test_battle_factories.py | Test | Rename mock_fleet1/2, mock_ship1/2 in factory tests (added 2026-04-10) |
