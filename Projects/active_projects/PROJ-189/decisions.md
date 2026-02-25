# PROJ-189: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for Storms Environmental Hazards |
| 2026-02-24 | Data-driven effects (StormEffect dataclass) over true Ability instances | User approved. Simpler approach - multiplier values feed same stat pipeline without coupling strategy to simulation ability lifecycle. Avoids needing a "component" owner for abilities. |
| 2026-02-24 | Effects apply to both stationary and moving fleets | User approved. Most realistic - can't avoid storm by sitting still. Both take effects each tick proportional to presence. |
| 2026-02-24 | Separate loader for storm types (like system_blueprints), NOT GameRegistries | Avoids modifying GameRegistries dataclass, RegistryManager, hydrate(), clear(), DefaultRegistryProvider, TestRegistryProvider, registry_loader.py, and every test fixture. Storm instances self-describe (carry type name, effects). User agreed after pros/cons discussion. |
| 2026-02-24 | Storm entity lives in `game/strategy/data/storm.py` | Spatial entity tied to hex grid like Star, Planet, WarpPoint. Follows established strategy layer data model pattern. |
| 2026-02-24 | AreaEffectManager is a stateless service, not a turn engine sub-engine | Consumed by multiple engines (movement, environmental, conflict) and UI. A service in `game/strategy/services/` is the right abstraction. |
| 2026-02-24 | New Phase 0f in tick loop for environmental processing | After economy phases (0-0e), before movement (2-3). Matches architecture of existing engine delegation. |
| 2026-02-24 | SHIELD_CAPACITY_MULT as new StatKey | Existing CAPACITY_MULT is for generic ResourceStorage capacity. Dedicated shield mult allows targeting shields without affecting cargo/ammo. |
| 2026-02-24 | Irregular hex clusters via random walk algorithm | Organic shapes within 1-10 hex constraint. Implemented as `hex_random_cluster()` utility in hex_math.py. |
| 2026-02-24 | Nebulae transparent PNGs for storm rendering | 6 variants already exist at 1024x1024. Currently unused. Deterministic selection via `hash(storm)` seed. |
