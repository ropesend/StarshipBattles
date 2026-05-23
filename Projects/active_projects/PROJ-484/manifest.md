# PROJ-484 File Manifest

> Generated during /claude-proj-from-legacy-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/simulation/combat/combat_events.py` | Production | Edit | Delete `DamageContext` re-export at line 62 (Phase 2) |
| `game/simulation/entities/ship.py` | Production | Edit | Delete `DEFAULT_MAX_MASS` re-export (line 22, Phase 2) and `CombatConstants` re-export (line 23, Phase 1); remove orphan header comment at line 21 |
| `game/ui/services/image/__init__.py` | Production | Edit | Delete unused `_null_provider` side-effect import at line 37 (Phase 1) |
| `tests/unit/simulation/combat/test_combat_events.py` | Test | Migrate-callers | Update line 14 to import `DamageContext` from `game.core.combat_types` (Phase 2) |
| `tests/unit/entities/test_ship.py` | Test | Migrate-callers | Update line 472 to import `DEFAULT_MAX_MASS` from `game.simulation.physics_constants` (Phase 2) |
