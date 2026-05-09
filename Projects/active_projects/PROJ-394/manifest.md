# PROJ-394 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/galaxy.py` | Production | Add public `state: GalaxyState` `@property` |
| `game/strategy/data/galaxy_state.py` | Production | MIN-004 — update module + class docstrings |
| `game/strategy/engine/handlers/movement.py` | Production | Migrate `galaxy._state.X` → `galaxy.state.X` |
| `game/strategy/services/fleet_navigation_service.py` | Production | Same |
| `game/ui/screens/strategy_render/hex_outlines.py` | Production | Same |
| `tests/unit/strategy/data/test_galaxy_state_encapsulation.py` | Test | MAJ-001 — empty `GRANDFATHERED_EXTERNAL_READS`, update docstring (MIN-003) |
| `tests/unit/strategy/engine/handlers/test_movement_handlers.py` | Test | Migrate `_state.X`; add `state` property to `_FakeGalaxy` |
| `tests/unit/strategy/fleet_navigation/test_navigation_pure.py` | Test | Migrate-callers |
| `tests/unit/strategy/services/test_fleet_navigation_gaps.py` | Test | Migrate-callers |
| `tests/unit/strategy/services/test_fleet_navigation_action_timing.py` | Test | Migrate-callers |
| `tests/unit/ui/screens/strategy_render/test_hex_outlines.py` | Test | Migrate-callers |
| `tests/unit/ui/screens/test_strategy_renderer.py` | Test | Migrate-callers |
| `tests/integration/strategy/test_warp_orders.py` | Test | Migrate-callers |
| `tests/unit/strategy/data/test_galaxy_cleanup.py` | Test | Migrate-callers |
| `Projects/active_projects/PROJ-387/plan.md` | Tracking | MIN-005 — fix `movement.py` path on line 40 |
