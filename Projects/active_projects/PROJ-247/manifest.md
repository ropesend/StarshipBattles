# PROJ-247 File Manifest

> Generated during project initialization. Used for conflict detection.

| File | Type | Notes |
|------|------|-------|
| `game/simulation/entities/ship.py` | Production | Line 78 — change id to uuid4 |
| `game/simulation/battle_controller.py` | Production | 12 sites — replace id() with ship.id |
| `game/simulation/managers/retreat_manager.py` | Production | 4 sites — replace id() with ship.id |
| `game/simulation/battle_state.py` | Production | 6 sites — replace id() with ship.id |
| `tests/unit/simulation/managers/test_retreat_manager.py` | Test | Update fixtures |
