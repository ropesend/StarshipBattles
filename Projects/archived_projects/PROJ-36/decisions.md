# PROJ-36: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Project initialized | Starting point for TurnEngine God Class Decomposition |
| 2026-01-27 | Remove legacy wrapper methods (`_calculate_next_hex`, `_spawn_complex`, `_spawn_ship`) | Clean break - external code should use engines directly. These are just pass-through delegations that add no value. |
| 2026-01-27 | Create `game/strategy/validation/` module for order validation | Follows existing pattern from `game/simulation/validation/`. Allows for future expansion to validate all order types. Single source of truth for validation logic. |
| 2026-01-27 | Do NOT create ISubSystem interface | At 5-6 engines, explicit delegation is manageable. Movement engine has two-phase design (collect→apply) that doesn't fit uniform interface. Avoids over-engineering. Can revisit if adding 3+ more phases later. |
| 2026-01-27 | Keep IBattleResolver injection pattern | Clean strategy-simulation separation already established in PROJ-11. Works well for testing with mock resolvers. |
| 2026-01-27 | Consolidate duplicate validation in FleetOrderProcessor | FleetOrderProcessor has inline validation that duplicates TurnEngine.validate_colonize_order. Single source of truth is better for maintenance. |
| 2026-01-27 | Remove unused `_apply_battle_results` method | Method at lines 433-467 is never called. Results are already applied in `_resolve_combat_simulated` via `fleet.update_from_battle_results()`. |
