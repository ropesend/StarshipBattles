# PROJ-488 File Manifest

> Generated during /claude-proj-from-legacy-audit. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/strategy/data/planet_physics.py` | Production | Delete | Deleted `MASS_EARTH = EARTH_MASS` alias and its now-unused `from game.core.constants import EARTH_MASS` line. |
| `game/strategy/data/planet_atmosphere.py` | Production | Migrate-callers | 4 refs renamed; import switched to `from game.core.constants import EARTH_MASS`. |
| `game/strategy/data/planet_gen_surface.py` | Production | Migrate-callers | 2 refs renamed; import switched to `from game.core.constants import EARTH_MASS`. |
| `game/ui/screens/galaxy_test/system_mode.py` | Production | Migrate-callers | 2 refs renamed; runtime-local import switched to `from game.core.constants import EARTH_MASS`. |
| `Tools/diagnose_blueprints/diagnose_blueprints.py` | Tool | Migrate-callers | 3 refs renamed; import switched to `from game.core.constants import EARTH_MASS`. |
| `tests/integration/strategy/test_planet_physics.py` | Test | Migrate-callers | 4 refs renamed; import switched. |
| `tests/unit/strategy/planet_atmosphere/test_generation.py` | Test | Migrate-callers | 5 refs renamed; import switched. |
| `tests/unit/strategy/planet_atmosphere/test_calculations.py` | Test | Migrate-callers | 10 refs renamed; import switched. |
| `tests/unit/strategy/planet_atmosphere/conftest.py` | Test | Migrate-callers | 2 refs renamed; import switched. |
| `tests/unit/strategy/data/test_planet_physics.py` | Test | Migrate-callers | 1 ref renamed; import switched. |
| `tests/unit/strategy/data/test_planet_gen.py` | Test | Migrate-callers | 19 refs renamed across many local lazy imports; all switched to `from game.core.constants import EARTH_MASS`. |
| `tests/static_guards/test_facade_read_path_imports_guard.py` | Test (static-guard fixture) | Edit | Line 208 tuple changed from `(system_mode.py, game.strategy.data.planet_physics, MASS_EARTH)` to `(system_mode.py, game.core.constants, EARTH_MASS)`. |
