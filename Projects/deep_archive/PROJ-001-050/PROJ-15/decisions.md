# PROJ-15: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Project initialized | Starting point for Phase 2 - Remove Shims and Aliases |
| 2026-01-25 | Include to_hit_profile removal | Investigation confirmed stats_layout.json is NOT deprecated - it's the active UI config system. The `to_hit_profile` attribute is simply an alias for `total_defense_score`. Safe to remove by updating JSON key. |
| 2026-01-25 | Defer project_path_as_dicts() wrapper | Used by `game/strategy/data/pathfinding.py` line 227. Requires updating pathfinding callers and potentially changing return format expectations. Better suited for Phase 3. |
| 2026-01-25 | Keep TurnEngine._spawn_complex, _spawn_ship, _calculate_next_hex | These are delegation methods to ProductionEngine/FleetMovementEngine, not aliases. They serve as useful extension points for subclassing TurnEngine. |
| 2026-01-25 | Order phases by risk | Start with singleton aliases (lowest risk, independent changes) and end with builder shims (highest risk, most test dependencies). This allows early validation and easier rollback if issues found. |
| 2026-01-25 | Delete TestBackwardCompatibility test class | This test class explicitly tests the deprecated `has_energy_for_warp()` and `consume_warp_energy()` aliases. Since we're removing the aliases, the tests should be deleted rather than updated. The canonical methods (`has_resources_for_warp`, `consume_warp_resources`) are already tested elsewhere. |
| 2026-01-25 | Update test_advanced_fleet_orders.py rather than delete | The test tests intercept functionality, not the deprecated `_execute_move_step()` method. Update to use `_calculate_next_hex()` + manual location update instead of deleting valuable test coverage. |
