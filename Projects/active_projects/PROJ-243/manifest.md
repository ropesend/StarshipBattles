# PROJ-243 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/entities/ship.py | Production | Declare fleet_attack_bonus, fleet_defense_bonus in __init__ |
| game/simulation/systems/battle_engine.py | Production | Extract _initialize_ship(), fix add_ship_mid_battle(), refactor fighter launch |
| game/simulation/combat/fleet_aura_manager.py | Production | Add register_ship() method |
| tests/unit/simulation/entities/test_ship_fleet_attrs.py | Test | New — fleet bonus attribute tests |
| tests/unit/simulation/systems/test_battle_engine_init_ship.py | Test | New — _initialize_ship() tests |
| tests/unit/simulation/combat/test_fleet_aura_register.py | Test | New — register_ship() tests |
| tests/unit/simulation/systems/test_add_ship_mid_battle.py | Test | New — mid-battle addition tests |
| tests/unit/simulation/systems/test_fighter_launch_init.py | Test | New — fighter launch initialization tests |
| tests/integration/simulation/test_mid_battle_reinforcement.py | Test | New — end-to-end reinforcement test |
