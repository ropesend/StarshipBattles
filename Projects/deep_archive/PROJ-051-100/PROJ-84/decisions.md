# PROJ-84: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-09 | Project initialized | Starting point for Ship Layer Data Typed Structures |
| 2026-02-09 | Drop dead `hp` field from LayerData | The `hp` key is initialized to 0 in every layer dict but never read or written after init. It's confused with `ship.hp` (a cached property calculating from component HP). Removing it cleans up the model. |
| 2026-02-09 | Consolidate Ship/ShipComponentManager layer init | `Ship._initialize_layers()` and `ShipComponentManager.initialize_layers()` are near-identical copies. Ship should delegate to ShipComponentManager (or both should use `LayerData.create_hull()` / `LayerData.from_definition()`) to eliminate duplication. |
| 2026-02-09 | No backward-compat shims on LayerData | Per CLAUDE.md: "When a new system replaces an old one, ERADICATE the old system completely." No `__getitem__`, no dict-like interface, no compatibility layer. Clean break — all consumers updated to use attribute access. |
| 2026-02-09 | Mutable dataclass (not frozen) | `components` list is mutated via append/pop, `mass` is recalculated every stats cycle, `hp_pool`/`max_hp_pool` are updated for ARMOR layer. Freezing would require wholesale API changes. |
| 2026-02-09 | Use factory classmethods | `LayerData.create_hull()` and `LayerData.from_definition(l_def)` reduce boilerplate and centralize default values. A `clear()` method handles builder reset. |
| 2026-02-09 | Place LayerData in `game/simulation/entities/layer_data.py` | Follows existing pattern of entity classes in this directory. Keeps it co-located with Ship and ShipComponentManager. |
| 2026-02-09 | 7-phase plan ordering: core → simulation → serialization → UI → test scenarios → tests → cleanup | Core changes first to define the new type, then ripple outward. Each phase ends with tests passing. Test file updates are last (Phase 6) because they're the bulk of changes and benefit from all production code being updated first. |
