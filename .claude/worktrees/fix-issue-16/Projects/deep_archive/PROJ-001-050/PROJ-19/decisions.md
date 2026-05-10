# PROJ-19: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Project initialized | Starting point for Type Safety via Protocols |
| 2026-01-25 | Use @runtime_checkable Protocols, not ABCs | Protocols work via structural typing - no need to modify entity classes to inherit from a base class |
| 2026-01-25 | Keep IControllable as ABC | Different purpose (AI interface), well-tested with ShipControllableAdapter, no benefit to migrate |
| 2026-01-25 | Use TYPE_CHECKING guards in protocols.py | Avoid circular imports when referencing HexCoord, ShipInstance, FleetOrder |
| 2026-01-25 | Create TypeGuard functions | Provides clean type narrowing for mypy and IDE support after isinstance checks |
| 2026-01-25 | Focus on strategy/UI layers first | Largest impact (strategy_screen.py has 29 hasattr), clearest duck typing patterns |
| 2026-01-25 | Keep formation getattr in behaviors.py | These are genuinely optional attributes (formation_rotation_mode, is_derelict, etc.) |
| 2026-01-25 | Keep app.py hasattr patterns out of scope | These are lazy initialization checks, different category from duck typing |
| 2026-01-25 | Simulation layer out of scope | Many hasattr/getattr in simulation are for component capability checks - different pattern |
| 2026-01-26 | Final count: 281 hasattr, target not achieved | Analysis: 163 are legitimate attribute checks (hasattr(self, ...) or hasattr(self.something, ...)). Remaining ~118 include simulation/builder patterns out of scope. All key duck typing clusters replaced (strategy_screen, strategy_detail_fmt, controller, system_tree_panel). Project achieved its goal of replacing type discrimination patterns with Protocols. |
| 2026-01-26 | Keep defensive planet attribute checks | In format_planet_info(): hasattr(obj, 'owner_id') and hasattr(obj, 'resources') are defensive checks, not type discrimination. IPlanet Protocol guarantees these exist but keeping for backwards compatibility. |
