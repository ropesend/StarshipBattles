# PROJ-222: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-24 | Project initialized | Starting point for Fleet Join Order Redirect and Pursuer Tracking |
| 2026-03-24 | Include intercept orders (MOVE_TO_FLEET) in pursuer tracking | Intercept orders suffer the same orphaned-reference bug. Minimal extra work since they share MOVE_TO_FLEET. |
| 2026-03-24 | Extract pursuer logic to FleetPursuerTracker delegate | Keeps Fleet class from growing. Consistent with existing delegate pattern (FleetCapabilityCalculator, FleetResourceAggregator, FleetBattleAdapter). Eases future PROJ-86 god class decomposition. |
| 2026-03-24 | Add same-empire validation to JoinCommandHandler and InterceptCommandHandler | Prevents potential exploits. Small scope addition — one check per handler. Also add self-targeting validation. |
| 2026-03-24 | Refactor command handlers to use Fleet's public API for order mutations | ClearOrdersHandler, DeleteOrderHandler, RemoveBuildOrderHandler directly mutate fleet.orders bypassing Fleet methods. Refactoring them to use Fleet API makes Fleet the sole gatekeeper, enabling pursuer cleanup hooks. |
| 2026-03-24 | Pursuers set is NOT serialized — rebuilt from order targets on load | Zero serialization overhead. Rebuilt deterministically in GameSession.from_dict() after resolve_order_references(). |
| 2026-03-24 | Use Set[Fleet] (not WeakSet) for pursuer tracking | Strong references are fine because Empire.remove_fleet() is the single choke point for all fleet removal, and we add cleanup there. WeakSet has unpredictable GC timing. |
| 2026-03-24 | New EventCategory: FLEET_OPERATIONS | Fleet join/redirect/cancel events are not combat, production, or superweapon events. New category keeps filtering clean. |
