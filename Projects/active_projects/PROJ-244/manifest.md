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
