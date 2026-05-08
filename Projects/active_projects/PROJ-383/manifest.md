# PROJ-383 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/engine/command_handlers.py` | Production | Delete | LEG-01-005 — whole-file deletion (82 LOC); transitional shim |
| `game/strategy/engine/planet_command_handlers.py` | Production | Migrate-callers | LEG-01-015 — 4 function-local imports at lines 55, 123, 145, 181 |
| `game/strategy/engine/superweapon_command_handlers.py` | Production | Migrate-callers | LEG-01-016 — top-level import at line 15 |
| `game/strategy/engine/game_session.py` | Production | Migrate-callers | LEG-01-018 — top-level import at line 67 |
| `tests/` (25 sites) | Test | Migrate-callers | Test-file imports of `game.strategy.engine.command_handlers` (enumerate via grep in Task 1.4) |
