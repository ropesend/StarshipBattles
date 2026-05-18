# PROJ-405 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/entities/projectile.py | Production | `event_logger` kwarg already exists (PROJ-382); ensure callers pass real bus. |
| game/simulation/combat/families/seeker.py | Production | Thread EventBus into `Seeker` constructor. |
| game/simulation/combat/families/projectile.py | Production | Thread EventBus into projectile-family construction. |
| game/simulation/battle_state.py | Production | Top of construction chain — already holds the session EventBus. |
| game/simulation/combat/weapon_firing_system.py | Production (probable) | Confirm during Task 1.1 — the most-likely intermediate spawner. |
| tests/unit/simulation/test_projectile_event_bus_wiring.py | Test (new) | Regression that asserts `SEEKER_EXPIRE` is observed via production path. |
