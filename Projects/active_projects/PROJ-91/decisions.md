# PROJ-91: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Project initialized | Starting point for Unify Resource/State Logic Between Strategy and Simulation Layers |
| 2026-02-09 | Eliminate type-specific methods entirely, not delegate | Cleanest API — removes 7 redundant methods. All callers already have access to generic methods. Per CLAUDE.md: "minimize technical debt, maximize maintainability." |
| 2026-02-09 | Add IResourceHolder protocol in game/core/protocols.py | Formalizes the resource access contract between ShipInstance bridge methods and Ship. Eliminates hasattr checks. Follows existing protocol patterns in the codebase. |
| 2026-02-09 | Fix resupply() and get_resource_percentage() bugs in-scope | Both have the same root cause (wrong key lookup). We're already modifying these methods — fixing bugs here avoids a separate project. |
| 2026-02-09 | Add get_resource_names() to ResourceRegistry | Enables dynamic resource discovery, eliminating hardcoded ['fuel', 'energy', 'ammo'] lists in bridge methods and BattleState. |
| 2026-02-09 | Refactor Fleet type-specific wrappers alongside ShipInstance | Fleet's fuel/energy-specific methods (get_fuel_cost_per_hex, fuel_endurance, warp_jumps_remaining) directly call the ShipInstance methods being removed. Refactoring them together avoids breaking changes. |
